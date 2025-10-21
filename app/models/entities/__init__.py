"""
数据实体模块
提供各种业务数据模型
使用智能导入，自动发现所有模型类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)