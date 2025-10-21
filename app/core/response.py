"""
响应处理模块
提供统一的API响应格式
"""
from typing import Any, Dict, Optional


def success_response(data: Any = None, msg: str = "操作成功", code: int = 2000) -> Dict[str, Any]:
    """
    成功响应
    
    Args:
        data: 响应数据
        msg: 响应消息
        code: 响应码
        
    Returns:
        标准响应格式
    """
    response = {
        "code": code,
        "msg": msg
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def error_response(msg: str = "操作失败", code: int = 4000, data: Any = None) -> Dict[str, Any]:
    """
    错误响应
    
    Args:
        msg: 错误消息
        code: 错误码
        data: 错误数据
        
    Returns:
        标准错误响应格式
    """
    response = {
        "code": code,
        "msg": msg
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def pagination_response(data: list, total: int, page: int, limit: int, 
                      msg: str = "获取成功", code: int = 2000) -> Dict[str, Any]:
    """
    分页响应
    
    Args:
        data: 数据列表
        total: 总数量
        page: 当前页
        limit: 每页数量
        msg: 响应消息
        code: 响应码
        
    Returns:
        分页响应格式
    """
    return {
        "code": code,
        "msg": msg,
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    }