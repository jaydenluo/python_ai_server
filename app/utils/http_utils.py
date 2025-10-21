"""
网络请求工具
提供HTTP请求、API响应、分页等功能
"""

import requests
import json
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlencode, urlparse, parse_qs
import time
import hashlib


def make_http_request(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
                     data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None,
                     timeout: int = 30, **kwargs) -> Dict[str, Any]:
    """
    发送HTTP请求
    
    Args:
        url: 请求URL
        method: 请求方法
        headers: 请求头
        data: 表单数据
        json_data: JSON数据
        timeout: 超时时间
        **kwargs: 其他requests参数
        
    Returns:
        Dict: 响应结果
    """
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=data,
            json=json_data,
            timeout=timeout,
            **kwargs
        )
        
        # 尝试解析JSON响应
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = response.text
        
        return {
            'success': response.status_code < 400,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response_data,
            'url': response.url,
            'elapsed': response.elapsed.total_seconds()
        }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timeout',
            'status_code': 0
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Connection error',
            'status_code': 0
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': 0
        }


def download_file(url: str, save_path: str, chunk_size: int = 8192, 
                 headers: Optional[Dict[str, str]] = None) -> bool:
    """
    下载文件
    
    Args:
        url: 文件URL
        save_path: 保存路径
        chunk_size: 块大小
        headers: 请求头
        
    Returns:
        bool: 是否下载成功
    """
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        
        return True
    except Exception:
        return False


def get_client_ip(request_headers: Dict[str, str]) -> str:
    """
    获取客户端IP地址
    
    Args:
        request_headers: 请求头字典
        
    Returns:
        str: 客户端IP地址
    """
    # 检查常见的代理头
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Client-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP'
    ]
    
    for header in ip_headers:
        ip = request_headers.get(header)
        if ip:
            # X-Forwarded-For 可能包含多个IP，取第一个
            return ip.split(',')[0].strip()
    
    # 默认返回远程地址
    return request_headers.get('REMOTE_ADDR', '127.0.0.1')


def get_user_agent(request_headers: Dict[str, str]) -> str:
    """
    获取用户代理字符串
    
    Args:
        request_headers: 请求头字典
        
    Returns:
        str: 用户代理字符串
    """
    return request_headers.get('User-Agent', '')


def build_api_response(data: Any = None, message: str = "success", 
                      code: int = 200, success: bool = True) -> Dict[str, Any]:
    """
    构建API响应格式
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 响应代码
        success: 是否成功
        
    Returns:
        Dict: 标准化的API响应
    """
    response = {
        'success': success,
        'code': code,
        'message': message,
        'timestamp': int(time.time())
    }
    
    if data is not None:
        response['data'] = data
    
    return response


def build_error_response(message: str, code: int = 400, error_code: Optional[str] = None) -> Dict[str, Any]:
    """
    构建错误响应
    
    Args:
        message: 错误消息
        code: HTTP状态码
        error_code: 业务错误码
        
    Returns:
        Dict: 错误响应
    """
    response = build_api_response(
        message=message,
        code=code,
        success=False
    )
    
    if error_code:
        response['error_code'] = error_code
    
    return response


