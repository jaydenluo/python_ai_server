"""
业务模型模块
提供各种业务数据模型
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入
__getattr__, __dir__ = setup_smart_import(__name__)

