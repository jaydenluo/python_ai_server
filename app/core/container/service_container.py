"""
服务容器
提供依赖注入和依赖解析功能
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional, Union
from abc import ABC, abstractmethod
import inspect
from functools import wraps

T = TypeVar('T')


class Binding(ABC):
    """绑定抽象基类"""
    
    @abstractmethod
    def resolve(self, container: 'ServiceContainer') -> Any:
        """解析依赖"""
        pass


class SingletonBinding(Binding):
    """单例绑定"""
    
    def __init__(self, concrete: Union[Type, Callable]):
        self.concrete = concrete
        self._instance = None
    
    def resolve(self, container: 'ServiceContainer') -> Any:
        if self._instance is None:
            self._instance = container.build(self.concrete)
        return self._instance


class InstanceBinding(Binding):
    """实例绑定"""
    
    def __init__(self, instance: Any):
        self.instance = instance
    
    def resolve(self, container: 'ServiceContainer') -> Any:
        return self.instance


class FactoryBinding(Binding):
    """工厂绑定"""
    
    def __init__(self, factory: Callable):
        self.factory = factory
    
    def resolve(self, container: 'ServiceContainer') -> Any:
        return self.factory(container)


class ServiceContainer:
    """服务容器"""
    
    def __init__(self):
        self._bindings: Dict[str, Binding] = {}
        self._instances: Dict[str, Any] = {}
        self._resolving: set = set()
    
    def bind(self, abstract: Union[str, Type], concrete: Union[Type, Callable, Any] = None) -> 'ServiceContainer':
        """绑定服务"""
        if concrete is None:
            concrete = abstract
        
        if isinstance(concrete, type):
            self._bindings[str(abstract)] = SingletonBinding(concrete)
        elif callable(concrete):
            self._bindings[str(abstract)] = FactoryBinding(concrete)
        else:
            self._bindings[str(abstract)] = InstanceBinding(concrete)
        
        return self
    
    def singleton(self, abstract: Union[str, Type], concrete: Union[Type, Callable] = None) -> 'ServiceContainer':
        """绑定单例服务"""
        if concrete is None:
            concrete = abstract
        
        self._bindings[str(abstract)] = SingletonBinding(concrete)
        return self
    
    def instance(self, abstract: Union[str, Type], instance: Any) -> 'ServiceContainer':
        """绑定实例"""
        self._bindings[str(abstract)] = InstanceBinding(instance)
        return self
    
    def factory(self, abstract: Union[str, Type], factory: Callable) -> 'ServiceContainer':
        """绑定工厂"""
        self._bindings[str(abstract)] = FactoryBinding(factory)
        return self
    
    def get(self, abstract: Union[str, Type]) -> Any:
        """获取服务"""
        key = str(abstract)
        
        if key in self._instances:
            return self._instances[key]
        
        if key not in self._bindings:
            # 尝试自动绑定
            if isinstance(abstract, type):
                self.bind(abstract)
            else:
                raise ValueError(f"Service '{abstract}' not bound")
        
        # 检查循环依赖
        if key in self._resolving:
            raise ValueError(f"Circular dependency detected for '{abstract}'")
        
        self._resolving.add(key)
        
        try:
            instance = self._bindings[key].resolve(self)
            self._instances[key] = instance
            return instance
        finally:
            self._resolving.discard(key)
    
    def build(self, concrete: Union[Type, Callable]) -> Any:
        """构建实例"""
        if isinstance(concrete, type):
            return self._build_class(concrete)
        elif callable(concrete):
            return self._build_callable(concrete)
        else:
            return concrete
    
    def _build_class(self, cls: Type) -> Any:
        """构建类实例"""
        constructor = cls.__init__
        signature = inspect.signature(constructor)
        
        args = []
        kwargs = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                try:
                    dependency = self.get(param.annotation)
                    args.append(dependency)
                except ValueError:
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise ValueError(f"Cannot resolve dependency '{param_name}' for {cls.__name__}")
            elif param.default != inspect.Parameter.empty:
                kwargs[param_name] = param.default
            else:
                raise ValueError(f"Cannot resolve dependency '{param_name}' for {cls.__name__}")
        
        return cls(*args, **kwargs)
    
    def _build_callable(self, func: Callable) -> Any:
        """构建可调用对象"""
        signature = inspect.signature(func)
        
        args = []
        kwargs = {}
        
        for param_name, param in signature.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                try:
                    dependency = self.get(param.annotation)
                    args.append(dependency)
                except ValueError:
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise ValueError(f"Cannot resolve dependency '{param_name}' for {func.__name__}")
            elif param.default != inspect.Parameter.empty:
                kwargs[param_name] = param.default
            else:
                raise ValueError(f"Cannot resolve dependency '{param_name}' for {func.__name__}")
        
        return func(*args, **kwargs)
    
    def has(self, abstract: Union[str, Type]) -> bool:
        """检查服务是否已绑定"""
        return str(abstract) in self._bindings
    
    def unbind(self, abstract: Union[str, Type]) -> 'ServiceContainer':
        """解绑服务"""
        key = str(abstract)
        if key in self._bindings:
            del self._bindings[key]
        if key in self._instances:
            del self._instances[key]
        return self
    
    def flush(self) -> 'ServiceContainer':
        """清空容器"""
        self._bindings.clear()
        self._instances.clear()
        self._resolving.clear()
        return self


class ServiceProvider:
    """服务提供者基类"""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
    
    def register(self):
        """注册服务"""
        raise NotImplementedError("Subclasses must implement register method")
    
    def boot(self):
        """启动服务"""
        pass


def inject(abstract: Union[str, Type]):
    """依赖注入装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里需要从全局容器获取实例
            # 实际实现中需要传入容器实例
            container = getattr(func, '_container', None)
            if container:
                dependency = container.get(abstract)
                return func(dependency, *args, **kwargs)
            else:
                raise ValueError("Container not available for dependency injection")
        
        return wrapper
    return decorator


# 全局容器实例
container = ServiceContainer()