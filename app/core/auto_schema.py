"""
自动 Schema 生成器
从 SQLAlchemy 模型自动生成 Pydantic Schema
"""

from typing import Type, Optional, Set, Dict, Any, get_type_hints
from pydantic import BaseModel, create_model, Field
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta
from datetime import datetime, date
from decimal import Decimal
import enum


class SchemaGenerator:
    """Schema 自动生成器"""
    
    # 类型映射
    TYPE_MAPPING = {
        int: int,
        str: str,
        float: float,
        bool: bool,
        datetime: datetime,
        date: date,
        Decimal: Decimal,
    }
    
    @classmethod
    def _get_python_type(cls, column):
        """获取列的 Python 类型"""
        try:
            python_type = column.type.python_type
            
            # 处理枚举
            if hasattr(column.type, 'enum_class'):
                return column.type.enum_class
            
            # 映射到 Pydantic 兼容的类型
            return cls.TYPE_MAPPING.get(python_type, str)
        except:
            return str
    
    @classmethod
    def from_orm_model(
        cls,
        orm_model: Type[DeclarativeMeta],
        name: str = None,
        exclude: Set[str] = None,
        include: Set[str] = None,
        optional_fields: Set[str] = None,
        descriptions: Dict[str, str] = None
    ) -> Type[BaseModel]:
        """
        从 SQLAlchemy 模型生成 Pydantic Schema
        
        Args:
            orm_model: SQLAlchemy 模型类
            name: Schema 名称
            exclude: 排除的字段
            include: 只包含的字段（与 exclude 互斥）
            optional_fields: 设为可选的字段
            descriptions: 字段描述
        
        Returns:
            Pydantic BaseModel 类
        """
        exclude = exclude or set()
        optional_fields = optional_fields or set()
        descriptions = descriptions or {}
        
        # 获取模型检查器
        inspector = inspect(orm_model)
        
        # 构建字段字典
        fields: Dict[str, Any] = {}
        field_definitions: Dict[str, Any] = {}
        
        # 处理列
        for column in inspector.columns:
            field_name = column.name
            
            # 处理 include/exclude
            if include and field_name not in include:
                continue
            if field_name in exclude:
                continue
            
            # 获取 Python 类型
            python_type = cls._get_python_type(column)
            
            # 处理可空和可选
            is_optional = column.nullable or field_name in optional_fields
            if is_optional:
                field_type = Optional[python_type]
                default = None
            else:
                field_type = python_type
                # 处理默认值
                if column.default is not None:
                    if hasattr(column.default, 'arg'):
                        default = column.default.arg
                    else:
                        default = ...
                elif column.server_default is not None:
                    default = None
                else:
                    default = ...
            
            # 创建 Field
            field_kwargs = {}
            if field_name in descriptions:
                field_kwargs['description'] = descriptions[field_name]
            
            # 处理字符串长度限制
            if python_type == str and hasattr(column.type, 'length') and column.type.length:
                field_kwargs['max_length'] = column.type.length
            
            if field_kwargs:
                field_definitions[field_name] = (field_type, Field(default=default, **field_kwargs))
            else:
                field_definitions[field_name] = (field_type, default)
        
        # 创建 Schema
        schema_name = name or f"{orm_model.__name__}Schema"
        
        # 配置类
        config = type('Config', (), {
            'from_attributes': True,
            'use_enum_values': True,
            'json_encoders': {
                datetime: lambda v: v.isoformat(),
                date: lambda v: v.isoformat(),
            }
        })
        
        schema = create_model(
            schema_name,
            __config__=config,
            **field_definitions
        )
        
        return schema
    
    @classmethod
    def create_response_schema(
        cls,
        orm_model: Type[DeclarativeMeta],
        exclude: Set[str] = None,
        additional_exclude: Set[str] = None
    ) -> Type[BaseModel]:
        """
        创建响应 Schema（自动排除敏感字段）
        
        Args:
            orm_model: SQLAlchemy 模型
            exclude: 额外排除的字段
            additional_exclude: 追加排除的字段
        """
        # 默认排除的敏感字段
        default_exclude = {'password', 'remember_token', 'secret_key', 'api_key', 'token'}
        
        if exclude is None:
            exclude = default_exclude
        else:
            exclude = exclude | default_exclude
        
        if additional_exclude:
            exclude = exclude | additional_exclude
        
        return cls.from_orm_model(
            orm_model,
            name=f"{orm_model.__name__}Response",
            exclude=exclude
        )
    
    @classmethod
    def create_create_schema(
        cls,
        orm_model: Type[DeclarativeMeta],
        exclude: Set[str] = None,
        additional_exclude: Set[str] = None
    ) -> Type[BaseModel]:
        """
        创建 Create Schema（排除自动生成的字段）
        
        Args:
            orm_model: SQLAlchemy 模型
            exclude: 额外排除的字段
            additional_exclude: 追加排除的字段
        """
        # 默认排除的自动字段
        default_exclude = {
            'id', 'created_at', 'updated_at', 'deleted_at',
            'create_time', 'update_time', 'delete_time'
        }
        
        if exclude is None:
            exclude = default_exclude
        else:
            exclude = exclude | default_exclude
        
        if additional_exclude:
            exclude = exclude | additional_exclude
        
        return cls.from_orm_model(
            orm_model,
            name=f"{orm_model.__name__}Create",
            exclude=exclude
        )
    
    @classmethod
    def create_update_schema(
        cls,
        orm_model: Type[DeclarativeMeta],
        exclude: Set[str] = None,
        additional_exclude: Set[str] = None
    ) -> Type[BaseModel]:
        """
        创建 Update Schema（所有字段可选）
        
        Args:
            orm_model: SQLAlchemy 模型
            exclude: 额外排除的字段
            additional_exclude: 追加排除的字段
        """
        # 默认排除的字段
        default_exclude = {
            'id', 'created_at', 'updated_at', 'deleted_at',
            'create_time', 'update_time', 'delete_time'
        }
        
        if exclude is None:
            exclude = default_exclude
        else:
            exclude = exclude | default_exclude
        
        if additional_exclude:
            exclude = exclude | additional_exclude
        
        # 获取所有字段
        inspector = inspect(orm_model)
        all_fields = {col.name for col in inspector.columns}
        optional_fields = all_fields - exclude
        
        return cls.from_orm_model(
            orm_model,
            name=f"{orm_model.__name__}Update",
            exclude=exclude,
            optional_fields=optional_fields
        )
    
    @classmethod
    def create_all_schemas(
        cls,
        orm_model: Type[DeclarativeMeta],
        exclude_from_response: Set[str] = None,
        exclude_from_create: Set[str] = None,
        exclude_from_update: Set[str] = None
    ) -> Dict[str, Type[BaseModel]]:
        """
        一次性创建所有 Schema
        
        Returns:
            {'Response': ..., 'Create': ..., 'Update': ...}
        """
        return {
            'Response': cls.create_response_schema(orm_model, additional_exclude=exclude_from_response),
            'Create': cls.create_create_schema(orm_model, additional_exclude=exclude_from_create),
            'Update': cls.create_update_schema(orm_model, additional_exclude=exclude_from_update),
        }


