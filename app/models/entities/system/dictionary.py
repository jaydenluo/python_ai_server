"""
字典管理相关实体模型
基于Django-Vue3-Admin的字典管理功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.models.base import AuditModel


class Dictionary(AuditModel):
    """字典表"""
    __tablename__ = 'dictionaries'
    
    label = Column(String(100), nullable=True, comment="字典标签")
    value = Column(String(200), nullable=True, comment="字典值")
    parent_id = Column(BigInteger, ForeignKey('dictionaries.id', ondelete='PROTECT'), nullable=True, comment="父字典ID")
    type = Column(Integer, default=0, comment="数据值类型: 0-字符串 1-数字 2-布尔 3-日期 4-时间 5-日期时间 6-JSON 7-数组")
    color = Column(String(20), nullable=True, comment="颜色")
    is_value = Column(Boolean, default=False, comment="是否为值")
    status = Column(Boolean, default=True, comment="状态")
    sort = Column(Integer, default=1, comment="排序")
    remark = Column(String(2000), nullable=True, comment="备注")
    
    # 关系
    parent = relationship("Dictionary", remote_side=[id], back_populates="children")
    children = relationship("Dictionary", back_populates="parent")