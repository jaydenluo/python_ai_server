"""
通用自动发现系统
自动发现和注册 Models、Services、Controllers 等
"""

import os
import importlib
import pkgutil
import inspect
from typing import Dict, List, Any, Type, Optional
from dataclasses import dataclass


@dataclass
class DiscoveredItem:
    """发现的项目信息"""
    name: str
    module_path: str
    class_obj: Type
    item_type: str  # 'model', 'service', 'controller'


class AutoDiscovery:
    """自动发现系统"""
    
    def __init__(self):
        self.discovered_items: Dict[str, List[DiscoveredItem]] = {
            'models': [],
            'services': [],
            'controllers': []
        }
        self.scanned_modules = set()
    
    def discover_models(self, base_package: str = "app.models.entities") -> List[DiscoveredItem]:
        """自动发现模型类"""
        return self._discover_by_pattern(
            base_package=base_package,
            item_type='models',
            class_filter=self._is_model_class
        )
    
    def discover_services(self, base_package: str = "app.services") -> List[DiscoveredItem]:
        """自动发现服务类"""
        return self._discover_by_pattern(
            base_package=base_package,
            item_type='services',
            class_filter=self._is_service_class
        )
    
    def discover_controllers(self, base_package: str = "app.controller") -> List[DiscoveredItem]:
        """自动发现控制器类"""
        return self._discover_by_pattern(
            base_package=base_package,
            item_type='controllers',
            class_filter=self._is_controller_class
        )
    
    def _discover_by_pattern(self, base_package: str, item_type: str, 
                           class_filter: callable) -> List[DiscoveredItem]:
        """按模式发现类"""
        discovered = []
        
        try:
            # 导入基础包
            base_module = importlib.import_module(base_package)
            base_path = base_module.__path__[0]
            
            print(f"🔍 扫描 {item_type}: {base_package}")
            
            # 递归扫描所有子模块
            for importer, modname, ispkg in pkgutil.walk_packages([base_path], base_package + "."):
                if modname in self.scanned_modules:
                    continue
                
                # 跳过 __init__.py 文件
                if modname.endswith('.__init__'):
                    continue
                    
                try:
                    # 导入模块
                    module = importlib.import_module(modname)
                    self.scanned_modules.add(modname)
                    
                    # 扫描模块中的类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # 只处理在当前模块中定义的类（避免导入的类）
                        if obj.__module__ != modname:
                            continue
                            
                        # 应用过滤器
                        if class_filter(obj, name):
                            item = DiscoveredItem(
                                name=name,
                                module_path=modname,
                                class_obj=obj,
                                item_type=item_type
                            )
                            discovered.append(item)
                            # 不打印每个成功扫描的项，只在最后显示统计
                            
                except ImportError as e:
                    print(f"  ⚠️ 跳过模块 {modname}: {e}")
                except Exception as e:
                    print(f"  ❌ 扫描模块 {modname} 时出错: {e}")
                    
        except Exception as e:
            print(f"❌ 扫描 {item_type} 失败: {e}")
        
        # 存储发现的项目
        self.discovered_items[item_type] = discovered
        print(f"✅ {item_type} 扫描完成，共发现 {len(discovered)} 个")
        
        return discovered
    
    def _is_model_class(self, cls: Type, name: str) -> bool:
        """判断是否是模型类"""
        # 检查是否继承自常见的模型基类
        base_classes = [base.__name__ for base in cls.__mro__]
        
        # 常见的模型基类名称
        model_base_classes = [
            'BaseModel', 'Model', 'Entity', 'Base',
            'SQLAlchemyBase', 'DeclarativeBase'
        ]
        
        # 检查是否继承自模型基类
        has_model_base = any(base in model_base_classes for base in base_classes)
        
        # 检查是否有模型特征
        has_model_attrs = (
            hasattr(cls, '__tablename__') or  # SQLAlchemy
            hasattr(cls, '_meta') or          # Django-like
            hasattr(cls, '__table__') or      # SQLAlchemy
            name.endswith('Model') or         # 命名约定
            name.endswith('Entity')           # 命名约定
        )
        
        return has_model_base or has_model_attrs
    
    def _is_service_class(self, cls: Type, name: str) -> bool:
        """判断是否是服务类"""
        # 检查是否继承自服务基类
        base_classes = [base.__name__ for base in cls.__mro__]
        
        # 常见的服务基类名称
        service_base_classes = [
            'BaseService', 'Service', 'AbstractService'
        ]
        
        # 检查是否继承自服务基类
        has_service_base = any(base in service_base_classes for base in base_classes)
        
        # 检查命名约定
        has_service_name = name.endswith('Service')
        
        return has_service_base or has_service_name
    
    def _is_controller_class(self, cls: Type, name: str) -> bool:
        """判断是否是控制器类"""
        # 检查是否有控制器装饰器
        has_controller_decorator = (
            hasattr(cls, '_prefix') and 
            hasattr(cls, '_version')
        )
        
        # 检查命名约定
        has_controller_name = (
            name.endswith('Controller') or 
            name.endswith('Api') or
            'Controller' in name
        )
        
        return has_controller_decorator or has_controller_name
    
    def discover_all(self) -> Dict[str, List[DiscoveredItem]]:
        """发现所有类型的项目"""
        print("\n" + "="*80)
        print("🚀 开始自动发现所有组件")
        print("="*80)
        
        self.discover_models()
        self.discover_services()
        self.discover_controllers()
        
        print("\n📊 发现统计:")
        for item_type, items in self.discovered_items.items():
            print(f"  {item_type}: {len(items)} 个")
        
        total = sum(len(items) for items in self.discovered_items.values())
        print(f"\n✅ 总计发现: {total} 个组件")
        print("="*80)
        
        return self.discovered_items
    
    def get_discovered_items(self, item_type: str) -> List[DiscoveredItem]:
        """获取指定类型的发现项目"""
        return self.discovered_items.get(item_type, [])
    
    def get_all_classes(self, item_type: str) -> List[Type]:
        """获取指定类型的所有类"""
        return [item.class_obj for item in self.get_discovered_items(item_type)]
    
    def get_class_by_name(self, item_type: str, name: str) -> Optional[Type]:
        """根据名称获取类"""
        for item in self.get_discovered_items(item_type):
            if item.name == name:
                return item.class_obj
        return None
    
    def print_discovery_report(self):
        """打印发现报告"""
        print("\n" + "="*80)
        print("📋 自动发现报告")
        print("="*80)
        
        for item_type, items in self.discovered_items.items():
            if not items:
                continue
                
            print(f"\n📦 {item_type.upper()}:")
            for i, item in enumerate(items, 1):
                print(f"  {i:2d}. {item.name:20} ({item.module_path})")
        
        print("\n" + "="*80)


# 全局自动发现实例
_auto_discovery = AutoDiscovery()


def get_auto_discovery() -> AutoDiscovery:
    """获取自动发现实例"""
    return _auto_discovery


def discover_all_components():
    """发现所有组件（便捷函数）"""
    return _auto_discovery.discover_all()


def get_models() -> List[Type]:
    """获取所有模型类"""
    return _auto_discovery.get_all_classes('models')


def get_services() -> List[Type]:
    """获取所有服务类"""
    return _auto_discovery.get_all_classes('services')


def get_controllers() -> List[Type]:
    """获取所有控制器类"""
    return _auto_discovery.get_all_classes('controllers')


def get_model_by_name(name: str) -> Optional[Type]:
    """根据名称获取模型类"""
    return _auto_discovery.get_class_by_name('models', name)


def get_service_by_name(name: str) -> Optional[Type]:
    """根据名称获取服务类"""
    return _auto_discovery.get_class_by_name('services', name)


def print_discovery_report():
    """打印发现报告（便捷函数）"""
    _auto_discovery.print_discovery_report()