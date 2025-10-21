# 服务架构指南

## 🏗️ 服务分类

本项目中的服务分为两大类：

### 1️⃣ 数据库服务（需要继承 BaseService）

**特征**：
- ✅ 需要对数据库进行 CRUD 操作
- ✅ 使用 `Repository` 进行数据访问
- ✅ 管理持久化数据

**示例**：
```python
from app.core.repositories.repository import Repository
from app.services.base_service import BaseService
from app.models.entities.user import User

class UserService(BaseService):
    """用户服务 - 需要数据库"""
    
    def __init__(self, session):
        repository = Repository(User, session)
        super().__init__(repository)
    
    def create_user(self, username, email):
        # 使用 repository 的方法
        return self.repository.create(
            username=username,
            email=email
        )
    
    def get_active_users(self):
        # 使用 repository 的查询方法
        return self.repository.filter_by_conditions({
            'status': 'active'
        })
```

**适用场景**：
- 用户管理（User）
- 权限管理（Permission）
- 角色管理（Role）
- 数据记录（Log）
- 任务管理（Task）
- 订单管理（Order）
- 等需要持久化的业务数据

---

### 2️⃣ 业务服务（不需要继承 BaseService）

**特征**：
- ❌ 不直接操作数据库
- ✅ 调用第三方 API
- ✅ 处理内存数据
- ✅ 提供业务逻辑封装

**示例 1：第三方 API 服务**
```python
class XunfeiService:
    """讯飞服务 - 第三方API，不需要数据库"""
    
    def __init__(self, app_id: str, api_key: str, api_secret: str):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
    
    def generate_tts_auth(self, params: dict):
        # 调用第三方API
        return self._call_xunfei_api(params)
```

**示例 2：内存数据服务**
```python
class VoiceService:
    """语音服务 - 纯内存数据，不需要数据库"""
    
    def __init__(self):
        self._providers = self._load_providers()
        self._voices = self._load_voices()
    
    def get_providers(self):
        return self._providers
    
    def search_voices(self, keyword):
        return [v for v in self._voices if keyword in v['name']]
```

**适用场景**：
- 第三方 API 封装（讯飞、百度、OpenAI）
- 配置数据管理（音色列表、模型列表）
- Token 生成服务
- 文件处理服务
- 缓存服务
- 工具类服务

---

## 📋 当前项目服务分类

### ✅ 应该继承 BaseService（需要数据库）

```python
# app/services/user_service.py
class UserService(BaseService):
    """用户管理 - 需要数据库"""
    pass

# app/services/auth_service.py  
class AuthService(BaseService):
    """认证服务 - 可能需要存储会话、令牌"""
    pass
```

### ❌ 不应该继承 BaseService（不需要数据库）

```python
# app/services/ai/voice_service.py
class VoiceService:  # ✅ 已修复
    """语音服务 - 纯内存数据"""
    pass

# app/services/ai/xunfei_service.py
class XunfeiService:  # ✅ 已修复
    """讯飞服务 - 第三方API"""
    pass

# app/services/ai/tts_service.py
class TTSService:  # ⚠️ 建议修改
    """TTS服务 - 第三方API"""
    pass

# app/services/ai/agent_service.py
class AgentService:  # ⚠️ 建议修改
    """智能体服务 - 业务逻辑"""
    pass

# app/services/ai/workflow_service.py
class WorkflowService:  # ⚠️ 建议修改
    """工作流服务 - 业务逻辑"""
    pass

# app/services/ai/rag_service.py
class RAGService:  # ⚠️ 建议修改
    """RAG服务 - 业务逻辑"""
    pass

# app/services/ai/monitoring_service.py
class MonitoringService:  # ⚠️ 建议修改
    """监控服务 - 业务逻辑"""
    pass

# app/services/token_service.py
class TokenService:  # ✅ 已正确
    """Token服务 - 不需要数据库"""
    pass
```

---

## 🎯 最佳实践

### ✅ DO（推荐做法）

1. **只在需要数据库时继承 BaseService**
   ```python
   class UserService(BaseService):
       def __init__(self, session):
           repository = Repository(User, session)
           super().__init__(repository)
   ```

2. **第三方API服务保持独立**
   ```python
   class XunfeiService:
       def __init__(self, api_key):
           self.api_key = api_key
   ```

3. **内存数据服务保持简单**
   ```python
   class VoiceService:
       def __init__(self):
           self._data = self._load_data()
   ```

### ❌ DON'T（不推荐做法）

1. **不要为了继承而继承**
   ```python
   # ❌ 错误：不需要数据库却继承了 BaseService
   class XunfeiService(BaseService):
       def __init__(self):
           super().__init__()  # 没用到 repository
   ```

2. **不要在服务中混杂数据库和业务逻辑**
   ```python
   # ❌ 错误：职责不清晰
   class TTSService(BaseService):
       def synthesize(self):
           # 调用第三方API
           result = self._call_api()
           # 又操作数据库
           self.repository.create(...)
   ```

3. **不要传入不使用的 repository**
   ```python
   # ❌ 错误：传入了 repository 但从不使用
   class VoiceService(BaseService):
       def __init__(self):
           super().__init__()  # repository=None
   ```

---

## 🔄 重构建议

如果你的服务**不需要数据库**，请按以下步骤重构：

### 步骤 1：移除 BaseService 继承
```python
# Before
from app.services.base_service import BaseService
class MyService(BaseService):
    pass

# After
class MyService:
    pass
```

### 步骤 2：移除 super().__init__() 调用
```python
# Before
def __init__(self):
    super().__init__()
    
# After
def __init__(self):
    # 直接初始化你的数据
```

### 步骤 3：移除未使用的 repository 引用
```python
# Before
result = self.repository.create(...)  # ❌ 不存在

# After  
result = self._process_data(...)  # ✅ 使用自己的方法
```

---

## 📚 总结

- **BaseService** = 数据库服务的基类
- **Repository** = 数据访问层
- **纯业务服务** = 不需要继承，保持独立

**原则**：**有数据库操作 → 继承 BaseService；无数据库操作 → 独立类**

这样的架构更清晰、更易维护！✨

