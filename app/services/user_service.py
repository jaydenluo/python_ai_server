"""
用户服务
提供用户管理相关的业务逻辑
"""

from typing import Any, List, Optional, TypeVar
from app.core.services import BaseService
from app.core.repositories.repository import Repository

T = TypeVar('T')


class UserService(BaseService):
    """用户服务类"""
    
    def __init__(self, repository: Repository):
        super().__init__(repository)
    
    def create_user(self, username: str, email: str, password: str, **kwargs) -> T:
        """创建用户（带业务逻辑）"""
        # 检查用户名是否已存在
        if self.repository.get_by_field("username", username):
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        if self.repository.get_by_field("email", email):
            raise ValueError("邮箱已存在")
        
        # 密码加密（这里应该使用真实的加密方法）
        hashed_password = self._hash_password(password)
        
        return self.repository.create(
            username=username,
            email=email,
            password=hashed_password,
            **kwargs
        )
    
    def authenticate(self, email: str, password: str) -> Optional[T]:
        """用户认证"""
        user = self.repository.get_by_field("email", email)
        if user and self._check_password(password, user.password):
            return user
        return None
    
    def activate_user(self, id: Any) -> Optional[T]:
        """激活用户"""
        return self.repository.update(id, status="active")
    
    def deactivate_user(self, id: Any) -> Optional[T]:
        """停用用户"""
        return self.repository.update(id, status="inactive")
    
    def get_active_users(self) -> List[T]:
        """获取活跃用户"""
        return self.repository.filter_by_conditions({"status": "active"})
    
    def get_users_by_role(self, role: str) -> List[T]:
        """根据角色获取用户"""
        return self.repository.filter_by_conditions({"role": role})
    
    def _hash_password(self, password: str) -> str:
        """密码加密"""
        # 这里应该使用真实的密码加密方法（如 bcrypt）
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return self._hash_password(password) == hashed
