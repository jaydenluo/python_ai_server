"""
缓存管理器
提供统一的缓存接口和多种缓存驱动
"""

from typing import Any, Dict, Optional, Union, Callable, List
from abc import ABC, abstractmethod
import json
import pickle
import hashlib
import time
from datetime import datetime, timedelta
import threading
from pathlib import Path


class CacheDriver(ABC):
    """缓存驱动基类"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """获取缓存键列表"""
        pass


class MemoryCache(CacheDriver):
    """内存缓存驱动"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # 检查是否过期
            if item['expires_at'] and datetime.now() > item['expires_at']:
                del self._cache[key]
                return None
            
            return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            
            return True
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        with self._lock:
            if key not in self._cache:
                return False
            
            item = self._cache[key]
            
            # 检查是否过期
            if item['expires_at'] and datetime.now() > item['expires_at']:
                del self._cache[key]
                return False
            
            return True
    
    def clear(self) -> bool:
        with self._lock:
            self._cache.clear()
            return True
    
    def keys(self, pattern: str = "*") -> List[str]:
        with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            
            # 简单的模式匹配
            import fnmatch
            return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_items = len(self._cache)
            expired_items = 0
            
            for item in self._cache.values():
                if item['expires_at'] and datetime.now() > item['expires_at']:
                    expired_items += 1
            
            return {
                'total_items': total_items,
                'expired_items': expired_items,
                'active_items': total_items - expired_items
            }


class FileCache(CacheDriver):
    """文件缓存驱动"""
    
    def __init__(self, cache_dir: Union[str, Path] = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用哈希避免文件名冲突
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 检查是否过期
            if data.get('expires_at') and datetime.now() > data['expires_at']:
                file_path.unlink()
                return None
            
            return data['value']
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        file_path = self._get_file_path(key)
        
        try:
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            data = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        file_path = self._get_file_path(key)
        
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        
        return False
    
    def exists(self, key: str) -> bool:
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 检查是否过期
            if data.get('expires_at') and datetime.now() > data['expires_at']:
                file_path.unlink()
                return False
            
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        try:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()
            return True
        except Exception:
            return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        # 文件缓存无法直接获取键列表
        return []


class RedisCache(CacheDriver):
    """Redis缓存驱动"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        try:
            import redis
            self.redis = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=False)
            self.redis.ping()  # 测试连接
        except ImportError:
            raise ImportError("Redis driver not installed. Install with: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis.get(key)
            if data is None:
                return None
            
            return pickle.loads(data)
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            data = pickle.dumps(value)
            if ttl:
                return self.redis.setex(key, ttl, data)
            else:
                return self.redis.set(key, data)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        try:
            return bool(self.redis.exists(key))
        except Exception:
            return False
    
    def clear(self) -> bool:
        try:
            return self.redis.flushdb()
        except Exception:
            return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        try:
            return [key.decode() for key in self.redis.keys(pattern)]
        except Exception:
            return []


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, default_driver: str = "memory"):
        self._drivers: Dict[str, CacheDriver] = {}
        self._default_driver = default_driver
        self._prefix = ""
        self._serializer = "pickle"  # json, pickle
    
    def add_driver(self, name: str, driver: CacheDriver) -> 'CacheManager':
        """添加缓存驱动"""
        self._drivers[name] = driver
        return self
    
    def set_default_driver(self, name: str) -> 'CacheManager':
        """设置默认驱动"""
        if name not in self._drivers:
            raise ValueError(f"Driver '{name}' not found")
        self._default_driver = name
        return self
    
    def set_prefix(self, prefix: str) -> 'CacheManager':
        """设置缓存前缀"""
        self._prefix = prefix
        return self
    
    def set_serializer(self, serializer: str) -> 'CacheManager':
        """设置序列化器"""
        if serializer not in ['json', 'pickle']:
            raise ValueError("Serializer must be 'json' or 'pickle'")
        self._serializer = serializer
        return self
    
    def _get_driver(self, driver: Optional[str] = None) -> CacheDriver:
        """获取缓存驱动"""
        driver_name = driver or self._default_driver
        if driver_name not in self._drivers:
            raise ValueError(f"Driver '{driver_name}' not found")
        return self._drivers[driver_name]
    
    def _make_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self._prefix}{key}" if self._prefix else key
    
    def get(self, key: str, default: Any = None, driver: Optional[str] = None) -> Any:
        """获取缓存"""
        cache_key = self._make_key(key)
        cache_driver = self._get_driver(driver)
        
        value = cache_driver.get(cache_key)
        return value if value is not None else default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, driver: Optional[str] = None) -> bool:
        """设置缓存"""
        cache_key = self._make_key(key)
        cache_driver = self._get_driver(driver)
        
        return cache_driver.set(cache_key, value, ttl)
    
    def delete(self, key: str, driver: Optional[str] = None) -> bool:
        """删除缓存"""
        cache_key = self._make_key(key)
        cache_driver = self._get_driver(driver)
        
        return cache_driver.delete(cache_key)
    
    def exists(self, key: str, driver: Optional[str] = None) -> bool:
        """检查缓存是否存在"""
        cache_key = self._make_key(key)
        cache_driver = self._get_driver(driver)
        
        return cache_driver.exists(cache_key)
    
    def clear(self, driver: Optional[str] = None) -> bool:
        """清空缓存"""
        cache_driver = self._get_driver(driver)
        return cache_driver.clear()
    
    def keys(self, pattern: str = "*", driver: Optional[str] = None) -> List[str]:
        """获取缓存键列表"""
        cache_driver = self._get_driver(driver)
        keys = cache_driver.keys(pattern)
        
        # 移除前缀
        if self._prefix:
            prefix_len = len(self._prefix)
            keys = [key[prefix_len:] for key in keys if key.startswith(self._prefix)]
        
        return keys
    
    def remember(self, key: str, callback: Callable, ttl: Optional[int] = None, driver: Optional[str] = None) -> Any:
        """记住缓存（如果不存在则执行回调）"""
        value = self.get(key, driver=driver)
        if value is not None:
            return value
        
        value = callback()
        self.set(key, value, ttl, driver)
        return value
    
    def forget(self, key: str, driver: Optional[str] = None) -> bool:
        """忘记缓存（删除）"""
        return self.delete(key, driver)
    
    def flush(self, driver: Optional[str] = None) -> bool:
        """刷新缓存（清空）"""
        return self.clear(driver)
    
    def get_stats(self, driver: Optional[str] = None) -> Dict[str, Any]:
        """获取缓存统计信息"""
        cache_driver = self._get_driver(driver)
        
        if hasattr(cache_driver, 'get_stats'):
            return cache_driver.get_stats()
        
        return {
            'driver': driver or self._default_driver,
            'keys_count': len(self.keys(driver=driver))
        }


# 全局缓存管理器实例
cache = CacheManager()

# 添加默认驱动
cache.add_driver("memory", MemoryCache())
cache.add_driver("file", FileCache())