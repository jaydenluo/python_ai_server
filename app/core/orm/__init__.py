"""
智能ORM系统
提供模型变更检测和自动数据库更新功能
"""

from .models import Model, RelationshipType, Relationship
from .query import ModelQuery, QueryOperator, QueryCondition, QueryJoin
# 移除循环导入，迁移系统功能已整合到其他模块
from .commands import ORMCommands
from .decorators import (
    auto_migrate, track_changes, schema_version, auto_timestamps, auto_validate,
    required, email, min_length, max_length, unique
)
from .seeders import (
    SeederManager, SeederInfo, seeder_manager, seeder, create_seeder,
    run_seeder, run_all_seeders, reset_seeders
)
# 关系映射使用SQLAlchemy原生功能，不需要重复实现
from .advanced_features import (
    ModelEventManager, ModelEvent, ModelEventData, SoftDeleteMixin, AuditMixin,
    VersionMixin, TimestampMixin, CacheMixin, ObserverMixin, ModelScope,
    ModelFactory, ModelRepository, event_manager, model_event, observer, factory, repository
)
# 迁移系统增强功能已整合到migration_system.py中

__all__ = [
    # 基础模型
    "Model",
    "RelationshipType",
    "Relationship",
    
    # 查询构建器
    "ModelQuery",
    "QueryOperator",
    "QueryCondition", 
    "QueryJoin",
    
    # 核心组件（迁移系统功能已整合到其他模块）
    
    # 命令系统
    "ORMCommands",
    
    # 装饰器
    "auto_migrate",
    "track_changes", 
    "schema_version",
    "auto_timestamps",
    "auto_validate",
    
    # 验证规则
    "required",
    "email",
    "min_length",
    "max_length", 
    "unique",
    
    # 种子数据
    "SeederManager",
    "SeederInfo",
    "seeder_manager",
    "seeder",
    "create_seeder",
    "run_seeder",
    "run_all_seeders",
    "reset_seeders",
    
    # 关系映射使用SQLAlchemy原生功能
    
    # 高级功能
    "ModelEventManager",
    "ModelEvent",
    "ModelEventData",
    "SoftDeleteMixin",
    "AuditMixin",
    "VersionMixin",
    "TimestampMixin",
    "CacheMixin",
    "ObserverMixin",
    "ModelScope",
    "ModelFactory",
    "ModelRepository",
    "event_manager",
    "model_event",
    "observer",
    "factory",
    "repository",
    
    # 迁移系统功能已整合
]