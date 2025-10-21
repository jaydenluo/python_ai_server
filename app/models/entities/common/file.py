"""
文件管理相关实体模型
基于Django-Vue3-Admin的文件管理功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, SmallInteger
from sqlalchemy.orm import relationship
from app.core.models.base import AuditModel


class FileList(AuditModel):
    """文件列表表"""
    __tablename__ = 'file_lists'
    
    name = Column(String(200), nullable=True, comment="文件名")
    url = Column(String(100), nullable=True, comment="文件路径")
    file_url = Column(String(255), nullable=True, comment="文件地址")
    engine = Column(String(100), default='local', comment="存储引擎")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    size = Column(String(36), nullable=True, comment="文件大小")
    md5sum = Column(String(36), nullable=True, comment="MD5校验值")
    upload_method = Column(SmallInteger, default=0, comment="上传方式: 0-默认上传 1-文件选择器上传")
    file_type = Column(SmallInteger, default=3, comment="文件类型: 0-图片 1-视频 2-音频 3-其他")