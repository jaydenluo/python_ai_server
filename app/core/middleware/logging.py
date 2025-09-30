"""
日志中间件
记录请求和响应日志
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime
from .base import Middleware, Request, Response


class LoggingMiddleware(Middleware):
    """日志中间件"""
    
    def __init__(self, logger_name: str = "framework", log_level: str = "INFO", **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(logger_name)
        self.log_level = getattr(logging, log_level.upper())
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理日志记录"""
        start_time = time.time()
        
        # 记录请求信息
        self.logger.log(
            self.log_level,
            f"Request: {request.method} {request.path}",
            extra={
                "request_id": self._generate_request_id(),
                "method": request.method,
                "path": request.path,
                "headers": request.headers,
                "query_params": request.query_params,
                "user": request.user.get("username") if request.user else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        try:
            # 处理请求
            response = await next_handler()
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            self.logger.log(
                self.log_level,
                f"Response: {response.status_code} - {process_time:.3f}s",
                extra={
                    "request_id": getattr(request, "request_id", None),
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "response_size": len(str(response.body)) if response.body else 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return response
            
        except Exception as e:
            # 记录错误信息
            process_time = time.time() - start_time
            
            self.logger.error(
                f"Error: {str(e)} - {process_time:.3f}s",
                extra={
                    "request_id": getattr(request, "request_id", None),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": process_time,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exc_info=True
            )
            
            # 返回错误响应
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                body={"error": "Internal server error"}
            )
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4())


class AccessLogMiddleware(Middleware):
    """访问日志中间件"""
    
    def __init__(self, log_file: str = None, **kwargs):
        super().__init__(**kwargs)
        self.log_file = log_file
        
        # 配置访问日志记录器
        self.access_logger = logging.getLogger("access")
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(remote_addr)s - %(method)s %(path)s - %(status_code)s - %(process_time)s'
            )
            handler.setFormatter(formatter)
            self.access_logger.addHandler(handler)
    
    async def handle(self, request: Request, next_handler) -> Response:
        """记录访问日志"""
        start_time = time.time()
        
        # 处理请求
        response = await next_handler()
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录访问日志
        self.access_logger.info(
            f"{request.method} {request.path}",
            extra={
                "remote_addr": request.headers.get("X-Forwarded-For", "127.0.0.1"),
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
                "user_agent": request.headers.get("User-Agent", ""),
                "user": request.user.get("username") if request.user else None
            }
        )
        
        return response


class PerformanceMiddleware(Middleware):
    """性能监控中间件"""
    
    def __init__(self, slow_request_threshold: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.slow_request_threshold = slow_request_threshold
        self.performance_logger = logging.getLogger("performance")
    
    async def handle(self, request: Request, next_handler) -> Response:
        """监控性能"""
        start_time = time.time()
        
        # 处理请求
        response = await next_handler()
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录性能信息
        if process_time > self.slow_request_threshold:
            self.performance_logger.warning(
                f"Slow request detected: {request.method} {request.path} - {process_time:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "process_time": process_time,
                    "threshold": self.slow_request_threshold,
                    "user": request.user.get("username") if request.user else None
                }
            )
        
        return response