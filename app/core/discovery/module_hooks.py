"""
模块钩子助手
提供极简的 __init__.py 实现方案
"""

from .smart_importer import smart_import, get_available_exports


def setup_smart_import(package_name: str):
    """
    为 __init__.py 设置智能导入
    
    使用方法:
    # 在 __init__.py 中只需要两行代码:
    from app.core.discovery.module_hooks import setup_smart_import
    __getattr__, __dir__ = setup_smart_import(__name__)
    """
    
    def __getattr__(name: str):
        """延迟导入钩子"""
        try:
            return smart_import(name, package_name)
        except AttributeError:
            raise AttributeError(f"module '{package_name}' has no attribute '{name}'")
    
    def __dir__():
        """目录列表钩子"""
        try:
            return get_available_exports(package_name)
        except Exception:
            return []
    
    return __getattr__, __dir__


def create_smart_init(package_name: str, docstring: str = ""):
    """
    创建完整的智能 __init__.py 内容
    
    返回一个字典，包含所有需要的模块级别变量
    """
    __getattr__, __dir__ = setup_smart_import(package_name)
    
    result = {
        '__doc__': docstring,
        '__getattr__': __getattr__,
        '__dir__': __dir__,
    }
    
    # 尝试获取 __all__ 列表
    try:
        result['__all__'] = get_available_exports(package_name)
    except Exception:
        pass
    
    return result