def paginate_data(data: List[Any], page: int, per_page: int) -> Dict[str, Any]:
    """
    数据分页
    
    Args:
        data: 原始数据列表
        page: 页码（从1开始）
        per_page: 每页数量
        
    Returns:
        Dict: 分页结果
    """
    total = len(data)
    total_pages = (total + per_page - 1) // per_page
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    page_data = data[start_index:end_index]
    
    return {
        'data': page_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


def parse_query_params(query_string: str) -> Dict[str, Any]:
    """
    解析查询参数
    
    Args:
        query_string: 查询字符串
        
    Returns:
        Dict: 解析后的参数字典
    """
    if not query_string:
        return {}
    
    # 移除开头的?
    if query_string.startswith('?'):
        query_string = query_string[1:]
    
    params = parse_qs(query_string)
    
    # 简化单值参数
    result = {}
    for key, values in params.items():
        if len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = values
    
    return result


def build_query_string(params: Dict[str, Any]) -> str:
    """
    构建查询字符串
    
    Args:
        params: 参数字典
        
    Returns:
        str: 查询字符串
    """
    return urlencode(params)


def validate_url_format(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        bool: 是否为有效URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> Optional[str]:
    """
    从URL中提取域名
    
    Args:
        url: URL字符串
        
    Returns:
        str: 域名，失败返回None
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def is_same_origin(url1: str, url2: str) -> bool:
    """
    检查两个URL是否同源
    
    Args:
        url1: 第一个URL
        url2: 第二个URL
        
    Returns:
        bool: 是否同源
    """
    try:
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        return (parsed1.scheme == parsed2.scheme and
                parsed1.netloc == parsed2.netloc and
                parsed1.port == parsed2.port)
    except Exception:
        return False


def generate_request_id() -> str:
    """
    生成请求ID
    
    Returns:
        str: 唯一的请求ID
    """
    timestamp = str(int(time.time() * 1000))
    random_str = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"req_{timestamp}_{random_str}"


def rate_limit_key(identifier: str, window: str = "1h") -> str:
    """
    生成限流键
    
    Args:
        identifier: 标识符（如IP、用户ID）
        window: 时间窗口
        
    Returns:
        str: 限流键
    """
    current_time = int(time.time())
    
    if window == "1m":
        window_start = current_time // 60 * 60
    elif window == "1h":
        window_start = current_time // 3600 * 3600
    elif window == "1d":
        window_start = current_time // 86400 * 86400
    else:
        window_start = current_time // 3600 * 3600  # 默认1小时
    
    return f"rate_limit:{identifier}:{window_start}"


def parse_accept_header(accept_header: str) -> List[Dict[str, Union[str, float]]]:
    """
    解析Accept头
    
    Args:
        accept_header: Accept头值
        
    Returns:
        List: 解析后的媒体类型列表，按优先级排序
    """
    if not accept_header:
        return []
    
    media_types = []
    
    for item in accept_header.split(','):
        item = item.strip()
        
        # 分离媒体类型和参数
        parts = item.split(';')
        media_type = parts[0].strip()
        
        # 解析质量值
        quality = 1.0
        for param in parts[1:]:
            param = param.strip()
            if param.startswith('q='):
                try:
                    quality = float(param[2:])
                except ValueError:
                    quality = 1.0
                break
        
        media_types.append({
            'type': media_type,
            'quality': quality
        })
    
    # 按质量值降序排序
    media_types.sort(key=lambda x: x['quality'], reverse=True)
    
    return media_types


def build_cors_headers(origin: Optional[str] = None, methods: Optional[List[str]] = None,
                      headers: Optional[List[str]] = None, credentials: bool = False) -> Dict[str, str]:
    """
    构建CORS响应头
    
    Args:
        origin: 允许的源
        methods: 允许的方法
        headers: 允许的头
        credentials: 是否允许凭证
        
    Returns:
        Dict: CORS头字典
    """
    cors_headers = {}
    
    if origin:
        cors_headers['Access-Control-Allow-Origin'] = origin
    else:
        cors_headers['Access-Control-Allow-Origin'] = '*'
    
    if methods:
        cors_headers['Access-Control-Allow-Methods'] = ', '.join(methods)
    
    if headers:
        cors_headers['Access-Control-Allow-Headers'] = ', '.join(headers)
    
    if credentials:
        cors_headers['Access-Control-Allow-Credentials'] = 'true'
    
    return cors_headers


def compress_response_data(data: str, method: str = 'gzip') -> bytes:
    """
    压缩响应数据
    
    Args:
        data: 要压缩的数据
        method: 压缩方法
        
    Returns:
        bytes: 压缩后的数据
    """
    import gzip
    import zlib
    
    if method == 'gzip':
        return gzip.compress(data.encode('utf-8'))
    elif method == 'deflate':
        return zlib.compress(data.encode('utf-8'))
    else:
        return data.encode('utf-8')