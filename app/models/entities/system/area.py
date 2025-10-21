"""
地区管理相关实体模型
基于Django-Vue3-Admin的地区管理功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.models.base import AuditModel


class Area(AuditModel):
    """地区表"""
    __tablename__ = 'areas'
    
    name = Column(String(100), nullable=False, comment="地区名称")
    code = Column(String(20), unique=True, nullable=False, comment="地区编码")
    level = Column(BigInteger, nullable=False, comment="地区级别: 1-省份 2-城市 3-区县 4-乡级")
    pinyin = Column(String(255), nullable=False, comment="拼音")
    initials = Column(String(20), nullable=False, comment="首字母")
    enable = Column(Boolean, default=True, comment="是否启用")
    pcode = Column(String(20), ForeignKey('areas.code', ondelete='CASCADE'), nullable=True, comment="父地区编码")
    
    # 关系
    parent = relationship("Area", remote_side=[code], back_populates="children")
    children = relationship("Area", back_populates="parent")
    
    # 索引
    __table_args__ = (
        Index('idx_area_code', 'code'),
    )