"""
智能ORM迁移系统
基于模型变更自动生成和执行数据库迁移
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import inspect
from pathlib import Path

from app.models.base import Model
from app.core.config.settings import config


class MigrationType(Enum):
    """迁移类型"""
    CREATE_TABLE = "create_table"
    ALTER_TABLE = "alter_table"
    DROP_TABLE = "drop_table"
    CREATE_INDEX = "create_index"
    DROP_INDEX = "drop_index"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"


@dataclass
class ColumnDefinition:
    """列定义"""
    name: str
    type: str
    nullable: bool = True
    default: Any = None
    primary_key: bool = False
    auto_increment: bool = False
    unique: bool = False
    index: bool = False
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None


@dataclass
class TableDefinition:
    """表定义"""
    name: str
    columns: List[ColumnDefinition] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, Any]] = field(default_factory=list)
    timestamps: bool = True


@dataclass
class Migration:
    """迁移定义"""
    id: str
    type: MigrationType
    table_name: str
    changes: Dict[str, Any]
    timestamp: datetime
    description: str
    rollback_sql: Optional[str] = None


class ModelAnalyzer:
    """模型分析器"""
    
    def __init__(self):
        self.models: Dict[str, Type[Model]] = {}
        self.schema_cache: Dict[str, TableDefinition] = {}
    
    def register_model(self, model_class: Type[Model]):
        """注册模型"""
        table_name = getattr(model_class, '__table__', model_class.__name__.lower())
        self.models[table_name] = model_class
    
    def analyze_model(self, model_class: Type[Model]) -> TableDefinition:
        """分析模型结构"""
        table_name = getattr(model_class, '__table__', model_class.__name__.lower())
        
        # 获取模型属性
        columns = []
        for name, annotation in model_class.__annotations__.items():
            if name.startswith('_'):
                continue
            
            column_def = self._parse_column_definition(name, annotation, model_class)
            columns.append(column_def)
        
        # 添加时间戳字段
        if getattr(model_class, '__timestamps__', True):
            columns.extend([
                ColumnDefinition("created_at", "datetime", nullable=False),
                ColumnDefinition("updated_at", "datetime", nullable=False)
            ])
        
        return TableDefinition(
            name=table_name,
            columns=columns,
            timestamps=getattr(model_class, '__timestamps__', True)
        )
    
    def _parse_column_definition(self, name: str, annotation: Any, model_class: Type[Model]) -> ColumnDefinition:
        """解析列定义"""
        # 基础类型映射
        type_mapping = {
            int: "integer",
            str: "varchar",
            float: "decimal",
            bool: "boolean",
            datetime: "datetime",
            list: "json",
            dict: "json"
        }
        
        # 获取字段类型
        field_type = "varchar"
        if hasattr(annotation, '__origin__'):
            # 处理 Optional[Type] 等复合类型
            if annotation.__origin__ is Union:
                for arg in annotation.__args__:
                    if arg is not type(None):
                        field_type = type_mapping.get(arg, "varchar")
                        break
        else:
            field_type = type_mapping.get(annotation, "varchar")
        
        # 检查是否为主键
        primary_key = name == getattr(model_class, '__primary_key__', 'id')
        
        # 检查是否可空
        nullable = not primary_key
        
        # 检查默认值
        default_value = None
        if hasattr(model_class, '__defaults__'):
            defaults = getattr(model_class, '__defaults__', {})
            if name in defaults:
                default_value = defaults[name]
        
        return ColumnDefinition(
            name=name,
            type=field_type,
            nullable=nullable,
            default=default_value,
            primary_key=primary_key,
            auto_increment=primary_key
        )
    
    def compare_schemas(self, old_schema: TableDefinition, new_schema: TableDefinition) -> List[Migration]:
        """比较模式差异"""
        migrations = []
        
        # 检查表是否存在
        if not old_schema:
            # 创建新表
            migrations.append(Migration(
                id=self._generate_migration_id(),
                type=MigrationType.CREATE_TABLE,
                table_name=new_schema.name,
                changes={"schema": new_schema},
                timestamp=datetime.now(),
                description=f"Create table {new_schema.name}"
            ))
        else:
            # 比较列差异
            old_columns = {col.name: col for col in old_schema.columns}
            new_columns = {col.name: col for col in new_schema.columns}
            
            # 新增列
            for name, column in new_columns.items():
                if name not in old_columns:
                    migrations.append(Migration(
                        id=self._generate_migration_id(),
                        type=MigrationType.ADD_COLUMN,
                        table_name=new_schema.name,
                        changes={"column": column},
                        timestamp=datetime.now(),
                        description=f"Add column {name} to {new_schema.name}"
                    ))
            
            # 删除列
            for name, column in old_columns.items():
                if name not in new_columns:
                    migrations.append(Migration(
                        id=self._generate_migration_id(),
                        type=MigrationType.DROP_COLUMN,
                        table_name=new_schema.name,
                        changes={"column": column},
                        timestamp=datetime.now(),
                        description=f"Drop column {name} from {new_schema.name}"
                    ))
            
            # 修改列
            for name, new_column in new_columns.items():
                if name in old_columns:
                    old_column = old_columns[name]
                    if self._columns_different(old_column, new_column):
                        migrations.append(Migration(
                            id=self._generate_migration_id(),
                            type=MigrationType.MODIFY_COLUMN,
                            table_name=new_schema.name,
                            changes={"old_column": old_column, "new_column": new_column},
                            timestamp=datetime.now(),
                            description=f"Modify column {name} in {new_schema.name}"
                        ))
        
        return migrations
    
    def _columns_different(self, old_col: ColumnDefinition, new_col: ColumnDefinition) -> bool:
        """检查列是否不同"""
        return (old_col.type != new_col.type or
                old_col.nullable != new_col.nullable or
                old_col.default != new_col.default or
                old_col.unique != new_col.unique)
    
    def _generate_migration_id(self) -> str:
        """生成迁移ID"""
        return hashlib.md5(f"{datetime.now()}".encode()).hexdigest()[:8]


class MigrationGenerator:
    """迁移生成器"""
    
    def __init__(self):
        self.migrations_dir = Path("database/migrations")
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_migration(self, migration: Migration) -> str:
        """生成迁移文件"""
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{migration.id}_{migration.table_name}.py"
        filepath = self.migrations_dir / filename
        
        # 生成迁移内容
        content = self._generate_migration_content(migration)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def _generate_migration_content(self, migration: Migration) -> str:
        """生成迁移文件内容"""
        content = f'''"""
