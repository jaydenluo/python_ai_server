"""
自动 CRUD 生成器
一行代码生成完整的 CRUD API
"""

from typing import Type, TypeVar, Generic, Optional, List, Callable, Any
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy import func, and_, or_
from pydantic import BaseModel
from datetime import datetime

from app.core.auto_schema import SchemaGenerator

T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    per_page: int = 20


class ListResponse(BaseModel, Generic[T]):
    """列表响应"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    timestamp: datetime = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class AutoCRUD(Generic[T]):
    """
    自动 CRUD 生成器
    
    用法：
        from app.models.entities.system.user_management import User
        
        user_crud = AutoCRUD(User, prefix="/users", tags=["用户管理"])
        app.include_router(user_crud.router)
    """
    
    def __init__(
        self,
        model: Type[DeclarativeMeta],
        prefix: str = None,
        tags: List[str] = None,
        dependencies: List[Depends] = None,
        db_dependency: Callable = None,
        # Schema 自定义
        response_schema: Type[BaseModel] = None,
        create_schema: Type[BaseModel] = None,
        update_schema: Type[BaseModel] = None,
        # 功能开关
        enable_list: bool = True,
        enable_get: bool = True,
        enable_create: bool = True,
        enable_update: bool = True,
        enable_delete: bool = True,
        # 搜索配置
        search_fields: List[str] = None,
    ):
        """
        初始化自动 CRUD
        
        Args:
            model: SQLAlchemy 模型
            prefix: 路由前缀
            tags: 标签
            dependencies: 依赖项
            db_dependency: 数据库会话依赖
            response_schema: 自定义响应 Schema
            create_schema: 自定义创建 Schema
            update_schema: 自定义更新 Schema
            enable_*: 功能开关
            search_fields: 可搜索的字段
        """
        self.model = model
        self.prefix = prefix or f"/{model.__tablename__}"
        self.tags = tags or [model.__name__]
        self.dependencies = dependencies or []
        self.db_dependency = db_dependency or self._default_db_dependency
        self.search_fields = search_fields or []
        
        # 自动生成 Schema（如果没有提供）
        if response_schema is None or create_schema is None or update_schema is None:
            auto_schemas = SchemaGenerator.create_all_schemas(model)
            self.ResponseSchema = response_schema or auto_schemas['Response']
            self.CreateSchema = create_schema or auto_schemas['Create']
            self.UpdateSchema = update_schema or auto_schemas['Update']
        else:
            self.ResponseSchema = response_schema
            self.CreateSchema = create_schema
            self.UpdateSchema = update_schema
        
        # 创建路由器
        self.router = APIRouter(
            prefix=self.prefix,
            tags=self.tags,
            dependencies=self.dependencies
        )
        
        # 注册路由
        if enable_list:
            self._register_list_route()
        if enable_get:
            self._register_get_route()
        if enable_create:
            self._register_create_route()
        if enable_update:
            self._register_update_route()
        if enable_delete:
            self._register_delete_route()
    
    def _default_db_dependency(self):
        """默认数据库依赖（需要用户实现）"""
        from app.core.database import get_db
        return Depends(get_db)
    
    def _apply_search(self, query, search: str):
        """应用搜索"""
        if not search or not self.search_fields:
            return query
        
        filters = []
        for field_name in self.search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                filters.append(field.like(f"%{search}%"))
        
        if filters:
            query = query.filter(or_(*filters))
        
        return query
    
    def _register_list_route(self):
        """注册列表路由"""
        
        @self.router.get(
            "",
            response_model=ApiResponse[ListResponse[self.ResponseSchema]],
            summary=f"获取{self.model.__name__}列表"
        )
        async def get_list(
            page: int = Query(1, ge=1, description="页码"),
            per_page: int = Query(20, ge=1, le=100, description="每页数量"),
            search: Optional[str] = Query(None, description="搜索关键词"),
            db: Session = self.db_dependency()
        ):
            """获取列表"""
            query = db.query(self.model)
            
            # 应用搜索
            query = self._apply_search(query, search)
            
            # 统计总数
            total = query.count()
            
            # 计算分页
            pages = (total + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # 查询数据
            items = query.offset(offset).limit(per_page).all()
            
            return ApiResponse(
                success=True,
                message="获取成功",
                data=ListResponse(
                    items=items,
                    total=total,
                    page=page,
                    per_page=per_page,
                    pages=pages
                )
            )
    
    def _register_get_route(self):
        """注册获取详情路由"""
        
        @self.router.get(
            "/{id}",
            response_model=ApiResponse[self.ResponseSchema],
            summary=f"获取{self.model.__name__}详情"
        )
        async def get_one(
            id: int = Path(..., description="ID", gt=0),
            db: Session = self.db_dependency()
        ):
            """获取详情"""
            item = db.query(self.model).filter(self.model.id == id).first()
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} 不存在"
                )
            
            return ApiResponse(
                success=True,
                message="获取成功",
                data=item
            )
    
    def _register_create_route(self):
        """注册创建路由"""
        
        @self.router.post(
            "",
            response_model=ApiResponse[self.ResponseSchema],
            status_code=status.HTTP_201_CREATED,
            summary=f"创建{self.model.__name__}"
        )
        async def create(
            data: self.CreateSchema = Body(..., description="创建数据"),
            db: Session = self.db_dependency()
        ):
            """创建"""
            # 创建实例
            item = self.model(**data.dict())
            
            db.add(item)
            db.commit()
            db.refresh(item)
            
            return ApiResponse(
                success=True,
                message="创建成功",
                data=item
            )
    
    def _register_update_route(self):
        """注册更新路由"""
        
        @self.router.put(
            "/{id}",
            response_model=ApiResponse[self.ResponseSchema],
            summary=f"更新{self.model.__name__}"
        )
        async def update(
            id: int = Path(..., description="ID", gt=0),
            data: self.UpdateSchema = Body(..., description="更新数据"),
            db: Session = self.db_dependency()
        ):
            """更新"""
            item = db.query(self.model).filter(self.model.id == id).first()
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} 不存在"
                )
            
            # 更新字段
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(item, key, value)
            
            db.commit()
            db.refresh(item)
            
            return ApiResponse(
                success=True,
                message="更新成功",
                data=item
            )
    
    def _register_delete_route(self):
        """注册删除路由"""
        
        @self.router.delete(
            "/{id}",
            response_model=ApiResponse[None],
            summary=f"删除{self.model.__name__}"
        )
        async def delete(
            id: int = Path(..., description="ID", gt=0),
            db: Session = self.db_dependency()
        ):
            """删除"""
            item = db.query(self.model).filter(self.model.id == id).first()
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} 不存在"
                )
            
            db.delete(item)
            db.commit()
            
            return ApiResponse(
                success=True,
                message="删除成功",
                data=None
            )
    
    def add_custom_route(
        self,
        path: str,
        methods: List[str],
        endpoint: Callable,
        **kwargs
    ):
        """添加自定义路由"""
        for method in methods:
            route_method = getattr(self.router, method.lower())
            route_method(path, **kwargs)(endpoint)
        
        return self


# 批量 CRUD 生成器
class BatchAutoCRUD:
    """批量生成 CRUD"""
    
    def __init__(
        self,
        models: List[Type[DeclarativeMeta]],
        prefix: str = "/api/v1",
        **kwargs
    ):
        """
        批量生成 CRUD
        
        Args:
            models: 模型列表
            prefix: 统一前缀
            **kwargs: 传递给 AutoCRUD 的参数
        """
        self.router = APIRouter(prefix=prefix)
        self.cruds = []
        
        for model in models:
            crud = AutoCRUD(model, **kwargs)
            self.cruds.append(crud)
            self.router.include_router(crud.router)


# 使用示例
if __name__ == "__main__":
    """
    # 基本用法
    from app.models.entities.system.user_management import User
    
    # 1. 自动生成 CRUD
    user_crud = AutoCRUD(User, tags=["用户管理"], search_fields=["username", "email", "name"])
    app.include_router(user_crud.router, prefix="/api/v1")
    
    # 自动生成以下路由：
    # GET    /api/v1/users          - 获取用户列表（支持搜索和分页）
    # GET    /api/v1/users/{id}     - 获取用户详情
    # POST   /api/v1/users          - 创建用户
    # PUT    /api/v1/users/{id}     - 更新用户
    # DELETE /api/v1/users/{id}     - 删除用户
    
    # 2. 添加自定义路由
    @user_crud.router.post("/batch-delete")
    async def batch_delete_users(user_ids: List[int], db: Session = Depends(get_db)):
        # 自定义批量删除逻辑
        pass
    
    # 3. 批量生成多个模型的 CRUD
    from app.models.entities.system import User, Role, Dept
    
    batch_crud = BatchAutoCRUD(
        models=[User, Role, Dept],
        prefix="/api/v1"
    )
    app.include_router(batch_crud.router)
    """
    pass

