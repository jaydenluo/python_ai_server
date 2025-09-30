# 快速入门指南

本指南将帮助您快速上手Python AI框架的核心功能。

## 🚀 5分钟快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基础设置

```python
# main.py
from app.core.container import ServiceContainer
from app.core.events import EventDispatcher
from app.core.config.advanced_config import AdvancedConfig
from app.core.cache import CacheManager, MemoryCache

# 初始化核心组件
container = ServiceContainer()
dispatcher = EventDispatcher()
config = AdvancedConfig()
cache = CacheManager()

# 配置缓存
cache.add_driver("memory", MemoryCache())
cache.set_prefix("app:")

# 加载配置
config.load()
```

### 3. 创建第一个服务

```python
# app/services/user_service.py
from app.core.container import inject

class UserService:
    def __init__(self, cache: CacheManager):
        self.cache = cache
    
    def get_user(self, user_id: int):
        # 使用缓存
        user = self.cache.get(f"user:{user_id}")
        if not user:
            user = self._fetch_from_database(user_id)
            self.cache.set(f"user:{user_id}", user, ttl=3600)
        return user
    
    def _fetch_from_database(self, user_id: int):
        # 模拟数据库查询
        return {"id": user_id, "name": f"User {user_id}"}
```

### 4. 注册服务

```python
# 注册服务到容器
container.singleton(UserService)
```

### 5. 使用服务

```python
# 获取服务实例
user_service = container.get(UserService)

# 使用服务
user = user_service.get_user(1)
print(f"用户信息: {user}")
```

## 📡 添加事件系统

### 1. 定义事件

```python
# app/events/user_events.py
from app.core.events import Event

class UserCreatedEvent(Event):
    def __init__(self, user: dict):
        super().__init__(user=user)
```

### 2. 创建监听器

```python
# app/listeners/email_listener.py
from app.core.events import EventListener

class EmailListener(EventListener):
    def handle(self, event: Event) -> None:
        if hasattr(event, 'data') and 'user' in event.data:
            print(f"📧 发送欢迎邮件给: {event.data['user']['name']}")
```

### 3. 注册监听器

```python
# 注册事件监听器
dispatcher.listen(UserCreatedEvent, EmailListener())
```

### 4. 分发事件

```python
# 在服务中分发事件
class UserService:
    def create_user(self, user_data: dict):
        user = self._create_user(user_data)
        
        # 分发事件
        dispatcher.emit(UserCreatedEvent(user))
        
        return user
```

## ⚙️ 配置管理

### 1. 设置配置

```python
# 设置应用配置
config.set("app.name", "My Application")
config.set("app.version", "1.0.0")
config.set("app.debug", True)

# 设置数据库配置
config.set("database.host", "localhost")
config.set("database.port", 5432)
config.set("database.name", "myapp")
```

### 2. 使用配置

```python
# 获取配置
app_name = config.get("app.name")
debug_mode = config.get("app.debug", False)
db_host = config.get("database.host", "localhost")
```

### 3. 配置验证

```python
from app.core.config.advanced_config import TypeValidator, RangeValidator

# 添加验证器
config.add_validator("app.port", TypeValidator(int))
config.add_validator("app.port", RangeValidator(1000, 65535))

# 设置配置（会自动验证）
config.set("app.port", 8000)
```

## 💾 缓存使用

### 1. 基础缓存操作

```python
# 设置缓存
cache.set("user:1", {"id": 1, "name": "John"}, ttl=3600)

# 获取缓存
user = cache.get("user:1")

# 检查缓存是否存在
if cache.exists("user:1"):
    print("用户缓存存在")

# 删除缓存
cache.delete("user:1")
```

### 2. 记住缓存

```python
def expensive_operation():
    print("执行耗时操作...")
    time.sleep(2)
    return {"result": "expensive_data"}

# 如果缓存不存在，执行回调并缓存结果
result = cache.remember("expensive:key", expensive_operation, ttl=300)
```

## 🔗 完整示例

```python
# main.py
from app.core.container import ServiceContainer
from app.core.events import EventDispatcher, Event, EventListener
from app.core.config.advanced_config import AdvancedConfig
from app.core.cache import CacheManager, MemoryCache

# 定义事件
class UserCreatedEvent(Event):
    def __init__(self, user: dict):
        super().__init__(user=user)

# 定义监听器
class EmailListener(EventListener):
    def handle(self, event: Event) -> None:
        print(f"📧 发送欢迎邮件给: {event.data['user']['name']}")

# 定义服务
class UserService:
    def __init__(self, cache: CacheManager, config: AdvancedConfig):
        self.cache = cache
        self.config = config
    
    def create_user(self, user_data: dict) -> dict:
        # 创建用户
        user = {
            "id": len(self.cache.keys("user:*")) + 1,
            "name": user_data["name"],
            "email": user_data["email"]
        }
        
        # 缓存用户
        self.cache.set(f"user:{user['id']}", user, ttl=3600)
        
        # 分发事件
        dispatcher.emit(UserCreatedEvent(user))
        
        return user

def main():
    # 初始化组件
    container = ServiceContainer()
    dispatcher = EventDispatcher()
    config = AdvancedConfig()
    cache = CacheManager()
    
    # 配置缓存
    cache.add_driver("memory", MemoryCache())
    cache.set_prefix("app:")
    
    # 设置配置
    config.set("app.name", "User Management System")
    config.set("app.debug", True)
    
    # 注册服务
    container.singleton(CacheManager, lambda c: cache)
    container.singleton(AdvancedConfig, lambda c: config)
    container.singleton(UserService)
    
    # 注册事件监听器
    dispatcher.listen(UserCreatedEvent, EmailListener())
    
    # 使用服务
    user_service = container.get(UserService)
    
    # 创建用户
    user = user_service.create_user({
        "name": "John Doe",
        "email": "john@example.com"
    })
    
    print(f"创建用户: {user}")
    
    # 获取用户
    cached_user = cache.get(f"user:{user['id']}")
    print(f"缓存用户: {cached_user}")

if __name__ == "__main__":
    main()
```

## 🎯 下一步

1. **查看详细文档**: [核心功能使用指南](core_features_guide.md)
2. **运行示例**: `python examples/core_features_demo.py`
3. **探索更多功能**: 查看 `app/core/` 目录下的其他模块

## ❓ 常见问题

### Q: 如何添加新的缓存驱动？
A: 继承 `CacheDriver` 基类并实现必要方法，然后使用 `cache.add_driver()` 注册。

### Q: 如何配置环境变量？
A: 使用 `EnvironmentConfigSource` 并设置环境变量前缀。

### Q: 如何处理事件处理失败？
A: 在监听器中添加 try-catch 块，或使用队列处理异步事件。

### Q: 如何测试依赖注入？
A: 使用 `container.instance()` 绑定测试实例，或使用模拟对象。

## 📞 获取帮助

- 查看示例代码: `examples/` 目录
- 阅读详细文档: `docs/` 目录
- 运行测试: `python -m pytest tests/`