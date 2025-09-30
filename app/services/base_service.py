"""
基础服务类
提供通用的业务逻辑处理
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from app.core.repositories.base_repository import BaseRepository

T = TypeVar('T')


class BaseService:
    """基础服务类"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def create(self, **kwargs) -> T:
        """创建记录"""
        # 可以在这里添加业务逻辑验证
        return self.repository.create(**kwargs)
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """根据ID获取记录"""
        return self.repository.get_by_id(id)
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """获取所有记录"""
        return self.repository.get_all(limit=limit, offset=offset)
    
    def update(self, id: Any, **kwargs) -> Optional[T]:
        """更新记录"""
        # 可以在这里添加业务逻辑验证
        return self.repository.update(id, **kwargs)
    
    def delete(self, id: Any) -> bool:
        """删除记录"""
        # 可以在这里添加业务逻辑验证
        return self.repository.delete(id)
    
    def count(self) -> int:
        """统计记录数"""
        return self.repository.count()
    
    def exists(self, id: Any) -> bool:
        """检查记录是否存在"""
        return self.repository.exists(id)
    
    def filter(self, **filters) -> List[T]:
        """根据条件过滤记录"""
        return self.repository.filter(**filters)
    
    def search(self, field: str, value: str) -> List[T]:
        """模糊搜索"""
        return self.repository.search(field, value)
    
    def paginate(self, page: int, per_page: int) -> Dict[str, Any]:
        """分页查询"""
        return self.repository.paginate(page, per_page)
    
    def bulk_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """批量创建"""
        return self.repository.bulk_create(items)
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """批量更新"""
        return self.repository.bulk_update(updates)
    
    def bulk_delete(self, ids: List[Any]) -> int:
        """批量删除"""
        return self.repository.bulk_delete(ids)


class UserService(BaseService):
    """用户服务类"""
    
    def __init__(self, repository: BaseRepository):
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
        return self.repository.filter(status="active")
    
    def get_users_by_role(self, role: str) -> List[T]:
        """根据角色获取用户"""
        return self.repository.filter(role=role)
    
    def _hash_password(self, password: str) -> str:
        """密码加密"""
        # 这里应该使用真实的密码加密方法
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return self._hash_password(password) == hashed