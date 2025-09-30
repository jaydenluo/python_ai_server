"""
自动模型发现系统
自动扫描和注册所有模型类
"""

import os
import importlib
import inspect
from typing import Dict, List, Type, Any
from pathlib import Path


class ModelAutoDiscovery:
    """模型自动发现器"""
    
    def __init__(self, base_path: str = "app.models"):
        self.base_path = base_path
        self.discovered_models: Dict[str, Type] = {}
        self.discovered_enums: Dict[str, Type] = {}
        
    def scan_models(self) -> Dict[str, Any]:
        """扫描所有模型和枚举"""
        models = {}
        
        # 扫描实体模型
        entities_path = Path("app/models/entities")
        if entities_path.exists():
            models.update(self._scan_directory(entities_path, "entities"))
        
        # 扫描枚举
        enums_path = Path("app/models/enums")
        if enums_path.exists():
            models.update(self._scan_directory(enums_path, "enums"))
            
        return models
    
    def _scan_directory(self, directory: Path, category: str) -> Dict[str, Any]:
        """扫描指定目录下的所有Python文件"""
        models = {}
        
        for file_path in directory.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
                
            module_name = file_path.stem
            full_module_path = f"app.models.{category}.{module_name}"
            
            try:
                # 动态导入模块
                module = importlib.import_module(full_module_path)
                
                # 扫描模块中的所有类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # 跳过私有类和导入的类
                    if not name.startswith('_') and obj.__module__ == full_module_path:
                        models[name] = obj
                        
            except Exception as e:
                print(f"警告: 无法导入模块 {full_module_path}: {e}")
                
        return models
    
    def get_all_models(self) -> Dict[str, Type]:
        """获取所有发现的模型"""
        if not self.discovered_models:
            self.discovered_models = self.scan_models()
        return self.discovered_models
    
    def get_model_by_name(self, name: str) -> Type:
        """根据名称获取模型类"""
        models = self.get_all_models()
        return models.get(name)
    
    def create_auto_imports(self) -> str:
        """生成自动导入代码"""
        models = self.get_all_models()
        
        imports = []
        for name, model_class in models.items():
            module_path = model_class.__module__
            imports.append(f"from {module_path} import {name}")
        
        return "\n".join(imports)
    
    def generate_init_file(self) -> str:
        """生成 __init__.py 文件内容"""
        models = self.get_all_models()
        
        # 按类别分组
        entities = {}
        enums = {}
        
        for name, model_class in models.items():
            module_path = model_class.__module__
            if "entities" in module_path:
                entities[name] = model_class
            elif "enums" in module_path:
                enums[name] = model_class
        
        # 生成导入语句
        import_lines = []
        all_items = []
        
        # 实体导入
        for name, model_class in entities.items():
            module_path = model_class.__module__
            import_lines.append(f"from {module_path} import {name}")
            all_items.append(f'"{name}"')
        
        # 枚举导入
        for name, model_class in enums.items():
            module_path = model_class.__module__
            import_lines.append(f"from {module_path} import {name}")
            all_items.append(f'"{name}"')
        
        # 生成完整的 __init__.py 内容
        content = f'''"""
自动生成的模型导入文件
由 ModelAutoDiscovery 自动生成
"""

# 自动导入的实体模型
{chr(10).join(import_lines)}

__all__ = [
    {chr(10).join(f"    {item}," for item in all_items)}
]
'''
        return content


# 全局发现器实例
model_discovery = ModelAutoDiscovery()


def auto_discover_models():
    """自动发现所有模型"""
    return model_discovery.scan_models()


def get_model(name: str):
    """获取指定名称的模型"""
    return model_discovery.get_model_by_name(name)


def generate_auto_init():
    """生成自动导入的 __init__.py 文件"""
    return model_discovery.generate_init_file()