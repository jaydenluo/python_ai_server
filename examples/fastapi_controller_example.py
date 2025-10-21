"""
FastAPI 标准控制器示例
展示如何使用 FastAPI 最佳实践重写控制器
"""

# ============================================================
# 1. Pydantic Schemas (数据验证和序列化)
# ============================================================
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    name: Optional[str] = Field(None, max_length=100, description="姓名")
    mobile: Optional[str] = Field(None, regex=r"^1[3-9]\d{9}$", description="手机号")
    gender: Optional[GenderEnum] = Field(GenderEnum.OTHER, description="性别")
    is_active: bool = Field(True, description="是否激活")


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(..., min_length=8, max_length=50, description="密码")
    role_ids: List[int] = Field(default=[], description="角色ID列表")
    dept_id: Optional[int] = Field(None, description="部门ID")
    post_ids: List[int] = Field(default=[], description="岗位ID列表")
    
    @validator('password')
    def validate_password(cls, v):
        """密码强度验证"""
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含字母')
        return v


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=100)
    mobile: Optional[str] = Field(None, regex=r"^1[3-9]\d{9}$")
    gender: Optional[GenderEnum] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    dept_id: Optional[int] = None
    post_ids: Optional[List[int]] = None


class RoleInfo(BaseModel):
    """角色信息"""
    id: int
    name: str
    key: str
    
    class Config:
        from_attributes = True


class DeptInfo(BaseModel):
    """部门信息"""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """用户响应模型（自动隐藏敏感字段）"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    dept: Optional[DeptInfo] = None
    roles: List[RoleInfo] = []
    
    class Config:
        from_attributes = True  # 允许从 ORM 模型转换


class UserListItem(BaseModel):
    """用户列表项（简化信息）"""
    id: int
    username: str
    email: str
    name: Optional[str]
    is_active: bool
    dept_name: Optional[str] = None
    role_names: List[str] = []
    
    class Config:
        from_attributes = True


class PaginatedUserList(BaseModel):
    """分页用户列表"""
    items: List[UserListItem]
    total: int
    page: int
    per_page: int
    pages: int


class ApiResponse(BaseModel):
    """统一 API 响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================
# 2. Service 层 (业务逻辑)
# ============================================================
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.entities.system.user_management import User, Role, Dept, Post


