# 服务器启动指南

## ✅ 问题已修复

所有接口现在都能正常工作了！主要修复了异步路由装饰器的问题。详细修复说明请查看 `BUG_FIX_SUMMARY.md`。

## 🚀 启动服务器

### 方法1：直接启动（推荐）

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动，支持热重载（debug模式）。

### 方法2：使用批处理脚本（Windows）

```bash
start_server.bat
```

## 📖 API 文档

启动后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 测试接口

运行综合测试：
```bash
python test_final.py
```

### 快速测试单个接口

**1. 获取支持的平台列表：**
```bash
curl http://localhost:8000/api/auth/platforms
```

**2. 生成讯飞TTS鉴权（需要用工具如 Postman 或 curl）：**
```bash
curl -X POST http://localhost:8000/api/auth/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xunfei",
    "service": "tts",
    "user_id": "test_user",
    "params": {
      "text": "你好，世界",
      "voice": "x5_lingfeiyi_flow"
    }
  }'
```

## ✨ 主要功能

### 统一鉴权服务

- **POST /api/auth/generate** - 生成AI平台WebSocket鉴权
  - 支持平台：讯飞、百度、阿里云
  - 支持服务：TTS（语音合成）、ASR（语音识别）、LLM（大语言模型）
  - 返回：WebSocket URL、请求参数、过期时间等

- **GET /api/auth/platforms** - 获取支持的平台列表

### 用户管理（需要认证）

- **GET /admin/user/list** - 管理后台用户列表
- **POST /admin/user/create** - 创建用户
- **PUT /admin/user/{id}** - 更新用户
- **DELETE /admin/user/{id}** - 删除用户

## 🔧 配置

主配置文件：`config.yaml`

### 讯飞配置示例

```yaml
xunfei:
  app_id: "your_app_id"
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  endpoints:
    super_tts: "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6"
  quota:
    tts: 100
    asr: 100
    spark: 50
  defaults:
    tts:
      voice: "x5_lingfeiyi_flow"
      speed: 50
      volume: 50
      pitch: 50
      audio_format: "lame"
      oral_level: "mid"
```

## 📊 数据库

默认使用 PostgreSQL，配置在 `config.yaml`：

```yaml
database:
  type: postgresql
  host: local
  port: 5432
  database: suartix
  username: root
  password: suartixdb
```

**注意：** 当前已禁用自动迁移（`auto_migrate: false`），如需启用请修改配置。

## 🐛 排查问题

### 服务器启动失败

1. 检查数据库连接：确保PostgreSQL服务正在运行
2. 检查端口占用：确保8000端口未被占用
3. 查看日志：启动时会显示详细的错误信息

### 接口返回500错误

1. 检查服务器控制台的错误日志
2. 确保所有依赖已安装：`pip install -r requirements.txt`
3. 检查配置文件是否正确

### API返回401（未授权）

某些接口需要认证。可以：
1. 使用公开接口（如 `/api/auth/*`、`/api/voice/*`）
2. 先登录获取token，然后在请求头中添加：`Authorization: Bearer <token>`

## 📝 API分组

- **AdminAPI** (`/admin/*`) - 管理后台接口，需要管理员权限
- **API** (`/api/*`) - 通用API接口
- **WebAPI** (`/web/*`) - Web前端接口

## 🔐 认证说明

公开接口（无需认证）：
- `/docs`, `/redoc`, `/openapi.json`
- `/api/auth/*` - 鉴权服务
- `/api/voice/*` - 语音管理
- `/api/test/*` - 测试接口
- `/health` - 健康检查

其他接口需要在请求头中提供有效的JWT token。

## 📞 联系方式

如有问题，请查看：
- 详细API文档：http://localhost:8000/docs
- 修复说明：`BUG_FIX_SUMMARY.md`
- 代码规范：`.cursor/rules/base.mdc`

---

**最后更新：** 2025-10-19  
**状态：** ✅ 所有功能正常

