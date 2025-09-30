"""
数据模型模块 - 智能自动导入
提供各种数据模型和关系，支持自动发现
"""

# 从核心模型导入基础组件
from app.core.models.base import BaseModel, SoftDeleteModel, AuditModel, TenantModel

# 智能导入器 - 支持自动发现和懒加载
from app.core.models.smart_importer import smart_models

# 自动发现所有模型
from app.core.models.auto_discovery import auto_discover_models

# 自动发现并导入所有模型
_discovered_models = auto_discover_models()

# 动态创建模块属性
for model_name, model_class in _discovered_models.items():
    globals()[model_name] = model_class

# 基础模型
__all__ = [
    "BaseModel",
    "SoftDeleteModel", 
    "AuditModel",
    "TenantModel",
    "smart_models",  # 智能导入器
]

# 动态添加发现的模型到 __all__
__all__.extend(_discovered_models.keys())

# 便捷函数
def get_model(name: str):
    """获取模型类"""
    return getattr(smart_models, name)

def list_models():
    """列出所有可用模型"""
    return smart_models.get_available_models()

def reload_models():
    """重新加载所有模型"""
    smart_models.reload_models()