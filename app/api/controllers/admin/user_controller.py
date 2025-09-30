"""
管理员用户控制器
负责管理员用户管理功能
"""

from typing import Dict, Any, List
from app.api.controllers.base import ResourceController, APIResponse
from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    admin_required, rate_limit, cache, validate, api_doc
)
from app.models.user import User
from app.core.middleware.base import Request, Response


@api_controller(prefix="/admin", version="v1", middleware=["auth", "admin"])
class AdminUserController(ResourceController):
    """管理员用户控制器 - 管理员专用功能"""
    
    def __init__(self):
        super().__init__(User)
    
    @get("/users", name="admin.users.index")
    @admin_required
    @rate_limit(requests_per_minute=100, requests_per_hour=2000)
    @cache(ttl=300)
    @api_doc(
        summary="获取所有用户列表",
        description="管理员获取系统中所有用户的详细信息",
        tags=["管理员-用户管理"],
        responses={
            "200": {"description": "成功获取用户列表"},
            "401": {"description": "未授权访问"},
            "403": {"description": "权限不足"}
        }
    )
    async def index(self, request: Request) -> Response:
        """获取所有用户列表 - 管理员专用"""
        try:
            # 获取查询参数
            page = int(request.query_params.get("page", 1))
            per_page = int(request.query_params.get("per_page", 20))
            search = request.query_params.get("search", "")
            role = request.query_params.get("role", "")
            status = request.query_params.get("status", "")
            
            # 构建查询
            query = self.query
            
            # 搜索功能
            if search:
                query = query.where("username", "like", f"%{search}%")
            
            # 角色筛选
            if role:
                query = query.where("role", role)
            
            # 状态筛选
            if status:
                query = query.where("status", status)
            
            # 分页
            users = query.paginate(page, per_page)
            
            # 转换数据格式
            users_data = []
            for user in users:
                user_dict = user.to_dict()
                # 管理员可以看到所有信息
                users_data.append(user_dict)
            
            return self._create_response(
                self.success_response(
                    data={
                        "users": users_data,
                        "pagination": {
                            "page": page,
                            "per_page": per_page,
                            "total": query.count()
                        }
                    },
                    message="获取用户列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"获取用户列表失败: {str(e)}")
            )
    
    @get("/users/{id}", name="admin.users.show")
    @admin_required
    @cache(ttl=600)
    @api_doc(
        summary="获取用户详细信息",
        description="管理员获取指定用户的详细信息",
        tags=["管理员-用户管理"],
        responses={
            "200": {"description": "成功获取用户信息"},
            "404": {"description": "用户不存在"},
            "403": {"description": "权限不足"}
        }
    )
    async def show(self, request: Request) -> Response:
        """获取用户详细信息 - 管理员专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            user_id = path_parts[-1]
            
            # 查找用户
            user = self.query.find(user_id)
            
            if not user:
                return self._create_response(
                    self.not_found_response("用户不存在")
                )
            
            # 转换数据格式 - 管理员可以看到所有信息
            user_dict = user.to_dict()
            
            return self._create_response(
                self.success_response(
                    data=user_dict,
                    message="获取用户信息成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"获取用户信息失败: {str(e)}")
            )
    
    @post("/users", name="admin.users.store")
    @admin_required
    @validate({
        "username": "required|unique:users,username",
        "email": "required|email|unique:users,email",
        "password": "required|min:8",
        "role": "required|in:admin,user,guest"
    })
    @api_doc(
        summary="创建用户",
        description="管理员创建新用户账户",
        tags=["管理员-用户管理"],
        responses={
            "201": {"description": "用户创建成功"},
            "400": {"description": "请求参数错误"},
            "403": {"description": "权限不足"}
        }
    )
    async def store(self, request: Request) -> Response:
        """创建用户 - 管理员专用"""
        try:
            # 获取请求数据
            data = request.json
            
            # 创建用户
            user = User()
            user.username = data.get("username")
            user.email = data.get("email")
            user.password = data.get("password")
            user.role = data.get("role", "user")
            user.status = "active"
            
            # 保存用户
            user.save()
            
            return self._create_response(
                self.success_response(
                    data=user.to_dict(),
                    message="用户创建成功",
                    status_code=201
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"创建用户失败: {str(e)}")
            )
    
    @put("/users/{id}", name="admin.users.update")
    @admin_required
    @validate({
        "username": "required",
        "email": "required|email",
        "role": "required|in:admin,user,guest",
        "status": "required|in:active,inactive,suspended"
    })
    @api_doc(
        summary="更新用户信息",
        description="管理员更新用户信息",
        tags=["管理员-用户管理"],
        responses={
            "200": {"description": "用户更新成功"},
            "404": {"description": "用户不存在"},
            "403": {"description": "权限不足"}
        }
    )
    async def update(self, request: Request) -> Response:
        """更新用户信息 - 管理员专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            user_id = path_parts[-1]
            
            # 查找用户
            user = self.query.find(user_id)
            
            if not user:
                return self._create_response(
                    self.not_found_response("用户不存在")
                )
            
            # 获取请求数据
            data = request.json
            
            # 更新用户信息
            user.username = data.get("username", user.username)
            user.email = data.get("email", user.email)
            user.role = data.get("role", user.role)
            user.status = data.get("status", user.status)
            
            # 保存更新
            user.save()
            
            return self._create_response(
                self.success_response(
                    data=user.to_dict(),
                    message="用户更新成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"更新用户失败: {str(e)}")
            )
    
    @delete("/users/{id}", name="admin.users.destroy")
    @admin_required
    @api_doc(
        summary="删除用户",
        description="管理员删除用户账户",
        tags=["管理员-用户管理"],
        responses={
            "200": {"description": "用户删除成功"},
            "404": {"description": "用户不存在"},
            "403": {"description": "权限不足"}
        }
    )
    async def destroy(self, request: Request) -> Response:
        """删除用户 - 管理员专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            user_id = path_parts[-1]
            
            # 查找用户
            user = self.query.find(user_id)
            
            if not user:
                return self._create_response(
                    self.not_found_response("用户不存在")
                )
            
            # 删除用户
            user.delete()
            
            return self._create_response(
                self.success_response(
                    message="用户删除成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"删除用户失败: {str(e)}")
            )
    
    @post("/users/{id}/reset-password", name="admin.users.reset_password")
    @admin_required
    @api_doc(
        summary="重置用户密码",
        description="管理员重置用户密码",
        tags=["管理员-用户管理"],
        responses={
            "200": {"description": "密码重置成功"},
            "404": {"description": "用户不存在"},
            "403": {"description": "权限不足"}
        }
    )
    async def reset_password(self, request: Request) -> Response:
        """重置用户密码 - 管理员专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            user_id = path_parts[-2]  # 因为路径是 /users/{id}/reset-password
            
            # 查找用户
            user = self.query.find(user_id)
            
            if not user:
                return self._create_response(
                    self.not_found_response("用户不存在")
                )
            
            # 生成新密码
            import secrets
            new_password = secrets.token_urlsafe(12)
            
            # 更新密码
            user.password = new_password
            user.save()
            
            return self._create_response(
                self.success_response(
                    data={"new_password": new_password},
                    message="密码重置成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"重置密码失败: {str(e)}")
            )