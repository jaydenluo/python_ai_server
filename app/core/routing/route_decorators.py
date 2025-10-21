"""
路由装饰器
提供类似Laravel和Spring Boot的注解路由功能
"""

import sys
import io

# 设置UTF-8输出（必须在最开始，避免Windows emoji错误）
if sys.platform == 'win32' and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from enum import Enum
from dataclasses import dataclass
import inspect
import os
import importlib
import pkgutil


def _should_suppress_scan_logs() -> bool:
    """判断是否应该抑制扫描日志（避免 reload 模式重复）"""
    import os
    import tempfile
    
    flag_file = os.path.join(tempfile.gettempdir(), 'python_ai_framework_scan.flag')
    
    if os.path.exists(flag_file):
        return False  # 不抑制，显示日志
    else:
        try:
            with open(flag_file, 'w') as f:
                f.write('1')
        except:
            pass
        return True  # 抑制日志


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
    tags: List[str] = None
    
    def __post_init__(self):
        if self.middleware is None:
            self.middleware = []
        if self.tags is None:
            self.tags = []
        if not self.name:
            self.name = f"{self.handler.__name__}"


class RouteRegistry:
    """路由注册表"""
    
    def __init__(self):
        self.routes: List[RouteInfo] = []
        self.route_groups: Dict[str, List[RouteInfo]] = {}
        self.scanned_controllers = set()
    
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
    
    def auto_scan_controllers(self, base_package: str = "app.controller"):
        """自动扫描控制器"""
        try:
            # 导入基础包
            base_module = importlib.import_module(base_package)
            base_path = base_module.__path__[0]
            
            # 递归扫描所有子模块
            for importer, modname, ispkg in pkgutil.walk_packages([base_path], base_package + "."):
                if modname in self.scanned_controllers:
                    continue
                    
                try:
                    # 导入模块
                    module = importlib.import_module(modname)
                    self.scanned_controllers.add(modname)
                    
                    # 扫描模块中的类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # 检查是否是控制器类（有 @api_controller 装饰器）
                        if hasattr(obj, '_prefix') and hasattr(obj, '_version'):
                            # 扫描类中的方法
                            for method_name, method in inspect.getmembers(obj, inspect.ismethod):
                                if hasattr(method, '_route_info'):
                                    # 路由已经在装饰器中注册了
                                    pass
                            
                            # 不打印每个成功扫描的控制器，只显示警告和最终统计
                            
                except ImportError as e:
                    print(f"⚠️ 跳过模块 {modname}: {e}")
                except Exception as e:
                    print(f"❌ 扫描模块 {modname} 时出错: {e}")
                    
        except Exception as e:
            print(f"❌ 自动扫描控制器失败: {e}")
    
    def scan_and_register_all(self):
        """扫描并注册所有控制器"""
        # 只在工作进程中打印日志（避免 reload 模式重复）
        should_log = not _should_suppress_scan_logs()
        
        if should_log:
            print("🔍 开始自动扫描控制器...")
            
        self.auto_scan_controllers()
        
        if should_log:
            print(f"✅ 扫描完成，共注册 {len(self.routes)} 个路由")


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
        
        # 保持原函数不变（处理async函数）
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
        else:
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


def api_controller(prefix: str = "", version: Optional[str] = None, middleware: List[str] = None,
                   tags: List[str] = None,
                   # 简称参数
                   p: str = "", v: Optional[str] = None, m: List[str] = None):
    """API控制器装饰器 - 支持中间件装饰器和标签分组"""
    def decorator(cls):
        # 处理简称参数
        final_prefix = p or prefix
        final_version = v or version or "v1"
        final_tags = tags or []
        
        # 检查类是否有中间件装饰器设置的默认中间件
        if hasattr(cls, '_default_middleware'):
            final_middleware = cls._default_middleware
        else:
            final_middleware = m or middleware or ["auth"]  # 默认需要认证
        
        # 为类添加控制器信息
        cls._prefix = final_prefix
        cls._version = final_version
        cls._middleware = final_middleware
        cls._tags = final_tags
        
        # 扫描类中的方法，自动注册路由
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_route_info'):
                # 更新路由信息
                route_info = method._route_info
                route_info.prefix = final_prefix
                route_info.version = final_version
                route_info.tags = final_tags
                
                # 合并中间件：类级别 + 方法级别
                method_middleware = getattr(method, '_middleware', [])
                if method_middleware:
                    route_info.middleware = final_middleware + method_middleware
                else:
                    route_info.middleware = final_middleware
        
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
    """认证必需装饰器 - 已废弃，推荐使用 @auth"""
    # 为了向后兼容保留，推荐使用新的 @auth 装饰器
    return middleware(["auth"])(func)


