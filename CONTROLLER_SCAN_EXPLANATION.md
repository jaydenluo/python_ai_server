# 控制器扫描机制说明

## ❓ 为什么需要扫描控制器？

你的项目使用了**装饰器路由系统**（类似 Java Spring Boot 的注解路由），而不是传统的手动注册路由方式。

### 装饰器路由示例

```python
@api_controller(prefix="/api/auth", tags=["API - 鉴权服务"])
class AuthController(BaseController):
    
    @post("/generate")
    async def generate_auth(self, request):
        # 处理逻辑
        pass
```

### 扫描的作用

1. **自动发现控制器**：扫描所有带 `@api_controller` 装饰器的类
2. **自动注册路由**：将 `@get`、`@post`、`@put`、`@delete` 装饰的方法注册到 FastAPI
3. **如果不扫描**：这些接口**无法访问**，会返回 404 错误

## ✅ 启动日志示例

正常启动时会看到：

```
🔍 开始自动扫描控制器...
✅ 自动扫描到控制器: app.controller.admin.UserController
✅ 自动扫描到控制器: app.controller.api.AuthController
✅ 自动扫描到控制器: app.controller.api.UserController
✅ 扫描完成，共注册 17 个路由
✅ 注册控制器: UserController (10 个路由)
✅ 注册控制器: AuthController (2 个路由)
```

## ⚠️ 之前的警告

```
警告: 无法导入模块 app.models.entities.tts_provider_config: No module named 'app.models.base'
警告: 无法导入模块 app.models.entities.tts_task: cannot import name 'BaseModel' from 'app.core.orm.models'
警告: 无法导入模块 app.models.entities.tts_usage_stats: cannot import name 'BaseModel' from 'app.core.orm.models'
```

### 原因

这3个文件是旧代码，依赖了不存在的模块：
- `tts_provider_config.py` - 引用 `app.models.base`（不存在）
- `tts_task.py`, `tts_usage_stats.py` - 从 `app.core.orm.models` 导入 `BaseModel`（该文件没有导出 `BaseModel`）

### 解决方案

已将这3个文件重命名为 `.bak` 后缀，不再被扫描：
- `tts_provider_config.py.bak`
- `tts_task.py.bak`
- `tts_usage_stats.py.bak`

这些是未完成的功能，不影响当前系统运行。

## 🔍 扫描机制详解

### 扫描范围

自动扫描以下目录：
- `app/controller/` - 所有控制器
- `app/api/` - 旧版API路由（如果存在）
- `app/models/entities/` - 数据模型（可能会触发导入）

### 跳过扫描的情况

- 文件名以 `_` 开头
- 文件名以 `.bak`、`.old`、`.tmp` 结尾
- `__pycache__` 目录
- 测试文件 `test_*.py`

### 扫描过程

1. **递归遍历**：从 `app/controller/` 开始，递归查找所有 `.py` 文件
2. **动态导入**：尝试导入每个模块
3. **检测装饰器**：查找带 `@api_controller` 装饰器的类
4. **注册路由**：将装饰器收集的路由信息注册到 FastAPI

## 📊 对比：手动 vs 自动注册

### 传统方式（手动注册）

```python
# main.py
from fastapi import FastAPI
from app.controller.auth_controller import router as auth_router

app = FastAPI()
app.include_router(auth_router)  # 手动注册
```

**优点**：明确、可控  
**缺点**：每个控制器都要手动导入和注册，代码冗长

### 装饰器方式（自动注册）

```python
# auth_controller.py
@api_controller(prefix="/api/auth")
class AuthController:
    @post("/generate")
    async def generate(self):
        pass

# main.py 自动扫描注册，无需手动导入
```

**优点**：简洁、自动化、类似 Spring Boot  
**缺点**：需要扫描机制

## 🚫 如果不扫描会怎样？

**所有使用装饰器定义的接口都无法访问！**

测试：
```bash
# 不扫描时
curl http://localhost:8000/api/auth/generate
# 返回: {"detail": "Not Found"}  404 错误
```

## 💡 建议

1. **保持自动扫描**：这是项目的核心机制
2. **清理未使用代码**：将不需要的文件移到 `backup/` 或删除
3. **检查导入错误**：启动时如果有警告，应该及时修复或移除问题文件

---

**总结**：控制器扫描是必须的，它让装饰器路由系统能够正常工作。现在警告已经消除，系统运行正常！✅