# 装饰器：自动为模型添加 schemas 属性
def auto_schema(
    exclude_from_response: Set[str] = None,
    exclude_from_create: Set[str] = None,
    exclude_from_update: Set[str] = None
):
    """
    自动生成 Schema 的装饰器
    
    用法：
        @auto_schema()
        class User(Base):
            ...
        
        # 使用
        User.schemas['Response']
        User.schemas['Create']
        User.schemas['Update']
    """
    def decorator(orm_model: Type[DeclarativeMeta]) -> Type[DeclarativeMeta]:
        # 生成所有 Schema
        schemas = SchemaGenerator.create_all_schemas(
            orm_model,
            exclude_from_response=exclude_from_response,
            exclude_from_create=exclude_from_create,
            exclude_from_update=exclude_from_update
        )
        
        # 添加到模型类
        orm_model.schemas = schemas
        
        # 便捷访问
        orm_model.ResponseSchema = schemas['Response']
        orm_model.CreateSchema = schemas['Create']
        orm_model.UpdateSchema = schemas['Update']
        
        return orm_model
    
    return decorator


# 使用示例
if __name__ == "__main__":
    # 假设有这样的模型
    from sqlalchemy import Column, Integer, String, Boolean, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    
    Base = declarative_base()
    
    @auto_schema()
    class User(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True)
        username = Column(String(50), nullable=False, unique=True)
        email = Column(String(100), nullable=False, unique=True)
        password = Column(String(255), nullable=False)
        name = Column(String(100))
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
    
    # 自动生成的 Schema 可以直接使用
    print(User.ResponseSchema.schema_json(indent=2))
    print(User.CreateSchema.schema_json(indent=2))
    print(User.UpdateSchema.schema_json(indent=2))
    
    # 或者手动生成
    UserResponse = SchemaGenerator.create_response_schema(User)
    print(UserResponse.schema_json(indent=2))

