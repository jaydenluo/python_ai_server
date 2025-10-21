"""
FastAPI路由注册器
将装饰器收集的路由信息注册到FastAPI应用
"""

from typing import List, Dict, Any
from fastapi import FastAPI, APIRouter, Request, Response, Depends
from app.core.routing.route_decorators import get_routes, RouteInfo, HTTPMethod, auto_discover_controllers as scan_controllers
import inspect
from functools import wraps


class FastAPIRouteRegistry:
    """FastAPI路由注册器 - 简化版"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.registered_controllers = set()
        self.controller_instances = {}  # 保存控制器实例
    
    def register_from_decorators(self):
        """从装饰器系统注册所有路由到FastAPI"""
        # 先执行自动扫描
        scan_controllers()
        
        # 获取所有路由信息
        routes = get_routes()
        
        # 按控制器分组
        controller_routes = {}
        for route in routes:
            controller_name = route.handler.__qualname__.split('.')[0]
            if controller_name not in controller_routes:
                controller_routes[controller_name] = []
            controller_routes[controller_name].append(route)
        
        # 为每个控制器创建路由器
        for controller_name, routes_list in controller_routes.items():
            if not routes_list:
                continue
                
            # 获取第一个路由的信息作为控制器信息
            first_route = routes_list[0]
            prefix = first_route.prefix
            version = first_route.version
            tags = first_route.tags or [controller_name]  # 使用自定义tags或控制器名称
            
            # 创建API路由器
            # 直接使用prefix，不添加/api前缀（让控制器自己指定完整路径）
            router = APIRouter(
                prefix=prefix,
                tags=tags
            )
            
            # 注册路由到FastAPI路由器
            for route in routes_list:
                self._register_single_route(router, route)
            
            # 将路由器添加到主应用
            self.app.include_router(router)
            
            # 简化日志：不打印每个控制器的注册信息
            # print(f"✅ 注册控制器: {controller_name} ({len(routes_list)} 个路由)")
    
    def _register_single_route(self, router: APIRouter, route: RouteInfo):
        """注册单个路由到FastAPI路由器"""
        # 根据HTTP方法注册路由
        method_map = {
            HTTPMethod.GET: router.get,
            HTTPMethod.POST: router.post,
            HTTPMethod.PUT: router.put,
            HTTPMethod.PATCH: router.patch,
            HTTPMethod.DELETE: router.delete,
            HTTPMethod.OPTIONS: router.options,
            HTTPMethod.HEAD: router.head,
        }
        
        if route.method in method_map:
            # 获取控制器类
            handler_qualname = route.handler.__qualname__
            if '.' in handler_qualname:
                # 实例方法
                class_name = handler_qualname.split('.')[0]
                method_name = route.handler.__name__
                
                # 从handler的__globals__中找到控制器类
                controller_class = None
                if hasattr(route.handler, '__globals__'):
                    controller_class = route.handler.__globals__.get(class_name)
                
                # 使用完整标识符（模块 + 类名）作为键，避免同名类冲突
                module_name = route.handler.__module__ if hasattr(route.handler, '__module__') else ''
                full_class_key = f"{module_name}.{class_name}"
                
                if controller_class and full_class_key not in self.controller_instances:
                    # 创建控制器实例（单例）
                    self.controller_instances[full_class_key] = controller_class()
                
                if full_class_key in self.controller_instances:
                    # 直接使用绑定的方法
                    handler = getattr(self.controller_instances[full_class_key], method_name)
                else:
                    handler = route.handler
            else:
                # 函数：直接使用
                handler = route.handler
            
            # 直接使用router的add_api_route方法注册
            # FastAPI会自动识别Request类型参数为依赖注入
            router.add_api_route(
                path=route.path,
                endpoint=handler,
                methods=[route.method.value],
                name=route.name,
                summary=getattr(route.handler, '_api_doc', {}).get('summary', ''),
                description=getattr(route.handler, '_api_doc', {}).get('description', ''),
                tags=getattr(route.handler, '_api_doc', {}).get('tags', []),
                response_model=None  # 允许自定义Response，不指定response_class让FastAPI自动处理
            )
    
    def get_route_info(self) -> List[Dict[str, Any]]:
        """获取所有路由信息"""
        routes = []
        for route in get_routes():
            routes.append({
                "name": route.name,
                "method": route.method.value,
                "path": f"/api/{route.version}{route.prefix}{route.path}",
                "handler": f"{route.handler.__qualname__}",
                "middleware": route.middleware,
                "permissions": getattr(route.handler, '_permissions', [])
            })
        return routes
    
    def print_routes(self):
        """打印所有路由信息"""
        print("\n" + "="*80)
        print("🛣️  已注册的路由")
        print("="*80)
        
        routes = self.get_route_info()
        for i, route in enumerate(routes, 1):
            method = route['method']
            path = route['path']
            handler = route['handler']
            name = route['name']
            
            print(f"{i:3d}. {method:6} {path:40} -> {handler}")
            if route['permissions']:
                print(f"     🔒 权限: {', '.join(route['permissions'])}")
            if route['middleware']:
                print(f"     🔧 中间件: {', '.join(route['middleware'])}")
            print()
        
        print(f"✅ 总计: {len(routes)} 个路由")
        print("="*80)


# 全局注册器实例
_registry = None


def init_fastapi_registry(app: FastAPI) -> FastAPIRouteRegistry:
    """初始化FastAPI路由注册器"""
    global _registry
    _registry = FastAPIRouteRegistry(app)
    return _registry


def get_fastapi_registry() -> FastAPIRouteRegistry:
    """获取FastAPI路由注册器"""
    if _registry is None:
        raise RuntimeError("FastAPI路由注册器未初始化，请先调用 init_fastapi_registry(app)")
    return _registry


def register_all_routes():
    """注册所有路由到FastAPI（便捷函数）"""
    registry = get_fastapi_registry()
    registry.register_from_decorators()


def print_all_routes():
    """打印所有路由信息（便捷函数）"""
    registry = get_fastapi_registry()
    registry.print_routes()