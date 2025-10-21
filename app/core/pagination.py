"""
分页处理模块
提供分页查询功能
"""
from typing import List, Dict, Any, Type
from sqlalchemy.orm import Query
from sqlalchemy import func


def paginate(query: Query, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """
    分页查询
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码，从1开始
        limit: 每页数量
        
    Returns:
        包含数据和分页信息的字典
    """
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    data = query.offset(offset).limit(limit).all()
    
    return {
        'data': data,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit  # 总页数
    }


def paginate_with_count(query: Query, page: int = 1, limit: int = 20) -> Dict[str, Any]:
    """
    带计数的分页查询（优化版本）
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码，从1开始
        limit: 每页数量
        
    Returns:
        包含数据和分页信息的字典
    """
    # 使用窗口函数优化计数
    from sqlalchemy import text
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 使用子查询优化
    count_query = query.statement.with_only_columns([func.count()]).order_by(None)
    total = query.session.execute(count_query).scalar()
    
    # 分页查询
    data = query.offset(offset).limit(limit).all()
    
    return {
        'data': data,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit if total > 0 else 0
    }