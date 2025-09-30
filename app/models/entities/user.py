"""
用户实体
基于SQLAlchemy的用户模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.models.base import BaseModel


class User(BaseModel):
    """用户模型 - 基于SQLAlchemy的数据定义"""

    __tablename__ = "users"

    # 基础信息字段
    username = Column(
        String(20), 
        nullable=False, 
        unique=True, 
        comment="用户登录名，唯一"
    )
    
    email = Column(
        String(255), 
        nullable=False, 
        unique=True, 
        comment="用户邮箱地址，唯一"
    )
    
    password = Column(
        String(255), 
        nullable=False, 
        comment="加密后的密码"
    )
    
    first_name = Column(
        String(50), 
        nullable=False, 
        comment="用户名字"
    )
    
    last_name = Column(
        String(50), 
        nullable=False, 
        comment="用户姓氏"
    )
    
    phone = Column(
        String(15), 
        nullable=True, 
        comment="用户手机号码"
    )
    
    avatar = Column(
        String(255), 
        nullable=True, 
        comment="用户头像文件路径"
    )

    # 状态字段
    status = Column(
        String(20), 
        nullable=False, 
        default="pending", 
        comment="用户状态：pending, active, inactive, suspended"
    )

    # 时间字段
    email_verified_at = Column(
        DateTime, 
        nullable=True, 
        comment="邮箱验证时间"
    )

    last_login_at = Column(
        DateTime, 
        nullable=True, 
        comment="最后登录时间"
    )

    # 统计字段
    login_count = Column(
        Integer, 
        nullable=False, 
        default=0, 
        comment="用户登录次数"
    )

    # 权限字段
    is_superuser = Column(
        Boolean, 
        nullable=False, 
        default=False, 
        comment="是否为超级用户"
    )

    permissions = Column(
        JSON, 
        nullable=True, 
        comment="用户权限列表，JSON格式"
    )

    # 档案数据字段
    profile_data = Column(
        JSON, 
        nullable=True, 
        comment="用户档案信息，JSON格式"
    )

    # 隐藏字段（不在API中暴露）
    remember_token = Column(
        String(100), 
        nullable=True, 
        comment="记住我令牌"
    )

    password_reset_token = Column(
        String(100), 
        nullable=True, 
        comment="密码重置令牌"
    )

    # 索引定义
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_status", "status"),
        Index("idx_users_created_at", "created_at"),
    )

    # 关系定义
    # posts = relationship("Post", back_populates="user")
    # comments = relationship("Comment", back_populates="user")
    # ai_models = relationship("AIModel", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    # 属性方法
    @property
    def full_name(self) -> str:
        """获取全名"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == "active"

    @property
    def is_verified(self) -> bool:
        """是否已验证邮箱"""
        return self.email_verified_at is not None

    # 序列化配置
    __hidden_fields__ = ["password", "remember_token", "password_reset_token"]
    __exclude_fields__ = ["password_reset_token"]  # 默认排除密码重置令牌
    
    # 数据转换方法（由BaseModel提供）
    # to_dict() - 自动序列化所有字段
    # to_json() - 自动转换为JSON
    # to_public_dict() - 自动隐藏敏感信息
    # to_admin_dict() - 包含所有信息