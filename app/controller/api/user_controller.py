"""
API用户控制器
负责API用户管理功能
"""

from typing import Dict, Any, List
from app.core.controllers.base_controller import *
from app.models.entities.system.user_management import User


@api_controller(prefix="/api/user", tags=["API - 用户管理"])
@auth
class UserController(BaseController):
    """前端用户API控制器"""
    
    def __init__(self):
        super().__init__(User)
    
    @get("/users", name="api.users.index")
    @requires(["user", "read:user"])
    @title("获取用户列表")
    async def index(self, request: Request) -> Response:
        """获取用户列表 - API专用"""
        try:
            # 获取查询参数
            page = int(request.query_params.get("page", 1))
            per_page = int(request.query_params.get("per_page", 15))
            search = request.query_params.get("search", "")
            
            # 构建查询
            query = self.query
            
            # 搜索功能
            if search:
                query = query.where("username", "like", f"%{search}%")
            
            # 分页
            users = query.paginate(page, per_page)
            
            # 转换数据格式
            users_data = []
            for user in users:
                user_dict = user.to_dict()
                # 隐藏敏感信息
                user_dict.pop("password", None)
                user_dict.pop("remember_token", None)
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
    
    @get("/users/{id}", name="api.users.show")
    @auth
    @cache(ttl=600)
    @api_doc(
        summary="获取用户详细信息",
        description="获取指定用户的详细信息",
        tags=["API-用户管理"],
        responses={
            "200": {"description": "成功获取用户信息"},
            "404": {"description": "用户不存在"},
            "401": {"description": "未授权访问"}
        }
    )
    async def show(self, request: Request) -> Response:
        """获取用户详细信息 - API专用"""
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
            
            # 转换数据格式
            user_dict = user.to_dict()
            # 隐藏敏感信息
            user_dict.pop("password", None)
            user_dict.pop("remember_token", None)
            
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
    
    @post("/users", name="api.users.store")
    @auth
    @validate({
        "username": "required|unique:users,username",
        "email": "required|email|unique:users,email",
        "password": "required|min:8"
    })
    @api_doc(
        summary="创建用户",
        description="创建新的用户账户",
        tags=["API-用户管理"],
        responses={
            "201": {"description": "用户创建成功"},
            "400": {"description": "请求参数错误"},
            "401": {"description": "未授权访问"}
        }
    )
    async def store(self, request: Request) -> Response:
        """创建用户 - API专用"""
        try:
            # 获取请求数据
            data = request.json
            
            # 创建用户
            user = User()
            user.username = data.get("username")
            user.email = data.get("email")
            user.password = data.get("password")
            user.role = "user"
            user.status = "active"
            
            # 保存用户
            user.save()
            
            # 隐藏敏感信息
            user_dict = user.to_dict()
            user_dict.pop("password", None)
            user_dict.pop("remember_token", None)
            
            return self._create_response(
                self.success_response(
                    data=user_dict,
                    message="用户创建成功",
                    status_code=201
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"创建用户失败: {str(e)}")
            )
    
    @put("/users/{id}", name="api.users.update")
    @auth
    @validate({
        "username": "required",
        "email": "required|email"
    })
    @api_doc(
        summary="更新用户信息",
        description="更新用户信息",
        tags=["API-用户管理"],
        responses={
            "200": {"description": "用户更新成功"},
            "404": {"description": "用户不存在"},
            "401": {"description": "未授权访问"}
        }
    )
    async def update(self, request: Request) -> Response:
        """更新用户信息 - API专用"""
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
            
            # 保存更新
            user.save()
            
            # 隐藏敏感信息
            user_dict = user.to_dict()
            user_dict.pop("password", None)
            user_dict.pop("remember_token", None)
            
            return self._create_response(
                self.success_response(
                    data=user_dict,
                    message="用户更新成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"更新用户失败: {str(e)}")
            )
    
    @delete("/users/{id}", name="api.users.destroy")
    @auth
    @api_doc(
        summary="删除用户",
        description="删除用户账户",
        tags=["API-用户管理"],
        responses={
            "200": {"description": "用户删除成功"},
            "404": {"description": "用户不存在"},
            "401": {"description": "未授权访问"}
        }
    )
    async def destroy(self, request: Request) -> Response:
        """删除用户 - API专用"""
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