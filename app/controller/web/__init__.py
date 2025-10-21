"""
Web控制器模块
提供Web页面API
使用智能导入，自动发现所有Web控制器类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)