class UserService:
    """用户服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_list(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        dept_id: Optional[int] = None,
        role_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """
        获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            dept_id: 部门ID
            role_id: 角色ID
            is_active: 是否激活
        
        Returns:
            {items: List[User], total: int, page: int, per_page: int, pages: int}
        """
        query = self.db.query(User)
        
        # 应用过滤条件
        filters = []
        
        if search:
            # 模糊搜索：用户名、姓名、邮箱、手机号
            search_filter = or_(
                User.username.like(f"%{search}%"),
                User.name.like(f"%{search}%"),
                User.email.like(f"%{search}%"),
                User.mobile.like(f"%{search}%")
            )
            filters.append(search_filter)
        
        if dept_id:
            filters.append(User.dept_id == dept_id)
        
        if role_id:
            # 通过角色过滤（多对多关系）
            query = query.join(User.roles).filter(Role.id == role_id)
        
        if is_active is not None:
            filters.append(User.is_active == is_active)
        
        # 应用所有过滤条件
        if filters:
            query = query.filter(and_(*filters))
        
        # 统计总数
        total = query.count()
        
        # 计算总页数
        pages = (total + per_page - 1) // per_page
        
        # 分页查询
        offset = (page - 1) * per_page
        users = query.order_by(User.created_at.desc()).offset(offset).limit(per_page).all()
        
        # 组装用户列表数据（添加关联信息）
        user_items = []
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
                "dept_name": user.dept.name if user.dept else None,
                "role_names": [role.name for role in user.roles]
            }
            user_items.append(user_dict)
        
        return {
            "items": user_items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        获取用户详情
        
        Args:
            user_id: 用户ID
        
        Returns:
            User 对象
        
        Raises:
            HTTPException: 用户不存在时抛出 404
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户 ID {user_id} 不存在"
            )
        return user
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        创建用户
        
        Args:
            user_data: 用户创建数据
        
        Returns:
            创建的 User 对象
        
        Raises:
            HTTPException: 用户名或邮箱已存在时抛出 400
        """
        # 检查用户名是否已存在
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"用户名 '{user_data.username}' 已存在"
            )
        
        # 检查邮箱是否已存在
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"邮箱 '{user_data.email}' 已存在"
            )
        
        # 创建用户对象
        user_dict = user_data.dict(exclude={"password", "role_ids", "post_ids"})
        user = User(**user_dict)
        
        # 设置密码（哈希加密）
        from app.core.security import get_password_hash
        user.password = get_password_hash(user_data.password)
        
        self.db.add(user)
        self.db.flush()  # 获取 user.id
        
        # 设置角色关联
        if user_data.role_ids:
            roles = self.db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            if len(roles) != len(user_data.role_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部分角色ID不存在"
                )
            user.roles = roles
        
        # 设置岗位关联
        if user_data.post_ids:
            posts = self.db.query(Post).filter(Post.id.in_(user_data.post_ids)).all()
            if len(posts) != len(user_data.post_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部分岗位ID不存在"
                )
            user.posts = posts
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        更新用户
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
        
        Returns:
            更新后的 User 对象
        """
        user = self.get_user_by_id(user_id)
        
        # 检查用户名唯一性
        if user_data.username and user_data.username != user.username:
            if self.db.query(User).filter(User.username == user_data.username).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"用户名 '{user_data.username}' 已存在"
                )
        
        # 检查邮箱唯一性
        if user_data.email and user_data.email != user.email:
            if self.db.query(User).filter(User.email == user_data.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"邮箱 '{user_data.email}' 已存在"
                )
        
        # 更新基本字段
        update_dict = user_data.dict(
            exclude_unset=True,  # 只更新提供的字段
            exclude={"role_ids", "post_ids"}
        )
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        # 更新角色关联
        if user_data.role_ids is not None:
            roles = self.db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            user.roles = roles
        
        # 更新岗位关联
        if user_data.post_ids is not None:
            posts = self.db.query(Post).filter(Post.id.in_(user_data.post_ids)).all()
            user.posts = posts
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: int) -> None:
        """
        删除用户
        
        Args:
            user_id: 用户ID
        
        Raises:
            HTTPException: 用户不存在或不能删除时抛出异常
        """
        user = self.get_user_by_id(user_id)
        
        # 检查是否为超级管理员
        if getattr(user, 'is_superuser', False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除超级管理员账户"
            )
        
        # 软删除或硬删除
        self.db.delete(user)
        self.db.commit()
    
    def batch_delete_users(self, user_ids: List[int]) -> int:
        """
        批量删除用户
        
        Args:
            user_ids: 用户ID列表
        
        Returns:
            删除的用户数量
        """
        # 查找所有要删除的用户
        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        
        # 检查是否包含超级管理员
        for user in users:
            if getattr(user, 'is_superuser', False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"用户 ID {user.id} 是超级管理员，不能删除"
                )
        
        # 批量删除
        count = len(users)
        for user in users:
            self.db.delete(user)
        
        self.db.commit()
        return count


# ============================================================
# 3. 依赖注入
# ============================================================
from fastapi import Depends
from app.core.database import get_db


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """获取用户服务实例"""
    return UserService(db)


# ============================================================
# 4. API 路由（控制器）
# ============================================================
from fastapi import APIRouter, Query, Path, Body


router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="获取用户列表",
    description="分页获取用户列表，支持搜索和多条件筛选"
)
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名、姓名、邮箱、手机号）"),
    dept_id: Optional[int] = Query(None, description="部门ID筛选"),
    role_id: Optional[int] = Query(None, description="角色ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取用户列表
    
    - **page**: 页码，从 1 开始
    - **per_page**: 每页数量，最大 100
    - **search**: 搜索关键词，支持用户名、姓名、邮箱、手机号
    - **dept_id**: 按部门筛选
    - **role_id**: 按角色筛选
    - **is_active**: 按激活状态筛选
    """
    result = user_service.get_user_list(
        page=page,
        per_page=per_page,
        search=search,
        dept_id=dept_id,
        role_id=role_id,
        is_active=is_active
    )
    
    return {
        "success": True,
        "message": "获取用户列表成功",
        "data": result,
        "timestamp": datetime.utcnow()
    }