def admin_required(func):
    """管理员必需装饰器 - 已废弃，推荐使用 @admin"""
    # 为了向后兼容保留，推荐使用新的 @admin 装饰器
    return middleware(["auth", "admin"])(func)


def anonymous(func_or_cls):
    """匿名访问装饰器 - 可用于方法或类"""
    if inspect.isclass(func_or_cls):
        # 类装饰器
        func_or_cls._default_middleware = ["anonymous"]
        return func_or_cls
    else:
        # 方法装饰器
        return middleware(["anonymous"])(func_or_cls)


def auth(func_or_cls):
    """认证访问装饰器 - 可用于方法或类"""
    if inspect.isclass(func_or_cls):
        # 类装饰器
        func_or_cls._default_middleware = ["auth"]
        return func_or_cls
    else:
        # 方法装饰器
        return middleware(["auth"])(func_or_cls)


def admin(func_or_cls):
    """管理员访问装饰器 - 可用于方法或类"""
    if inspect.isclass(func_or_cls):
        # 类装饰器
        func_or_cls._default_middleware = ["auth", "admin"]
        return func_or_cls
    else:
        # 方法装饰器
        return middleware(["auth", "admin"])(func_or_cls)


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


def doc(summary: str, description: str = ""):
    """简化的文档装饰器 - 只需要标题和描述"""
    def decorator(func):
        if not hasattr(func, '_api_doc'):
            func._api_doc = {}
        
        # 智能推断标签
        class_name = func.__qualname__.split('.')[0] if '.' in func.__qualname__ else ""
        if "Admin" in class_name:
            default_tags = ["管理后台"]
        elif "Web" in class_name:
            default_tags = ["Web端"]
        elif "Api" in class_name:
            default_tags = ["API"]
        else:
            default_tags = ["通用"]
        
        # 智能推断响应
        method_name = func.__name__.lower()
        if method_name in ['index', 'list', 'get']:
            default_responses = {
                "200": {"description": "获取成功"},
                "401": {"description": "未授权"},
                "403": {"description": "权限不足"}
            }
        elif method_name in ['store', 'create', 'post']:
            default_responses = {
                "201": {"description": "创建成功"},
                "400": {"description": "请求参数错误"},
                "401": {"description": "未授权"},
                "422": {"description": "数据验证失败"}
            }
        elif method_name in ['update', 'put', 'patch']:
            default_responses = {
                "200": {"description": "更新成功"},
                "400": {"description": "请求参数错误"},
                "401": {"description": "未授权"},
                "404": {"description": "资源不存在"}
            }
        elif method_name in ['destroy', 'delete']:
            default_responses = {
                "204": {"description": "删除成功"},
                "401": {"description": "未授权"},
                "404": {"description": "资源不存在"}
            }
        else:
            default_responses = {
                "200": {"description": "操作成功"},
                "401": {"description": "未授权"}
            }
        
        func._api_doc = {
            "summary": summary,
            "description": description or summary,
            "tags": default_tags,
            "responses": default_responses
        }
        return func
    return decorator


def title(summary: str):
    """最简化的文档装饰器 - 只需要一个标题"""
    return doc(summary, summary)