迁移文件: {migration.description}
生成时间: {migration.timestamp}
"""

from app.core.orm.migration_system import Migration, MigrationType
from app.core.orm.sql_generator import SQLGenerator


def up():
    """执行迁移"""
    sql_generator = SQLGenerator()
    
    if migration.type == MigrationType.CREATE_TABLE:
        sql = sql_generator.generate_create_table_sql(migration.changes["schema"])
    elif migration.type == MigrationType.ADD_COLUMN:
        sql = sql_generator.generate_add_column_sql(migration.table_name, migration.changes["column"])
    elif migration.type == MigrationType.DROP_COLUMN:
        sql = sql_generator.generate_drop_column_sql(migration.table_name, migration.changes["column"])
    elif migration.type == MigrationType.MODIFY_COLUMN:
        sql = sql_generator.generate_modify_column_sql(migration.table_name, migration.changes["old_column"], migration.changes["new_column"])
    
    # 执行SQL
    # database.execute(sql)


def down():
    """回滚迁移"""
    sql_generator = SQLGenerator()
    
    if migration.type == MigrationType.CREATE_TABLE:
        sql = sql_generator.generate_drop_table_sql(migration.table_name)
    elif migration.type == MigrationType.ADD_COLUMN:
        sql = sql_generator.generate_drop_column_sql(migration.table_name, migration.changes["column"])
    elif migration.type == MigrationType.DROP_COLUMN:
        sql = sql_generator.generate_add_column_sql(migration.table_name, migration.changes["column"])
    elif migration.type == MigrationType.MODIFY_COLUMN:
        sql = sql_generator.generate_modify_column_sql(migration.table_name, migration.changes["new_column"], migration.changes["old_column"])
    
    # 执行SQL
    # database.execute(sql)
'''
        return content


class SQLGenerator:
    """SQL生成器"""
    
    def generate_create_table_sql(self, schema: TableDefinition) -> str:
        """生成创建表SQL"""
        columns = []
        for col in schema.columns:
            col_def = self._generate_column_definition(col)
            columns.append(col_def)
        
        sql = f"CREATE TABLE {schema.name} (\n"
        sql += ",\n".join(f"  {col}" for col in columns)
        sql += "\n);"
        
        return sql
    
    def generate_add_column_sql(self, table_name: str, column: ColumnDefinition) -> str:
        """生成添加列SQL"""
        col_def = self._generate_column_definition(column)
        return f"ALTER TABLE {table_name} ADD COLUMN {col_def};"
    
    def generate_drop_column_sql(self, table_name: str, column: ColumnDefinition) -> str:
        """生成删除列SQL"""
        return f"ALTER TABLE {table_name} DROP COLUMN {column.name};"
    
    def generate_modify_column_sql(self, table_name: str, old_column: ColumnDefinition, new_column: ColumnDefinition) -> str:
        """生成修改列SQL"""
        col_def = self._generate_column_definition(new_column)
        return f"ALTER TABLE {table_name} MODIFY COLUMN {col_def};"
    
    def generate_drop_table_sql(self, table_name: str) -> str:
        """生成删除表SQL"""
        return f"DROP TABLE {table_name};"
    
    def _generate_column_definition(self, column: ColumnDefinition) -> str:
        """生成列定义"""
        parts = [column.name]
        
        # 类型
        if column.type == "varchar":
            length = column.length or 255
            parts.append(f"VARCHAR({length})")
        elif column.type == "integer":
            parts.append("INTEGER")
        elif column.type == "decimal":
            precision = column.precision or 10
            scale = column.scale or 2
            parts.append(f"DECIMAL({precision},{scale})")
        elif column.type == "boolean":
            parts.append("BOOLEAN")
        elif column.type == "datetime":
            parts.append("DATETIME")
        elif column.type == "json":
            parts.append("JSON")
        
        # 可空性
        if not column.nullable:
            parts.append("NOT NULL")
        
        # 默认值
        if column.default is not None:
            if isinstance(column.default, str):
                parts.append(f"DEFAULT '{column.default}'")
            else:
                parts.append(f"DEFAULT {column.default}")
        
        # 主键
        if column.primary_key:
            parts.append("PRIMARY KEY")
        
        # 自增
        if column.auto_increment:
            parts.append("AUTO_INCREMENT")
        
        # 唯一
        if column.unique:
            parts.append("UNIQUE")
        
        return " ".join(parts)


class SmartMigrationManager:
    """智能迁移管理器"""
    
    def __init__(self):
        self.analyzer = ModelAnalyzer()
        self.generator = MigrationGenerator()
        self.sql_generator = SQLGenerator()
    
    def detect_changes(self, model_classes: List[Type[Model]]) -> List[Migration]:
        """检测模型变更"""
        migrations = []
        
        for model_class in model_classes:
            # 分析当前模型
            current_schema = self.analyzer.analyze_model(model_class)
            
            # 获取数据库中的模式（这里需要实现数据库模式读取）
            # existing_schema = self._get_existing_schema(current_schema.name)
            
            # 比较差异（这里暂时跳过，实际需要从数据库读取现有模式）
            # model_migrations = self.analyzer.compare_schemas(existing_schema, current_schema)
            # migrations.extend(model_migrations)
        
        return migrations
    
    def generate_migrations(self, migrations: List[Migration]) -> List[str]:
        """生成迁移文件"""
        generated_files = []
        
        for migration in migrations:
            filepath = self.generator.generate_migration(migration)
            generated_files.append(filepath)
        
        return generated_files
    
    def auto_migrate(self, model_classes: List[Type[Model]], dry_run: bool = True) -> Dict[str, Any]:
        """自动迁移"""
        result = {
            "detected_changes": [],
            "generated_files": [],
            "sql_statements": [],
            "warnings": []
        }
        
        # 检测变更
        migrations = self.detect_changes(model_classes)
        result["detected_changes"] = [m.description for m in migrations]
        
        if not migrations:
            result["message"] = "没有检测到模型变更"
            return result
        
        # 生成迁移文件
        if not dry_run:
            generated_files = self.generate_migrations(migrations)
            result["generated_files"] = generated_files
        
        # 生成SQL语句
        for migration in migrations:
            sql = self._generate_migration_sql(migration)
            result["sql_statements"].append({
                "migration": migration.description,
                "sql": sql
            })
        
        return result
    
    def _generate_migration_sql(self, migration: Migration) -> str:
        """生成迁移SQL"""
        if migration.type == MigrationType.CREATE_TABLE:
            return self.sql_generator.generate_create_table_sql(migration.changes["schema"])
        elif migration.type == MigrationType.ADD_COLUMN:
            return self.sql_generator.generate_add_column_sql(migration.table_name, migration.changes["column"])
        elif migration.type == MigrationType.DROP_COLUMN:
            return self.sql_generator.generate_drop_column_sql(migration.table_name, migration.changes["column"])
        elif migration.type == MigrationType.MODIFY_COLUMN:
            return self.sql_generator.generate_modify_column_sql(
                migration.table_name, 
                migration.changes["old_column"], 
                migration.changes["new_column"]
            )
        
        return ""


# 全局迁移管理器实例
migration_manager = SmartMigrationManager()