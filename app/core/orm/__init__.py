"""
智能ORM系统
提供模型变更检测和自动数据库更新功能
"""

from .models import Model, RelationshipType, Relationship
from .query import ModelQuery, QueryOperator, QueryCondition, QueryJoin
from .migration_system import (
    ModelAnalyzer, MigrationGenerator, SQLGenerator, SmartMigrationManager,
    migration_manager
)
from .commands import ORMCommands
from .decorators import (
    auto_migrate, track_changes, schema_version, auto_timestamps, auto_validate,
    required, email, min_length, max_length, unique
)

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
    
    # 核心组件
    "ModelAnalyzer",
    "MigrationGenerator", 
    "SQLGenerator",
    "SmartMigrationManager",
    "migration_manager",
    
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
    "unique"
]