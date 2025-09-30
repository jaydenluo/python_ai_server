"""
API认证控制器
负责认证相关功能
"""

from typing import Dict, Any, List
from app.api.controllers.base import ResourceController, APIResponse
from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    rate_limit, cache, validate, api_doc
)
from app.models.user import User
from app.services.auth.auth_service import auth_service
from app.core.middleware.base import Request, Response


@api_controller(prefix="/api", version="v1", middleware=["anonymous"])
class APIAuthController(ResourceController):
    """API认证控制器 - 认证相关功能"""
    
    def __init__(self):
        super().__init__(User)
    
    @post("/auth/login", name="api.auth.login")
    @rate_limit(requests_per_minute=10, requests_per_hour=100)
    @validate({
        "username": "required",
        "password": "required"
    })
    @api_doc(
        summary="用户登录",
        description="用户登录获取访问令牌",
        tags=["API-认证管理"],
        responses={
            "200": {"description": "登录成功"},
            "400": {"description": "请求参数错误"},
            "401": {"description": "用户名或密码错误"},
            "429": {"description": "请求过于频繁"}
        }
    )
    async def login(self, request: Request) -> Response:
        """用户登录 - API专用"""
        try:
            # 获取请求数据
            data = request.json
            username = data.get("username")
            password = data.get("password")
            
            # 验证用户凭据
            user = auth_service.authenticate(username, password)
            
            if not user:
                return self._create_response(
                    self.unauthorized_response("用户名或密码错误")
                )
            
            # 生成访问令牌
            token = auth_service.generate_token(user)
            
            return self._create_response(
                self.success_response(
                    data={
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role
                        },
                        "token": token,
                        "token_type": "Bearer",
                        "expires_in": 3600
                    },
                    message="登录成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"登录失败: {str(e)}")
            )
    
    @post("/auth/register", name="api.auth.register")
    @rate_limit(requests_per_minute=5, requests_per_hour=50)
    @validate({
        "username": "required|unique:users,username",
        "email": "required|email|unique:users,email",
        "password": "required|min:8",
        "password_confirmation": "required|same:password"
    })
    @api_doc(
        summary="用户注册",
        description="用户注册新账户",
        tags=["API-认证管理"],
        responses={
            "201": {"description": "注册成功"},
            "400": {"description": "请求参数错误"},
            "429": {"description": "请求过于频繁"}
        }
    )
    async def register(self, request: Request) -> Response:
        """用户注册 - API专用"""
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
            
            # 生成访问令牌
            token = auth_service.generate_token(user)
            
            # 隐藏敏感信息
            user_dict = user.to_dict()
            user_dict.pop("password", None)
            user_dict.pop("remember_token", None)
            
            return self._create_response(
                self.success_response(
                    data={
                        "user": user_dict,
                        "token": token,
                        "token_type": "Bearer",
                        "expires_in": 3600
                    },
                    message="注册成功",
                    status_code=201
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"注册失败: {str(e)}")
            )
    
    @post("/auth/logout", name="api.auth.logout")
    @rate_limit(requests_per_minute=20, requests_per_hour=200)
    @api_doc(
        summary="用户登出",
        description="用户登出并撤销访问令牌",
        tags=["API-认证管理"],
        responses={
            "200": {"description": "登出成功"},
            "401": {"description": "未授权访问"}
        }
    )
    async def logout(self, request: Request) -> Response:
        """用户登出 - API专用"""
        try:
            # 获取访问令牌
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return self._create_response(
                    self.unauthorized_response("无效的访问令牌")
                )
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            # 撤销令牌
            auth_service.revoke_token(token)
            
            return self._create_response(
                self.success_response(
                    message="登出成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"登出失败: {str(e)}")
            )
    
    @post("/auth/refresh", name="api.auth.refresh")
    @rate_limit(requests_per_minute=10, requests_per_hour=100)
    @api_doc(
        summary="刷新访问令牌",
        description="刷新访问令牌",
        tags=["API-认证管理"],
        responses={
            "200": {"description": "令牌刷新成功"},
            "401": {"description": "无效的访问令牌"}
        }
    )
    async def refresh(self, request: Request) -> Response:
        """刷新访问令牌 - API专用"""
        try:
            # 获取访问令牌
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return self._create_response(
                    self.unauthorized_response("无效的访问令牌")
                )
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            # 验证令牌
            user = auth_service.verify_token(token)
            
            if not user:
                return self._create_response(
                    self.unauthorized_response("无效的访问令牌")
                )
            
            # 生成新的访问令牌
            new_token = auth_service.generate_token(user)
            
            return self._create_response(
                self.success_response(
                    data={
                        "token": new_token,
                        "token_type": "Bearer",
                        "expires_in": 3600
                    },
                    message="令牌刷新成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"令牌刷新失败: {str(e)}")
            )
    
    @get("/auth/me", name="api.auth.me")
    @rate_limit(requests_per_minute=30, requests_per_hour=500)
    @cache(ttl=300)
    @api_doc(
        summary="获取当前用户信息",
        description="获取当前登录用户的信息",
        tags=["API-认证管理"],
        responses={
            "200": {"description": "成功获取用户信息"},
            "401": {"description": "未授权访问"}
        }
    )
    async def me(self, request: Request) -> Response:
        """获取当前用户信息 - API专用"""
        try:
            # 获取访问令牌
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return self._create_response(
                    self.unauthorized_response("无效的访问令牌")
                )
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            # 验证令牌
            user = auth_service.verify_token(token)
            
            if not user:
                return self._create_response(
                    self.unauthorized_response("无效的访问令牌")
                )
            
            # 隐藏敏感信息
            user_dict = user.to_dict()
            user_dict.pop("password", None)
            user_dict.pop("remember_token", None)
            
            return self._create_response(
                self.success_response(
                    data={"user": user_dict},
                    message="获取用户信息成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"获取用户信息失败: {str(e)}")
            )