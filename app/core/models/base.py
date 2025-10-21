"""
基础模型类
提供所有实体模型的通用功能
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.mixins.serialization import SerializationMixin, TimestampMixin

# 创建基础类
Base = declarative_base()


class BaseModel(Base, SerializationMixin, TimestampMixin):
    """基础模型类 - 所有实体模型的基类"""
    
    # 通用配置
    __abstract__ = True  # 这是一个抽象基类，不会创建表
    
    # 通用字段（所有模型都有）
    id = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="主键ID"
    )
    
    created_at = Column(
        DateTime, 
        nullable=False, 
        default=func.now(),
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
         comment="更新时间"
    )
    
    # 序列化配置
    __hidden_fields__ = []  # 子类可以重写
    __exclude_fields__ = []  # 子类可以重写
    __serialize_fields__ = None  # 子类可以重写
    
    def __repr__(self):
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    # 模型只负责数据定义和序列化，不包含CRUD操作
    # CRUD操作由Repository层和Service层处理


class SoftDeleteModel(BaseModel):
    """软删除模型基类"""
    
    __abstract__ = True
    
    deleted_at = Column(
        DateTime, 
        nullable=True,
        comment="删除时间"
    )
    
    is_deleted = Column(
        Boolean, 
        nullable=False, 
        default=False,
        comment="是否已删除"
    )
    
    def soft_delete(self, session):
        """软删除"""
        self.deleted_at = datetime.now()
        self.is_deleted = True
        session.commit()
        return self
    
    def restore(self, session):
        """恢复"""
        self.deleted_at = None
        self.is_deleted = False
        session.commit()
        return self
    
    @classmethod
    def get_active(cls, session):
        """获取未删除的模型"""
        return session.query(cls).filter(cls.is_deleted == False).all()
    
    @classmethod
    def get_deleted(cls, session):
        """获取已删除的模型"""
        return session.query(cls).filter(cls.is_deleted == True).all()


class AuditModel(BaseModel):
    """审计模型基类"""
    
    __abstract__ = True
    
    created_by = Column(
        Integer, 
        nullable=True,
        comment="创建者ID"
    )
    
    updated_by = Column(
        Integer, 
        nullable=True,
        comment="更新者ID"
    )
    
    def set_created_by(self, user_id):
        """设置创建者"""
        self.created_by = user_id
        return self
    
    def set_updated_by(self, user_id):
        """设置更新者"""
        self.updated_by = user_id
        return self


class TenantModel(BaseModel):
    """多租户模型基类"""
    
    __abstract__ = True
    
    tenant_id = Column(
        Integer, 
        nullable=False,
        comment="租户ID"
    )
    
    @classmethod
    def get_by_tenant(cls, session, tenant_id):
        """根据租户获取模型"""
        return session.query(cls).filter(cls.tenant_id == tenant_id).all()
    
    @classmethod
    def create_for_tenant(cls, session, tenant_id, **kwargs):
        """为租户创建模型"""
        kwargs['tenant_id'] = tenant_id
        return cls.create(session, **kwargs)