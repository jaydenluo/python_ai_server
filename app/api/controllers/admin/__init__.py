"""
管理员控制器模块
所有管理员相关的控制器都放在这里
"""

from .user_controller import AdminUserController
from .role_controller import AdminRoleController
from .permission_controller import AdminPermissionController

__all__ = [
    "AdminUserController",
    "AdminRoleController", 
    "AdminPermissionController"
]