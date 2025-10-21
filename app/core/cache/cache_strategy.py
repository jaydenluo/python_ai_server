"""
缓存策略
提供缓存失效、更新、预热等策略
"""

import time
import hashlib
import threading
from typing import Any, Dict, Optional, List, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import logging


class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    TTL = "ttl"  # 基于时间过期
    WRITE_THROUGH = "write_through"  # 写穿透
    WRITE_BEHIND = "write_behind"  # 写回
    REFRESH_AHEAD = "refresh_ahead"  # 提前刷新


class CacheInvalidationStrategy(Enum):
    """缓存失效策略"""
    TIME_BASED = "time_based"  # 基于时间
    EVENT_BASED = "event_based"  # 基于事件
    TAG_BASED = "tag_based"  # 基于标签
    MANUAL = "manual"  # 手动失效


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: Optional[int] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def touch(self):
        """更新访问时间"""
        self.accessed_at = datetime.now()
        self.access_count += 1


class CacheStrategyManager:
    """缓存策略管理器"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        self._strategies: Dict[str, CacheStrategy] = {}
        self._invalidation_strategies: Dict[str, CacheInvalidationStrategy] = {}
        self._cache_entries: Dict[str, CacheEntry] = {}
        self._tag_index: Dict[str, List[str]] = {}  # 标签到键的映射
        self._lock = threading.RLock()
        
    def set_strategy(self, key: str, strategy: CacheStrategy, **kwargs):
        """设置缓存策略"""
        with self._lock:
            self._strategies[key] = strategy
            
            # 根据策略设置参数
            if strategy == CacheStrategy.TTL:
                ttl = kwargs.get('ttl', 3600)
                self._cache_entries[key] = CacheEntry(
                    key=key,
                    value=None,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    ttl=ttl
                )
    
    def set_invalidation_strategy(self, key: str, strategy: CacheInvalidationStrategy, **kwargs):
        """设置失效策略"""
        with self._lock:
            self._invalidation_strategies[key] = strategy
    
    def get_with_strategy(self, key: str, default: Any = None) -> Any:
        """根据策略获取缓存"""
        with self._lock:
            # 检查缓存条目
            if key in self._cache_entries:
                entry = self._cache_entries[key]
                
                # 检查是否过期
                if entry.is_expired():
                    self._remove_entry(key)
                    return default
                
                # 更新访问信息
                entry.touch()
                
                # 获取实际值
                value = self.cache_manager.get(key)
                if value is not None:
                    return value
            
            return default
    
    def set_with_strategy(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """根据策略设置缓存"""
        with self._lock:
            # 设置缓存
            success = self.cache_manager.set(key, value, ttl)
            
            if success:
                # 创建缓存条目
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    ttl=ttl,
                    tags=tags or []
                )
                
                self._cache_entries[key] = entry
                
                # 更新标签索引
                if tags:
                    for tag in tags:
                        if tag not in self._tag_index:
                            self._tag_index[tag] = []
                        if key not in self._tag_index[tag]:
                            self._tag_index[tag].append(key)
            
            return success
    
    def invalidate_by_tag(self, tag: str) -> int:
        """根据标签失效缓存"""
        with self._lock:
            if tag not in self._tag_index:
                return 0
            
            keys_to_remove = self._tag_index[tag].copy()
            removed_count = 0
            
            for key in keys_to_remove:
                if self._remove_entry(key):
                    removed_count += 1
            
            # 清理标签索引
            del self._tag_index[tag]
            
            return removed_count
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """根据模式失效缓存"""
        with self._lock:
            keys = self.cache_manager.keys(pattern)
            removed_count = 0
            
            for key in keys:
                if self._remove_entry(key):
                    removed_count += 1
            
            return removed_count
    
    def invalidate_expired(self) -> int:
        """失效过期的缓存"""
        with self._lock:
            expired_keys = []
            
            for key, entry in self._cache_entries.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            removed_count = 0
            for key in expired_keys:
                if self._remove_entry(key):
                    removed_count += 1
            
            return removed_count
    
    def warm_up(self, warm_up_data: Dict[str, Any], ttl: Optional[int] = None):
        """缓存预热"""
        with self._lock:
            for key, value in warm_up_data.items():
                self.set_with_strategy(key, value, ttl)
            
            self.logger.info(f"Cache warmed up with {len(warm_up_data)} entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_entries = len(self._cache_entries)
            expired_entries = sum(1 for entry in self._cache_entries.values() if entry.is_expired())
            
            # 计算访问统计
            access_counts = [entry.access_count for entry in self._cache_entries.values()]
            avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'avg_access_count': round(avg_access, 2),
                'tags_count': len(self._tag_index),
                'strategies_count': len(self._strategies)
            }
    
    def _remove_entry(self, key: str) -> bool:
        """移除缓存条目"""
        if key in self._cache_entries:
            entry = self._cache_entries[key]
            
            # 从标签索引中移除
            for tag in entry.tags:
                if tag in self._tag_index and key in self._tag_index[tag]:
                    self._tag_index[tag].remove(key)
                    if not self._tag_index[tag]:
                        del self._tag_index[tag]
            
            # 从缓存中删除
            self.cache_manager.delete(key)
            
            # 从条目中删除
            del self._cache_entries[key]
            
            return True
        
        return False
    
    def cleanup(self):
        """清理过期缓存"""
        with self._lock:
            expired_count = self.invalidate_expired()
            self.logger.info(f"Cleaned up {expired_count} expired cache entries")


class CacheRefreshManager:
    """缓存刷新管理器"""
    
    def __init__(self, cache_manager, strategy_manager):
        self.cache_manager = cache_manager
        self.strategy_manager = strategy_manager
        self.logger = logging.getLogger(__name__)
        self._refresh_tasks: Dict[str, Callable] = {}
        self._refresh_intervals: Dict[str, int] = {}
        self._refresh_threads: Dict[str, threading.Thread] = {}
        self._stop_refresh = False
    
    def add_refresh_task(self, key: str, refresh_func: Callable, interval: int = 300):
        """添加刷新任务"""
        self._refresh_tasks[key] = refresh_func
        self._refresh_intervals[key] = interval
        
        # 启动刷新线程
        if key not in self._refresh_threads:
            thread = threading.Thread(target=self._refresh_worker, args=(key,))
            thread.daemon = True
            thread.start()
            self._refresh_threads[key] = thread
    
    def remove_refresh_task(self, key: str):
        """移除刷新任务"""
        if key in self._refresh_tasks:
            del self._refresh_tasks[key]
            del self._refresh_intervals[key]
    
    def _refresh_worker(self, key: str):
        """刷新工作线程"""
        while not self._stop_refresh and key in self._refresh_tasks:
            try:
                # 执行刷新函数
                refresh_func = self._refresh_tasks[key]
                new_value = refresh_func()
                
                if new_value is not None:
                    # 更新缓存
                    self.strategy_manager.set_with_strategy(key, new_value)
                    self.logger.info(f"Refreshed cache for key: {key}")
                
                # 等待下次刷新
                time.sleep(self._refresh_intervals[key])
                
            except Exception as e:
                self.logger.error(f"Error refreshing cache for key '{key}': {e}")
                time.sleep(60)  # 错误时等待1分钟再重试
    
    def stop_all_refresh(self):
        """停止所有刷新任务"""
        self._stop_refresh = True
        
        # 等待所有线程结束
        for thread in self._refresh_threads.values():
            thread.join(timeout=5)


class CachePenetrationProtection:
    """缓存穿透防护"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        self._null_cache_ttl = 300  # 空值缓存5分钟
        self._request_locks: Dict[str, threading.Lock] = {}
        self._lock = threading.Lock()
    
    def get_with_protection(self, key: str, fetch_func: Callable, ttl: Optional[int] = None) -> Any:
        """带防护的获取缓存"""
        # 尝试从缓存获取
        value = self.cache_manager.get(key)
        
        if value is not None:
            # 检查是否是空值标记
            if value == "__NULL_CACHE__":
                return None
            return value
        
        # 缓存未命中，需要获取锁防止并发请求
        with self._lock:
            if key not in self._request_locks:
                self._request_locks[key] = threading.Lock()
            lock = self._request_locks[key]
        
        with lock:
            # 再次检查缓存（双重检查）
            value = self.cache_manager.get(key)
            if value is not None:
                if value == "__NULL_CACHE__":
                    return None
                return value
            
            try:
                # 执行获取函数
                value = fetch_func()
                
                if value is None:
                    # 缓存空值，防止缓存穿透
                    self.cache_manager.set(key, "__NULL_CACHE__", self._null_cache_ttl)
                    self.logger.info(f"Cached null value for key: {key}")
                else:
                    # 缓存实际值
                    self.cache_manager.set(key, value, ttl)
                    self.logger.info(f"Cached value for key: {key}")
                
                return value
                
            except Exception as e:
                self.logger.error(f"Error fetching value for key '{key}': {e}")
                return None
            finally:
                # 清理锁
                with self._lock:
                    if key in self._request_locks:
                        del self._request_locks[key]


# 全局缓存策略管理器
cache_strategy_manager = None


def init_cache_strategy(cache_manager) -> CacheStrategyManager:
    """初始化缓存策略管理器"""
    global cache_strategy_manager
    cache_strategy_manager = CacheStrategyManager(cache_manager)
    return cache_strategy_manager


def get_cache_strategy() -> CacheStrategyManager:
    """获取缓存策略管理器"""
    if cache_strategy_manager is None:
        raise RuntimeError("Cache strategy manager not initialized")
    return cache_strategy_manager