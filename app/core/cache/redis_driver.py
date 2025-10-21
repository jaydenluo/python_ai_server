"""
Redis缓存驱动
提供高性能的Redis缓存支持，包括连接池、错误处理、重试机制等
"""

import time
import logging
from typing import Any, Dict, Optional, List, Union, Callable
from contextlib import contextmanager
import json
import pickle
import hashlib
from datetime import datetime, timedelta

try:
    import redis
    from redis.connection import ConnectionPool
    from redis.exceptions import RedisError, ConnectionError, TimeoutError
except ImportError:
    redis = None
    ConnectionPool = None
    RedisError = Exception
    ConnectionError = Exception
    TimeoutError = Exception


class RedisConfig:
    """Redis配置类"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 max_connections: int = 20,
                 retry_on_timeout: bool = True,
                 socket_timeout: int = 5,
                 socket_connect_timeout: int = 5,
                 health_check_interval: int = 30):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.retry_on_timeout = retry_on_timeout
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.health_check_interval = health_check_interval


class RedisCache:
    """增强的Redis缓存驱动"""
    
    def __init__(self, config: RedisConfig):
        if redis is None:
            raise ImportError("Redis driver not installed. Install with: pip install redis")
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._connection_pool = None
        self._redis_client = None
        self._last_health_check = 0
        self._stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'operations': 0
        }
        
        self._init_connection()
    
    def _init_connection(self):
        """初始化连接"""
        try:
            # 创建连接池
            self._connection_pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                health_check_interval=self.config.health_check_interval
            )
            
            # 创建Redis客户端
            self._redis_client = redis.Redis(
                connection_pool=self._connection_pool,
                decode_responses=False
            )
            
            # 测试连接
            self._redis_client.ping()
            self.logger.info(f"Redis connection established: {self.config.host}:{self.config.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def _check_health(self) -> bool:
        """检查连接健康状态"""
        current_time = time.time()
        if current_time - self._last_health_check < self.config.health_check_interval:
            return True
        
        try:
            self._redis_client.ping()
            self._last_health_check = current_time
            return True
        except Exception as e:
            self.logger.warning(f"Redis health check failed: {e}")
            return False
    
    def _retry_on_failure(self, func: Callable, *args, **kwargs) -> Any:
        """失败重试机制"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                if not self._check_health():
                    self._init_connection()
                
                result = func(*args, **kwargs)
                self._stats['operations'] += 1
                return result
                
            except (ConnectionError, TimeoutError) as e:
                self._stats['errors'] += 1
                self.logger.warning(f"Redis operation failed (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    raise e
            except RedisError as e:
                self._stats['errors'] += 1
                self.logger.error(f"Redis error: {e}")
                raise e
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            result = self._retry_on_failure(self._redis_client.get, key)
            
            if result is None:
                self._stats['misses'] += 1
                return None
            
            # 反序列化数据
            data = pickle.loads(result)
            self._stats['hits'] += 1
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get cache key '{key}': {e}")
            self._stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            # 序列化数据
            data = pickle.dumps(value)
            
            if ttl:
                result = self._retry_on_failure(self._redis_client.setex, key, ttl, data)
            else:
                result = self._retry_on_failure(self._redis_client.set, key, data)
            
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to set cache key '{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            result = self._retry_on_failure(self._redis_client.delete, key)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to delete cache key '{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            result = self._retry_on_failure(self._redis_client.exists, key)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to check cache key '{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            result = self._retry_on_failure(self._redis_client.flushdb)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            self._stats['errors'] += 1
            return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        """获取缓存键列表"""
        try:
            result = self._retry_on_failure(self._redis_client.keys, pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in result]
            
        except Exception as e:
            self.logger.error(f"Failed to get cache keys: {e}")
            self._stats['errors'] += 1
            return []
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间"""
        try:
            result = self._retry_on_failure(self._redis_client.expire, key, ttl)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to set expiry for key '{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        try:
            result = self._retry_on_failure(self._redis_client.ttl, key)
            return result if result >= 0 else -1
            
        except Exception as e:
            self.logger.error(f"Failed to get TTL for key '{key}': {e}")
            self._stats['errors'] += 1
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """递增计数器"""
        try:
            result = self._retry_on_failure(self._redis_client.incrby, key, amount)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to increment key '{key}': {e}")
            self._stats['errors'] += 1
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """递减计数器"""
        try:
            result = self._retry_on_failure(self._redis_client.decrby, key, amount)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to decrement key '{key}': {e}")
            self._stats['errors'] += 1
            return None
    
    def hash_set(self, name: str, key: str, value: Any) -> bool:
        """设置哈希字段"""
        try:
            data = pickle.dumps(value)
            result = self._retry_on_failure(self._redis_client.hset, name, key, data)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to set hash field '{name}.{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def hash_get(self, name: str, key: str) -> Optional[Any]:
        """获取哈希字段"""
        try:
            result = self._retry_on_failure(self._redis_client.hget, name, key)
            
            if result is None:
                self._stats['misses'] += 1
                return None
            
            data = pickle.loads(result)
            self._stats['hits'] += 1
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get hash field '{name}.{key}': {e}")
            self._stats['errors'] += 1
            return None
    
    def hash_delete(self, name: str, key: str) -> bool:
        """删除哈希字段"""
        try:
            result = self._retry_on_failure(self._redis_client.hdel, name, key)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to delete hash field '{name}.{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def list_push(self, key: str, value: Any) -> bool:
        """推入列表"""
        try:
            data = pickle.dumps(value)
            result = self._retry_on_failure(self._redis_client.lpush, key, data)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to push to list '{key}': {e}")
            self._stats['errors'] += 1
            return False
    
    def list_pop(self, key: str) -> Optional[Any]:
        """弹出列表元素"""
        try:
            result = self._retry_on_failure(self._redis_client.rpop, key)
            
            if result is None:
                self._stats['misses'] += 1
                return None
            
            data = pickle.loads(result)
            self._stats['hits'] += 1
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to pop from list '{key}': {e}")
            self._stats['errors'] += 1
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_operations = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'driver': 'redis',
            'host': f"{self.config.host}:{self.config.port}",
            'db': self.config.db,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'errors': self._stats['errors'],
            'operations': self._stats['operations'],
            'hit_rate': round(hit_rate, 2),
            'keys_count': len(self.keys()),
            'connection_pool_size': self.config.max_connections
        }
    
    def close(self):
        """关闭连接"""
        if self._connection_pool:
            self._connection_pool.disconnect()
            self.logger.info("Redis connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 全局Redis配置
redis_config = RedisConfig(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    max_connections=20,
    retry_on_timeout=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    health_check_interval=30
)


def create_redis_cache(config: Optional[RedisConfig] = None) -> RedisCache:
    """创建Redis缓存实例"""
    return RedisCache(config or redis_config)