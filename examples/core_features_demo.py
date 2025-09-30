"""
核心功能演示
展示依赖注入、事件系统、配置管理、缓存系统的作用
"""

from app.core.container import ServiceContainer, ServiceProvider
from app.core.events import EventDispatcher, Event, EventListener
from app.core.config.advanced_config import AdvancedConfig, TypeValidator, RangeValidator
from app.core.cache import CacheManager, MemoryCache, FileCache
from app.models.entities.user import User
from app.services.base_service import UserService
from app.core.repositories.base_repository import BaseRepository
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import time


# ==================== 依赖注入演示 ====================

class DatabaseService:
    """数据库服务"""
    
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()


class UserRepository:
    """用户仓储"""
    
    def __init__(self, database: DatabaseService):
        self.database = database
    
    def get_user(self, user_id: int) -> User:
        session = self.database.get_session()
        return session.query(User).filter(User.id == user_id).first()


class UserController:
    """用户控制器"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def get_user(self, user_id: int) -> User:
        return self.user_service.get_by_id(user_id)


def demo_dependency_injection():
    """演示依赖注入"""
    print("🔧 依赖注入演示")
    print("=" * 50)
    
    # 创建服务容器
    container = ServiceContainer()
    
    # 注册服务
    container.singleton(DatabaseService)
    container.singleton(UserRepository)
    container.singleton(UserController)
    
    # 自动解析依赖
    controller = container.get(UserController)
    print(f"控制器创建成功: {type(controller).__name__}")
    
    # 检查依赖关系
    user_service = controller.user_service
    print(f"用户服务: {type(user_service).__name__}")
    
    # 检查仓储
    repository = user_service.repository
    print(f"用户仓储: {type(repository).__name__}")


# ==================== 事件系统演示 ====================

class UserCreatedEvent(Event):
    """用户创建事件"""
    
    def __init__(self, user: User):
        super().__init__(user=user)


class UserUpdatedEvent(Event):
    """用户更新事件"""
    
    def __init__(self, user: User, old_data: dict):
        super().__init__(user=user, old_data=old_data)


class EmailNotificationListener(EventListener):
    """邮件通知监听器"""
    
    def handle(self, event: Event) -> None:
        if isinstance(event, UserCreatedEvent):
            print(f"📧 发送欢迎邮件给: {event.data['user'].username}")
        elif isinstance(event, UserUpdatedEvent):
            print(f"📧 发送更新通知给: {event.data['user'].username}")
    
    def should_queue(self, event: Event) -> bool:
        return True  # 邮件发送应该排队处理


class LoggingListener(EventListener):
    """日志监听器"""
    
    def handle(self, event: Event) -> None:
        print(f"📝 记录事件: {event.__class__.__name__} - {event.timestamp}")
    
    def should_queue(self, event: Event) -> bool:
        return False  # 日志记录可以同步处理


def demo_event_system():
    """演示事件系统"""
    print("\n📡 事件系统演示")
    print("=" * 50)
    
    # 创建事件分发器
    dispatcher = EventDispatcher()
    
    # 注册监听器
    dispatcher.listen(UserCreatedEvent, EmailNotificationListener())
    dispatcher.listen(UserCreatedEvent, LoggingListener())
    dispatcher.listen(UserUpdatedEvent, EmailNotificationListener())
    dispatcher.listen(UserUpdatedEvent, LoggingListener())
    
    # 创建用户
    user = User(username="event_user", email="event@example.com", password="password")
    
    # 分发事件
    print("分发用户创建事件:")
    dispatcher.emit(UserCreatedEvent(user))
    
    print("\n分发用户更新事件:")
    dispatcher.emit(UserUpdatedEvent(user, {"old_status": "pending"}))
    
    # 停止事件分发器
    dispatcher.stop()


# ==================== 配置管理演示 ====================

def demo_config_management():
    """演示配置管理"""
    print("\n⚙️ 配置管理演示")
    print("=" * 50)
    
    # 创建配置管理器
    config = AdvancedConfig()
    
    # 添加配置验证器
    config.add_validator("app.port", TypeValidator(int))
    config.add_validator("app.port", RangeValidator(1000, 65535))
    config.add_validator("app.debug", TypeValidator(bool))
    config.add_validator("app.env", TypeValidator(str))
    
    # 设置配置
    config.set("app.name", "Python AI Framework")
    config.set("app.version", "1.0.0")
    config.set("app.port", 8000)
    config.set("app.debug", True)
    config.set("app.env", "development")
    
    # 设置数据库配置
    config.set("database.host", "localhost")
    config.set("database.port", 5432)
    config.set("database.name", "ai_framework")
    config.set("database.user", "admin")
    config.set("database.password", "secret")
    
    # 设置缓存配置
    config.set("cache.driver", "redis")
    config.set("cache.host", "localhost")
    config.set("cache.port", 6379)
    config.set("cache.ttl", 3600)
    
    # 获取配置
    print(f"应用名称: {config.get('app.name')}")
    print(f"应用端口: {config.get('app.port')}")
    print(f"调试模式: {config.get('app.debug')}")
    print(f"数据库主机: {config.get('database.host')}")
    print(f"缓存驱动: {config.get('cache.driver')}")
    
    # 配置观察者
    def config_watcher(key: str, value: Any):
        print(f"🔔 配置变更: {key} = {value}")
    
    config.add_watcher("app.debug", config_watcher)
    
    # 修改配置（触发观察者）
    config.set("app.debug", False)
    
    # 验证配置
    try:
        config.set("app.port", "invalid")  # 应该失败
    except ValueError as e:
        print(f"配置验证失败: {e}")
    
    # 保存配置
    config.save()
    print("配置已保存")


# ==================== 缓存系统演示 ====================

def demo_cache_system():
    """演示缓存系统"""
    print("\n💾 缓存系统演示")
    print("=" * 50)
    
    # 创建缓存管理器
    cache = CacheManager()
    
    # 添加缓存驱动
    cache.add_driver("memory", MemoryCache())
    cache.add_driver("file", FileCache("cache"))
    
    # 设置默认驱动
    cache.set_default_driver("memory")
    cache.set_prefix("app:")
    
    # 基础缓存操作
    print("1. 基础缓存操作")
    cache.set("user:1", {"id": 1, "name": "John Doe"}, ttl=60)
    cache.set("user:2", {"id": 2, "name": "Jane Smith"}, ttl=60)
    
    user1 = cache.get("user:1")
    print(f"获取用户1: {user1}")
    
    # 检查缓存是否存在
    exists = cache.exists("user:1")
    print(f"用户1缓存存在: {exists}")
    
    # 记住缓存（如果不存在则执行回调）
    print("\n2. 记住缓存功能")
    def expensive_operation():
        print("执行昂贵的操作...")
        time.sleep(1)  # 模拟耗时操作
        return {"result": "expensive_data", "timestamp": datetime.now()}
    
    # 第一次调用（会执行回调）
    result1 = cache.remember("expensive:data", expensive_operation, ttl=30)
    print(f"第一次结果: {result1}")
    
    # 第二次调用（从缓存获取）
    result2 = cache.remember("expensive:data", expensive_operation, ttl=30)
    print(f"第二次结果: {result2}")
    
    # 缓存统计
    print("\n3. 缓存统计")
    stats = cache.get_stats()
    print(f"缓存统计: {stats}")
    
    # 获取所有键
    keys = cache.keys()
    print(f"缓存键: {keys}")
    
    # 清空缓存
    cache.clear()
    print("缓存已清空")


# ==================== 综合演示 ====================

def demo_integrated_features():
    """演示综合功能"""
    print("\n🔗 综合功能演示")
    print("=" * 50)
    
    # 创建服务容器
    container = ServiceContainer()
    
    # 注册服务
    container.singleton(DatabaseService)
    container.singleton(UserRepository)
    container.singleton(UserController)
    
    # 创建事件分发器
    dispatcher = EventDispatcher()
    dispatcher.listen(UserCreatedEvent, EmailNotificationListener())
    dispatcher.listen(UserCreatedEvent, LoggingListener())
    
    # 创建配置管理器
    config = AdvancedConfig()
    config.set("app.name", "Integrated Demo")
    config.set("app.debug", True)
    
    # 创建缓存管理器
    cache = CacheManager()
    cache.add_driver("memory", MemoryCache())
    cache.set_prefix("demo:")
    
    # 模拟用户创建流程
    print("模拟用户创建流程:")
    
    # 1. 从配置获取设置
    app_name = config.get("app.name")
    debug_mode = config.get("app.debug")
    print(f"应用名称: {app_name}, 调试模式: {debug_mode}")
    
    # 2. 检查缓存
    cached_user = cache.get("user:demo")
    if cached_user:
        print(f"从缓存获取用户: {cached_user}")
    else:
        print("缓存中无用户数据")
    
    # 3. 创建用户（通过依赖注入）
    controller = container.get(UserController)
    print(f"控制器创建成功: {type(controller).__name__}")
    
    # 4. 分发事件
    user = User(username="demo_user", email="demo@example.com", password="password")
    dispatcher.emit(UserCreatedEvent(user))
    
    # 5. 缓存结果
    cache.set("user:demo", user.to_dict(), ttl=300)
    print("用户数据已缓存")
    
    # 6. 获取缓存统计
    cache_stats = cache.get_stats()
    print(f"缓存统计: {cache_stats}")


if __name__ == "__main__":
    print("🎯 核心功能完整演示")
    print("=" * 60)
    
    # 运行演示
    demo_dependency_injection()
    demo_event_system()
    demo_config_management()
    demo_cache_system()
    demo_integrated_features()
    
    print("\n🎉 演示完成！")
    print("\n💡 核心功能作用:")
    print("1. 依赖注入 - 自动管理服务依赖，提高代码可测试性")
    print("2. 事件系统 - 解耦业务逻辑，支持异步处理")
    print("3. 配置管理 - 统一配置管理，支持验证和观察者")
    print("4. 缓存系统 - 提高性能，支持多种缓存驱动")
    print("5. 综合使用 - 各功能协同工作，构建完整应用")