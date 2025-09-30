"""
路由注册器
自动注册注解路由到FastAPI
"""

from typing import List, Dict, Any
from fastapi import FastAPI, APIRouter
from app.core.routing.route_decorators import get_routes, RouteInfo, HTTPMethod
from app.core.middleware.base import Request, Response
import asyncio


class RouteRegistry:
    """路由注册器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.registered_routes: List[RouteInfo] = []
    
    def register_controller_routes(self, controller_class: Any):
        """注册控制器路由"""
        # 获取控制器实例
        controller = controller_class()
        
        # 获取控制器信息
        prefix = getattr(controller_class, '_prefix', '')
        version = getattr(controller_class, '_version', 'v1')
        middleware = getattr(controller_class, '_middleware', [])
        
        # 创建API路由器
        router = APIRouter(prefix=f"/api/{version}{prefix}")
        
        # 注册路由
        for route_info in get_routes():
            if hasattr(controller, route_info.handler.__name__):
                # 获取处理方法
                handler_method = getattr(controller, route_info.handler.__name__)
                
                # 注册到FastAPI路由器
                if route_info.method == HTTPMethod.GET:
                    router.get(route_info.path, name=route_info.name)(handler_method)
                elif route_info.method == HTTPMethod.POST:
                    router.post(route_info.path, name=route_info.name)(handler_method)
                elif route_info.method == HTTPMethod.PUT:
                    router.put(route_info.path, name=route_info.name)(handler_method)
                elif route_info.method == HTTPMethod.PATCH:
                    router.patch(route_info.path, name=route_info.name)(handler_method)
                elif route_info.method == HTTPMethod.DELETE:
                    router.delete(route_info.path, name=route_info.name)(handler_method)
                elif route_info.method == HTTPMethod.OPTIONS:
                    router.options(route_info.path, name=route_info.name)(handler_method)
                elif route_info.method == HTTPMethod.HEAD:
                    router.head(route_info.path, name=route_info.name)(handler_method)
        
        # 将路由器添加到主应用
        self.app.include_router(router)
        
        # 记录已注册的路由
        self.registered_routes.extend(get_routes())
    
    def register_all_routes(self, controllers: List[Any]):
        """注册所有控制器路由"""
        for controller_class in controllers:
            self.register_controller_routes(controller_class)
    
    def get_registered_routes(self) -> List[RouteInfo]:
        """获取已注册的路由"""
        return self.registered_routes
    
    def get_route_by_name(self, name: str) -> RouteInfo:
        """根据名称获取路由"""
        for route in self.registered_routes:
            if route.name == name:
                return route
        return None
    
    def generate_url(self, name: str, **params) -> str:
        """生成URL"""
        route = self.get_route_by_name(name)
        if not route:
            raise ValueError(f"Route '{name}' not found")
        
        url = f"/api/{route.version}{route.prefix}{route.path}"
        
        # 替换路径参数
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))
        
        return url


class AutoRouteRegistry:
    """自动路由注册器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.registry = RouteRegistry(app)
        self.controllers: List[Any] = []
    
    def register_controller(self, controller_class: Any):
        """注册控制器"""
        self.controllers.append(controller_class)
        self.registry.register_controller_routes(controller_class)
    
    def register_controllers(self, controllers: List[Any]):
        """批量注册控制器"""
        for controller_class in controllers:
            self.register_controller(controller_class)
    
    def auto_discover_controllers(self, module_path: str):
        """自动发现控制器"""
        import importlib
        import inspect
        
        try:
            module = importlib.import_module(module_path)
            
            # 查找所有控制器类
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '_prefix') and 
                    hasattr(obj, '_version')):
                    self.register_controller(obj)
                    
        except ImportError as e:
            print(f"无法导入模块 {module_path}: {e}")
    
    def get_all_routes(self) -> List[Dict[str, Any]]:
        """获取所有路由信息"""
        routes = []
        for route in self.registry.get_registered_routes():
            routes.append({
                "name": route.name,
                "method": route.method.value,
                "path": f"/api/{route.version}{route.prefix}{route.path}",
                "handler": route.handler.__name__,
                "middleware": route.middleware
            })
        return routes
    
    def print_routes(self):
        """打印所有路由"""
        print("\n=== 注册的路由 ===")
        for route in self.get_all_routes():
            print(f"{route['method']:6} {route['path']:30} -> {route['handler']} ({route['name']})")
        print("=" * 50)


# 全局路由注册器实例
auto_registry = None


def init_auto_registry(app: FastAPI):
    """初始化自动路由注册器"""
    global auto_registry
    auto_registry = AutoRouteRegistry(app)
    return auto_registry


def get_auto_registry() -> AutoRouteRegistry:
    """获取自动路由注册器"""
    if auto_registry is None:
        raise RuntimeError("自动路由注册器未初始化")
    return auto_registry


def register_controller(controller_class: Any):
    """注册控制器（便捷函数）"""
    registry = get_auto_registry()
    registry.register_controller(controller_class)


def register_controllers(controllers: List[Any]):
    """批量注册控制器（便捷函数）"""
    registry = get_auto_registry()
    registry.register_controllers(controllers)


def auto_discover_controllers(module_path: str):
    """自动发现控制器（便捷函数）"""
    registry = get_auto_registry()
    registry.auto_discover_controllers(module_path)