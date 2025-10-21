"""
缓存工具
提供缓存操作、装饰器等功能
"""

import json
import time
import hashlib
import functools
from typing import Any, Optional, Callable, Dict, List
import redis
from datetime import datetime, timedelta


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        初始化缓存管理器
        
        Args:
            redis_client: Redis客户端，None时使用内存缓存
        """
        self.redis_client = redis_client
        self.memory_cache = {}  # 内存缓存
        self.memory_expire = {}  # 内存缓存过期时间
    
    def get(self, key: str) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存值，不存在返回None
        """
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value.decode('utf-8'))
            except Exception:
                pass
        else:
            # 使用内存缓存
            if key in self.memory_cache:
                # 检查是否过期
                if key in self.memory_expire:
                    if time.time() > self.memory_expire[key]:
                        del self.memory_cache[key]
                        del self.memory_expire[key]
                        return None
                
                return self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            if self.redis_client:
                json_value = json.dumps(value, default=str)
                return self.redis_client.setex(key, expire, json_value)
            else:
                # 使用内存缓存
                self.memory_cache[key] = value
                if expire > 0:
                    self.memory_expire[key] = time.time() + expire
                return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                # 使用内存缓存
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.memory_expire:
                    del self.memory_expire[key]
                return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception:
                return False
        else:
            return key in self.memory_cache
    
    def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的缓存
        
        Args:
            pattern: 匹配模式
            
        Returns:
            int: 删除的键数量
        """
        count = 0
        
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            except Exception:
                pass
        else:
            # 内存缓存简单匹配
            import fnmatch
            keys_to_delete = []
            
            for key in self.memory_cache.keys():
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.delete(key)
                count += 1
        
        return count
    
    def get_ttl(self, key: str) -> int:
        """
        获取缓存剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余秒数，-1表示永不过期，-2表示不存在
        """
        if self.redis_client:
            try:
                return self.redis_client.ttl(key)
            except Exception:
                return -2
        else:
            if key not in self.memory_cache:
                return -2
            
            if key not in self.memory_expire:
                return -1
            
            remaining = self.memory_expire[key] - time.time()
            return int(remaining) if remaining > 0 else -2
    
    def increment(self, key: str, amount: int = 1) -> int:
        """
        递增缓存值
        
        Args:
            key: 缓存键
            amount: 递增量
            
        Returns:
            int: 递增后的值
        """
        if self.redis_client:
            try:
                return self.redis_client.incr(key, amount)
            except Exception:
                return 0
        else:
            current = self.get(key) or 0
            new_value = int(current) + amount
            self.set(key, new_value)
            return new_value


# 全局缓存管理器实例
cache_manager = CacheManager()


def cache_get(key: str) -> Any:
    """获取缓存值的便捷函数"""
    return cache_manager.get(key)


def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """设置缓存值的便捷函数"""
    return cache_manager.set(key, value, expire)


def cache_delete(key: str) -> bool:
    """删除缓存的便捷函数"""
    return cache_manager.delete(key)


def cache_clear_pattern(pattern: str) -> int:
    """清除匹配模式缓存的便捷函数"""
    return cache_manager.clear_pattern(pattern)


def generate_cache_key(*args, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        str: 缓存键
    """
    # 将参数转换为字符串
    key_parts = []
    
    for arg in args:
        key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    key_string = "|".join(key_parts)
    
    # 生成MD5哈希
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()


def cache_result(expire: int = 3600, key_prefix: str = ""):
    """
    缓存函数结果的装饰器
    
    Args:
        expire: 过期时间（秒）
        key_prefix: 键前缀
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            func_name = func.__name__
            cache_key = f"{key_prefix}{func_name}:{generate_cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_result = cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_set(cache_key, result, expire)
            
            return result
        
        return wrapper
    return decorator


def cache_with_lock(expire: int = 3600, lock_timeout: int = 10):
    """
    带锁的缓存装饰器，防止缓存击穿
    
    Args:
        expire: 缓存过期时间
        lock_timeout: 锁超时时间
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            cache_key = f"cache:{func_name}:{generate_cache_key(*args, **kwargs)}"
            lock_key = f"lock:{cache_key}"
            
            # 尝试从缓存获取
            cached_result = cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 尝试获取锁
            if cache_manager.redis_client:
                try:
                    # 使用Redis分布式锁
                    lock_acquired = cache_manager.redis_client.set(
                        lock_key, "1", nx=True, ex=lock_timeout
                    )
                    
                    if not lock_acquired:
                        # 等待一段时间后重试
                        time.sleep(0.1)
                        cached_result = cache_get(cache_key)
                        if cached_result is not None:
                            return cached_result
                    
                    try:
                        # 执行函数并缓存结果
                        result = func(*args, **kwargs)
                        cache_set(cache_key, result, expire)
                        return result
                    finally:
                        # 释放锁
                        cache_manager.redis_client.delete(lock_key)
                        
                except Exception:
                    # Redis异常时直接执行函数
                    return func(*args, **kwargs)
            else:
                # 内存缓存简单实现
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


class CacheStats:
    """缓存统计"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
    
    def record_hit(self):
        """记录缓存命中"""
        self.hits += 1
    
    def record_miss(self):
        """记录缓存未命中"""
        self.misses += 1
    
    def record_set(self):
        """记录缓存设置"""
        self.sets += 1
    
    def record_delete(self):
        """记录缓存删除"""
        self.deletes += 1
    
    def get_hit_rate(self) -> float:
        """获取命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'hit_rate': self.get_hit_rate(),
            'total_operations': self.hits + self.misses + self.sets + self.deletes
        }
    
    def reset(self):
        """重置统计"""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0


# 全局缓存统计实例
cache_stats = CacheStats()


def warm_up_cache(data_loader: Callable, cache_keys: List[str], 
                 expire: int = 3600) -> Dict[str, bool]:
    """
    缓存预热
    
    Args:
        data_loader: 数据加载函数
        cache_keys: 缓存键列表
        expire: 过期时间
        
    Returns:
        Dict: 预热结果
    """
    results = {}
    
    for key in cache_keys:
        try:
            data = data_loader(key)
            success = cache_set(key, data, expire)
            results[key] = success
        except Exception:
            results[key] = False
    
    return results


def cache_aside_pattern(key: str, data_loader: Callable, 
                       expire: int = 3600) -> Any:
    """
    Cache-Aside模式
    
    Args:
        key: 缓存键
        data_loader: 数据加载函数
        expire: 过期时间
        
    Returns:
        Any: 数据
    """
    # 先从缓存获取
    data = cache_get(key)
    
    if data is None:
        # 缓存未命中，从数据源加载
        data = data_loader()
        
        # 写入缓存
        cache_set(key, data, expire)
        cache_stats.record_miss()
    else:
        cache_stats.record_hit()
    
    return data


def invalidate_related_cache(pattern: str) -> int:
    """
    失效相关缓存
    
    Args:
        pattern: 匹配模式
        
    Returns:
        int: 失效的缓存数量
    """
    return cache_clear_pattern(pattern)