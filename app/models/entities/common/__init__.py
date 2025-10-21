"""
通用模型模块
提供文件、日志等通用数据模型
"""

from app.core.discovery.module_hooks import setup_smart_import

# 显式导入通用模型
from .file import FileList
from .log import OperationLog, LoginLog

# 设置智能导入
__getattr__, __dir__ = setup_smart_import(__name__)

