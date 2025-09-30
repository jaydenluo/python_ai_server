"""
API控制器模块
按功能模块组织控制器
"""

# 基础控制器
from .base import ResourceController

# 模块化控制器
from .admin import (
    AdminUserController,
    AdminRoleController,
    AdminPermissionController
)

from .api import (
    APIUserController,
    APIAIModelController,
    APIAuthController
)

from .web import (
    WebHomeController,
    WebUserController,
    WebAIController
)

__all__ = [
    # 基础控制器
    "ResourceController",
    
    # 管理员控制器
    "AdminUserController",
    "AdminRoleController",
    "AdminPermissionController",
    
    # API控制器
    "APIUserController",
    "APIAIModelController",
    "APIAuthController",
    
    # Web控制器
    "WebHomeController",
    "WebUserController",
    "WebAIController"
]