"""
基础模型类
提供类似Laravel Eloquent的ORM功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type, TypeVar
from datetime import datetime
from dataclasses import dataclass, field
import json
from enum import Enum

T = TypeVar('T', bound='Model')


class RelationshipType(Enum):
    """关系类型枚举"""
    HAS_ONE = "has_one"
    HAS_MANY = "has_many"
    BELONGS_TO = "belongs_to"
    MANY_TO_MANY = "many_to_many"


@dataclass
class Relationship:
    """关系定义"""
    type: RelationshipType
    model: Type['Model']
    foreign_key: Optional[str] = None
    local_key: Optional[str] = None
    pivot_table: Optional[str] = None
    pivot_foreign_key: Optional[str] = None
    pivot_local_key: Optional[str] = None


class Model(ABC):
    """基础模型类"""
    
    # 表名
    __table__: Optional[str] = None
    
    # 主键
    __primary_key__: str = "id"
    
    # 时间戳
    __timestamps__: bool = True
    
    # 可填充字段
    __fillable__: List[str] = field(default_factory=list)
    
    # 隐藏字段
    __hidden__: List[str] = field(default_factory=list)
    
    # 关系定义
    __relationships__: Dict[str, Relationship] = field(default_factory=dict)
    
    # 模型属性
    _attributes: Dict[str, Any] = field(default_factory=dict)
    _original: Dict[str, Any] = field(default_factory=dict)
    _exists: bool = False
    
    def __init__(self, **kwargs):
        """初始化模型"""
        self._attributes = {}
        self._original = {}
        self._exists = False
        
        # 设置属性
        for key, value in kwargs.items():
            self._attributes[key] = value
            self._original[key] = value
        
        # 如果提供了主键，标记为已存在
        if self.__primary_key__ in self._attributes:
            self._exists = True
    
    def __getattr__(self, name: str) -> Any:
        """获取属性"""
        if name in self._attributes:
            return self._attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """设置属性"""
        if name.startswith('_') or name in ['__table__', '__primary_key__', '__timestamps__', '__fillable__', '__hidden__', '__relationships__']:
            super().__setattr__(name, value)
        else:
            if not hasattr(self, '_attributes'):
                self._attributes = {}
            self._attributes[name] = value
    
    def __repr__(self) -> str:
        """字符串表示"""
        attrs = []
        for key, value in self._attributes.items():
            if key not in self.__hidden__:
                attrs.append(f"{key}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"
    
    @property
    def table(self) -> str:
        """获取表名"""
        return self.__table__ or self.__class__.__name__.lower()
    
    @property
    def primary_key(self) -> str:
        """获取主键字段名"""
        return self.__primary_key__
    
    @property
    def key(self) -> Any:
        """获取主键值"""
        return self._attributes.get(self.__primary_key__)
    
    @property
    def exists(self) -> bool:
        """检查模型是否已存在"""
        return self._exists
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """获取属性值"""
        return self._attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """设置属性值"""
        self._attributes[key] = value
    
    def get_attributes(self) -> Dict[str, Any]:
        """获取所有属性"""
        return self._attributes.copy()
    
    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """批量设置属性"""
        for key, value in attributes.items():
            self._attributes[key] = value
    
    def fill(self, attributes: Dict[str, Any]) -> 'Model':
        """填充属性（只填充可填充字段）"""
        for key, value in attributes.items():
            if key in self.__fillable__:
                self._attributes[key] = value
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self._attributes.items():
            if key not in self.__hidden__:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, (list, dict)):
                    result[key] = json.dumps(value) if isinstance(value, (list, dict)) else value
                else:
                    result[key] = value
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def save(self) -> bool:
        """保存模型"""
        if self._exists:
            return self._update()
        else:
            return self._create()
    
    def delete(self) -> bool:
        """删除模型"""
        if not self._exists:
            return False
        
        # 这里应该实现删除逻辑
        # 实际实现需要数据库连接
        print(f"删除 {self.__class__.__name__} 记录: {self.key}")
        self._exists = False
        return True
    
    def _create(self) -> bool:
        """创建新记录"""
        # 添加时间戳
        if self.__timestamps__:
            now = datetime.now()
            self._attributes['created_at'] = now
            self._attributes['updated_at'] = now
        
        # 这里应该实现插入逻辑
        # 实际实现需要数据库连接
        print(f"创建 {self.__class__.__name__} 记录: {self._attributes}")
        self._exists = True
        return True
    
    def _update(self) -> bool:
        """更新记录"""
        # 更新时间戳
        if self.__timestamps__:
            self._attributes['updated_at'] = datetime.now()
        
        # 这里应该实现更新逻辑
        # 实际实现需要数据库连接
        print(f"更新 {self.__class__.__name__} 记录: {self._attributes}")
        return True
    
    def refresh(self) -> 'Model':
        """刷新模型数据"""
        if not self._exists:
            return self
        
        # 这里应该从数据库重新加载数据
        # 实际实现需要数据库连接
        print(f"刷新 {self.__class__.__name__} 数据")
        return self
    
    def replicate(self, attributes: Dict[str, Any] = None) -> 'Model':
        """复制模型"""
        new_attributes = self._attributes.copy()
        if attributes:
            new_attributes.update(attributes)
        
        # 移除主键
        if self.__primary_key__ in new_attributes:
            del new_attributes[self.__primary_key__]
        
        return self.__class__(**new_attributes)
    
    @classmethod
    def create(cls, **attributes) -> 'Model':
        """创建新模型实例"""
        instance = cls(**attributes)
        instance.save()
        return instance
    
    @classmethod
    def find(cls, key: Any) -> Optional['Model']:
        """根据主键查找模型"""
        # 这里应该实现查找逻辑
        # 实际实现需要数据库连接
        print(f"查找 {cls.__name__} 记录: {key}")
        return None
    
    @classmethod
    def all(cls) -> List['Model']:
        """获取所有记录"""
        # 这里应该实现查询逻辑
        # 实际实现需要数据库连接
        print(f"获取所有 {cls.__name__} 记录")
        return []
    
    @classmethod
    def where(cls, column: str, operator: str, value: Any) -> 'ModelQuery':
        """创建查询构建器"""
        from .query import ModelQuery
        return ModelQuery(cls).where(column, operator, value)
    
    @classmethod
    def query(cls) -> 'ModelQuery':
        """创建查询构建器"""
        from .query import ModelQuery
        return ModelQuery(cls)
    
    def has_one(self, model: Type['Model'], foreign_key: str = None, local_key: str = None) -> 'Model':
        """一对一关系"""
        if not foreign_key:
            foreign_key = f"{self.__class__.__name__.lower()}_id"
        if not local_key:
            local_key = self.__primary_key__
        
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"一对一关系: {self.__class__.__name__} -> {model.__name__}")
        return None
    
    def has_many(self, model: Type['Model'], foreign_key: str = None, local_key: str = None) -> List['Model']:
        """一对多关系"""
        if not foreign_key:
            foreign_key = f"{self.__class__.__name__.lower()}_id"
        if not local_key:
            local_key = self.__primary_key__
        
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"一对多关系: {self.__class__.__name__} -> {model.__name__}")
        return []
    
    def belongs_to(self, model: Type['Model'], foreign_key: str = None, owner_key: str = None) -> 'Model':
        """多对一关系"""
        if not foreign_key:
            foreign_key = f"{model.__name__.lower()}_id"
        if not owner_key:
            owner_key = model.__primary_key__
        
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"多对一关系: {self.__class__.__name__} -> {model.__name__}")
        return None
    
    def belongs_to_many(self, model: Type['Model'], pivot_table: str = None, 
                       foreign_pivot_key: str = None, related_pivot_key: str = None) -> List['Model']:
        """多对多关系"""
        if not pivot_table:
            pivot_table = f"{self.__class__.__name__.lower()}_{model.__name__.lower()}"
        if not foreign_pivot_key:
            foreign_pivot_key = f"{self.__class__.__name__.lower()}_id"
        if not related_pivot_key:
            related_pivot_key = f"{model.__name__.lower()}_id"
        
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"多对多关系: {self.__class__.__name__} -> {model.__name__}")
        return []