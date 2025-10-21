"""
安全配置
统一管理所有安全防护配置
"""

import os
from typing import Dict, Any, List
from app.core.cache import CacheManager
from app.core.security import (
    CSRFProtection, CSRFMiddleware,
    SQLInjectionProtection, SQLInjectionMiddleware,
    XSSProtection, XSSMiddleware,
    InputValidator, ValidationMiddleware, ValidationRule
)


class SecurityConfig:
    """安全配置类"""
    
    def __init__(self):
        self.cache = CacheManager()
        self._init_security_components()
    
    def _init_security_components(self):
        """初始化安全组件"""
        # 获取配置
        self.secret_key = os.getenv("SECURITY_CSRF_SECRET_KEY", "your-secret-key-change-this")
        self.csrf_expire_hours = int(os.getenv("SECURITY_CSRF_EXPIRE_HOURS", "24"))
        self.max_suspicious_requests = int(os.getenv("SECURITY_MAX_SUSPICIOUS_REQUESTS", "5"))
        
        # 初始化安全防护
        self.csrf_protection = CSRFProtection(self.secret_key, self.cache)
        self.sql_protection = SQLInjectionProtection()
        self.xss_protection = XSSProtection()
        self.validator = InputValidator()
        
        # 配置验证规则
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """设置验证规则"""
        self.validation_schemas = {
            "user": {
                "username": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MIN_LENGTH, 3),
                    ValidationRule(ValidationRule.MAX_LENGTH, 20),
                    ValidationRule(ValidationRule.PATTERN, r"^[a-zA-Z0-9_]+$")
                ],
                "email": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.EMAIL)
                ],
                "password": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MIN_LENGTH, 8),
                    ValidationRule(ValidationRule.PATTERN, r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
                ],
                "age": [
                    ValidationRule(ValidationRule.INTEGER),
                    ValidationRule(ValidationRule.MIN_VALUE, 0),
                    ValidationRule(ValidationRule.MAX_VALUE, 150)
                ]
            },
            "ai_model": {
                "name": [
                    ValidationRule(ValidationRule.REQUIRED),
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MIN_LENGTH, 1),
                    ValidationRule(ValidationRule.MAX_LENGTH, 100)
                ],
                "description": [
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.MAX_LENGTH, 1000)
                ],
                "version": [
                    ValidationRule(ValidationRule.STRING),
                    ValidationRule(ValidationRule.PATTERN, r"^\d+\.\d+\.\d+$")
                ]
            }
        }
    
    def get_csrf_middleware(self) -> CSRFMiddleware:
        """获取CSRF中间件"""
        return CSRFMiddleware(
            secret_key=self.secret_key,
            cache=self.cache,
            exempt_methods={"GET", "HEAD", "OPTIONS"},
            exempt_paths={"/api/health", "/api/info", "/api/docs"}
        )
    
    def get_sql_injection_middleware(self) -> SQLInjectionMiddleware:
        """获取SQL注入中间件"""
        return SQLInjectionMiddleware(
            protection=self.sql_protection,
            block_threats=True,
            log_threats=True
        )
    
    def get_xss_middleware(self) -> XSSMiddleware:
        """获取XSS中间件"""
        return XSSMiddleware(
            protection=self.xss_protection,
            block_threats=True,
            log_threats=True,
            sanitize_output=True
        )
    
    def get_validation_middleware(self) -> ValidationMiddleware:
        """获取验证中间件"""
        return ValidationMiddleware(
            validator=self.validator,
            validation_schemas=self.validation_schemas,
            block_invalid=True
        )
    
    def get_all_middlewares(self) -> List:
        """获取所有安全中间件"""
        return [
            self.get_csrf_middleware(),
            self.get_sql_injection_middleware(),
            self.get_xss_middleware(),
            self.get_validation_middleware()
        ]
    
    def get_security_headers(self) -> Dict[str, str]:
        """获取安全响应头"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


# 全局安全配置实例
security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """获取安全配置实例"""
    return security_config


def apply_security_middlewares(app):
    """应用安全中间件到应用"""
    middlewares = security_config.get_all_middlewares()
    
    for middleware in middlewares:
        app.add_middleware(middleware)
    
    # 添加安全响应头
    @app.middleware("response")
    async def add_security_headers(request, response):
        """添加安全响应头"""
        headers = security_config.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        return response