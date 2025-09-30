"""
智能模型导入器
提供懒加载和自动发现功能
"""

import sys
from typing import Any, Dict, Type, Optional
from .auto_discovery import model_discovery


class SmartModelImporter:
    """智能模型导入器 - 支持懒加载和自动发现"""
    
    def __init__(self):
        self._cache: Dict[str, Type] = {}
        self._discovered = False
    
    def __getattr__(self, name: str) -> Any:
        """动态获取模型类"""
        # 如果缓存中有，直接返回
        if name in self._cache:
            return self._cache[name]
        
        # 尝试从自动发现中获取
        model_class = self._try_discover_model(name)
        if model_class:
            self._cache[name] = model_class
            return model_class
        
        # 如果找不到，抛出 AttributeError
        raise AttributeError(f"模型 '{name}' 未找到")
    
    def _try_discover_model(self, name: str) -> Optional[Type]:
        """尝试发现模型"""
        try:
            # 尝试从实体模块导入
            entity_module = f"app.models.entities.{name.lower()}"
            module = __import__(entity_module, fromlist=[name])
            model_class = getattr(module, name, None)
            if model_class:
                return model_class
        except ImportError:
            pass
        
        try:
            # 尝试从枚举模块导入
            enum_module = f"app.models.enums.{name.lower()}"
            module = __import__(enum_module, fromlist=[name])
            model_class = getattr(module, name, None)
            if model_class:
                return model_class
        except ImportError:
            pass
        
        # 使用自动发现器
        return model_discovery.get_model_by_name(name)
    
    def get_available_models(self) -> list:
        """获取所有可用的模型名称"""
        if not self._discovered:
            model_discovery.scan_models()
            self._discovered = True
        
        return list(model_discovery.get_all_models().keys())
    
    def reload_models(self):
        """重新加载所有模型"""
        self._cache.clear()
        model_discovery.discovered_models.clear()
        model_discovery.scan_models()
        self._discovered = True


# 创建全局智能导入器实例
smart_models = SmartModelImporter()


# 便捷函数
def get_model(name: str) -> Type:
    """获取模型类"""
    return getattr(smart_models, name)


def list_models() -> list:
    """列出所有可用模型"""
    return smart_models.get_available_models()


def reload_models():
    """重新加载所有模型"""
    smart_models.reload_models()