"""
权限服务
提供基于RBAC的权限验证功能
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

from app.models.entities.user import User
from app.core.config.settings import config


class PermissionResult(Enum):
    """权限结果枚举"""
    ALLOWED = "allowed"
    DENIED = "denied"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    ROLE_REQUIRED = "role_required"
    PERMISSION_REQUIRED = "permission_required"


@dataclass
class PermissionResponse:
    """权限响应"""
    allowed: bool
    result: PermissionResult
    message: Optional[str] = None
    required_permissions: Optional[List[str]] = None
    required_roles: Optional[List[str]] = None


class PermissionService:
    """权限服务"""
    
    def __init__(self):
        self.cache_enabled = True
        self.permission_cache: Dict[str, List[str]] = {}
        self.role_cache: Dict[str, List[str]] = {}
    
    def check_permission(self, user: User, permission: str) -> PermissionResponse:
        """检查用户权限"""
        try:
            # 检查用户是否有直接权限
            if self._has_direct_permission(user, permission):
                return PermissionResponse(
                    allowed=True,
                    result=PermissionResult.ALLOWED,
                    message="权限验证通过"
                )
            
            # 检查用户角色是否有权限
            if self._has_role_permission(user, permission):
                return PermissionResponse(
                    allowed=True,
                    result=PermissionResult.ALLOWED,
                    message="权限验证通过"
                )
            
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.INSUFFICIENT_PERMISSIONS,
                message=f"缺少权限: {permission}",
                required_permissions=[permission]
            )
            
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.DENIED,
                message=f"权限检查失败: {str(e)}"
            )
    
    def check_role(self, user: User, role: str) -> PermissionResponse:
        """检查用户角色"""
        try:
            user_roles = self._get_user_roles(user)
            
            if role in user_roles:
                return PermissionResponse(
                    allowed=True,
                    result=PermissionResult.ALLOWED,
                    message="角色验证通过"
                )
            
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.ROLE_REQUIRED,
                message=f"缺少角色: {role}",
                required_roles=[role]
            )
            
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.DENIED,
                message=f"角色检查失败: {str(e)}"
            )
    
    def check_multiple_permissions(self, user: User, permissions: List[str], 
                                 require_all: bool = True) -> PermissionResponse:
        """检查多个权限"""
        try:
            if require_all:
                # 需要所有权限
                missing_permissions = []
                for permission in permissions:
                    if not self._has_permission(user, permission):
                        missing_permissions.append(permission)
                
                if missing_permissions:
                    return PermissionResponse(
                        allowed=False,
                        result=PermissionResult.INSUFFICIENT_PERMISSIONS,
                        message=f"缺少权限: {', '.join(missing_permissions)}",
                        required_permissions=missing_permissions
                    )
                
                return PermissionResponse(
                    allowed=True,
                    result=PermissionResult.ALLOWED,
                    message="所有权限验证通过"
                )
            else:
                # 需要任一权限
                for permission in permissions:
                    if self._has_permission(user, permission):
                        return PermissionResponse(
                            allowed=True,
                            result=PermissionResult.ALLOWED,
                            message="权限验证通过"
                        )
                
                return PermissionResponse(
                    allowed=False,
                    result=PermissionResult.INSUFFICIENT_PERMISSIONS,
                    message=f"缺少权限: {', '.join(permissions)}",
                    required_permissions=permissions
                )
                
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.DENIED,
                message=f"权限检查失败: {str(e)}"
            )
    
    def check_multiple_roles(self, user: User, roles: List[str], 
                           require_all: bool = True) -> PermissionResponse:
        """检查多个角色"""
        try:
            user_roles = self._get_user_roles(user)
            
            if require_all:
                # 需要所有角色
                missing_roles = [role for role in roles if role not in user_roles]
                
                if missing_roles:
                    return PermissionResponse(
                        allowed=False,
                        result=PermissionResult.ROLE_REQUIRED,
                        message=f"缺少角色: {', '.join(missing_roles)}",
                        required_roles=missing_roles
                    )
                
                return PermissionResponse(
                    allowed=True,
                    result=PermissionResult.ALLOWED,
                    message="所有角色验证通过"
                )
            else:
                # 需要任一角色
                for role in roles:
                    if role in user_roles:
                        return PermissionResponse(
                            allowed=True,
                            result=PermissionResult.ALLOWED,
                            message="角色验证通过"
                        )
                
                return PermissionResponse(
                    allowed=False,
                    result=PermissionResult.ROLE_REQUIRED,
                    message=f"缺少角色: {', '.join(roles)}",
                    required_roles=roles
                )
                
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                result=PermissionResult.DENIED,
                message=f"角色检查失败: {str(e)}"
            )
    
    def get_user_permissions(self, user: User) -> List[str]:
        """获取用户所有权限"""
        try:
            # 检查缓存
            if self.cache_enabled and str(user.id) in self.permission_cache:
                return self.permission_cache[str(user.id)]
            
            permissions = []
            
            # 获取直接权限
            direct_permissions = self._get_direct_permissions(user)
            permissions.extend(direct_permissions)
            
            # 获取角色权限
            role_permissions = self._get_role_permissions(user)
            permissions.extend(role_permissions)
            
            # 去重
            permissions = list(set(permissions))
            
            # 缓存结果
            if self.cache_enabled:
                self.permission_cache[str(user.id)] = permissions
            
            return permissions
            
        except Exception as e:
            return []
    
    def get_user_roles(self, user: User) -> List[str]:
        """获取用户所有角色"""
        try:
            # 检查缓存
            if self.cache_enabled and str(user.id) in self.role_cache:
                return self.role_cache[str(user.id)]
            
            roles = self._get_user_roles(user)
            
            # 缓存结果
            if self.cache_enabled:
                self.role_cache[str(user.id)] = roles
            
            return roles
            
        except Exception as e:
            return []
    
    def clear_user_cache(self, user: User):
        """清除用户缓存"""
        user_id = str(user.id)
        if user_id in self.permission_cache:
            del self.permission_cache[user_id]
        if user_id in self.role_cache:
            del self.role_cache[user_id]
    
    def clear_all_cache(self):
        """清除所有缓存"""
        self.permission_cache.clear()
        self.role_cache.clear()
    
    def _has_permission(self, user: User, permission: str) -> bool:
        """检查用户是否有权限"""
        return (self._has_direct_permission(user, permission) or 
                self._has_role_permission(user, permission))
    
    def _has_direct_permission(self, user: User, permission: str) -> bool:
        """检查用户是否有直接权限"""
        try:
            # 这里应该查询用户权限表
            # 为了示例，我们返回False
            return False
        except Exception:
            return False
    
    def _has_role_permission(self, user: User, permission: str) -> bool:
        """检查用户角色是否有权限"""
        try:
            # 这里应该查询角色权限表
            # 为了示例，我们返回False
            return False
        except Exception:
            return False
    
    def _get_direct_permissions(self, user: User) -> List[str]:
        """获取用户直接权限"""
        try:
            # 这里应该查询用户权限表
            # 为了示例，我们返回空列表
            return []
        except Exception:
            return []
    
    def _get_role_permissions(self, user: User) -> List[str]:
        """获取用户角色权限"""
        try:
            # 这里应该查询角色权限表
            # 为了示例，我们返回空列表
            return []
        except Exception:
            return []
    
    def _get_user_roles(self, user: User) -> List[str]:
        """获取用户角色"""
        try:
            # 这里应该查询用户角色表
            # 为了示例，我们返回空列表
            return []
        except Exception:
            return []


# 全局权限服务实例
permission_service = PermissionService()