"""
API中间件
提供API专用的中间件功能
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.middleware.base import Middleware, Request, Response
from app.core.config.settings import config


class APIVersionMiddleware(Middleware):
    """API版本中间件"""
    
    def __init__(self, default_version: str = "v1", **kwargs):
        super().__init__(**kwargs)
        self.default_version = default_version
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理API版本"""
        # 从路径中提取版本
        path_parts = request.path.split("/")
        if len(path_parts) >= 3 and path_parts[1] == "api":
            version = path_parts[2]
            request.api_version = version
        else:
            request.api_version = self.default_version
        
        # 继续处理请求
        return await next_handler()


class APIResponseMiddleware(Middleware):
    """API响应中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理API响应"""
        # 处理请求
        response = await next_handler()
        
        # 确保响应格式正确
        if isinstance(response.body, dict):
            # 添加API元数据
            if "meta" not in response.body:
                response.body["meta"] = {}
            
            response.body["meta"]["api_version"] = getattr(request, "api_version", "v1")
            response.body["meta"]["timestamp"] = datetime.now().isoformat()
            response.body["meta"]["request_id"] = getattr(request, "request_id", None)
        
        return response


class CORSMiddleware(Middleware):
    """CORS中间件"""
    
    def __init__(self, 
                 allowed_origins: list = None,
                 allowed_methods: list = None,
                 allowed_headers: list = None,
                 allow_credentials: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["*"]
        self.allow_credentials = allow_credentials
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理CORS"""
        # 处理预检请求
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers=self._get_cors_headers(request),
                body=""
            )
        
        # 处理实际请求
        response = await next_handler()
        
        # 添加CORS头
        response.headers.update(self._get_cors_headers(request))
        
        return response
    
    def _get_cors_headers(self, request: Request) -> Dict[str, str]:
        """获取CORS头"""
        origin = request.headers.get("Origin", "")
        
        headers = {
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
            "Access-Control-Allow-Credentials": str(self.allow_credentials).lower()
        }
        
        if "*" in self.allowed_origins or origin in self.allowed_origins:
            headers["Access-Control-Allow-Origin"] = origin if origin else "*"
        
        return headers


class RequestLoggingMiddleware(Middleware):
    """请求日志中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """记录请求日志"""
        start_time = time.time()
        
        # 记录请求开始
        self.log_request_start(request)
        
        try:
            # 处理请求
            response = await next_handler()
            
            # 记录请求完成
            duration = time.time() - start_time
            self.log_request_complete(request, response, duration)
            
            return response
            
        except Exception as e:
            # 记录请求错误
            duration = time.time() - start_time
            self.log_request_error(request, e, duration)
            raise
    
    def log_request_start(self, request: Request):
        """记录请求开始"""
        print(f"[{datetime.now().isoformat()}] {request.method} {request.path} - 开始处理")
    
    def log_request_complete(self, request: Request, response: Response, duration: float):
        """记录请求完成"""
        print(f"[{datetime.now().isoformat()}] {request.method} {request.path} - 完成 ({response.status_code}) - {duration:.3f}s")
    
    def log_request_error(self, request: Request, error: Exception, duration: float):
        """记录请求错误"""
        print(f"[{datetime.now().isoformat()}] {request.method} {request.path} - 错误 ({type(error).__name__}) - {duration:.3f}s")


class RateLimitMiddleware(Middleware):
    """限流中间件"""
    
    def __init__(self, 
                 requests_per_minute: int = 60,
                 requests_per_hour: int = 1000,
                 **kwargs):
        super().__init__(**kwargs)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_counts: Dict[str, Dict[str, int]] = {}
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理限流"""
        client_ip = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", "unknown"))
        current_time = time.time()
        
        # 检查限流
        if self._is_rate_limited(client_ip, current_time):
            return Response(
                status_code=429,
                headers={"Content-Type": "application/json"},
                body={
                    "error": "请求过于频繁",
                    "message": "请稍后再试",
                    "retry_after": 60
                }
            )
        
        # 记录请求
        self._record_request(client_ip, current_time)
        
        # 处理请求
        return await next_handler()
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """检查是否被限流"""
        if client_ip not in self.request_counts:
            return False
        
        counts = self.request_counts[client_ip]
        
        # 检查每分钟限制
        minute_key = int(current_time // 60)
        if counts.get(f"minute_{minute_key}", 0) >= self.requests_per_minute:
            return True
        
        # 检查每小时限制
        hour_key = int(current_time // 3600)
        if counts.get(f"hour_{hour_key}", 0) >= self.requests_per_hour:
            return True
        
        return False
    
    def _record_request(self, client_ip: str, current_time: float):
        """记录请求"""
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}
        
        counts = self.request_counts[client_ip]
        minute_key = int(current_time // 60)
        hour_key = int(current_time // 3600)
        
        counts[f"minute_{minute_key}"] = counts.get(f"minute_{minute_key}", 0) + 1
        counts[f"hour_{hour_key}"] = counts.get(f"hour_{hour_key}", 0) + 1
        
        # 清理旧数据
        self._cleanup_old_data(client_ip, current_time)
    
    def _cleanup_old_data(self, client_ip: str, current_time: float):
        """清理旧数据"""
        counts = self.request_counts[client_ip]
        current_minute = int(current_time // 60)
        current_hour = int(current_time // 3600)
        
        # 清理超过1小时的分钟数据
        for key in list(counts.keys()):
            if key.startswith("minute_"):
                minute = int(key.split("_")[1])
                if minute < current_minute - 60:
                    del counts[key]
        
        # 清理超过24小时的小时数据
        for key in list(counts.keys()):
            if key.startswith("hour_"):
                hour = int(key.split("_")[1])
                if hour < current_hour - 24:
                    del counts[key]


class AuthenticationMiddleware(Middleware):
    """认证中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理认证"""
        # 检查是否需要认证
        if self._requires_auth(request):
            # 验证令牌
            if not self._validate_token(request):
                return Response(
                    status_code=401,
                    headers={"Content-Type": "application/json"},
                    body={
                        "error": "未认证",
                        "message": "需要有效的访问令牌"
                    }
                )
        
        # 处理请求
        return await next_handler()
    
    def _requires_auth(self, request: Request) -> bool:
        """检查是否需要认证"""
        # 这里可以根据路径、方法等判断是否需要认证
        # 例如：排除登录、注册等公开接口
        public_paths = ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/health"]
        return request.path not in public_paths
    
    def _validate_token(self, request: Request) -> bool:
        """验证令牌"""
        # 从请求头获取令牌
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        
        # 这里应该验证JWT令牌
        # 简化实现，实际应该使用JWT库
        return len(token) > 0


class AuthorizationMiddleware(Middleware):
    """授权中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理授权"""
        # 检查用户权限
        if not self._has_permission(request):
            return Response(
                status_code=403,
                headers={"Content-Type": "application/json"},
                body={
                    "error": "权限不足",
                    "message": "您没有执行此操作的权限"
                }
            )
        
        # 处理请求
        return await next_handler()
    
    def _has_permission(self, request: Request) -> bool:
        """检查用户权限"""
        # 这里应该根据用户角色和请求路径判断权限
        # 简化实现
        return True


class ErrorHandlingMiddleware(Middleware):
    """错误处理中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理错误"""
        try:
            # 处理请求
            return await next_handler()
            
        except Exception as e:
            # 记录错误
            self.log_error(request, e)
            
            # 返回错误响应
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                body={
                    "error": "服务器内部错误",
                    "message": str(e) if config.get("app.debug", False) else "服务器内部错误",
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def log_error(self, request: Request, error: Exception):
        """记录错误"""
        print(f"[{datetime.now().isoformat()}] 错误: {request.method} {request.path} - {type(error).__name__}: {error}")


class RequestIDMiddleware(Middleware):
    """请求ID中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """添加请求ID"""
        # 生成请求ID
        request_id = self._generate_request_id()
        request.request_id = request_id
        
        # 处理请求
        response = await next_handler()
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4())


class CompressionMiddleware(Middleware):
    """压缩中间件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理压缩"""
        # 处理请求
        response = await next_handler()
        
        # 检查是否支持压缩
        if self._should_compress(request, response):
            # 压缩响应
            response = self._compress_response(response)
        
        return response
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """检查是否应该压缩"""
        # 检查客户端是否支持压缩
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return False
        
        # 检查响应大小
        if isinstance(response.body, str):
            return len(response.body) > 1024  # 大于1KB才压缩
        elif isinstance(response.body, dict):
            import json
            body_str = json.dumps(response.body)
            return len(body_str) > 1024
        
        return False
    
    def _compress_response(self, response: Response) -> Response:
        """压缩响应"""
        import gzip
        
        if isinstance(response.body, str):
            compressed = gzip.compress(response.body.encode())
        elif isinstance(response.body, dict):
            import json
            body_str = json.dumps(response.body)
            compressed = gzip.compress(body_str.encode())
        else:
            return response
        
        response.body = compressed
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Type"] = "application/json"
        
        return response