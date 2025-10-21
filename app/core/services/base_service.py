"""
基础服务类
提供通用的业务逻辑处理和数据访问封装
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from app.core.repositories.repository import Repository

T = TypeVar('T')


class BaseService:
    """
    基础服务类
    
    为需要数据库操作的服务提供统一的数据访问接口。
    继承此类的服务将自动获得标准的 CRUD 操作能力。
    
    使用场景：
    - 用户管理服务
    - 权限管理服务  
    - 角色管理服务
    - 需要持久化数据的业务服务
    
    不适用场景：
    - 第三方API调用服务（如讯飞、百度）
    - 纯内存数据服务（如配置管理）
    - 工具类服务（如Token生成）
    
    示例：
        ```python
        from app.core.services.base_service import BaseService
        from app.core.repositories.repository import Repository
        from app.models.entities.user import User
        
        class UserService(BaseService):
            def __init__(self, session):
                repository = Repository(User, session)
                super().__init__(repository)
        ```
    """
    
    def __init__(self, repository: Optional[Repository] = None):
        """
        初始化服务
        
        Args:
            repository: 可选的 Repository 实例。如果服务不需要数据库操作，可以不传入。
        """
        self.repository = repository
    
    def create(self, **kwargs) -> T:
        """
        创建记录
        
        Args:
            **kwargs: 记录字段
            
        Returns:
            T: 创建的记录实例
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.create(**kwargs)
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        根据ID获取记录
        
        Args:
            id: 记录ID
            
        Returns:
            Optional[T]: 记录实例，不存在则返回 None
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.get_by_id(id)
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        获取所有记录
        
        Args:
            limit: 限制返回数量
            offset: 偏移量
            
        Returns:
            List[T]: 记录列表
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.get_all(limit=limit, offset=offset)
    
    def update(self, id: Any, **kwargs) -> Optional[T]:
        """
        更新记录
        
        Args:
            id: 记录ID
            **kwargs: 要更新的字段
            
        Returns:
            Optional[T]: 更新后的记录实例
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.update(id, **kwargs)
    
    def delete(self, id: Any) -> bool:
        """
        删除记录
        
        Args:
            id: 记录ID
            
        Returns:
            bool: 是否删除成功
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.delete(id)
    
    def count(self) -> int:
        """
        统计记录数
        
        Returns:
            int: 记录总数
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.count()
    
    def exists(self, id: Any) -> bool:
        """
        检查记录是否存在
        
        Args:
            id: 记录ID
            
        Returns:
            bool: 是否存在
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.exists(id)
    
    def filter(self, **filters) -> List[T]:
        """
        根据条件过滤记录（简单等值匹配）
        
        Args:
            **filters: 过滤条件
            
        Returns:
            List[T]: 符合条件的记录列表
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.filter_by_conditions(filters)
    
    def search(self, field: str, value: str) -> List[T]:
        """
        模糊搜索
        
        Args:
            field: 搜索字段
            value: 搜索值
            
        Returns:
            List[T]: 搜索结果列表
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.search_by_text([field], value)
    
    def paginate(self, page: int, per_page: int) -> Dict[str, Any]:
        """
        分页查询
        
        Args:
            page: 页码（从1开始）
            per_page: 每页数量
            
        Returns:
            Dict[str, Any]: 分页结果，包含 items, total, page, per_page, pages 等字段
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.paginate(page, per_page)
    
    def bulk_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """
        批量创建
        
        Args:
            items: 记录数据列表
            
        Returns:
            List[T]: 创建的记录列表
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        return self.repository.bulk_insert(items)
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """
        批量更新
        
        Args:
            updates: 更新数据列表，每项需包含 id 和要更新的字段
            
        Returns:
            int: 更新的记录数
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        
        count = 0
        for update_data in updates:
            record_id = update_data.pop('id', None)
            if record_id and self.repository.update(record_id, **update_data):
                count += 1
        return count
    
    def bulk_delete(self, ids: List[Any]) -> int:
        """
        批量删除
        
        Args:
            ids: 记录ID列表
            
        Returns:
            int: 删除的记录数
        """
        if not self.repository:
            raise RuntimeError("此服务未配置 Repository，无法执行数据库操作")
        
        count = 0
        for record_id in ids:
            if self.repository.delete(record_id):
                count += 1
        return count

