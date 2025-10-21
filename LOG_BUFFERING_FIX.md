# 日志缓冲问题修复

## 🔍 问题描述

运行 `python main.py` 后：
- 服务器正常启动（`Application startup complete`）
- API 可以正常访问
- **但是没有打印我们的自定义日志**（数据库初始化、扫描控制器、启动信息等）

## 🎯 根本原因

### Python 输出缓冲

Python 默认使用**行缓冲**（line buffering）或**块缓冲**（block buffering），导致：
- `print()` 的输出不是立即显示
- 输出会累积到缓冲区
- 只有当缓冲区满或程序结束时才刷新

### Uvicorn Reload 模式

当 `debug: true` 时，uvicorn 使用 reload 模式：
- 启动**两个进程**：主进程（监控）+ 工作进程（运行应用）
- 工作进程的输出可能被重定向或延迟
- 日志顺序可能混乱

## ✅ 解决方案

### 1. 启用行缓冲

在 `main.py` 中：
```python
# 之前
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 现在 - 添加 line_buffering=True
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
```

### 2. 强制刷新输出

所有重要日志使用 `sys.stdout.write()` + `flush()`：

```python
# 之前
print("🔧 初始化数据库...")

# 现在
import sys
msg = "🔧 初始化数据库...\n"
sys.stdout.write(msg)
sys.stdout.flush()
```

### 3. 修改的文件

#### `main.py`
- 启用行缓冲
- 使用 `sys.stdout.write()` + `flush()`

#### `app/framework.py`
- `_register_startup_event()` - 启动信息使用 `write()` + `flush()`
- `_init_database()` - 数据库初始化日志使用 `write()` + `flush()`

#### `app/core/routing/route_decorators.py`
- `scan_and_register_all()` - 扫描日志使用 `write()` + `flush()`

## 📊 现在的效果

运行 `python main.py` 应该立即看到：

```
🚀 启动Python AI开发框架
📖 API文档: http://localhost:8000/docs
🔧 路由信息: http://localhost:8000/api/v1/info

INFO:     Will watch for changes in these directories: ['D:\\AI\\python_base_server']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
🔧 初始化数据库...
📊 数据库类型: postgresql
✅ 数据库连接成功
🔍 开始自动扫描控制器...
⚠️ 跳过模块 app.controller.api.tts_controller: xxx
✅ 扫描完成，共注册 17 个路由
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

======================================================================
🎉 服务已正常启动，等待访问
======================================================================
📡 本地访问: http://localhost:8000
📡 局域网访问: http://192.168.1.100:8000
📖 API 文档: http://localhost:8000/docs
📖 ReDoc 文档: http://localhost:8000/redoc
======================================================================
💡 按 Ctrl+C 停止服务器

📝 GET /docs - 127.0.0.1
✅ GET /docs - 200 (0.023s)
```

## 🔧 如果还是看不到日志

### 方法1：禁用 Reload 模式

修改 `config.yaml`：
```yaml
app:
  debug: false  # 改为 false
```

这样 uvicorn 不会启动两个进程，日志会正常显示。

### 方法2：运行时禁用缓冲

```bash
# Windows
set PYTHONUNBUFFERED=1
python main.py

# Linux/Mac
PYTHONUNBUFFERED=1 python main.py
```

### 方法3：使用 -u 参数

```bash
python -u main.py
```

`-u` 参数强制 Python 使用无缓冲模式。

## 💡 技术细节

### Python 缓冲模式

| 模式 | 说明 | 何时刷新 |
|------|------|----------|
| 无缓冲 | `buffering=0` | 立即 |
| 行缓冲 | `line_buffering=True` | 遇到 `\n` 时 |
| 块缓冲 | 默认 | 缓冲区满（通常8KB）|

### sys.stdout.write() vs print()

```python
# print() - 使用缓冲
print("Hello")  # 可能延迟显示

# sys.stdout.write() + flush() - 立即显示
sys.stdout.write("Hello\n")
sys.stdout.flush()  # 立即刷新
```

## ✅ 验证

1. 运行 `python main.py`
2. 应该**立即**看到所有启动日志
3. 访问 API，应该**立即**看到访问日志

---

**最后更新：** 2025-10-20  
**状态：** ✅ 已修复

