"""
缓存监控
提供缓存性能监控、告警、统计等功能
"""

import time
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import psutil
import os


@dataclass
class CacheMetrics:
    """缓存指标"""
    hits: int = 0
    misses: int = 0
    errors: int = 0
    operations: int = 0
    memory_usage: float = 0.0
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        return (self.errors / self.operations * 100) if self.operations > 0 else 0.0


@dataclass
class CacheAlert:
    """缓存告警"""
    level: str  # INFO, WARNING, ERROR, CRITICAL
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Optional[CacheMetrics] = None


class CacheMonitor:
    """缓存监控器"""
    
    def __init__(self, cache_manager, check_interval: int = 60):
        self.cache_manager = cache_manager
        self.check_interval = check_interval
        self.logger = logging.getLogger(__name__)
        
        # 监控数据
        self._metrics_history: deque = deque(maxlen=1000)  # 保留最近1000个指标
        self._current_metrics = CacheMetrics()
        self._alerts: List[CacheAlert] = []
        self._alert_callbacks: List[Callable] = []
        
        # 阈值配置
        self._thresholds = {
            'hit_rate_min': 80.0,  # 最低命中率
            'error_rate_max': 5.0,  # 最高错误率
            'response_time_max': 100.0,  # 最高响应时间(ms)
            'memory_usage_max': 80.0,  # 最高内存使用率
            'operations_min': 10  # 最低操作数
        }
        
        # 监控线程
        self._monitor_thread = None
        self._stop_monitoring = False
        self._lock = threading.Lock()
        
        # 性能统计
        self._response_times: deque = deque(maxlen=100)
        self._operation_counts: Dict[str, int] = defaultdict(int)
        
    def start_monitoring(self):
        """开始监控"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_monitoring = False
            self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
            self._monitor_thread.start()
            self.logger.info("Cache monitoring started")
    
    def stop_monitoring(self):
        """停止监控"""
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("Cache monitoring stopped")
    
    def _monitor_worker(self):
        """监控工作线程"""
        while not self._stop_monitoring:
            try:
                self._collect_metrics()
                self._check_thresholds()
                self._cleanup_old_data()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in cache monitoring: {e}")
                time.sleep(60)  # 错误时等待1分钟再重试
    
    def _collect_metrics(self):
        """收集指标"""
        with self._lock:
            # 获取缓存统计
            cache_stats = self.cache_manager.get_stats()
            
            # 获取系统信息
            memory_info = psutil.virtual_memory()
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 计算平均响应时间
            avg_response_time = sum(self._response_times) / len(self._response_times) if self._response_times else 0
            
            # 创建指标对象
            metrics = CacheMetrics(
                hits=cache_stats.get('hits', 0),
                misses=cache_stats.get('misses', 0),
                errors=cache_stats.get('errors', 0),
                operations=cache_stats.get('operations', 0),
                memory_usage=memory_info.percent,
                response_time=avg_response_time,
                timestamp=datetime.now()
            )
            
            # 更新当前指标
            self._current_metrics = metrics
            
            # 添加到历史记录
            self._metrics_history.append(metrics)
            
            # 清理响应时间记录
            if len(self._response_times) > 50:
                self._response_times.clear()
    
    def _check_thresholds(self):
        """检查阈值"""
        metrics = self._current_metrics
        
        # 检查命中率
        if metrics.hit_rate < self._thresholds['hit_rate_min']:
            self._create_alert('WARNING', f"Low hit rate: {metrics.hit_rate:.2f}%")
        
        # 检查错误率
        if metrics.error_rate > self._thresholds['error_rate_max']:
            self._create_alert('ERROR', f"High error rate: {metrics.error_rate:.2f}%")
        
        # 检查响应时间
        if metrics.response_time > self._thresholds['response_time_max']:
            self._create_alert('WARNING', f"High response time: {metrics.response_time:.2f}ms")
        
        # 检查内存使用率
        if metrics.memory_usage > self._thresholds['memory_usage_max']:
            self._create_alert('CRITICAL', f"High memory usage: {metrics.memory_usage:.2f}%")
        
        # 检查操作数
        if metrics.operations < self._thresholds['operations_min']:
            self._create_alert('INFO', f"Low operation count: {metrics.operations}")
    
    def _create_alert(self, level: str, message: str):
        """创建告警"""
        alert = CacheAlert(
            level=level,
            message=message,
            timestamp=datetime.now(),
            metrics=self._current_metrics
        )
        
        self._alerts.append(alert)
        
        # 限制告警数量
        if len(self._alerts) > 1000:
            self._alerts = self._alerts[-500:]
        
        # 调用告警回调
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
        
        self.logger.warning(f"Cache alert [{level}]: {message}")
    
    def _cleanup_old_data(self):
        """清理旧数据"""
        # 清理超过1小时的告警
        cutoff_time = datetime.now() - timedelta(hours=1)
        self._alerts = [alert for alert in self._alerts if alert.timestamp > cutoff_time]
    
    def record_operation(self, operation: str, response_time: float):
        """记录操作"""
        with self._lock:
            self._operation_counts[operation] += 1
            self._response_times.append(response_time)
    
    def get_current_metrics(self) -> CacheMetrics:
        """获取当前指标"""
        return self._current_metrics
    
    def get_metrics_history(self, hours: int = 1) -> List[CacheMetrics]:
        """获取指标历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self._metrics_history if m.timestamp > cutoff_time]
    
    def get_alerts(self, level: Optional[str] = None, hours: int = 24) -> List[CacheAlert]:
        """获取告警"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = [a for a in self._alerts if a.timestamp > cutoff_time]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return alerts
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        with self._lock:
            current = self._current_metrics
            history = list(self._metrics_history)
            
            if not history:
                return {
                    'status': 'no_data',
                    'message': 'No metrics data available'
                }
            
            # 计算统计信息
            hit_rates = [m.hit_rate for m in history]
            error_rates = [m.error_rate for m in history]
            response_times = [m.response_time for m in history]
            
            # 计算趋势
            recent_hit_rate = sum(hit_rates[-10:]) / len(hit_rates[-10:]) if len(hit_rates) >= 10 else current.hit_rate
            recent_error_rate = sum(error_rates[-10:]) / len(error_rates[-10:]) if len(error_rates) >= 10 else current.error_rate
            
            # 计算趋势方向
            hit_rate_trend = "improving" if recent_hit_rate > current.hit_rate else "declining"
            error_rate_trend = "improving" if recent_error_rate < current.error_rate else "declining"
            
            return {
                'status': 'healthy' if current.hit_rate > 80 and current.error_rate < 5 else 'warning',
                'current_metrics': {
                    'hit_rate': round(current.hit_rate, 2),
                    'error_rate': round(current.error_rate, 2),
                    'response_time': round(current.response_time, 2),
                    'memory_usage': round(current.memory_usage, 2),
                    'operations': current.operations
                },
                'trends': {
                    'hit_rate_trend': hit_rate_trend,
                    'error_rate_trend': error_rate_trend
                },
                'statistics': {
                    'avg_hit_rate': round(sum(hit_rates) / len(hit_rates), 2),
                    'avg_error_rate': round(sum(error_rates) / len(error_rates), 2),
                    'avg_response_time': round(sum(response_times) / len(response_times), 2),
                    'max_response_time': round(max(response_times), 2),
                    'min_response_time': round(min(response_times), 2)
                },
                'operation_counts': dict(self._operation_counts),
                'alerts_count': len(self.get_alerts(hours=1)),
                'monitoring_duration': len(history) * self.check_interval
            }
    
    def set_threshold(self, name: str, value: float):
        """设置阈值"""
        if name in self._thresholds:
            self._thresholds[name] = value
            self.logger.info(f"Threshold '{name}' set to {value}")
        else:
            self.logger.warning(f"Unknown threshold: {name}")
    
    def add_alert_callback(self, callback: Callable):
        """添加告警回调"""
        self._alert_callbacks.append(callback)
    
    def clear_alerts(self):
        """清理告警"""
        with self._lock:
            self._alerts.clear()
    
    def export_metrics(self, format: str = 'json') -> str:
        """导出指标"""
        if format == 'json':
            data = {
                'current_metrics': {
                    'hits': self._current_metrics.hits,
                    'misses': self._current_metrics.misses,
                    'errors': self._current_metrics.errors,
                    'operations': self._current_metrics.operations,
                    'hit_rate': self._current_metrics.hit_rate,
                    'error_rate': self._current_metrics.error_rate,
                    'response_time': self._current_metrics.response_time,
                    'memory_usage': self._current_metrics.memory_usage,
                    'timestamp': self._current_metrics.timestamp.isoformat()
                },
                'metrics_history': [
                    {
                        'hits': m.hits,
                        'misses': m.misses,
                        'errors': m.errors,
                        'operations': m.operations,
                        'hit_rate': m.hit_rate,
                        'error_rate': m.error_rate,
                        'response_time': m.response_time,
                        'memory_usage': m.memory_usage,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in self._metrics_history
                ],
                'alerts': [
                    {
                        'level': a.level,
                        'message': a.message,
                        'timestamp': a.timestamp.isoformat()
                    }
                    for a in self._alerts
                ]
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


class CacheHealthChecker:
    """缓存健康检查器"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
    
    def check_health(self) -> Dict[str, Any]:
        """检查缓存健康状态"""
        start_time = time.time()
        
        try:
            # 测试基本操作
            test_key = f"health_check_{int(time.time())}"
            test_value = "health_check_value"
            
            # 测试设置
            set_success = self.cache_manager.set(test_key, test_value, ttl=60)
            if not set_success:
                return {
                    'status': 'unhealthy',
                    'message': 'Failed to set test value',
                    'response_time': time.time() - start_time
                }
            
            # 测试获取
            retrieved_value = self.cache_manager.get(test_key)
            if retrieved_value != test_value:
                return {
                    'status': 'unhealthy',
                    'message': 'Retrieved value does not match',
                    'response_time': time.time() - start_time
                }
            
            # 测试删除
            delete_success = self.cache_manager.delete(test_key)
            if not delete_success:
                return {
                    'status': 'unhealthy',
                    'message': 'Failed to delete test value',
                    'response_time': time.time() - start_time
                }
            
            # 获取统计信息
            stats = self.cache_manager.get_stats()
            
            return {
                'status': 'healthy',
                'message': 'All cache operations successful',
                'response_time': time.time() - start_time,
                'stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Cache health check failed: {str(e)}',
                'response_time': time.time() - start_time
            }


# 全局缓存监控器
cache_monitor = None


def init_cache_monitoring(cache_manager, check_interval: int = 60) -> CacheMonitor:
    """初始化缓存监控"""
    global cache_monitor
    cache_monitor = CacheMonitor(cache_manager, check_interval)
    return cache_monitor


def get_cache_monitor() -> CacheMonitor:
    """获取缓存监控器"""
    if cache_monitor is None:
        raise RuntimeError("Cache monitor not initialized")
    return cache_monitor