@router.get(
    "/{user_id}",
    response_model=ApiResponse,
    summary="获取用户详情",
    description="根据用户ID获取用户详细信息"
)
async def get_user_detail(
    user_id: int = Path(..., description="用户ID", gt=0),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取用户详情
    
    - **user_id**: 用户ID
    """
    user = user_service.get_user_by_id(user_id)
    
    return {
        "success": True,
        "message": "获取用户详情成功",
        "data": UserResponse.from_orm(user),
        "timestamp": datetime.utcnow()
    }


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新的用户账户"
)
async def create_user(
    user_data: UserCreate = Body(..., description="用户创建数据"),
    user_service: UserService = Depends(get_user_service)
):
    """
    创建用户
    
    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱（必须是有效邮箱格式，唯一）
    - **password**: 密码（至少8字符，必须包含字母和数字）
    - **name**: 姓名（可选）
    - **mobile**: 手机号（可选，必须是有效的中国手机号）
    - **role_ids**: 角色ID列表（可选）
    - **dept_id**: 部门ID（可选）
    """
    user = user_service.create_user(user_data)
    
    return {
        "success": True,
        "message": "创建用户成功",
        "data": UserResponse.from_orm(user),
        "timestamp": datetime.utcnow()
    }


@router.put(
    "/{user_id}",
    response_model=ApiResponse,
    summary="更新用户",
    description="更新用户信息"
)
async def update_user(
    user_id: int = Path(..., description="用户ID", gt=0),
    user_data: UserUpdate = Body(..., description="用户更新数据"),
    user_service: UserService = Depends(get_user_service)
):
    """
    更新用户
    
    - **user_id**: 用户ID
    - 其他字段都是可选的，只更新提供的字段
    """
    user = user_service.update_user(user_id, user_data)
    
    return {
        "success": True,
        "message": "更新用户成功",
        "data": UserResponse.from_orm(user),
        "timestamp": datetime.utcnow()
    }


@router.delete(
    "/{user_id}",
    response_model=ApiResponse,
    summary="删除用户",
    description="删除指定用户"
)
async def delete_user(
    user_id: int = Path(..., description="用户ID", gt=0),
    user_service: UserService = Depends(get_user_service)
):
    """
    删除用户
    
    - **user_id**: 用户ID
    
    注意：不能删除超级管理员账户
    """
    user_service.delete_user(user_id)
    
    return {
        "success": True,
        "message": "删除用户成功",
        "data": None,
        "timestamp": datetime.utcnow()
    }


@router.post(
    "/batch-delete",
    response_model=ApiResponse,
    summary="批量删除用户",
    description="批量删除多个用户"
)
async def batch_delete_users(
    user_ids: List[int] = Body(..., description="用户ID列表", min_items=1),
    user_service: UserService = Depends(get_user_service)
):
    """
    批量删除用户
    
    - **user_ids**: 用户ID列表
    
    注意：不能删除超级管理员账户
    """
    count = user_service.batch_delete_users(user_ids)
    
    return {
        "success": True,
        "message": f"成功删除 {count} 个用户",
        "data": {"deleted_count": count},
        "timestamp": datetime.utcnow()
    }


# ============================================================
# 5. 使用示例
# ============================================================

"""
在 main.py 中注册路由：

from fastapi import FastAPI
from examples.fastapi_controller_example import router

app = FastAPI()
app.include_router(router)

启动后，访问：
- http://localhost:8000/docs  -> Swagger UI 自动文档
- http://localhost:8000/redoc -> ReDoc 自动文档

API 调用示例：

1. 获取用户列表：
   GET /api/v1/users?page=1&per_page=20&search=张三

2. 获取用户详情：
   GET /api/v1/users/1

3. 创建用户：
   POST /api/v1/users
   Body: {
       "username": "zhangsan",
       "email": "zhangsan@example.com",
       "password": "password123",
       "name": "张三",
       "mobile": "13800138000",
       "role_ids": [1, 2],
       "dept_id": 1
   }

4. 更新用户：
   PUT /api/v1/users/1
   Body: {
       "name": "张三丰",
       "is_active": false
   }

5. 删除用户：
   DELETE /api/v1/users/1

6. 批量删除：
   POST /api/v1/users/batch-delete
   Body: {
       "user_ids": [2, 3, 4]
   }
"""

