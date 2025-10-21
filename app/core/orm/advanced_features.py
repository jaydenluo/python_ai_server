"""
高级ORM功能
提供模型事件、软删除、审计、版本控制等高级功能
"""

import logging
from typing import Any, Dict, List, Optional, Type, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from app.core.orm.models import Model

T = TypeVar('T', bound=Model)


class ModelEvent(Enum):
    """模型事件类型"""
    CREATING = "creating"
    CREATED = "created"
    UPDATING = "updating"
    UPDATED = "updated"
    DELETING = "deleting"
    DELETED = "deleted"
    SAVING = "saving"
    SAVED = "saved"
    LOADING = "loading"
    LOADED = "loaded"


@dataclass
class ModelEventData:
    """模型事件数据"""
    event: ModelEvent
    model: Model
    session: Session
    original_data: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None


class ModelEventManager:
    """模型事件管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._listeners: Dict[Type[Model], Dict[ModelEvent, List[Callable]]] = {}
        self._global_listeners: Dict[ModelEvent, List[Callable]] = {}
    
    def register_listener(self, model: Type[Model], event: ModelEvent, callback: Callable):
        """注册模型事件监听器"""
        if model not in self._listeners:
            self._listeners[model] = {}
        
        if event not in self._listeners[model]:
            self._listeners[model][event] = []
        
        self._listeners[model][event].append(callback)
        self.logger.info(f"Registered listener for {model.__name__}.{event.value}")
    
    def register_global_listener(self, event: ModelEvent, callback: Callable):
        """注册全局事件监听器"""
        if event not in self._global_listeners:
            self._global_listeners[event] = []
        
        self._global_listeners[event].append(callback)
        self.logger.info(f"Registered global listener for {event.value}")
    
    def fire_event(self, event_data: ModelEventData):
        """触发事件"""
        model = event_data.model
        event = event_data.event
        
        # 触发全局监听器
        if event in self._global_listeners:
            for callback in self._global_listeners[event]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Error in global listener: {e}")
        
        # 触发模型特定监听器
        if model.__class__ in self._listeners and event in self._listeners[model.__class__]:
            for callback in self._listeners[model.__class__][event]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Error in model listener: {e}")


class SoftDeleteMixin:
    """软删除混入类"""
    
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """软删除"""
        self.deleted_at = datetime.now()
        self.is_deleted = True
    
    def restore(self):
        """恢复软删除"""
        self.deleted_at = None
        self.is_deleted = False
    
    @classmethod
    def with_trashed(cls, session: Session):
        """包含软删除记录"""
        return session.query(cls)
    
    @classmethod
    def only_trashed(cls, session: Session):
        """仅软删除记录"""
        return session.query(cls).filter(cls.is_deleted == True)
    
    @classmethod
    def without_trashed(cls, session: Session):
        """排除软删除记录"""
        return session.query(cls).filter(cls.is_deleted == False)


class AuditMixin:
    """审计混入类"""
    
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def set_created_by(self, user_id: int):
        """设置创建者"""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: int):
        """设置更新者"""
        self.updated_by = user_id


class VersionMixin:
    """版本控制混入类"""
    
    version = Column(Integer, default=1, nullable=False)
    version_comment = Column(Text, nullable=True)
    
    def increment_version(self, comment: Optional[str] = None):
        """增加版本"""
        self.version += 1
        self.version_comment = comment


class TimestampMixin:
    """时间戳混入类"""
    
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class CacheMixin:
    """缓存混入类"""
    
    def cache_key(self) -> str:
        """生成缓存键"""
        return f"{self.__class__.__name__.lower()}:{self.id}"
    
    def cache_ttl(self) -> int:
        """缓存TTL（秒）"""
        return 3600  # 默认1小时
    
    def invalidate_cache(self):
        """使缓存失效"""
        # 这里可以集成缓存系统
        pass


class ObserverMixin:
    """观察者混入类"""
    
    @classmethod
    def observe(cls, event: ModelEvent, callback: Callable):
        """观察事件"""
        event_manager.register_listener(cls, event, callback)
    
    @classmethod
    def creating(cls, callback: Callable):
        """观察创建前事件"""
        cls.observe(ModelEvent.CREATING, callback)
    
    @classmethod
    def created(cls, callback: Callable):
        """观察创建后事件"""
        cls.observe(ModelEvent.CREATED, callback)
    
    @classmethod
    def updating(cls, callback: Callable):
        """观察更新前事件"""
        cls.observe(ModelEvent.UPDATING, callback)
    
    @classmethod
    def updated(cls, callback: Callable):
        """观察更新后事件"""
        cls.observe(ModelEvent.UPDATED, callback)
    
    @classmethod
    def deleting(cls, callback: Callable):
        """观察删除前事件"""
        cls.observe(ModelEvent.DELETING, callback)
    
    @classmethod
    def deleted(cls, callback: Callable):
        """观察删除后事件"""
        cls.observe(ModelEvent.DELETED, callback)


class ModelScope:
    """模型作用域"""
    
    def __init__(self, model: Type[Model], session: Session):
        self.model = model
        self.session = session
        self._query = session.query(model)
    
    def where(self, **conditions):
        """添加条件"""
        for field, value in conditions.items():
            if hasattr(self.model, field):
                self._query = self._query.filter(getattr(self.model, field) == value)
        return self
    
    def order_by(self, field: str, direction: str = "asc"):
        """排序"""
        if hasattr(self.model, field):
            if direction.lower() == "desc":
                self._query = self._query.order_by(getattr(self.model, field).desc())
            else:
                self._query = self._query.order_by(getattr(self.model, field))
        return self
    
    def limit(self, count: int):
        """限制数量"""
        self._query = self._query.limit(count)
        return self
    
    def offset(self, count: int):
        """偏移"""
        self._query = self._query.offset(count)
        return self
    
    def get(self):
        """获取结果"""
        return self._query.all()
    
    def first(self):
        """获取第一个结果"""
        return self._query.first()
    
    def count(self):
        """获取数量"""
        return self._query.count()


class ModelFactory:
    """模型工厂"""
    
    def __init__(self, model: Type[Model]):
        self.model = model
        self._attributes = {}
    
    def fill(self, **attributes):
        """填充属性"""
        self._attributes.update(attributes)
        return self
    
    def make(self, **attributes):
        """创建实例（不保存）"""
        all_attributes = {**self._attributes, **attributes}
        return self.model(**all_attributes)
    
    def create(self, **attributes):
        """创建并保存实例"""
        instance = self.make(**attributes)
        # 这里需要数据库会话来保存
        return instance
    
    def count(self, count: int):
        """创建多个实例"""
        instances = []
        for _ in range(count):
            instances.append(self.make())
        return instances


class ModelRepository:
    """模型仓储"""
    
    def __init__(self, model: Type[Model], session: Session):
        self.model = model
        self.session = session
    
    def find(self, id: int) -> Optional[Model]:
        """查找单个记录"""
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def find_or_fail(self, id: int) -> Model:
        """查找单个记录（失败时抛出异常）"""
        instance = self.find(id)
        if not instance:
            raise ValueError(f"{self.model.__name__} with id {id} not found")
        return instance
    
    def all(self) -> List[Model]:
        """获取所有记录"""
        return self.session.query(self.model).all()
    
    def where(self, **conditions) -> ModelScope:
        """创建查询作用域"""
        return ModelScope(self.model, self.session).where(**conditions)
    
    def create(self, **attributes) -> Model:
        """创建记录"""
        instance = self.model(**attributes)
        self.session.add(instance)
        self.session.commit()
        return instance
    
    def update(self, id: int, **attributes) -> Optional[Model]:
        """更新记录"""
        instance = self.find(id)
        if instance:
            for key, value in attributes.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.session.commit()
        return instance
    
    def delete(self, id: int) -> bool:
        """删除记录"""
        instance = self.find(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
    
    def count(self) -> int:
        """获取记录数量"""
        return self.session.query(self.model).count()
    
    def exists(self, **conditions) -> bool:
        """检查记录是否存在"""
        query = self.session.query(self.model)
        for field, value in conditions.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        return query.first() is not None


# 全局事件管理器
event_manager = ModelEventManager()


def model_event(event: ModelEvent):
    """模型事件装饰器"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def observer(model: Type[Model]):
    """观察者装饰器"""
    def decorator(cls):
        # 注册观察者
        for method_name in dir(cls):
            if method_name.startswith('on_'):
                event_name = method_name[3:].upper()
                if hasattr(ModelEvent, event_name):
                    event = getattr(ModelEvent, event_name)
                    method = getattr(cls, method_name)
                    event_manager.register_listener(model, event, method)
        return cls
    return decorator


def factory(model: Type[Model]) -> ModelFactory:
    """创建模型工厂"""
    return ModelFactory(model)


def repository(model: Type[Model], session: Session) -> ModelRepository:
    """创建模型仓储"""
    return ModelRepository(model, session)