def desc(description: str):
    """描述装饰器 - 从方法名自动生成标题"""
    def decorator(func):
        # 从方法名生成标题
        method_name = func.__name__
        if method_name == 'index':
            auto_summary = "获取列表"
        elif method_name == 'show':
            auto_summary = "获取详情"
        elif method_name == 'store':
            auto_summary = "创建资源"
        elif method_name == 'update':
            auto_summary = "更新资源"
        elif method_name == 'destroy':
            auto_summary = "删除资源"
        else:
            # 将驼峰命名转换为中文描述
            auto_summary = method_name.replace('_', ' ').title()
        
        return doc(auto_summary, description)(func)
    return decorator


# 预定义的常用文档装饰器
def get_list(description: str = "获取数据列表"):
    """获取列表的文档装饰器"""
    return doc("获取列表", description)


def get_detail(description: str = "获取详细信息"):
    """获取详情的文档装饰器"""
    return doc("获取详情", description)


def create_resource(description: str = "创建新资源"):
    """创建资源的文档装饰器"""
    return doc("创建资源", description)


def update_resource(description: str = "更新资源信息"):
    """更新资源的文档装饰器"""
    return doc("更新资源", description)


def delete_resource(description: str = "删除资源"):
    """删除资源的文档装饰器"""
    return doc("删除资源", description)


# ==================== 简化权限装饰器系统 ====================

def requires(permissions_list: List[str]):
    """权限装饰器 - 检查权限列表"""
    def decorator(func):
        if not hasattr(func, '_permissions'):
            func._permissions = []
        func._permissions.extend(permissions_list)
        return func
    return decorator




def cors(origins: List[str] = None, methods: List[str] = None, headers: List[str] = None):
    """CORS装饰器"""
    def decorator(func):
        if not hasattr(func, '_cors'):
            func._cors = {}
        func._cors = {
            "origins": origins or ["*"],
            "methods": methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "headers": headers or ["Content-Type", "Authorization"]
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


def auto_discover_controllers():
    """自动发现并注册所有控制器"""
    return route_registry.scan_and_register_all()


def get_all_controllers():
    """获取所有已扫描的控制器"""
    return list(route_registry.scanned_controllers)


# ==================== 路由组和资源路由 ====================

def route_group(prefix: str = "", middleware: List[str] = None, version: str = "v1"):
    """路由组装饰器"""
    def decorator(cls):
        # 为类添加组信息
        cls._group_prefix = prefix
        cls._group_middleware = middleware or []
        cls._group_version = version
        
        # 更新类中所有路由的信息
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_route_info'):
                route_info = method._route_info
                route_info.prefix = f"{prefix}{route_info.prefix}"
                route_info.version = version
                if middleware:
                    route_info.middleware.extend(middleware)
        
        return cls
    return decorator


def api_resource(resource_name: str, only: List[str] = None, except_: List[str] = None):
    """API资源装饰器 - 自动生成标准CRUD路由"""
    def decorator(cls):
        # 默认包含的方法
        default_methods = ['index', 'show', 'store', 'update', 'destroy']
        
        # 处理only和except参数
        if only:
            methods = only
        else:
            methods = default_methods
        
        if except_:
            methods = [m for m in methods if m not in except_]
        
        # 为类添加资源信息
        cls._resource_name = resource_name
        cls._resource_methods = methods
        
        # 自动添加路由装饰器
        if 'index' in methods and hasattr(cls, 'index'):
            get(f"/{resource_name}", name=f"{resource_name}.index")(cls.index)
        
        if 'show' in methods and hasattr(cls, 'show'):
            get(f"/{resource_name}/{{id}}", name=f"{resource_name}.show")(cls.show)
        
        if 'store' in methods and hasattr(cls, 'store'):
            post(f"/{resource_name}", name=f"{resource_name}.store")(cls.store)
        
        if 'update' in methods and hasattr(cls, 'update'):
            put(f"/{resource_name}/{{id}}", name=f"{resource_name}.update")(cls.update)
            patch(f"/{resource_name}/{{id}}", name=f"{resource_name}.patch")(cls.update)
        
        if 'destroy' in methods and hasattr(cls, 'destroy'):
            delete(f"/{resource_name}/{{id}}", name=f"{resource_name}.destroy")(cls.destroy)
        
        return cls
    return decorator