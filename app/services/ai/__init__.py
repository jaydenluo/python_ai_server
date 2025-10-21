"""
AI服务层
提供AI工作流编排、智能体管理、RAG系统等核心功能
使用智能导入，自动发现所有AI服务类
"""

from app.core.discovery.module_hooks import setup_smart_import

# 设置智能导入 - 只需要这两行代码！
__getattr__, __dir__ = setup_smart_import(__name__)