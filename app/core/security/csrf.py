"""
CSRF保护
防止跨站请求伪造攻击
"""

import secrets
import hashlib
import hmac
from typing import Dict, Set, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.core.middleware.base import Middleware, Request, Response
from app.core.cache import CacheManager


class CSRFError(Exception):
    """CSRF错误"""
    pass


class CSRFMethod(Enum):
    """CSRF方法枚举"""
    TOKEN = "token"
    DOUBLE_SUBMIT = "double_submit"
    SAME_SITE = "same_site"


@dataclass
class CSRFToken:
    """CSRF令牌"""
    token: str
    created_at: datetime
    expires_at: datetime
    user_id: Optional[str] = None
    
    def is_expired(self) -> bool:
        """检查令牌是否过期"""
        return datetime.now() > self.expires_at
    
    def is_valid(self, max_age: int = 3600) -> bool:
        """检查令牌是否有效"""
        return not self.is_expired() and (datetime.now() - self.created_at).seconds <= max_age


class CSRFProtection:
    """CSRF保护类"""
    
    def __init__(self, secret_key: str, cache: CacheManager):
        self.secret_key = secret_key
        self.cache = cache
        self.token_length = 32
        self.token_expire_hours = 24
        self.max_tokens_per_user = 10
        
    def generate_token(self, user_id: Optional[str] = None) -> str:
        """生成CSRF令牌"""
        # 生成随机令牌
        token = secrets.token_urlsafe(self.token_length)
        
        # 创建令牌对象
        now = datetime.now()
        csrf_token = CSRFToken(
            token=token,
            created_at=now,
            expires_at=now + timedelta(hours=self.token_expire_hours),
            user_id=user_id
        )
        
        # 存储令牌
        self._store_token(csrf_token)
        
        return token
    
    def validate_token(self, token: str, user_id: Optional[str] = None) -> bool:
        """验证CSRF令牌"""
        try:
            # 获取存储的令牌
            stored_token = self._get_token(token)
            if not stored_token:
                return False
            
            # 检查令牌是否过期
            if stored_token.is_expired():
                self._remove_token(token)
                return False
            
            # 检查用户ID是否匹配
            if user_id and stored_token.user_id != user_id:
                return False
            
            return True
            
        except Exception:
            return False
    
    def refresh_token(self, old_token: str, user_id: Optional[str] = None) -> str:
        """刷新CSRF令牌"""
        # 验证旧令牌
        if not self.validate_token(old_token, user_id):
            raise CSRFError("Invalid or expired token")
        
        # 删除旧令牌
        self._remove_token(old_token)
        
        # 生成新令牌
        return self.generate_token(user_id)
    
    def _store_token(self, csrf_token: CSRFToken):
        """存储CSRF令牌"""
        cache_key = f"csrf_token:{csrf_token.token}"
        self.cache.set(cache_key, csrf_token, ttl=self.token_expire_hours * 3600)
        
        # 如果指定了用户ID，也存储到用户令牌列表
        if csrf_token.user_id:
            user_tokens_key = f"csrf_user_tokens:{csrf_token.user_id}"
            user_tokens = self.cache.get(user_tokens_key, [])
            user_tokens.append(csrf_token.token)
            
            # 限制每个用户的令牌数量
            if len(user_tokens) > self.max_tokens_per_user:
                # 删除最旧的令牌
                oldest_token = user_tokens.pop(0)
                self._remove_token(oldest_token)
            
            self.cache.set(user_tokens_key, user_tokens, ttl=self.token_expire_hours * 3600)
    
    def _get_token(self, token: str) -> Optional[CSRFToken]:
        """获取CSRF令牌"""
        cache_key = f"csrf_token:{token}"
        return self.cache.get(cache_key)
    
    def _remove_token(self, token: str):
        """删除CSRF令牌"""
        cache_key = f"csrf_token:{token}"
        self.cache.delete(cache_key)
    
    def cleanup_expired_tokens(self):
        """清理过期的令牌"""
        # 这里可以实现定期清理过期令牌的逻辑
        pass


