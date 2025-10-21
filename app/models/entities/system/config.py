"""
系统配置管理相关实体模型
基于Django-Vue3-Admin的系统配置功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index
from app.core.models.base import AuditModel


class Config(AuditModel):
    """系统配置表"""
    __tablename__ = 'configs'
    
    parent_id = Column(BigInteger, ForeignKey('configs.id', ondelete='CASCADE'), nullable=True, comment="父配置ID")
    title = Column(String(50), nullable=False, comment="配置标题")
    key = Column(String(100), nullable=False, comment="配置键")
    value = Column(JSONB, nullable=True, comment="配置值")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
    data_options = Column(JSONB, nullable=True, comment="数据选项")
    form_item_type = Column(Integer, default=0, comment="表单项类型: 0-输入框 1-数字输入框 2-文本域 3-选择器 4-多选框 5-单选框 6-开关 7-日期选择器 8-时间选择器 9-日期时间选择器 10-文件上传 11-图片上传 12-富文本编辑器 13-代码编辑器 14-颜色选择器 15-滑块")
    rule = Column(JSONB, nullable=True, comment="验证规则")
    placeholder = Column(String(50), nullable=True, comment="占位符")
    setting = Column(JSONB, nullable=True, comment="设置")
    
    # 关系
    parent = relationship("Config", remote_side=[id], back_populates="children")
    children = relationship("Config", back_populates="parent")
    
    # 索引
    __table_args__ = (
        Index('idx_config_key', 'key'),
    )


class ApiWhiteList(AuditModel):
    """API白名单表"""
    __tablename__ = 'api_white_lists'
    
    url = Column(String(200), nullable=False, comment="URL")
    method = Column(Integer, default=0, comment="请求方法: 0-GET 1-POST 2-PUT 3-DELETE")
    enable_datasource = Column(Boolean, default=True, comment="是否启用数据源")