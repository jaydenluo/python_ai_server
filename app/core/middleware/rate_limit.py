"""
限流中间件
防止API滥用，实现请求频率限制
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from .base import Middleware, Request, Response


class RateLimitMiddleware(Middleware):
    """限流中间件"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000, 
                 requests_per_day: int = 10000, **kwargs):
        super().__init__(**kwargs)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        
        # 存储请求记录
        self.request_records: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: {
                "minute": deque(),
                "hour": deque(),
                "day": deque()
            }
        )
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端ID"""
        # 优先使用用户ID
        if request.user and request.user.get("id"):
            return f"user_{request.user['id']}"
        
        # 使用IP地址
        return request.headers.get("X-Forwarded-For", "127.0.0.1")
    
    def _clean_old_records(self, records: deque, window_seconds: int):
        """清理过期记录"""
        current_time = time.time()
        while records and current_time - records[0] > window_seconds:
            records.popleft()
    
    def _check_rate_limit(self, client_id: str) -> tuple[bool, str]:
        """检查限流"""
        current_time = time.time()
        records = self.request_records[client_id]
        
        # 清理过期记录
        self._clean_old_records(records["minute"], 60)
        self._clean_old_records(records["hour"], 3600)
        self._clean_old_records(records["day"], 86400)
        
        # 检查分钟级限流
        if len(records["minute"]) >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute"
        
        # 检查小时级限流
        if len(records["hour"]) >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour"
        
        # 检查天级限流
        if len(records["day"]) >= self.requests_per_day:
            return False, "Rate limit exceeded: too many requests per day"
        
        # 记录当前请求
        records["minute"].append(current_time)
        records["hour"].append(current_time)
        records["day"].append(current_time)
        
        return True, ""
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理限流"""
        client_id = self._get_client_id(request)
        
        # 检查限流
        allowed, error_message = self._check_rate_limit(client_id)
        
        if not allowed:
            return Response(
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": "60"
                },
                body={"error": error_message}
            )
        
        # 继续处理请求
        return await next_handler()


class IPRateLimitMiddleware(Middleware):
    """IP限流中间件"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600, **kwargs):
        super().__init__(**kwargs)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_requests: Dict[str, deque] = defaultdict(deque)
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        return request.headers.get("X-Forwarded-For", "127.0.0.1")
    
    def _clean_old_requests(self, requests: deque):
        """清理过期请求"""
        current_time = time.time()
        while requests and current_time - requests[0] > self.window_seconds:
            requests.popleft()
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理IP限流"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # 清理过期请求
        self._clean_old_requests(self.ip_requests[client_ip])
        
        # 检查请求数量
        if len(self.ip_requests[client_ip]) >= self.max_requests:
            return Response(
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(self.window_seconds)
                },
                body={"error": "Rate limit exceeded for IP address"}
            )
        
        # 记录请求
        self.ip_requests[client_ip].append(current_time)
        
        # 继续处理请求
        return await next_handler()


class UserRateLimitMiddleware(Middleware):
    """用户限流中间件"""
    
    def __init__(self, max_requests: int = 1000, window_seconds: int = 3600, **kwargs):
        super().__init__(**kwargs)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: Dict[str, deque] = defaultdict(deque)
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """获取用户ID"""
        if request.user and request.user.get("id"):
            return str(request.user["id"])
        return None
    
    def _clean_old_requests(self, requests: deque):
        """清理过期请求"""
        current_time = time.time()
        while requests and current_time - requests[0] > self.window_seconds:
            requests.popleft()
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理用户限流"""
        user_id = self._get_user_id(request)
        
        if not user_id:
            # 未认证用户，跳过限流
            return await next_handler()
        
        current_time = time.time()
        
        # 清理过期请求
        self._clean_old_requests(self.user_requests[user_id])
        
        # 检查请求数量
        if len(self.user_requests[user_id]) >= self.max_requests:
            return Response(
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(self.window_seconds)
                },
                body={"error": "Rate limit exceeded for user"}
            )
        
        # 记录请求
        self.user_requests[user_id].append(current_time)
        
        # 继续处理请求
        return await next_handler()