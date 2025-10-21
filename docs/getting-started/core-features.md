# 核心功能使用指南

本文档详细介绍Python AI框架的核心功能使用方法，包括依赖注入、事件系统、配置管理、缓存系统等。

## 📋 目录

- [依赖注入系统](#依赖注入系统)
- [事件系统](#事件系统)
- [配置管理](#配置管理)
- [缓存系统](#缓存系统)
- [综合使用示例](#综合使用示例)
- [最佳实践](#最佳实践)

## 🔧 依赖注入系统

### 概述

依赖注入系统提供自动依赖解析和生命周期管理，让代码更加模块化和可测试。

### 基本使用

```python
from app.core.container import ServiceContainer

# 创建服务容器
container = ServiceContainer()

# 注册服务
container.singleton(DatabaseService)
container.singleton(UserRepository)
container.singleton(UserService)

# 自动解析依赖
user_service = container.get(UserService)
```

### 绑定类型

#### 1. 单例绑定
```python
# 单例绑定 - 整个应用生命周期只有一个实例
container.singleton(UserService)
```

#### 2. 实例绑定
```python
# 实例绑定 - 绑定已存在的实例
user_service = UserService()
container.instance(UserService, user_service)
```

#### 3. 工厂绑定
```python
# 工厂绑定 - 每次获取时调用工厂函数
container.factory(UserService, lambda c: UserService(c.get(DatabaseService)))
```

### 自动依赖解析

```python
class UserService:
    def __init__(self, repository: UserRepository, cache: CacheService):
        self.repository = repository
        self.cache = cache

class UserRepository:
    def __init__(self, database: DatabaseService):
        self.database = database

# 容器会自动解析所有依赖
user_service = container.get(UserService)
```

### 循环依赖检测

```python
# 容器会自动检测并防止循环依赖
class ServiceA:
    def __init__(self, service_b: ServiceB):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a: ServiceA):  # 循环依赖
        self.service_a = service_a

# 会抛出 ValueError: Circular dependency detected
```

### 装饰器使用

```python
from app.core.container import inject

@inject(UserService)
def get_user(user_id: int, user_service: UserService):
    return user_service.get_by_id(user_id)
```

## 📡 事件系统

### 概述

事件系统基于观察者模式，提供解耦的事件处理机制，支持同步和异步处理。

### 基本使用

```python
from app.core.events import EventDispatcher, Event, EventListener

# 创建事件分发器
dispatcher = EventDispatcher()

# 注册监听器
dispatcher.listen(UserCreatedEvent, EmailNotificationListener())
dispatcher.listen(UserCreatedEvent, LoggingListener())

# 分发事件
dispatcher.emit(UserCreatedEvent(user))
```

### 定义事件

```python
class UserCreatedEvent(Event):
    def __init__(self, user: User):
        super().__init__(user=user)

class UserUpdatedEvent(Event):
    def __init__(self, user: User, old_data: dict):
        super().__init__(user=user, old_data=old_data)
```

### 创建监听器

```python
class EmailNotificationListener(EventListener):
    def handle(self, event: Event) -> None:
        if isinstance(event, UserCreatedEvent):
            send_welcome_email(event.data['user'])
    
    def should_queue(self, event: Event) -> bool:
        return True  # 邮件发送应该排队处理

class LoggingListener(EventListener):
    def handle(self, event: Event) -> None:
        logger.info(f"Event: {event.__class__.__name__}")
    
    def should_queue(self, event: Event) -> bool:
        return False  # 日志记录可以同步处理
```

### 异步事件处理

```python
import asyncio

async def handle_async_events():
    # 异步分发事件
    results = await dispatcher.emit_async(UserCreatedEvent(user))
    print(f"处理结果: {results}")
```

### 全局监听器

```python
# 注册全局监听器，监听所有事件
dispatcher.listen_all(GlobalEventListener())
```

### 事件队列

```python
class QueueListener(EventListener):
    def should_queue(self, event: Event) -> bool:
        return True  # 启用队列处理
    
    def get_queue_name(self, event: Event) -> str:
        return "email_queue"  # 指定队列名称
```

## ⚙️ 配置管理

### 概述

配置管理系统支持多源配置、配置验证、动态配置和配置观察者模式。

### 基本使用

```python
from app.core.config.advanced_config import AdvancedConfig

# 创建配置管理器
config = AdvancedConfig()

# 设置配置
config.set("app.name", "Python AI Framework")
config.set("app.port", 8000)
config.set("app.debug", True)

# 获取配置
app_name = config.get("app.name")
port = config.get("app.port", 3000)  # 默认值
```

### 配置源

#### 1. 环境变量源
```python
from app.core.config.advanced_config import EnvironmentConfigSource

# 添加环境变量配置源
config.add_source(EnvironmentConfigSource('APP'))
# 环境变量: APP_NAME=MyApp, APP_PORT=8000
```

#### 2. 文件配置源
```python
from app.core.config.advanced_config import FileConfigSource

# JSON文件配置
config.add_source(FileConfigSource('config.json'))

# YAML文件配置
config.add_source(FileConfigSource('config.yaml', 'yaml'))
```

### 配置验证

```python
from app.core.config.advanced_config import TypeValidator, RangeValidator, ChoiceValidator

# 类型验证
config.add_validator("app.port", TypeValidator(int))

# 范围验证
config.add_validator("app.port", RangeValidator(1000, 65535))

# 选择验证
config.add_validator("app.env", ChoiceValidator(["development", "production"]))

# 设置配置（会自动验证）
config.set("app.port", 8000)  # 成功
config.set("app.port", "invalid")  # 抛出 ValueError
```

### 配置观察者

```python
def config_watcher(key: str, value: Any):
    print(f"配置变更: {key} = {value}")

# 添加观察者
config.add_watcher("app.debug", config_watcher)

# 配置变更时会自动通知
config.set("app.debug", True)
```

### 嵌套配置

```python
# 设置嵌套配置
config.set("database.host", "localhost")
config.set("database.port", 5432)
config.set("database.name", "myapp")

# 获取嵌套配置
db_host = config.get("database.host")
db_port = config.get("database.port")
```

### 配置保存和加载

```python
# 加载配置
config.load()

# 保存配置
config.save()

# 检查配置是否存在
if config.has("app.name"):
    print("应用名称已配置")

# 移除配置
config.remove("app.debug")
```

## 💾 缓存系统

### 概述

缓存系统支持多种缓存驱动，提供统一的缓存接口和高级缓存功能。

### 基本使用

```python
from app.core.cache import CacheManager, MemoryCache

# 创建缓存管理器
cache = CacheManager()

# 添加缓存驱动
cache.add_driver("memory", MemoryCache())
cache.set_default_driver("memory")

# 基础操作
cache.set("user:1", {"id": 1, "name": "John"}, ttl=3600)
user = cache.get("user:1")
cache.delete("user:1")
```

### 缓存驱动

#### 1. 内存缓存
```python
from app.core.cache import MemoryCache

cache.add_driver("memory", MemoryCache())
```

#### 2. 文件缓存
```python
from app.core.cache import FileCache

cache.add_driver("file", FileCache("cache_dir"))
```

#### 3. Redis缓存
```python
from app.core.cache import RedisCache

cache.add_driver("redis", RedisCache(host="localhost", port=6379))
```

### 高级功能

#### 记住缓存
```python
def expensive_operation():
    # 模拟耗时操作
    time.sleep(2)
    return {"result": "expensive_data"}

# 如果缓存不存在，执行回调并缓存结果
result = cache.remember("expensive:data", expensive_operation, ttl=300)
```

#### 缓存前缀
```python
# 设置缓存前缀
cache.set_prefix("app:")

# 所有键都会自动添加前缀
cache.set("user:1", user_data)  # 实际键: app:user:1
```

#### 缓存统计
```python
# 获取缓存统计
stats = cache.get_stats()
print(f"缓存统计: {stats}")

# 获取所有键
keys = cache.keys()
print(f"缓存键: {keys}")

# 模式匹配
user_keys = cache.keys("user:*")
```

### 缓存操作

```python
# 检查缓存是否存在
if cache.exists("user:1"):
    user = cache.get("user:1")

# 清空缓存
cache.clear()

# 刷新缓存（清空）
cache.flush()

# 忘记缓存（删除）
cache.forget("user:1")
```

## 🔗 综合使用示例

### 完整应用示例

```python
from app.core.container import ServiceContainer
from app.core.events import EventDispatcher, Event, EventListener
from app.core.config.advanced_config import AdvancedConfig
from app.core.cache import CacheManager, MemoryCache

class UserCreatedEvent(Event):
    def __init__(self, user: User):
        super().__init__(user=user)

class EmailListener(EventListener):
    def handle(self, event: Event) -> None:
        if isinstance(event, UserCreatedEvent):
            print(f"发送欢迎邮件给: {event.data['user'].username}")

class UserService:
    def __init__(self, cache: CacheManager, config: AdvancedConfig):
        self.cache = cache
        self.config = config
    
    def create_user(self, user_data: dict) -> User:
        # 创建用户
        user = User(**user_data)
        
        # 缓存用户数据
        self.cache.set(f"user:{user.id}", user.to_dict(), ttl=3600)
        
        # 分发事件
        dispatcher.emit(UserCreatedEvent(user))
        
        return user

# 初始化所有组件
container = ServiceContainer()
dispatcher = EventDispatcher()
config = AdvancedConfig()
cache = CacheManager()

# 配置服务
config.set("app.name", "User Management System")
config.set("cache.ttl", 3600)

# 设置缓存
cache.add_driver("memory", MemoryCache())
cache.set_prefix("app:")

# 注册服务
container.singleton(CacheManager, lambda c: cache)
container.singleton(AdvancedConfig, lambda c: config)
container.singleton(UserService)

# 注册事件监听器
dispatcher.listen(UserCreatedEvent, EmailListener())

# 使用服务
user_service = container.get(UserService)
user = user_service.create_user({
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password"
})
```

## 🎯 最佳实践

### 1. 依赖注入最佳实践

```python
# ✅ 好的做法
class UserService:
    def __init__(self, repository: UserRepository, cache: CacheService):
        self.repository = repository
        self.cache = cache

# ❌ 避免的做法
class UserService:
    def __init__(self):
        self.repository = UserRepository()  # 硬编码依赖
        self.cache = CacheService()
```

### 2. 事件系统最佳实践

```python
# ✅ 好的做法
class UserCreatedEvent(Event):
    def __init__(self, user: User):
        super().__init__(user=user)

# ❌ 避免的做法
class UserCreatedEvent(Event):
    def __init__(self, user_id: int, username: str, email: str):
        # 传递太多参数，应该传递对象
        pass
```

### 3. 配置管理最佳实践

```python
# ✅ 好的做法
config.add_validator("app.port", TypeValidator(int))
config.add_validator("app.port", RangeValidator(1000, 65535))

# ❌ 避免的做法
port = config.get("app.port")
if not isinstance(port, int):
    raise ValueError("Port must be integer")  # 手动验证
```

### 4. 缓存系统最佳实践

```python
# ✅ 好的做法
def get_user(user_id: int):
    return cache.remember(f"user:{user_id}", lambda: fetch_user(user_id), ttl=3600)

# ❌ 避免的做法
def get_user(user_id: int):
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    else:
        user = fetch_user(user_id)
        cache.set(f"user:{user_id}", user, ttl=3600)
        return user
```

### 5. 错误处理

```python
# 依赖注入错误处理
try:
    service = container.get(ServiceClass)
except ValueError as e:
    logger.error(f"依赖解析失败: {e}")

# 事件处理错误处理
class SafeEventListener(EventListener):
    def handle(self, event: Event) -> None:
        try:
            # 处理事件
            pass
        except Exception as e:
            logger.error(f"事件处理失败: {e}")

# 配置验证错误处理
try:
    config.set("app.port", "invalid")
except ValueError as e:
    logger.error(f"配置验证失败: {e}")
```

### 6. 性能优化

```python
# 使用单例绑定减少对象创建
container.singleton(ExpensiveService)

# 使用缓存减少重复计算
result = cache.remember("expensive:key", expensive_function, ttl=3600)

# 使用事件队列处理耗时操作
class EmailListener(EventListener):
    def should_queue(self, event: Event) -> bool:
        return True  # 邮件发送应该排队处理
```

## 📚 总结

这些核心功能为您的应用提供了强大的基础设施支持：

- **依赖注入**: 提高代码可测试性和模块化
- **事件系统**: 实现解耦的业务逻辑和插件化架构
- **配置管理**: 统一配置管理，支持多环境部署
- **缓存系统**: 显著提升应用性能

通过合理使用这些功能，您可以构建出高质量、高性能、易维护的应用程序。