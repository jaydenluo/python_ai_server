"""
路由装饰器
提供类似Laravel和Spring Boot的注解路由功能
"""

from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from enum import Enum
from dataclasses import dataclass
import inspect


class HTTPMethod(Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class RouteInfo:
    """路由信息"""
    method: HTTPMethod
    path: str
    handler: Callable
    name: Optional[str] = None
    middleware: List[str] = None
    prefix: str = ""
    version: str = "v1"
    
    def __post_init__(self):
        if self.middleware is None:
            self.middleware = []
        if not self.name:
            self.name = f"{self.handler.__name__}"


class RouteRegistry:
    """路由注册表"""
    
    def __init__(self):
        self.routes: List[RouteInfo] = []
        self.route_groups: Dict[str, List[RouteInfo]] = {}
    
    def register_route(self, route_info: RouteInfo):
        """注册路由"""
        self.routes.append(route_info)
        
        # 按组分类
        group_key = f"{route_info.version}_{route_info.prefix}"
        if group_key not in self.route_groups:
            self.route_groups[group_key] = []
        self.route_groups[group_key].append(route_info)
    
    def get_routes(self, version: str = None, prefix: str = None) -> List[RouteInfo]:
        """获取路由"""
        if version is None and prefix is None:
            return self.routes
        
        filtered_routes = []
        for route in self.routes:
            if version and route.version != version:
                continue
            if prefix and not route.path.startswith(prefix):
                continue
            filtered_routes.append(route)
        
        return filtered_routes
    
    def get_route_by_name(self, name: str) -> Optional[RouteInfo]:
        """根据名称获取路由"""
        for route in self.routes:
            if route.name == name:
                return route
        return None


# 全局路由注册表
route_registry = RouteRegistry()


def route(method: HTTPMethod, path: str, name: Optional[str] = None, 
          middleware: List[str] = None, prefix: str = "", version: Optional[str] = None,
          # 简称参数
          p: str = "", v: Optional[str] = None, m: List[str] = None):
    """路由装饰器"""
    def decorator(func):
        # 如果没有提供名称，自动生成
        route_name = name
        if not route_name:
            # 使用类名和方法名生成路由名称
            class_name = func.__qualname__.split('.')[0].lower()
            method_name = func.__name__
            route_name = f"{class_name}.{method_name}"
        
        # 如果没有提供版本，从控制器获取或使用默认值
        route_version = version
        if not route_version:
            # 尝试从控制器类获取版本
            if hasattr(func, '__self__') and hasattr(func.__self__, '_version'):
                route_version = func.__self__._version
            else:
                # 使用默认版本
                route_version = "v1"
        
        # 处理简称参数
        final_prefix = p or prefix
        final_version = v or version
        final_middleware = m or middleware or []
        
        # 智能中间件处理
        route_middleware = final_middleware
        
        # 如果没有指定中间件，默认需要认证
        if not route_middleware:
            route_middleware = ["auth"]
        # 如果指定了匿名访问，则不需要认证
        elif "anonymous" in route_middleware:
            route_middleware = [m for m in route_middleware if m != "anonymous"]
        # 如果指定了其他权限，自动添加认证
        elif any(m not in ["auth", "anonymous"] for m in route_middleware):
            if "auth" not in route_middleware:
                route_middleware = ["auth"] + route_middleware
        
        # 创建路由信息
        route_info = RouteInfo(
            method=method,
            path=path,
            handler=func,
            name=route_name,
            middleware=route_middleware,
            prefix=final_prefix,
            version=final_version or route_version
        )
        
        # 注册路由
        route_registry.register_route(route_info)
        
        # 保持原函数不变
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 添加路由信息到函数
        wrapper._route_info = route_info
        return wrapper
    
    return decorator


def get(path: str, name: Optional[str] = None, middleware: List[str] = None, 
        prefix: str = "", version: Optional[str] = None,
        # 简称参数
        p: str = "", v: Optional[str] = None, m: List[str] = None):
    """GET路由装饰器"""
    return route(HTTPMethod.GET, path, name, middleware, prefix, version, p, v, m)


def post(path: str, name: Optional[str] = None, middleware: List[str] = None, 
         prefix: str = "", version: Optional[str] = None,
         # 简称参数
         p: str = "", v: Optional[str] = None, m: List[str] = None):
    """POST路由装饰器"""
    return route(HTTPMethod.POST, path, name, middleware, prefix, version, p, v, m)


def put(path: str, name: Optional[str] = None, middleware: List[str] = None, 
        prefix: str = "", version: Optional[str] = None,
        # 简称参数
        p: str = "", v: Optional[str] = None, m: List[str] = None):
    """PUT路由装饰器"""
    return route(HTTPMethod.PUT, path, name, middleware, prefix, version, p, v, m)


def patch(path: str, name: Optional[str] = None, middleware: List[str] = None, 
          prefix: str = "", version: Optional[str] = None,
          # 简称参数
          p: str = "", v: Optional[str] = None, m: List[str] = None):
    """PATCH路由装饰器"""
    return route(HTTPMethod.PATCH, path, name, middleware, prefix, version, p, v, m)


def delete(path: str, name: Optional[str] = None, middleware: List[str] = None, 
           prefix: str = "", version: Optional[str] = None,
           # 简称参数
           p: str = "", v: Optional[str] = None, m: List[str] = None):
    """DELETE路由装饰器"""
    return route(HTTPMethod.DELETE, path, name, middleware, prefix, version, p, v, m)


def options(path: str, name: Optional[str] = None, middleware: List[str] = None, 
           prefix: str = "", version: Optional[str] = None,
           # 简称参数
           p: str = "", v: Optional[str] = None, m: List[str] = None):
    """OPTIONS路由装饰器"""
    return route(HTTPMethod.OPTIONS, path, name, middleware, prefix, version, p, v, m)


def head(path: str, name: Optional[str] = None, middleware: List[str] = None, 
         prefix: str = "", version: Optional[str] = None,
         # 简称参数
         p: str = "", v: Optional[str] = None, m: List[str] = None):
    """HEAD路由装饰器"""
    return route(HTTPMethod.HEAD, path, name, middleware, prefix, version, p, v, m)


def api_resource(resource_name: str, prefix: str = "", version: Optional[str] = None, 
                 middleware: List[str] = None):
    """API资源装饰器 - 自动生成CRUD路由"""
    def decorator(cls):
        # 如果没有提供版本，使用默认值
        resource_version = version or "v1"
        
        # 为类添加路由信息
        cls._resource_name = resource_name
        cls._prefix = prefix
        cls._version = resource_version
        cls._middleware = middleware or []
        
        # 自动生成CRUD方法的路由
        if hasattr(cls, 'index'):
            get(f"/{resource_name}", name=f"{resource_name}.index", 
                middleware=cls._middleware, prefix=prefix, version=resource_version)(cls.index)
        
        if hasattr(cls, 'show'):
            get(f"/{resource_name}/{{id}}", name=f"{resource_name}.show", 
                middleware=cls._middleware, prefix=prefix, version=resource_version)(cls.show)
        
        if hasattr(cls, 'store'):
            post(f"/{resource_name}", name=f"{resource_name}.store", 
                 middleware=cls._middleware, prefix=prefix, version=resource_version)(cls.store)
        
        if hasattr(cls, 'update'):
            put(f"/{resource_name}/{{id}}", name=f"{resource_name}.update", 
                middleware=cls._middleware, prefix=prefix, version=resource_version)(cls.update)
            patch(f"/{resource_name}/{{id}}", name=f"{resource_name}.patch", 
                  middleware=cls._middleware, prefix=prefix, version=resource_version)(cls.patch)
        
        if hasattr(cls, 'destroy'):
            delete(f"/{resource_name}/{{id}}", name=f"{resource_name}.destroy", 
                   middleware=cls._middleware, prefix=prefix, version=resource_version)(cls.destroy)
        
        return cls
    
    return decorator


def controller(prefix: str = "", version: Optional[str] = None, middleware: List[str] = None,
               # 简称参数
               p: str = "", v: Optional[str] = None, m: List[str] = None):
    """控制器装饰器"""
    def decorator(cls):
        # 处理简称参数
        final_prefix = p or prefix
        final_version = v or version or "v1"
        final_middleware = m or middleware or []
        
        # 为类添加控制器信息
        cls._prefix = final_prefix
        cls._version = final_version
        cls._middleware = final_middleware
        
        # 扫描类中的方法，自动注册路由
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_route_info'):
                # 更新路由信息
                route_info = method._route_info
                route_info.prefix = final_prefix
                route_info.version = final_version
                if not route_info.middleware:
                    route_info.middleware = cls._middleware
                else:
                    route_info.middleware.extend(cls._middleware)
        
        return cls
    
    return decorator


def middleware(middleware_names: List[str]):
    """中间件装饰器"""
    def decorator(func):
        if not hasattr(func, '_middleware'):
            func._middleware = []
        func._middleware.extend(middleware_names)
        return func
    return decorator


def auth_required(func):
    """认证必需装饰器"""
    return middleware(["auth"])(func)


def admin_required(func):
    """管理员必需装饰器"""
    return middleware(["auth", "admin"])(func)


def rate_limit(requests_per_minute: int = 60, requests_per_hour: int = 1000):
    """限流装饰器"""
    def decorator(func):
        if not hasattr(func, '_rate_limit'):
            func._rate_limit = {}
        func._rate_limit = {
            "requests_per_minute": requests_per_minute,
            "requests_per_hour": requests_per_hour
        }
        return func
    return decorator


def cache(ttl: int = 300, key: Optional[str] = None):
    """缓存装饰器"""
    def decorator(func):
        if not hasattr(func, '_cache'):
            func._cache = {}
        func._cache = {
            "ttl": ttl,
            "key": key
        }
        return func
    return decorator


def validate(schema: Any):
    """验证装饰器"""
    def decorator(func):
        if not hasattr(func, '_validation'):
            func._validation = {}
        func._validation = {
            "schema": schema
        }
        return func
    return decorator


def api_doc(summary: str = "", description: str = "", 
            tags: List[str] = None, responses: Dict[str, Any] = None):
    """API文档装饰器"""
    def decorator(func):
        if not hasattr(func, '_api_doc'):
            func._api_doc = {}
        func._api_doc = {
            "summary": summary,
            "description": description,
            "tags": tags or [],
            "responses": responses or {}
        }
        return func
    return decorator


def get_routes() -> List[RouteInfo]:
    """获取所有路由"""
    return route_registry.get_routes()


def get_route_by_name(name: str) -> Optional[RouteInfo]:
    """根据名称获取路由"""
    return route_registry.get_route_by_name(name)


def generate_url(name: str, **params) -> str:
    """生成URL"""
    route = get_route_by_name(name)
    if not route:
        raise ValueError(f"Route '{name}' not found")
    
    url = f"/api/{route.version}{route.prefix}{route.path}"
    
    # 替换路径参数
    for key, value in params.items():
        url = url.replace(f"{{{key}}}", str(value))
    
    return url