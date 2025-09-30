"""
路由系统核心实现
提供类似Laravel的优雅路由定义
"""

from typing import Dict, List, Callable, Any, Optional, Union
from functools import wraps
import re
from enum import Enum


class HTTPMethod(Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class Route:
    """路由类"""
    
    def __init__(self, method: HTTPMethod, path: str, handler: Callable, 
                 name: Optional[str] = None, middleware: List[str] = None):
        self.method = method
        self.path = path
        self.handler = handler
        self.name = name
        self.middleware = middleware or []
        self.pattern = self._compile_pattern()
    
    def _compile_pattern(self) -> re.Pattern:
        """编译路由模式"""
        # 将Laravel风格的路由参数转换为正则表达式
        pattern = self.path
        pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', pattern)
        pattern = re.sub(r'\{([^}]+)\?\}', r'(?P<\1>[^/]*)', pattern)
        pattern = f"^{pattern}$"
        return re.compile(pattern)
    
    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        """匹配路由"""
        if self.method.value != method:
            return None
        
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None


class Router:
    """路由器"""
    
    def __init__(self):
        self.routes: List[Route] = []
        self.named_routes: Dict[str, Route] = {}
        self.middleware_groups: Dict[str, List[str]] = {}
        self.prefix = ""
        self.middleware = []
    
    def add_route(self, method: HTTPMethod, path: str, handler: Callable, 
                  name: Optional[str] = None, middleware: List[str] = None) -> Route:
        """添加路由"""
        full_path = f"{self.prefix}{path}"
        route = Route(method, full_path, handler, name, middleware or self.middleware)
        self.routes.append(route)
        
        if name:
            self.named_routes[name] = route
        
        return route
    
    def get(self, path: str, handler: Callable, name: Optional[str] = None, 
            middleware: List[str] = None) -> Route:
        """GET路由"""
        return self.add_route(HTTPMethod.GET, path, handler, name, middleware)
    
    def post(self, path: str, handler: Callable, name: Optional[str] = None, 
             middleware: List[str] = None) -> Route:
        """POST路由"""
        return self.add_route(HTTPMethod.POST, path, handler, name, middleware)
    
    def put(self, path: str, handler: Callable, name: Optional[str] = None, 
            middleware: List[str] = None) -> Route:
        """PUT路由"""
        return self.add_route(HTTPMethod.PUT, path, handler, name, middleware)
    
    def delete(self, path: str, handler: Callable, name: Optional[str] = None, 
               middleware: List[str] = None) -> Route:
        """DELETE路由"""
        return self.add_route(HTTPMethod.DELETE, path, handler, name, middleware)
    
    def patch(self, path: str, handler: Callable, name: Optional[str] = None, 
              middleware: List[str] = None) -> Route:
        """PATCH路由"""
        return self.add_route(HTTPMethod.PATCH, path, handler, name, middleware)
    
    def options(self, path: str, handler: Callable, name: Optional[str] = None, 
                middleware: List[str] = None) -> Route:
        """OPTIONS路由"""
        return self.add_route(HTTPMethod.OPTIONS, path, handler, name, middleware)
    
    def head(self, path: str, handler: Callable, name: Optional[str] = None, 
             middleware: List[str] = None) -> Route:
        """HEAD路由"""
        return self.add_route(HTTPMethod.HEAD, path, handler, name, middleware)
    
    def match(self, method: str, path: str) -> Optional[tuple[Route, Dict[str, str]]]:
        """匹配路由"""
        for route in self.routes:
            params = route.match(method, path)
            if params is not None:
                return route, params
        return None
    
    def group(self, prefix: str = "", middleware: List[str] = None):
        """路由组装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                old_prefix = self.prefix
                old_middleware = self.middleware
                
                self.prefix = f"{old_prefix}{prefix}"
                self.middleware = (middleware or []) + old_middleware
                
                try:
                    return func(*args, **kwargs)
                finally:
                    self.prefix = old_prefix
                    self.middleware = old_middleware
            
            return wrapper
        return decorator
    
    def middleware(self, middleware: Union[str, List[str]]):
        """中间件装饰器"""
        if isinstance(middleware, str):
            middleware = [middleware]
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                old_middleware = self.middleware
                self.middleware = middleware + old_middleware
                
                try:
                    return func(*args, **kwargs)
                finally:
                    self.middleware = old_middleware
            
            return wrapper
        return decorator
    
    def resource(self, name: str, controller: str, only: List[str] = None, 
                 except_: List[str] = None):
        """资源路由"""
        if only is None:
            only = ['index', 'show', 'store', 'update', 'destroy']
        if except_:
            only = [action for action in only if action not in except_]
        
        routes = []
        
        if 'index' in only:
            routes.append(self.get(f"/{name}", f"{controller}.index", f"{name}.index"))
        
        if 'show' in only:
            routes.append(self.get(f"/{name}/{{id}}", f"{controller}.show", f"{name}.show"))
        
        if 'store' in only:
            routes.append(self.post(f"/{name}", f"{controller}.store", f"{name}.store"))
        
        if 'update' in only:
            routes.append(self.put(f"/{name}/{{id}}", f"{controller}.update", f"{name}.update"))
            routes.append(self.patch(f"/{name}/{{id}}", f"{controller}.update", f"{name}.update"))
        
        if 'destroy' in only:
            routes.append(self.delete(f"/{name}/{{id}}", f"{controller}.destroy", f"{name}.destroy"))
        
        return routes
    
    def url(self, name: str, **params) -> str:
        """生成URL"""
        if name not in self.named_routes:
            raise ValueError(f"Route '{name}' not found")
        
        route = self.named_routes[name]
        url = route.path
        
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))
            url = url.replace(f"{{{key}?}}", str(value))
        
        return url


# 全局路由器实例
router = Router()


def route(method: HTTPMethod, path: str, name: Optional[str] = None, 
          middleware: List[str] = None):
    """路由装饰器"""
    def decorator(func):
        router.add_route(method, path, func, name, middleware)
        return func
    return decorator


def get(path: str, name: Optional[str] = None, middleware: List[str] = None):
    """GET路由装饰器"""
    return route(HTTPMethod.GET, path, name, middleware)


def post(path: str, name: Optional[str] = None, middleware: List[str] = None):
    """POST路由装饰器"""
    return route(HTTPMethod.POST, path, name, middleware)


def put(path: str, name: Optional[str] = None, middleware: List[str] = None):
    """PUT路由装饰器"""
    return route(HTTPMethod.PUT, path, name, middleware)


def delete(path: str, name: Optional[str] = None, middleware: List[str] = None):
    """DELETE路由装饰器"""
    return route(HTTPMethod.DELETE, path, name, middleware)


def patch(path: str, name: Optional[str] = None, middleware: List[str] = None):
    """PATCH路由装饰器"""
    return route(HTTPMethod.PATCH, path, name, middleware)