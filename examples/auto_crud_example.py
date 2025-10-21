"""
自动 CRUD 完整示例
展示如何使用自动化工具快速构建 API
"""

# ============================================================
# 方式 1：使用装饰器自动生成 Schema
# ============================================================

from app.core.auto_schema import auto_schema
from app.core.models.base import BaseModel as Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

@auto_schema()  # 自动生成 Response、Create、Update Schema
class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # 自动在 Response 中排除
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# 使用自动生成的 Schema
print("✅ 用户模型已自动生成 Schema：")
print(f"  - User.ResponseSchema")
print(f"  - User.CreateSchema")
print(f"  - User.UpdateSchema")

# ============================================================
# 方式 2：手动使用 SchemaGenerator
# ============================================================

from app.core.auto_schema import SchemaGenerator
from app.models.entities.system.user_management import Role

# 一次性生成所有 Schema
RoleSchemas = SchemaGenerator.create_all_schemas(Role)

RoleResponse = RoleSchemas['Response']
RoleCreate = RoleSchemas['Create']
RoleUpdate = RoleSchemas['Update']

print("\n✅ 角色 Schema 已手动生成")

# ============================================================
# 方式 3：使用 AutoCRUD 自动生成完整 API
# ============================================================

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.auto_crud import AutoCRUD, BatchAutoCRUD
from app.core.database import get_db

app = FastAPI(title="自动化 API 示例")

# 3.1 基础用法 - 自动生成用户 CRUD
user_crud = AutoCRUD(
    User,
    prefix="/users",
    tags=["用户管理"],
    search_fields=["username", "email", "name"]  # 支持搜索的字段
)

# 注册路由 - 自动生成 5 个接口！
app.include_router(user_crud.router, prefix="/api/v1")

"""
自动生成的路由：
  GET    /api/v1/users              获取用户列表（支持分页、搜索）
  GET    /api/v1/users/{id}         获取用户详情
  POST   /api/v1/users              创建用户
  PUT    /api/v1/users/{id}         更新用户
  DELETE /api/v1/users/{id}         删除用户
"""

# 3.2 扩展自定义路由
from typing import List
from pydantic import BaseModel

class BatchDeleteRequest(BaseModel):
    user_ids: List[int]

@user_crud.router.post("/batch-delete", summary="批量删除用户")
async def batch_delete_users(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """批量删除用户（自定义逻辑）"""
    deleted_count = db.query(User).filter(User.id.in_(request.user_ids)).delete()
    db.commit()
    
    return {
        "success": True,
        "message": f"成功删除 {deleted_count} 个用户",
        "data": {"deleted_count": deleted_count}
    }

@user_crud.router.post("/{id}/reset-password", summary="重置密码")
async def reset_password(
    id: int,
    new_password: str,
    db: Session = Depends(get_db)
):
    """重置用户密码（自定义逻辑）"""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}
    
    # 加密密码
    from app.core.security import get_password_hash
    user.password = get_password_hash(new_password)
    db.commit()
    
    return {"success": True, "message": "密码重置成功"}

# 3.3 批量生成多个模型的 CRUD
from app.models.entities.system.user_management import Role, Dept, Post

batch_crud = BatchAutoCRUD(
    models=[Role, Dept, Post],
    prefix="/api/v1",
    search_fields=["name"]  # 统一配置
)

app.include_router(batch_crud.router)

"""
自动生成的路由：
  角色管理（15个接口）：
    GET    /api/v1/roles              获取角色列表
    GET    /api/v1/roles/{id}         获取角色详情
    POST   /api/v1/roles              创建角色
    PUT    /api/v1/roles/{id}         更新角色
    DELETE /api/v1/roles/{id}         删除角色
  
  部门管理（5个接口）
  岗位管理（5个接口）
"""

# ============================================================
# 方式 4：混合使用 - 装饰器控制器 + 自动 Schema
# ============================================================

from app.core.decorators.controller import controller, get, post, put, delete, BaseController, ApiResponse
from app.services.user_service import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@controller(prefix="/advanced-users", tags=["高级用户管理"])
class AdvancedUserController(BaseController):
    """高级用户控制器 - 使用装饰器 + 自动 Schema"""
    
    @get("", summary="获取用户列表")
    async def get_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str = None,
        user_service: UserService = Depends(get_user_service)
    ) -> ApiResponse:
        """获取用户列表（业务逻辑在 Service 层）"""
        result = user_service.get_user_list(page, per_page, search)
        
        # 使用自动生成的 Schema 序列化
        serialized_items = [User.ResponseSchema.from_orm(item) for item in result['items']]
        result['items'] = serialized_items
        
        return self.success(data=result)
    
    @post("", summary="创建用户")
    async def create_user(
        self,
        user_data: User.CreateSchema,  # 使用自动生成的 Schema
        user_service: UserService = Depends(get_user_service)
    ) -> ApiResponse:
        """创建用户"""
        user = user_service.create_user(user_data)
        return self.success(data=User.ResponseSchema.from_orm(user), message="创建成功")
    
    @put("/{user_id}", summary="更新用户")
    async def update_user(
        self,
        user_id: int,
        user_data: User.UpdateSchema,  # 使用自动生成的 Schema
        user_service: UserService = Depends(get_user_service)
    ) -> ApiResponse:
        """更新用户"""
        user = user_service.update_user(user_id, user_data)
        return self.success(data=User.ResponseSchema.from_orm(user), message="更新成功")

# 注册装饰器控制器
app.include_router(AdvancedUserController.router, prefix="/api/v1")

# ============================================================
# 方式 5：终极方案 - 零代码生成
# ============================================================

"""
如果你的 API 都是标准 CRUD，可以这样：

# app/api/v1/auto_routes.py
from app.core.auto_crud import BatchAutoCRUD
from app.models.entities.system import User, Role, Dept, Post, Menu
from app.models.entities.common import FileList, OperationLog, LoginLog

# 一行代码生成所有模型的 CRUD API
auto_api = BatchAutoCRUD(
    models=[User, Role, Dept, Post, Menu, FileList, OperationLog, LoginLog],
    prefix="/api/v1"
)

# main.py
app.include_router(auto_api.router)

# 完成！自动生成了 40+ 个 API 接口
"""

# ============================================================
# 对比：代码量差异
# ============================================================

print("\n" + "="*60)
print("📊 代码量对比")
print("="*60)

print("""
手动编写（传统方式）：
  - Schema 定义：       ~80 行（UserResponse, UserCreate, UserUpdate）
  - Service 层：        ~150 行（增删改查业务逻辑）
  - Controller 层：     ~200 行（5个接口）
  - 总计：             ~430 行代码
  
自动生成（本方案）：
  - 装饰器：            1 行（@auto_schema()）
  - AutoCRUD：          3 行（创建 + 注册）
  - 总计：             4 行代码
  
💡 代码减少：99% ！
""")

print("="*60)
print("✨ 核心优势")
print("="*60)

print("""
1. ✅ 零样板代码       - 装饰器自动生成 Schema
2. ✅ 一行生成 CRUD    - AutoCRUD 自动生成所有接口
3. ✅ 支持自定义扩展   - 随时添加自定义路由
4. ✅ 类型完全安全     - 完整的类型提示
5. ✅ 自动文档生成     - Swagger 自动更新
6. ✅ 易于维护         - 模型改动自动同步
7. ✅ 保留装饰器风格   - 优雅的代码组织
8. ✅ 渐进式采用       - 可以逐步迁移
""")

# ============================================================
# 运行示例
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 启动 API 服务器")
    print("="*60)
    print("\n访问 http://localhost:8000/docs 查看自动生成的 API 文档\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

