"""
智能ORM装饰器
提供模型变更检测和自动更新功能
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type
from datetime import datetime
import hashlib

from app.core.orm.migration_system import migration_manager, ModelAnalyzer
from app.models.base import Model


def auto_migrate(model_class: Type[Model] = None, force: bool = False):
    """
    自动迁移装饰器
    当模型类被修改时，自动检测变更并生成迁移
    """
    def decorator(cls):
        if not issubclass(cls, Model):
            raise ValueError("auto_migrate装饰器只能用于Model子类")
        
        # 注册模型到分析器
        migration_manager.analyzer.register_model(cls)
        
        # 添加模型变更检测
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def new_init(self, *args, **kwargs):
            # 检测模型变更
            if not force:
                self._check_model_changes()
            
            # 调用原始初始化
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        
        # 添加模型变更检测方法
        cls._check_model_changes = classmethod(_check_model_changes)
        
        return cls
    
    if model_class is None:
        return decorator
    else:
        return decorator(model_class)


def track_changes(model_class: Type[Model] = None):
    """
    变更跟踪装饰器
    跟踪模型属性的变更
    """
    def decorator(cls):
        if not issubclass(cls, Model):
            raise ValueError("track_changes装饰器只能用于Model子类")
        
        # 添加变更跟踪属性
        cls._original_values = {}
        cls._changed_fields = set()
        
        # 重写属性设置方法
        original_setattr = cls.__setattr__
        
        def new_setattr(self, name, value):
            # 记录原始值
            if not hasattr(self, '_original_values'):
                self._original_values = {}
            if not hasattr(self, '_changed_fields'):
                self._changed_fields = set()
            
            # 检查值是否真的改变了
            if hasattr(self, name):
                old_value = getattr(self, name)
                if old_value != value:
                    self._changed_fields.add(name)
                    if name not in self._original_values:
                        self._original_values[name] = old_value
            
            # 设置新值
            original_setattr(self, name, value)
        
        cls.__setattr__ = new_setattr
        
        # 添加变更检测方法
        cls.has_changes = _has_changes
        cls.get_changes = _get_changes
        cls.get_original_value = _get_original_value
        cls.reset_changes = _reset_changes
        
        return cls
    
    if model_class is None:
        return decorator
    else:
        return decorator(model_class)


def schema_version(version: str):
    """
    模式版本装饰器
    标记模型的模式版本
    """
    def decorator(cls):
        cls._schema_version = version
        return cls
    
    return decorator


def auto_timestamps(model_class: Type[Model] = None):
    """
    自动时间戳装饰器
    自动添加created_at和updated_at字段
    """
    def decorator(cls):
        if not issubclass(cls, Model):
            raise ValueError("auto_timestamps装饰器只能用于Model子类")
        
        # 添加时间戳字段
        cls.created_at = None
        cls.updated_at = None
        
        # 重写save方法
        original_save = getattr(cls, 'save', None)
        
        def new_save(self):
            now = datetime.now()
            
            if not hasattr(self, 'created_at') or self.created_at is None:
                self.created_at = now
            
            self.updated_at = now
            
            if original_save:
                return original_save(self)
            else:
                # 默认保存逻辑
                return self._default_save()
        
        cls.save = new_save
        
        return cls
    
    if model_class is None:
        return decorator
    else:
        return decorator(model_class)


def auto_validate(model_class: Type[Model] = None):
    """
    自动验证装饰器
    自动验证模型数据
    """
    def decorator(cls):
        if not issubclass(cls, Model):
            raise ValueError("auto_validate装饰器只能用于Model子类")
        
        # 添加验证规则
        cls._validation_rules = {}
        
        # 重写save方法
        original_save = getattr(cls, 'save', None)
        
        def new_save(self):
            # 执行验证
            self._validate()
            
            if original_save:
                return original_save(self)
            else:
                return self._default_save()
        
        cls.save = new_save
        cls._validate = _validate
        cls.add_validation_rule = _add_validation_rule
        
        return cls
    
    if model_class is None:
        return decorator
    else:
        return decorator(model_class)


# 辅助方法
def _check_model_changes(cls):
    """检查模型变更"""
    try:
        # 分析当前模型
        schema = migration_manager.analyzer.analyze_model(cls)
        
        # 这里可以添加变更检测逻辑
        # 例如：与数据库中的模式比较
        
        print(f"🔍 检查模型 {cls.__name__} 的变更...")
        
    except Exception as e:
        print(f"⚠️  检查模型变更时出错: {e}")


def _has_changes(self) -> bool:
    """检查是否有变更"""
    return len(self._changed_fields) > 0


def _get_changes(self) -> Dict[str, Any]:
    """获取变更的字段"""
    changes = {}
    for field in self._changed_fields:
        changes[field] = {
            'old': self._original_values.get(field),
            'new': getattr(self, field)
        }
    return changes


def _get_original_value(self, field: str) -> Any:
    """获取字段的原始值"""
    return self._original_values.get(field)


def _reset_changes(self):
    """重置变更跟踪"""
    self._original_values.clear()
    self._changed_fields.clear()


def _validate(self):
    """验证模型数据"""
    for field, rules in self._validation_rules.items():
        value = getattr(self, field, None)
        
        for rule in rules:
            if not rule(value):
                raise ValueError(f"验证失败: {field} 不符合规则 {rule.__name__}")


def _add_validation_rule(self, field: str, rule: Callable):
    """添加验证规则"""
    if field not in self._validation_rules:
        self._validation_rules[field] = []
    self._validation_rules[field].append(rule)


# 验证规则
def required(value) -> bool:
    """必填验证"""
    return value is not None and value != ""


def email(value) -> bool:
    """邮箱验证"""
    if value is None:
        return True
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(value)))


def min_length(length: int):
    """最小长度验证"""
    def rule(value) -> bool:
        if value is None:
            return True
        return len(str(value)) >= length
    return rule


def max_length(length: int):
    """最大长度验证"""
    def rule(value) -> bool:
        if value is None:
            return True
        return len(str(value)) <= length
    return rule


def unique(model_class: Type[Model], field: str):
    """唯一性验证"""
    def rule(value) -> bool:
        if value is None:
            return True
        # 这里需要实现数据库查询逻辑
        # 暂时返回True
        return True
    return rule


# 使用示例
if __name__ == "__main__":
    # 示例：使用装饰器
    @auto_migrate
    @track_changes
    @auto_timestamps
    @auto_validate
    @schema_version("1.0.0")
    class ExampleModel(Model):
        __table__ = "examples"
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # 添加验证规则
            self.add_validation_rule("email", required)
            self.add_validation_rule("email", email)
            self.add_validation_rule("name", min_length(2))
            self.add_validation_rule("name", max_length(50))