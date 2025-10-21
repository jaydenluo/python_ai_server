"""
中间件基类
定义中间件接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass


@dataclass
class Request:
    """请求对象"""
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Any
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None


@dataclass
class Response:
    """响应对象"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    content_type: str = "application/json"


class Middleware(ABC):
    """中间件基类"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    @abstractmethod
    async def handle(self, request: Request, next_handler: Callable) -> Response:
        """
        处理请求
        
        Args:
            request: 请求对象
            next_handler: 下一个处理器
            
        Returns:
            Response: 响应对象
        """
        pass


class MiddlewareManager:
    """中间件管理器"""
    
    def __init__(self):
        self.middlewares: Dict[str, Middleware] = {}
        self.global_middlewares: List[str] = []
    
    def register(self, name: str, middleware: Middleware):
        """注册中间件"""
        self.middlewares[name] = middleware
    
    def register_global(self, middleware_name: str):
        """注册全局中间件"""
        if middleware_name not in self.global_middlewares:
            self.global_middlewares.append(middleware_name)
    
    def get_middleware(self, name: str) -> Optional[Middleware]:
        """获取中间件"""
        return self.middlewares.get(name)
    
    async def process_request(self, request: Request, route_middlewares: List[str] = None) -> Response:
        """处理请求"""
        # 合并全局中间件和路由中间件
        all_middlewares = self.global_middlewares + (route_middlewares or [])
        
        # 创建中间件处理链
        async def create_handler(index: int = 0):
            if index >= len(all_middlewares):
                # 如果没有更多中间件，返回默认响应
                return Response(
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                    body={"error": "Not Found"}
                )
            
            middleware_name = all_middlewares[index]
            middleware = self.get_middleware(middleware_name)
            
            if not middleware:
                # 如果中间件不存在，跳过
                return await create_handler(index + 1)
            
            # 创建下一个处理器
            next_handler = await create_handler(index + 1)
            
            # 执行当前中间件
            return await middleware.handle(request, lambda: next_handler)
        
        return await create_handler()


# 全局中间件管理器
middleware_manager = MiddlewareManager()