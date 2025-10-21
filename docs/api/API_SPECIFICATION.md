# API接口规范文档

## 📋 概述

本文档定义了本项目所有API接口的统一规范，包括请求格式、响应格式、错误处理等。

---

## 🌐 基础信息

- **基础URL**: `http://your-backend.com/api`
- **请求格式**: JSON
- **响应格式**: JSON
- **字符编码**: UTF-8
- **HTTP方法**: GET, POST, PUT, DELETE, PATCH
- **认证方式**: JWT Token (可选)

---

## 📦 统一响应格式

本项目所有API接口遵循统一的响应格式：

### 成功响应

```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "errors": [],
  "meta": {},
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 错误响应

```json
{
  "success": false,
  "message": "操作失败",
  "data": null,
  "errors": ["错误信息1", "错误信息2"],
  "meta": {},
  "status_code": 400,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| success | Boolean | 是 | 请求是否成功 |
| message | String | 是 | 响应消息说明 |
| data | Any | 是 | 响应数据，成功时包含具体数据，失败时为null |
| errors | Array&lt;String&gt; | 是 | 错误信息数组，成功时为空数组[] |
| meta | Object | 是 | 元数据信息，如分页信息、统计数据等 |
| status_code | Number | 是 | HTTP状态码 |
| timestamp | String | 是 | 响应时间戳 (ISO 8601格式) |

---

## 🔢 HTTP状态码

本项目使用标准HTTP状态码：

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功（无返回内容） |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权，需要登录 |
| 403 | Forbidden | 无权访问该资源 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

---

## 📝 请求规范

### 请求头 (Headers)

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}  # 需要认证的接口
```

### URL参数 (Query Parameters)

使用标准URL编码：

```
GET /api/resources?page=1&per_page=20&sort=created_at&order=desc
```

### 请求体 (Request Body)

使用JSON格式：

```json
{
  "field1": "value1",
  "field2": 123,
  "field3": true
}
```

---

## 🎯 分页规范

### 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | Number | 1 | 当前页码 |
| per_page | Number | 20 | 每页条数 |
| sort | String | id | 排序字段 |
| order | String | asc | 排序方向 (asc/desc) |

### 响应格式

```json
{
  "success": true,
  "message": "获取列表成功",
  "data": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
  ],
  "meta": {
    "current_page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  },
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

---

## ⚠️ 错误处理规范

### 错误响应格式

```json
{
  "success": false,
  "message": "错误的主要描述",
  "data": null,
  "errors": [
    "具体错误信息1",
    "具体错误信息2"
  ],
  "meta": {
    "error_code": "VALIDATION_ERROR",
    "error_details": {
      "field1": "该字段不能为空",
      "field2": "该字段格式不正确"
    }
  },
  "status_code": 422,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 常见错误码

| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| VALIDATION_ERROR | 422 | 数据验证失败 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 无权限访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| RATE_LIMIT_EXCEEDED | 429 | 超过限流 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

---

## 🔐 认证规范

### JWT Token认证

#### 获取Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

响应：

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2024-10-20T12:00:00.000Z",
    "user": {
      "id": 1,
      "username": "user@example.com",
      "role": "user"
    }
  },
  "status_code": 200
}
```

#### 使用Token

```http
GET /api/protected-resource
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📊 数据类型规范

### 日期时间格式

- **ISO 8601格式**: `2024-10-19T12:00:00.000Z`
- **Unix时间戳**: 仅用于性能敏感场景

### 布尔值

- 使用 `true` / `false`，不使用 `1` / `0`

### 空值

- 使用 `null`，不使用空字符串 `""`

### 数组

- 空数组使用 `[]`，不使用 `null`

### 对象

- 空对象使用 `{}`，不使用 `null`

---

## 🎨 命名规范

### URL命名

- 使用小写字母
- 多个单词使用连字符 `-` 分隔
- 使用名词，不使用动词

```
✅ /api/voice-providers
✅ /api/user-profiles
❌ /api/getVoiceProviders
❌ /api/UserProfiles
```

### JSON字段命名

- 使用 `snake_case` (下划线命名)

```json
{
  "user_id": 1,
  "first_name": "John",
  "created_at": "2024-10-19T12:00:00.000Z"
}
```

---

## 📚 接口示例

### 示例1: 获取资源列表

**请求：**

```http
GET /api/voice/providers?page=1&per_page=10
Authorization: Bearer {token}
```

**响应：**

```json
{
  "success": true,
  "message": "获取提供商列表成功",
  "data": [
    {
      "id": "xunfei",
      "name": "讯飞语音",
      "description": "科大讯飞语音合成服务",
      "enabled": true
    },
    {
      "id": "baidu",
      "name": "百度语音",
      "description": "百度智能云语音合成服务",
      "enabled": true
    }
  ],
  "errors": [],
  "meta": {
    "current_page": 1,
    "per_page": 10,
    "total": 2,
    "total_pages": 1
  },
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 示例2: 创建资源

**请求：**

```http
POST /api/voice/favorites
Content-Type: application/json
Authorization: Bearer {token}

{
  "voice_id": "x5_lingfeiyi_flow",
  "provider_id": "xunfei"
}
```

**响应：**

```json
{
  "success": true,
  "message": "添加收藏成功",
  "data": {
    "id": 123,
    "user_id": 1,
    "voice_id": "x5_lingfeiyi_flow",
    "provider_id": "xunfei",
    "created_at": "2024-10-19T12:00:00.000Z"
  },
  "errors": [],
  "meta": {},
  "status_code": 201,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 示例3: 更新资源

**请求：**

```http
PUT /api/user/profile
Content-Type: application/json
Authorization: Bearer {token}

{
  "nickname": "新昵称",
  "avatar": "https://example.com/avatar.jpg"
}
```

**响应：**

```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "username": "user@example.com",
    "nickname": "新昵称",
    "avatar": "https://example.com/avatar.jpg",
    "updated_at": "2024-10-19T12:00:00.000Z"
  },
  "errors": [],
  "meta": {},
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 示例4: 删除资源

**请求：**

```http
DELETE /api/voice/favorites/123
Authorization: Bearer {token}
```

**响应：**

```json
{
  "success": true,
  "message": "删除成功",
  "data": null,
  "errors": [],
  "meta": {},
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 示例5: 验证失败

**请求：**

```http
POST /api/voice/generate
Content-Type: application/json

{
  "text": "",
  "voice": "invalid_voice"
}
```

**响应：**

```json
{
  "success": false,
  "message": "数据验证失败",
  "data": null,
  "errors": [
    "text字段不能为空",
    "voice字段值无效"
  ],
  "meta": {
    "error_code": "VALIDATION_ERROR",
    "error_details": {
      "text": "该字段不能为空",
      "voice": "音色不存在或未启用"
    }
  },
  "status_code": 422,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

---

## 🔒 安全规范

### 1. HTTPS

- 生产环境必须使用HTTPS
- 禁止在URL中传递敏感信息

### 2. API密钥

- 敏感API密钥存储在后端
- 不在前端暴露任何密钥

### 3. 输入验证

- 所有输入必须验证
- 防止SQL注入、XSS攻击

### 4. 限流

- 实施请求频率限制
- 返回429状态码和重试时间

```json
{
  "success": false,
  "message": "请求过于频繁，请稍后再试",
  "data": null,
  "errors": ["超过每分钟60次请求限制"],
  "meta": {
    "retry_after": 30,
    "limit": 60,
    "window": "1 minute"
  },
  "status_code": 429,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

---

## 📈 性能优化建议

### 1. 缓存策略

- 使用Redis缓存频繁访问的数据
- 设置合理的缓存过期时间
- 响应头添加缓存控制信息

```http
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### 2. 分页限制

- 默认每页20条
- 最大每页100条
- 大数据集使用游标分页

### 3. 字段过滤

支持通过参数选择返回字段：

```
GET /api/users?fields=id,name,email
```

### 4. 压缩

启用Gzip压缩：

```http
Accept-Encoding: gzip, deflate
```

---

## 🧪 测试规范

### 请求示例 (cURL)

```bash
# GET请求
curl -X GET "http://localhost:8000/api/voice/providers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}"

# POST请求
curl -X POST "http://localhost:8000/api/xunfei/tts/auth" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "text": "你好世界",
    "voice": "x5_lingfeiyi_flow"
  }'
```

---

## 📖 版本控制

### URL版本控制

```
/api/v1/voice/providers
/api/v2/voice/providers
```

### 响应头版本

```http
API-Version: 1.0
```

---

## 📋 最佳实践清单

- ✅ 使用统一的响应格式
- ✅ 正确使用HTTP状态码
- ✅ 提供清晰的错误信息
- ✅ 使用标准的命名规范
- ✅ 实施认证和授权
- ✅ 添加请求限流
- ✅ 记录API访问日志
- ✅ 提供完整的API文档
- ✅ 支持分页和过滤
- ✅ 验证所有输入数据
- ✅ 使用HTTPS加密传输
- ✅ 实施缓存策略
- ✅ 监控API性能
- ✅ 版本化API接口

---

## 📚 相关文档

- [讯飞语音API文档](./xunfei_api.md)
- [认证授权文档](../guides/authentication.md)
- [错误处理指南](../guides/error-handling.md)

---

## 📝 变更历史

- **v1.0** (2024-10-19): 初始版本，定义基础API规范

---

## 💬 支持

如有疑问或建议，请提交Issue或Pull Request。

