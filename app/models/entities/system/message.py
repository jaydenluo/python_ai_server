"""
消息中心相关实体模型
基于Django-Vue3-Admin的消息中心功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base import AuditModel


class MessageCenter(AuditModel):
    """消息中心表"""
    __tablename__ = 'message_centers'
    
    title = Column(String(100), nullable=False, comment="消息标题")
    content = Column(Text, nullable=False, comment="消息内容")
    target_type = Column(Integer, default=0, comment="目标类型")
    
    # 关系
    target_users = relationship("MessageCenterTargetUser", back_populates="message_center")
    target_depts = relationship("MessageCenterTargetDept", back_populates="message_center")
    target_roles = relationship("MessageCenterTargetRole", back_populates="message_center")


class MessageCenterTargetUser(AuditModel):
    """消息中心目标用户表"""
    __tablename__ = 'message_center_target_users'
    
    users_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="用户ID")
    messagecenter_id = Column(BigInteger, ForeignKey('message_centers.id', ondelete='CASCADE'), nullable=False, comment="消息中心ID")
    is_read = Column(Boolean, default=False, comment="是否已读")
    
    # 关系
    user = relationship("User")
    message_center = relationship("MessageCenter", back_populates="target_users")


class MessageCenterTargetDept(AuditModel):
    """消息中心目标部门关联表"""
    __tablename__ = 'message_center_target_depts'
    
    messagecenter_id = Column(BigInteger, ForeignKey('message_centers.id', ondelete='CASCADE'), nullable=False, comment="消息中心ID")
    dept_id = Column(BigInteger, ForeignKey('depts.id', ondelete='CASCADE'), nullable=False, comment="部门ID")
    
    # 关系
    dept = relationship("Dept")
    message_center = relationship("MessageCenter", back_populates="target_depts")


class MessageCenterTargetRole(AuditModel):
    """消息中心目标角色关联表"""
    __tablename__ = 'message_center_target_roles'
    
    messagecenter_id = Column(BigInteger, ForeignKey('message_centers.id', ondelete='CASCADE'), nullable=False, comment="消息中心ID")
    role_id = Column(BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, comment="角色ID")
    
    # 关系
    role = relationship("Role")
    message_center = relationship("MessageCenter", back_populates="target_roles")


class DownloadCenter(AuditModel):
    """下载中心表"""
    __tablename__ = 'download_centers'
    
    task_name = Column(String(255), nullable=False, comment="任务名称")
    task_status = Column(Integer, default=0, comment="任务状态: 0-已创建 1-进行中 2-完成 3-失败")
    file_name = Column(String(255), nullable=True, comment="文件名")
    url = Column(String(100), nullable=True, comment="文件路径")
    size = Column(BigInteger, default=0, comment="文件大小")
    md5sum = Column(String(36), nullable=True, comment="MD5校验值")