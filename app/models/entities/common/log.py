"""
日志管理相关实体模型
基于Django-Vue3-Admin的日志管理功能
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from app.core.models.base import AuditModel


class OperationLog(AuditModel):
    """操作日志表"""
    __tablename__ = 'operation_logs'
    
    request_modular = Column(String(64), nullable=True, comment="请求模块")
    request_path = Column(String(400), nullable=True, comment="请求路径")
    request_body = Column(Text, nullable=True, comment="请求体")
    request_method = Column(String(8), nullable=True, comment="请求方法")
    request_msg = Column(Text, nullable=True, comment="请求消息")
    request_ip = Column(String(32), nullable=True, comment="请求IP")
    request_browser = Column(String(64), nullable=True, comment="请求浏览器")
    response_code = Column(String(32), nullable=True, comment="响应码")
    request_os = Column(String(64), nullable=True, comment="请求操作系统")
    json_result = Column(Text, nullable=True, comment="JSON结果")
    status = Column(Boolean, default=False, comment="状态")


class LoginLog(AuditModel):
    """登录日志表"""
    __tablename__ = 'login_logs'
    
    username = Column(String(32), nullable=True, comment="用户名")
    ip = Column(String(32), nullable=True, comment="IP地址")
    agent = Column(Text, nullable=True, comment="用户代理")
    browser = Column(String(200), nullable=True, comment="浏览器")
    os = Column(String(200), nullable=True, comment="操作系统")
    continent = Column(String(50), nullable=True, comment="洲")
    country = Column(String(50), nullable=True, comment="国家")
    province = Column(String(50), nullable=True, comment="省份")
    city = Column(String(50), nullable=True, comment="城市")
    district = Column(String(50), nullable=True, comment="区县")
    isp = Column(String(50), nullable=True, comment="ISP")
    area_code = Column(String(50), nullable=True, comment="地区编码")
    country_english = Column(String(50), nullable=True, comment="国家英文名")
    country_code = Column(String(50), nullable=True, comment="国家编码")
    longitude = Column(String(50), nullable=True, comment="经度")
    latitude = Column(String(50), nullable=True, comment="纬度")
    login_type = Column(Integer, default=1, comment="登录类型: 1-普通登录 2-微信扫码登录")