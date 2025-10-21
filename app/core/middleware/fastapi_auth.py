"""
FastAPI 兼容的认证中间件
"""

import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class FastAPIAuthMiddleware(BaseHTTPMiddleware):
    """FastAPI 兼容的认证中间件"""
    
    def __init__(self, app, secret_key: str, algorithm: str = "HS256", 
                 token_expire_hours: int = 24):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_hours = token_expire_hours
        
        # 不需要认证的路径
        self.public_paths = {
            "/", "/docs", "/redoc", "/openapi.json", "/health", 
            "/api/info", "/api/v1/info",  # API信息接口
            "/api/v1/auth/login", "/api/v1/auth/register",
            "/api/auth",  # 统一鉴权接口（生成临时令牌）
            "/api/voice",  # 音色管理接口
            "/api/test",  # 测试接口
            "/favicon.ico", "/static"
        }
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 检查是否是公开路径
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # 获取 Authorization 头
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid authorization header"}
            )
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        
        try:
            # 验证 JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")
            
            if not user_id:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid token payload"}
                )
            
            # 检查 token 是否过期
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Token expired"}
                )
            
            # 将用户信息添加到请求状态中
            request.state.user_id = user_id
            request.state.user_data = payload
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"error": "Token expired"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Authentication error: {str(e)}"}
            )
        
        # 继续处理请求
        response = await call_next(request)
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """检查是否是公开路径"""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    def generate_token(self, user_id: str, user_data: Optional[Dict[str, Any]] = None) -> str:
        """生成 JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow()
        }
        
        if user_data:
            payload.update(user_data)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证 token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.InvalidTokenError:
            return None