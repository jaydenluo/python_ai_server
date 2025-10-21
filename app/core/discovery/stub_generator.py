"""
类型存根生成器
自动生成 .pyi 文件以支持 IDE 自动补全
"""

import os
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any
from .smart_importer import SmartImporter


class StubGenerator:
    """类型存根生成器"""
    
    def __init__(self):
        self.smart_importer = SmartImporter()
    
    def generate_stub_for_package(self, package_name: str, output_path: str = None) -> str:
        """为指定包生成类型存根文件"""
        
        # 如果没有指定输出路径，使用包路径 + .pyi
        if output_path is None:
            package = importlib.import_module(package_name)
            if hasattr(package, '__path__'):
                package_path = package.__path__[0]
                output_path = os.path.join(package_path, "__init__.pyi")
        
        # 获取包中的所有导出
        exports = self.smart_importer.get_available_exports(package_name)
        
        # 生成存根内容
        stub_content = self._generate_stub_content(package_name, exports)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stub_content)
        
        return output_path
    
    def _generate_stub_content(self, package_name: str, exports: List[str]) -> str:
        """生成存根文件内容"""
        
        lines = [
            "# 类型存根文件 - 支持 IDE 自动补全",
            "# 由 StubGenerator 自动生成",
            ""
        ]
        
        # 生成导入语句
        import_lines = []
        all_exports = []
        
        for export_name in exports:
            try:
                # 获取类对象
                cls = self.smart_importer.smart_import(export_name, package_name)
                
                # 获取模块名
                module_name = cls.__module__
                if module_name.startswith(package_name + "."):
                    relative_module = module_name[len(package_name) + 1:]
                    import_line = f"from .{relative_module} import {export_name} as {export_name}"
                    import_lines.append(import_line)
                    all_exports.append(export_name)
                
            except Exception:
                # 跳过有问题的导出
                continue
        
        # 添加导入语句
        lines.extend(import_lines)
        lines.append("")
        
        # 添加 __all__
        if all_exports:
            all_list = ", ".join(f'"{name}"' for name in all_exports)
            lines.append(f"__all__ = [{all_list}]")
        
        return "\n".join(lines)
    
    def generate_all_stubs(self, base_packages: List[str] = None):
        """为所有包生成类型存根"""
        
        if base_packages is None:
            base_packages = [
                "app.models.entities",
                "app.services",
                "app.services.ai",
                "app.controller.admin",
                "app.controller.api", 
                "app.controller.web"
            ]
        
        generated_files = []
        
        for package_name in base_packages:
            try:
                output_path = self.generate_stub_for_package(package_name)
                generated_files.append(output_path)
                print(f"✅ 生成存根文件: {output_path}")
            except Exception as e:
                print(f"❌ 生成 {package_name} 存根失败: {e}")
        
        return generated_files
    
    def update_stub_if_needed(self, package_name: str) -> bool:
        """如果需要，更新存根文件"""
        
        try:
            package = importlib.import_module(package_name)
            if not hasattr(package, '__path__'):
                return False
            
            package_path = package.__path__[0]
            stub_path = os.path.join(package_path, "__init__.pyi")
            init_path = os.path.join(package_path, "__init__.py")
            
            # 检查是否需要更新
            if os.path.exists(stub_path) and os.path.exists(init_path):
                stub_mtime = os.path.getmtime(stub_path)
                init_mtime = os.path.getmtime(init_path)
                
                # 如果存根文件比 __init__.py 新，不需要更新
                if stub_mtime >= init_mtime:
                    return False
            
            # 生成新的存根文件
            self.generate_stub_for_package(package_name, stub_path)
            return True
            
        except Exception:
            return False


# 全局存根生成器实例
_stub_generator = StubGenerator()


def generate_stub_for_package(package_name: str, output_path: str = None) -> str:
    """为指定包生成类型存根文件"""
    return _stub_generator.generate_stub_for_package(package_name, output_path)


def generate_all_stubs(base_packages: List[str] = None):
    """为所有包生成类型存根"""
    return _stub_generator.generate_all_stubs(base_packages)


def update_stub_if_needed(package_name: str) -> bool:
    """如果需要，更新存根文件"""
    return _stub_generator.update_stub_if_needed(package_name)