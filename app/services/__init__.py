"""
业务服务模块
提供认证、AI、用户等业务逻辑
使用智能导入，自动发现所有服务类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)