class CSRFMiddleware(Middleware):
    """CSRF中间件"""
    
    def __init__(self, 
                 secret_key: str,
                 cache: CacheManager,
                 exempt_methods: Set[str] = None,
                 exempt_paths: Set[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.csrf_protection = CSRFProtection(secret_key, cache)
        self.exempt_methods = exempt_methods or {"GET", "HEAD", "OPTIONS"}
        self.exempt_paths = exempt_paths or {"/api/health", "/api/info"}
        
    async def handle(self, request: Request, next_handler) -> Response:
        """处理CSRF保护"""
        # 检查是否豁免CSRF检查
        if self._is_exempt(request):
            return await next_handler()
        
        # 检查请求方法
        if request.method in self.exempt_methods:
            return await next_handler()
        
        # 获取用户ID（从JWT令牌或其他方式）
        user_id = self._get_user_id(request)
        
        # 验证CSRF令牌
        csrf_token = self._get_csrf_token(request)
        if not csrf_token:
            return self._create_csrf_error_response("CSRF token missing")
        
        if not self.csrf_protection.validate_token(csrf_token, user_id):
            return self._create_csrf_error_response("Invalid CSRF token")
        
        # 继续处理请求
        response = await next_handler()
        
        # 在响应中添加CSRF令牌（如果需要）
        if self._should_add_token_to_response(request):
            new_token = self.csrf_protection.generate_token(user_id)
            response.headers["X-CSRF-Token"] = new_token
        
        return response
    
    def _is_exempt(self, request: Request) -> bool:
        """检查是否豁免CSRF检查"""
        # 检查路径
        for exempt_path in self.exempt_paths:
            if request.path.startswith(exempt_path):
                return True
        
        # 检查请求头
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return True
        
        return False
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """获取用户ID"""
        # 从JWT令牌中获取用户ID
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                import jwt
                payload = jwt.decode(token, options={"verify_signature": False})
                return str(payload.get("user_id"))
            except Exception:
                pass
        
        return None
    
    def _get_csrf_token(self, request: Request) -> Optional[str]:
        """获取CSRF令牌"""
        # 优先从请求头获取
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token
        
        # 从表单数据获取
        if hasattr(request, 'form') and request.form:
            token = request.form.get("_csrf_token")
            if token:
                return token
        
        # 从查询参数获取
        token = request.query_params.get("_csrf_token")
        if token:
            return token
        
        return None
    
    def _should_add_token_to_response(self, request: Request) -> bool:
        """判断是否应该在响应中添加CSRF令牌"""
        # 对于需要CSRF保护的请求，添加令牌
        return request.method not in self.exempt_methods
    
    def _create_csrf_error_response(self, message: str) -> Response:
        """创建CSRF错误响应"""
        return Response(
            status_code=403,
            headers={"Content-Type": "application/json"},
            body={
                "error": "CSRF Protection",
                "message": message,
                "code": "CSRF_TOKEN_MISSING_OR_INVALID"
            }
        )


class DoubleSubmitCSRFProtection(CSRFProtection):
    """双重提交CSRF保护"""
    
    def __init__(self, secret_key: str, cache: CacheManager):
        super().__init__(secret_key, cache)
        self.cookie_name = "_csrf_token"
        self.header_name = "X-CSRF-Token"
    
    def generate_token(self, user_id: Optional[str] = None) -> str:
        """生成双重提交令牌"""
        # 生成随机令牌
        token = secrets.token_urlsafe(self.token_length)
        
        # 使用HMAC签名令牌
        signed_token = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{token}.{signed_token}"
    
    def validate_token(self, token: str, user_id: Optional[str] = None) -> bool:
        """验证双重提交令牌"""
        try:
            if "." not in token:
                return False
            
            token_part, signature = token.split(".", 1)
            
            # 验证签名
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token_part.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False


class SameSiteCSRFProtection:
    """SameSite Cookie CSRF保护"""
    
    def __init__(self):
        self.same_site_policy = "Strict"  # Strict, Lax, None
    
    def set_same_site_cookie(self, response: Response, name: str, value: str, **kwargs):
        """设置SameSite Cookie"""
        cookie_options = {
            "httponly": True,
            "secure": True,  # 仅在HTTPS下使用
            "samesite": self.same_site_policy,
            **kwargs
        }
        
        # 这里需要根据具体的响应对象设置Cookie
        # response.set_cookie(name, value, **cookie_options)
        pass


# 全局CSRF保护实例
csrf_protection = None


def init_csrf_protection(secret_key: str, cache: CacheManager):
    """初始化CSRF保护"""
    global csrf_protection
    csrf_protection = CSRFProtection(secret_key, cache)
    return csrf_protection


def get_csrf_protection() -> CSRFProtection:
    """获取CSRF保护实例"""
    if csrf_protection is None:
        raise RuntimeError("CSRF protection not initialized")
    return csrf_protection