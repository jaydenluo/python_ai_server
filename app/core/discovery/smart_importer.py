"""
智能导入器
使用模块钩子实现透明的自动发现和延迟加载
"""

import os
import importlib
import inspect
from typing import Any, List, Dict, Optional, Set
from pathlib import Path


class SmartImporter:
    """智能导入器 - 核心实现"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._scanned_modules: Set[str] = set()
    
    def smart_import(self, name: str, package_name: str) -> Any:
        """智能导入 - 根据名称自动查找和导入类"""
        # 检查缓存
        if package_name in self._cache and name in self._cache[package_name]:
            return self._cache[package_name][name]
        
        # 扫描包并缓存结果
        if package_name not in self._scanned_modules:
            self._scan_package(package_name)
            self._scanned_modules.add(package_name)
        
        # 从缓存中获取
        if package_name in self._cache and name in self._cache[package_name]:
            return self._cache[package_name][name]
        
        # 未找到，抛出 AttributeError
        raise AttributeError(f"module '{package_name}' has no attribute '{name}'")
    
    def get_available_exports(self, package_name: str) -> List[str]:
        """获取包中所有可用的导出"""
        if package_name not in self._scanned_modules:
            self._scan_package(package_name)
            self._scanned_modules.add(package_name)
        
        return list(self._cache.get(package_name, {}).keys())
    
    def _scan_package(self, package_name: str):
        """扫描包中的所有类"""
        try:
            # 获取包的路径
            package = importlib.import_module(package_name)
            if not hasattr(package, '__path__'):
                return
            
            package_path = package.__path__[0]
            
            # 初始化缓存
            if package_name not in self._cache:
                self._cache[package_name] = {}
            
            # 扫描包中的所有 .py 文件
            for file_path in Path(package_path).glob("*.py"):
                if file_path.name.startswith('__'):
                    continue
                
                module_name = file_path.stem
                full_module_name = f"{package_name}.{module_name}"
                
                try:
                    # 导入模块
                    module = importlib.import_module(full_module_name)
                    
                    # 扫描模块中的类
                    for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
                        # 只处理在当前模块中定义的类
                        if class_obj.__module__ == full_module_name:
                            # 根据包类型应用过滤器
                            if self._should_export_class(class_obj, class_name, package_name):
                                self._cache[package_name][class_name] = class_obj
                
                except Exception as e:
                    # 静默跳过有问题的模块
                    pass
        
        except Exception as e:
            # 静默跳过有问题的包
            pass
    
    def _should_export_class(self, cls: type, name: str, package_name: str) -> bool:
        """判断类是否应该被导出"""
        # 根据包名称判断类型
        if 'models' in package_name or 'entities' in package_name:
            return self._is_model_class(cls, name)
        elif 'services' in package_name:
            return self._is_service_class(cls, name)
        elif 'controller' in package_name:
            return self._is_controller_class(cls, name)
        else:
            # 默认导出所有非私有类
            return not name.startswith('_')
    
    def _is_model_class(self, cls: type, name: str) -> bool:
        """判断是否是模型类"""
        base_classes = [base.__name__ for base in cls.__mro__]
        
        model_base_classes = [
            'BaseModel', 'Model', 'Entity', 'Base',
            'SQLAlchemyBase', 'DeclarativeBase'
        ]
        
        has_model_base = any(base in model_base_classes for base in base_classes)
        
        has_model_attrs = (
            hasattr(cls, '__tablename__') or
            hasattr(cls, '_meta') or
            hasattr(cls, '__table__') or
            name.endswith('Model') or
            name.endswith('Entity')
        )
        
        return has_model_base or has_model_attrs
    
    def _is_service_class(self, cls: type, name: str) -> bool:
        """判断是否是服务类"""
        base_classes = [base.__name__ for base in cls.__mro__]
        
        service_base_classes = [
            'BaseService', 'Service', 'AbstractService'
        ]
        
        has_service_base = any(base in service_base_classes for base in base_classes)
        has_service_name = name.endswith('Service')
        
        return has_service_base or has_service_name
    
    def _is_controller_class(self, cls: type, name: str) -> bool:
        """判断是否是控制器类"""
        has_controller_decorator = (
            hasattr(cls, '_prefix') and 
            hasattr(cls, '_version')
        )
        
        has_controller_name = (
            name.endswith('Controller') or 
            name.endswith('Api') or
            'Controller' in name
        )
        
        return has_controller_decorator or has_controller_name


# 全局智能导入器实例
_smart_importer = SmartImporter()


def smart_import(name: str, package_name: str) -> Any:
    """智能导入函数"""
    return _smart_importer.smart_import(name, package_name)


def get_available_exports(package_name: str) -> List[str]:
    """获取可用导出函数"""
    return _smart_importer.get_available_exports(package_name)


def create_module_hooks(package_name: str):
    """为指定包创建模块钩子函数"""
    
    def __getattr__(name: str) -> Any:
        """模块级别的 __getattr__ 钩子"""
        return smart_import(name, package_name)
    
    def __dir__() -> List[str]:
        """模块级别的 __dir__ 钩子"""
        return get_available_exports(package_name)
    
    return __getattr__, __dir__


# 便捷的装饰器，用于在 __init__.py 中快速设置钩子
def auto_import_setup(package_name: str = None):
    """自动导入设置装饰器"""
    def decorator(module):
        # 如果没有提供包名，从模块中推断
        pkg_name = package_name or module.__name__
        
        # 创建钩子函数
        getattr_func, dir_func = create_module_hooks(pkg_name)
        
        # 将钩子函数添加到模块中
        module.__getattr__ = getattr_func
        module.__dir__ = dir_func
        
        return module
    
    return decorator