"""
数据实体模块
提供各种业务数据模型
使用智能导入，自动发现所有模型类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 显式导入所有系统模型，确保 Alembic 能检测到
from .area import Area
from .config import Config, ApiWhiteList
from .dictionary import Dictionary
from .menu import Menu, MenuButton, MenuField, FieldPermission, role_menu_permission, role_menu_button_permission, role_menu_button_permission_dept
from .message import MessageCenter, MessageCenterTargetUser, MessageCenterTargetDept, MessageCenterTargetRole, DownloadCenter
from .user_management import User, Role, Dept, Post, users_role, users_post, users_manage_dept

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)