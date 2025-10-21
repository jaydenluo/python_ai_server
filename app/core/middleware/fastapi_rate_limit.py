"""
FastAPI 兼容的限流中间件
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class FastAPIRateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI 兼容的限流中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60, 
                 requests_per_hour: int = 1000, requests_per_day: int = 10000,
                 burst_limit: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.burst_limit = burst_limit
        
        # 存储客户端请求记录
        self.client_requests = defaultdict(lambda: {
            'minute': deque(),
            'hour': deque(),
            'day': deque(),
            'burst': deque()
        })
        
        # 不限流的路径
        self.exempt_paths = {
            "/health", "/metrics", "/favicon.ico", "/docs", "/redoc", "/openapi.json"
        }
        
        # 清理间隔（秒）
        self.cleanup_interval = 300  # 5分钟
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        """处理请求并应用限流"""
        # 检查是否是免限流路径
        if self._is_exempt_path(request.url.path):
            return await call_next(request)
        
        # 获取客户端标识
        client_id = self._get_client_id(request)
        
        # 定期清理过期记录
        await self._cleanup_expired_records()
        
        # 检查限流
        rate_limit_result = self._check_rate_limit(client_id)
        
        if not rate_limit_result["allowed"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": rate_limit_result["message"],
                    "retry_after": rate_limit_result["retry_after"],
                    "limits": {
                        "requests_per_minute": self.requests_per_minute,
                        "requests_per_hour": self.requests_per_hour,
                        "requests_per_day": self.requests_per_day
                    }
                },
                headers={
                    "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
                    "X-RateLimit-Limit-Day": str(self.requests_per_day),
                    "X-RateLimit-Remaining-Minute": str(rate_limit_result["remaining_minute"]),
                    "X-RateLimit-Remaining-Hour": str(rate_limit_result["remaining_hour"]),
                    "X-RateLimit-Remaining-Day": str(rate_limit_result["remaining_day"]),
                    "Retry-After": str(rate_limit_result["retry_after"])
                }
            )
        
        # 记录请求
        self._record_request(client_id)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流信息到响应头
        response.headers.update({
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Limit-Day": str(self.requests_per_day),
            "X-RateLimit-Remaining-Minute": str(rate_limit_result["remaining_minute"]),
            "X-RateLimit-Remaining-Hour": str(rate_limit_result["remaining_hour"]),
            "X-RateLimit-Remaining-Day": str(rate_limit_result["remaining_day"])
        })
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端唯一标识"""
        # 优先使用认证用户ID
        if hasattr(request.state, 'user_id') and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        # 使用IP地址
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.headers.get("X-Real-IP")
            if not client_ip and hasattr(request, "client") and request.client:
                client_ip = request.client.host
            else:
                client_ip = "unknown"
        
        return f"ip:{client_ip}"
    
    def _is_exempt_path(self, path: str) -> bool:
        """检查是否是免限流路径"""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _check_rate_limit(self, client_id: str) -> Dict[str, Any]:
        """检查限流状态"""
        current_time = time.time()
        client_records = self.client_requests[client_id]
        
        # 清理过期记录
        self._clean_client_records(client_records, current_time)
        
        # 计算各时间窗口的请求数
        minute_count = len(client_records['minute'])
        hour_count = len(client_records['hour'])
        day_count = len(client_records['day'])
        burst_count = len(client_records['burst'])
        
        # 检查各种限制
        if burst_count >= self.burst_limit:
            return {
                "allowed": False,
                "message": f"Burst limit exceeded ({self.burst_limit} requests per 10 seconds)",
                "retry_after": 10,
                "remaining_minute": max(0, self.requests_per_minute - minute_count),
                "remaining_hour": max(0, self.requests_per_hour - hour_count),
                "remaining_day": max(0, self.requests_per_day - day_count)
            }
        
        if minute_count >= self.requests_per_minute:
            return {
                "allowed": False,
                "message": f"Minute limit exceeded ({self.requests_per_minute} requests per minute)",
                "retry_after": 60,
                "remaining_minute": 0,
                "remaining_hour": max(0, self.requests_per_hour - hour_count),
                "remaining_day": max(0, self.requests_per_day - day_count)
            }
        
        if hour_count >= self.requests_per_hour:
            return {
                "allowed": False,
                "message": f"Hour limit exceeded ({self.requests_per_hour} requests per hour)",
                "retry_after": 3600,
                "remaining_minute": max(0, self.requests_per_minute - minute_count),
                "remaining_hour": 0,
                "remaining_day": max(0, self.requests_per_day - day_count)
            }
        
        if day_count >= self.requests_per_day:
            return {
                "allowed": False,
                "message": f"Daily limit exceeded ({self.requests_per_day} requests per day)",
                "retry_after": 86400,
                "remaining_minute": max(0, self.requests_per_minute - minute_count),
                "remaining_hour": max(0, self.requests_per_hour - hour_count),
                "remaining_day": 0
            }
        
        return {
            "allowed": True,
            "message": "Request allowed",
            "retry_after": 0,
            "remaining_minute": max(0, self.requests_per_minute - minute_count),
            "remaining_hour": max(0, self.requests_per_hour - hour_count),
            "remaining_day": max(0, self.requests_per_day - day_count)
        }
    
    def _record_request(self, client_id: str):
        """记录请求"""
        current_time = time.time()
        client_records = self.client_requests[client_id]
        
        # 记录到各个时间窗口
        client_records['minute'].append(current_time)
        client_records['hour'].append(current_time)
        client_records['day'].append(current_time)
        client_records['burst'].append(current_time)
    
    def _clean_client_records(self, records: Dict[str, deque], current_time: float):
        """清理客户端的过期记录"""
        # 清理1分钟窗口
        while records['minute'] and current_time - records['minute'][0] > 60:
            records['minute'].popleft()
        
        # 清理1小时窗口
        while records['hour'] and current_time - records['hour'][0] > 3600:
            records['hour'].popleft()
        
        # 清理1天窗口
        while records['day'] and current_time - records['day'][0] > 86400:
            records['day'].popleft()
        
        # 清理突发窗口（10秒）
        while records['burst'] and current_time - records['burst'][0] > 10:
            records['burst'].popleft()
    
    async def _cleanup_expired_records(self):
        """定期清理过期记录"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # 清理所有客户端的过期记录
        clients_to_remove = []
        for client_id, records in self.client_requests.items():
            self._clean_client_records(records, current_time)
            
            # 如果客户端没有任何活跃记录，标记为删除
            if not any(records.values()):
                clients_to_remove.append(client_id)
        
        # 删除无活跃记录的客户端
        for client_id in clients_to_remove:
            del self.client_requests[client_id]
        
        self.last_cleanup = current_time