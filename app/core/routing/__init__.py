"""
路由模块
提供注解路由和路由管理功能
"""

from .route_decorators import (
    get, post, put, patch, delete, options, head,
    controller, route, HTTPMethod, RouteInfo
)
from .route_registry import FastAPIRouteRegistry as RouteRegistry

__all__ = [
    "get", "post", "put", "patch", "delete", "options", "head",
    "controller", "route", "HTTPMethod", "RouteInfo", "RouteRegistry"
]