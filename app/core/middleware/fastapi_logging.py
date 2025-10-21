"""
FastAPI 兼容的日志中间件
"""

import logging
import time
import json
from typing import Dict, Any
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class FastAPILoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI 兼容的日志中间件"""
    
    def __init__(self, app, logger_name: str = "fastapi", log_level: str = "INFO"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
        self.log_level = getattr(logging, log_level.upper())
        
        # 配置日志格式
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(self.log_level)
    
    async def dispatch(self, request: Request, call_next):
        """处理请求并记录日志"""
        start_time = time.time()
        
        # 记录请求信息
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 记录请求体（对于 POST/PUT 请求）
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # 尝试解析 JSON，如果失败则记录原始内容
                    try:
                        request_info["body"] = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_info["body"] = f"<binary data: {len(body)} bytes>"
            except Exception as e:
                request_info["body_error"] = str(e)
        
        # 简单的控制台日志
        print(f"📝 {request.method} {request.url.path} - {request_info['client_ip']}")
        
        self.logger.info(f"Request started: {request.method} {request.url.path}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            response_info = {
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "response_headers": dict(response.headers)
            }
            
            # 简单的控制台日志（成功）
            status_icon = "✅" if response.status_code < 400 else "❌"
            print(f"{status_icon} {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
            
            # 合并请求和响应信息
            log_data = {**request_info, **response_info}
            
            # 根据状态码选择日志级别
            if response.status_code >= 500:
                self.logger.error(f"Request failed: {json.dumps(log_data, ensure_ascii=False)}")
            elif response.status_code >= 400:
                self.logger.warning(f"Request error: {json.dumps(log_data, ensure_ascii=False)}")
            else:
                self.logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            error_info = {
                **request_info,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time": round(process_time, 4)
            }
            
            # 简单的控制台日志（错误）
            print(f"❌ {request.method} {request.url.path} - 异常: {type(e).__name__}: {str(e)}")
            
            self.logger.error(f"Request exception: {json.dumps(error_info, ensure_ascii=False)}")
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端 IP 地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 返回直接连接的 IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"


class RequestLoggingFilter(logging.Filter):
    """请求日志过滤器"""
    
    def __init__(self, exclude_paths: list = None):
        super().__init__()
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
    
    def filter(self, record):
        """过滤不需要记录的路径"""
        if hasattr(record, 'path'):
            for exclude_path in self.exclude_paths:
                if record.path.startswith(exclude_path):
                    return False
        return True