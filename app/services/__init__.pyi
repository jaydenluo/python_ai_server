# 类型存根文件 - 支持 IDE 自动补全
from .auth_service import AuthService as AuthService, AuthResponse as AuthResponse, AuthResult as AuthResult
from .base_service import BaseService as BaseService
from .permission_service import PermissionService as PermissionService

__all__ = ["AuthService", "AuthResponse", "AuthResult", "BaseService", "PermissionService"]