"""
认证中间件
处理用户认证和授权
"""

import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .base import Middleware, Request, Response


class AuthMiddleware(Middleware):
    """认证中间件"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 token_expire_hours: int = 24, **kwargs):
        super().__init__(**kwargs)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_hours = token_expire_hours
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理认证"""
        # 获取Authorization头
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                body={"error": "Invalid authorization header"}
            )
        
        token = auth_header[7:]  # 移除"Bearer "前缀
        
        try:
            # 验证JWT令牌
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查令牌是否过期
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return Response(
                    status_code=401,
                    headers={"Content-Type": "application/json"},
                    body={"error": "Token expired"}
                )
            
            # 将用户信息添加到请求中
            request.user = {
                "id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }
            
            # 继续处理请求
            return await next_handler()
            
        except jwt.InvalidTokenError:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                body={"error": "Invalid token"}
            )
        except Exception as e:
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                body={"error": f"Authentication error: {str(e)}"}
            )
    
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "roles": user_data.get("roles", []),
            "permissions": user_data.get("permissions", []),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.InvalidTokenError:
            return None


class PermissionMiddleware(Middleware):
    """权限中间件"""
    
    def __init__(self, required_permissions: list = None, **kwargs):
        super().__init__(**kwargs)
        self.required_permissions = required_permissions or []
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理权限验证"""
        if not request.user:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                body={"error": "Authentication required"}
            )
        
        user_permissions = request.user.get("permissions", [])
        
        # 检查是否有必需权限
        for permission in self.required_permissions:
            if permission not in user_permissions:
                return Response(
                    status_code=403,
                    headers={"Content-Type": "application/json"},
                    body={"error": f"Permission denied: {permission} required"}
                )
        
        # 继续处理请求
        return await next_handler()


class RoleMiddleware(Middleware):
    """角色中间件"""
    
    def __init__(self, required_roles: list = None, **kwargs):
        super().__init__(**kwargs)
        self.required_roles = required_roles or []
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理角色验证"""
        if not request.user:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                body={"error": "Authentication required"}
            )
        
        user_roles = request.user.get("roles", [])
        
        # 检查是否有必需角色
        for role in self.required_roles:
            if role not in user_roles:
                return Response(
                    status_code=403,
                    headers={"Content-Type": "application/json"},
                    body={"error": f"Role required: {role}"}
                )
        
        # 继续处理请求
        return await next_handler()