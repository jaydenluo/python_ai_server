"""
API控制器基类
提供类似Laravel的优雅控制器设计
包含常用的导入和装饰器，简化控制器开发
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from app.core.models.base import BaseModel
from app.core.middleware.base import Request, Response

# 导入常用的路由装饰器，供子类使用
from app.core.routing.route_decorators import (
    api_controller, get, post, put, delete, patch,
    rate_limit, cache, validate, api_doc, cors,
    # 中间件装饰器
    anonymous, auth, admin, middleware,
    # 简化的文档装饰器
    doc, title, desc, get_list, get_detail, 
    create_resource, update_resource, delete_resource,
    # 权限装饰器
    requires,
    # 自动扫描功能
    auto_discover_controllers, get_all_controllers,
    # 路由组和资源路由
    route_group, api_resource
)


class HTTPStatus(Enum):
    """HTTP状态码枚举"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


@dataclass
class APIResponse:
    """API响应数据类"""
    success: bool
    data: Any = None
    message: str = ""
    errors: List[str] = None
    meta: Dict[str, Any] = None
    status_code: int = 200
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.errors is None:
            self.errors = []
        if self.meta is None:
            self.meta = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "status_code": self.status_code
        }
        
        if self.data is not None:
            result["data"] = self.data
        
        if self.errors:
            result["errors"] = self.errors
        
        if self.meta:
            result["meta"] = self.meta
        
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)


T = TypeVar('T', bound=BaseModel)


class BaseController(ABC):
    """控制器基类"""
    
    def __init__(self, model: Type[T] = None):
        self.model = model
    
    def success_response(self, data: Any = None, message: str = "操作成功", 
                        status_code: int = 200, meta: Dict[str, Any] = None) -> APIResponse:
        """成功响应"""
        return APIResponse(
            success=True,
            data=data,
            message=message,
            status_code=status_code,
            meta=meta or {}
        )
    
    def error_response(self, message: str = "操作失败", errors: List[str] = None,
                      status_code: int = 400, data: Any = None) -> APIResponse:
        """错误响应"""
        return APIResponse(
            success=False,
            data=data,
            message=message,
            errors=errors or [],
            status_code=status_code
        )
    
    def not_found_response(self, message: str = "资源未找到") -> APIResponse:
        """未找到响应"""
        return self.error_response(
            message=message,
            status_code=HTTPStatus.NOT_FOUND.value
        )
    
    def validation_error_response(self, errors: List[str]) -> APIResponse:
        """验证错误响应"""
        return self.error_response(
            message="数据验证失败",
            errors=errors,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value
        )
    
    def unauthorized_response(self, message: str = "未授权访问") -> APIResponse:
        """未授权响应"""
        return self.error_response(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED.value
        )
    
    def forbidden_response(self, message: str = "禁止访问") -> APIResponse:
        """禁止访问响应"""
        return self.error_response(
            message=message,
            status_code=HTTPStatus.FORBIDDEN.value
        )
    
    def server_error_response(self, message: str = "服务器内部错误") -> APIResponse:
        """服务器错误响应"""
        return self.error_response(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value
        )
    
    def paginated_response(self, data: List[Any], page: int, per_page: int, 
                         total: int, message: str = "获取成功") -> APIResponse:
        """分页响应"""
        meta = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1
            }
        }
        
        return self.success_response(
            data=data,
            message=message,
            meta=meta
        )
    
    def _create_response(self, api_response: APIResponse) -> Response:
        """创建HTTP响应"""
        return Response(
            status_code=api_response.status_code,
            headers={"Content-Type": "application/json"},
            body=api_response.to_dict()
        )


class ResourceController(BaseController):
    """资源控制器"""
    
    def __init__(self, model: Type[T]):
        super().__init__(model)
        self.resource_name = model.__name__.lower()
        self.resource_name_plural = f"{self.resource_name}s"
    
    def _validate_data(self, data: Dict[str, Any], action: str) -> List[str]:
        """验证数据"""
        errors = []
        
        # 这里应该根据模型定义进行验证
        # 为了示例，我们进行基本验证
        if action == "create":
            if not data:
                errors.append("请求数据不能为空")
        
        return errors


# 导出所有常用的类和装饰器，方便子类一次性导入
__all__ = [
    # 基础类
    'BaseController', 
    'ResourceController', 
    'APIResponse', 
    'HTTPStatus',
    'Request', 
    'Response',
    
    # 路由装饰器
    'api_controller', 
    'get', 
    'post', 
    'put', 
    'delete', 
    'patch',
    
    # 中间件装饰器
    'rate_limit', 
    'cache', 
    'validate', 
    'api_doc', 
    'cors',
    'middleware',
    
    # 认证和权限装饰器
    'anonymous',
    'auth', 
    'admin',
    
    # 简化的文档装饰器
    'doc',
    'title', 
    'desc',
    'get_list',
    'get_detail',
    'create_resource',
    'update_resource',
    'delete_resource',
    
    # 权限装饰器
    'requires',
    
    # 自动扫描功能
    'auto_discover_controllers',
    'get_all_controllers',
    
    # 路由组和资源路由
    'route_group',
    'api_resource'
]