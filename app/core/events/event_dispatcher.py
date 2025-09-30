"""
事件分发器
提供观察者模式的事件处理功能
"""

from typing import Any, Dict, List, Callable, Type, Optional, Union
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import threading
from queue import Queue, Empty
import logging

logger = logging.getLogger(__name__)


class Event(ABC):
    """事件基类"""
    
    def __init__(self, **kwargs):
        self.timestamp = datetime.now()
        self.data = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'event': self.__class__.__name__,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }


class EventListener(ABC):
    """事件监听器基类"""
    
    @abstractmethod
    def handle(self, event: Event) -> Any:
        """处理事件"""
        pass
    
    def should_queue(self, event: Event) -> bool:
        """是否应该排队处理"""
        return False
    
    def get_queue_name(self, event: Event) -> str:
        """获取队列名称"""
        return 'default'


class EventDispatcher:
    """事件分发器"""
    
    def __init__(self):
        self._listeners: Dict[str, List[EventListener]] = {}
        self._wildcard_listeners: List[EventListener] = []
        self._queues: Dict[str, Queue] = {}
        self._queue_workers: Dict[str, threading.Thread] = {}
        self._running = True
        self._lock = threading.Lock()
    
    def listen(self, event_class: Union[str, Type[Event]], listener: EventListener) -> 'EventDispatcher':
        """注册事件监听器"""
        event_name = event_class if isinstance(event_class, str) else event_class.__name__
        
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(listener)
        
        logger.info(f"Registered listener for event: {event_name}")
        return self
    
    def listen_all(self, listener: EventListener) -> 'EventDispatcher':
        """注册全局监听器"""
        with self._lock:
            self._wildcard_listeners.append(listener)
        
        logger.info("Registered wildcard listener")
        return self
    
    def emit(self, event: Event, async_mode: bool = False) -> List[Any]:
        """分发事件"""
        event_name = event.__class__.__name__
        results = []
        
        # 获取监听器
        listeners = self._get_listeners(event_name)
        
        if not listeners:
            logger.warning(f"No listeners found for event: {event_name}")
            return results
        
        # 处理事件
        for listener in listeners:
            try:
                if listener.should_queue(event):
                    self._queue_event(event, listener)
                else:
                    if async_mode:
                        result = asyncio.create_task(self._handle_event_async(listener, event))
                    else:
                        result = self._handle_event(listener, event)
                    results.append(result)
            except Exception as e:
                logger.error(f"Error handling event {event_name}: {e}")
        
        return results
    
    async def emit_async(self, event: Event) -> List[Any]:
        """异步分发事件"""
        event_name = event.__class__.__name__
        results = []
        
        # 获取监听器
        listeners = self._get_listeners(event_name)
        
        if not listeners:
            logger.warning(f"No listeners found for event: {event_name}")
            return results
        
        # 处理事件
        tasks = []
        for listener in listeners:
            if listener.should_queue(event):
                self._queue_event(event, listener)
            else:
                task = asyncio.create_task(self._handle_event_async(listener, event))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def _get_listeners(self, event_name: str) -> List[EventListener]:
        """获取事件监听器"""
        listeners = []
        
        with self._lock:
            # 获取特定事件监听器
            if event_name in self._listeners:
                listeners.extend(self._listeners[event_name])
            
            # 获取全局监听器
            listeners.extend(self._wildcard_listeners)
        
        return listeners
    
    def _handle_event(self, listener: EventListener, event: Event) -> Any:
        """处理事件"""
        try:
            return listener.handle(event)
        except Exception as e:
            logger.error(f"Error in listener {listener.__class__.__name__}: {e}")
            raise
    
    async def _handle_event_async(self, listener: EventListener, event: Event) -> Any:
        """异步处理事件"""
        try:
            if asyncio.iscoroutinefunction(listener.handle):
                return await listener.handle(event)
            else:
                return listener.handle(event)
        except Exception as e:
            logger.error(f"Error in async listener {listener.__class__.__name__}: {e}")
            raise
    
    def _queue_event(self, event: Event, listener: EventListener) -> None:
        """将事件加入队列"""
        queue_name = listener.get_queue_name(event)
        
        if queue_name not in self._queues:
            self._queues[queue_name] = Queue()
            self._start_queue_worker(queue_name)
        
        self._queues[queue_name].put((event, listener))
    
    def _start_queue_worker(self, queue_name: str) -> None:
        """启动队列工作线程"""
        def worker():
            queue = self._queues[queue_name]
            while self._running:
                try:
                    event, listener = queue.get(timeout=1)
                    try:
                        self._handle_event(listener, event)
                    except Exception as e:
                        logger.error(f"Error processing queued event: {e}")
                    finally:
                        queue.task_done()
                except Empty:
                    continue
        
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        self._queue_workers[queue_name] = worker_thread
    
    def stop(self) -> None:
        """停止事件分发器"""
        self._running = False
        
        # 等待队列处理完成
        for queue in self._queues.values():
            queue.join()
        
        # 等待工作线程结束
        for worker in self._queue_workers.values():
            worker.join(timeout=5)
    
    def get_listeners(self, event_class: Union[str, Type[Event]]) -> List[EventListener]:
        """获取事件监听器列表"""
        event_name = event_class if isinstance(event_class, str) else event_class.__name__
        return self._get_listeners(event_name)
    
    def remove_listener(self, event_class: Union[str, Type[Event]], listener: EventListener) -> 'EventDispatcher':
        """移除事件监听器"""
        event_name = event_class if isinstance(event_class, str) else event_class.__name__
        
        with self._lock:
            if event_name in self._listeners:
                try:
                    self._listeners[event_name].remove(listener)
                except ValueError:
                    pass
        
        return self
    
    def clear_listeners(self, event_class: Union[str, Type[Event]] = None) -> 'EventDispatcher':
        """清空监听器"""
        with self._lock:
            if event_class:
                event_name = event_class if isinstance(event_class, str) else event_class.__name__
                if event_name in self._listeners:
                    del self._listeners[event_name]
            else:
                self._listeners.clear()
                self._wildcard_listeners.clear()
        
        return self


# 全局事件分发器实例
dispatcher = EventDispatcher()