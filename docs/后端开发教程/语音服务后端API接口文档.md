# 语音服务后端API接口文档

## 概述

本文档定义了SuArtix音频创作模块所需的后端API接口规范，用于获取语音服务提供商和音色列表信息。

## 基础信息

- **基础URL**: `http://your-backend.com/api`
- **请求格式**: JSON
- **响应格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

所有API接口遵循统一的响应格式：

```json
{
  "success": true,           // 请求是否成功
  "message": "操作成功",      // 响应消息
  "data": {},               // 响应数据（根据接口不同而不同）
  "error": null,            // 错误信息（成功时为null）
  "timestamp": 1234567890   // 时间戳
}
```

## 接口列表

### 1. 获取语音服务提供商列表

获取所有可用的语音服务提供商信息。

#### 接口地址

```
GET /api/voice/providers
```

#### 请求参数

无

#### 请求示例

```bash
curl -X GET "http://localhost:3000/api/voice/providers" \
  -H "Content-Type: application/json"
```

#### 响应示例

```json
{
  "success": true,
  "message": "获取提供商列表成功",
  "data": [
    {
      "id": "xunfei",
      "name": "讯飞语音",
      "englishName": "iFLYTEK",
      "description": "科大讯飞语音合成服务，支持多种音色",
      "enabled": true,
      "iconUrl": "https://your-cdn.com/icons/xunfei.png",
      "metadata": {
        "version": "v3.0",
        "supportedLanguages": ["zh_CN", "en_US"],
        "features": ["tts", "asr"]
      }
    },
    {
      "id": "baidu",
      "name": "百度语音",
      "englishName": "Baidu",
      "description": "百度智能云语音合成服务",
      "enabled": true,
      "iconUrl": "https://your-cdn.com/icons/baidu.png",
      "metadata": {
        "version": "v2.0",
        "supportedLanguages": ["zh_CN"],
        "features": ["tts"]
      }
    },
    {
      "id": "aliyun",
      "name": "阿里云语音",
      "englishName": "Alibaba Cloud",
      "description": "阿里云智能语音服务",
      "enabled": false,
      "iconUrl": "https://your-cdn.com/icons/aliyun.png",
      "metadata": {
        "version": "v1.0",
        "supportedLanguages": ["zh_CN", "en_US"],
        "features": ["tts", "asr"]
      }
    },
    {
      "id": "tencent",
      "name": "腾讯云语音",
      "englishName": "Tencent",
      "description": "腾讯云语音合成服务",
      "enabled": false,
      "iconUrl": "https://your-cdn.com/icons/tencent.png",
      "metadata": {
        "version": "v1.5",
        "supportedLanguages": ["zh_CN"],
        "features": ["tts"]
      }
    }
  ],
  "timestamp": 1697788800
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | String | 是 | 提供商唯一标识（如 'xunfei', 'baidu'） |
| name | String | 是 | 提供商显示名称（中文） |
| englishName | String | 否 | 提供商英文名称 |
| description | String | 是 | 提供商描述信息 |
| enabled | Boolean | 是 | 是否启用（false表示暂不可用） |
| iconUrl | String | 否 | 提供商图标URL |
| metadata | Object | 否 | 额外元数据信息 |

---

### 2. 获取指定提供商的音色列表

根据提供商ID获取该提供商支持的所有音色。

#### 接口地址

```
GET /api/voice/list?provider={providerId}
```

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider | String | 是 | 提供商ID（如 'xunfei', 'baidu'） |

#### 请求示例

```bash
curl -X GET "http://localhost:3000/api/voice/list?provider=xunfei" \
  -H "Content-Type: application/json"
```

#### 响应示例

```json
{
  "success": true,
  "message": "获取音色列表成功",
  "data": {
    "providerId": "xunfei",
    "voices": [
      {
        "id": "xiaoyan",
        "name": "小燕",
        "providerId": "xunfei",
        "language": "zh_CN",
        "gender": "female",
        "description": "温柔女声，适合叙事",
        "category": "播音员",
        "tags": ["温柔", "标准"],
        "previewUrl": "https://your-cdn.com/previews/xiaoyan.mp3",
        "isPremium": false,
        "voiceParams": {
          "vcn": "xiaoyan",
          "speed": 50,
          "volume": 50,
          "pitch": 50
        }
      },
      {
        "id": "aisjiuxu",
        "name": "许久",
        "providerId": "xunfei",
        "language": "zh_CN",
        "gender": "male",
        "description": "磁性男声，适合情感类内容",
        "category": "主播",
        "tags": ["磁性", "情感", "深沉"],
        "previewUrl": "https://your-cdn.com/previews/aisjiuxu.mp3",
        "isPremium": true,
        "voiceParams": {
          "vcn": "aisjiuxu",
          "speed": 50,
          "volume": 50,
          "pitch": 50
        }
      },
      {
        "id": "aisxping",
        "name": "小萍",
        "providerId": "xunfei",
        "language": "zh_CN",
        "gender": "female",
        "description": "活泼女声，适合儿童内容",
        "category": "儿童",
        "tags": ["活泼", "可爱", "清脆"],
        "previewUrl": "https://your-cdn.com/previews/aisxping.mp3",
        "isPremium": false,
        "voiceParams": {
          "vcn": "aisxping",
          "speed": 50,
          "volume": 50,
          "pitch": 50
        }
      },
      {
        "id": "aisjinger",
        "name": "京儿",
        "providerId": "xunfei",
        "language": "zh_CN",
        "gender": "female",
        "description": "京腔女声，适合说书",
        "category": "播音员",
        "tags": ["京腔", "说书", "韵味"],
        "previewUrl": "https://your-cdn.com/previews/aisjinger.mp3",
        "isPremium": false,
        "voiceParams": {
          "vcn": "aisjinger",
          "speed": 50,
          "volume": 50,
          "pitch": 50
        }
      },
      {
        "id": "aisbabyxu",
        "name": "许小宝",
        "providerId": "xunfei",
        "language": "zh_CN",
        "gender": "male",
        "description": "童声男孩，适合儿童故事",
        "category": "儿童",
        "tags": ["童声", "故事", "纯真"],
        "previewUrl": "https://your-cdn.com/previews/aisbabyxu.mp3",
        "isPremium": true,
        "voiceParams": {
          "vcn": "aisbabyxu",
          "speed": 50,
          "volume": 50,
          "pitch": 50
        }
      }
    ],
    "total": 5,
    "metadata": {
      "categories": ["播音员", "主播", "儿童"],
      "languages": ["zh_CN"],
      "premiumCount": 2,
      "freeCount": 3
    }
  },
  "timestamp": 1697788800
}
```

#### 字段说明

**响应根对象 (data)**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| providerId | String | 是 | 提供商ID |
| voices | Array | 是 | 音色列表 |
| total | Number | 否 | 音色总数 |
| metadata | Object | 否 | 额外元数据 |

**音色对象 (voices\[\])**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | String | 是 | 音色唯一标识 |
| name | String | 是 | 音色显示名称 |
| providerId | String | 是 | 所属提供商ID |
| language | String | 是 | 支持的语言（ISO 639-1，如 'zh_CN', 'en_US'） |
| gender | String | 是 | 性别：'male', 'female', 'neutral' |
| description | String | 否 | 音色描述 |
| category | String | 否 | 音色类别（如：播音员、主播、儿童等） |
| tags | Array&lt;String&gt; | 否 | 音色标签（如：温柔、活泼、专业等） |
| previewUrl | String | 否 | 试听音频URL |
| isPremium | Boolean | 否 | 是否为付费音色（默认false） |
| voiceParams | Object | 否 | 音色特定参数（根据提供商不同而不同） |

---

## 错误响应

当请求失败时，返回错误响应：

```json
{
  "success": false,
  "message": "错误描述信息",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "detail": "详细错误信息"
  },
  "timestamp": 1697788800
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| INVALID_PROVIDER | 400 | 无效的提供商ID |
| PROVIDER_NOT_FOUND | 404 | 提供商不存在 |
| PROVIDER_DISABLED | 403 | 提供商未启用 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| DATABASE_ERROR | 500 | 数据库错误 |

---

## 百度语音服务示例

获取百度语音的音色列表：

```bash
curl -X GET "http://localhost:3000/api/voice/list?provider=baidu" \
  -H "Content-Type: application/json"
```

响应：

```json
{
  "success": true,
  "message": "获取音色列表成功",
  "data": {
    "providerId": "baidu",
    "voices": [
      {
        "id": "duyy",
        "name": "度逍遥",
        "providerId": "baidu",
        "language": "zh_CN",
        "gender": "male",
        "description": "情感男声，富有表现力",
        "category": "播音员",
        "tags": ["情感", "磁性", "专业"],
        "previewUrl": "https://your-cdn.com/previews/duyy.mp3",
        "isPremium": false,
        "voiceParams": {
          "per": "5003",
          "spd": "5",
          "pit": "5",
          "vol": "5"
        }
      },
      {
        "id": "duxiaoyao",
        "name": "度小娇",
        "providerId": "baidu",
        "language": "zh_CN",
        "gender": "female",
        "description": "甜美女声，声音甜美可人",
        "category": "主播",
        "tags": ["甜美", "活泼", "温柔"],
        "previewUrl": "https://your-cdn.com/previews/duxiaoyao.mp3",
        "isPremium": false,
        "voiceParams": {
          "per": "5118",
          "spd": "5",
          "pit": "5",
          "vol": "5"
        }
      }
    ],
    "total": 2,
    "metadata": {
      "categories": ["播音员", "主播"],
      "languages": ["zh_CN"],
      "premiumCount": 0,
      "freeCount": 2
    }
  },
  "timestamp": 1697788800
}
```

---

## 实现建议

### 后端实现要点

1. **数据存储**：建议使用数据库存储提供商和音色信息，便于动态管理
2. **缓存策略**：音色列表变化不频繁，建议添加Redis缓存（TTL: 1小时）
3. **鉴权**：根据业务需求添加API鉴权（JWT Token等）
4. **限流**：添加请求限流保护，防止接口被滥用
5. **日志**：记录所有API调用日志，便于问题排查

### 数据库设计参考

**voice_providers 表**

```sql
CREATE TABLE voice_providers (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  english_name VARCHAR(100),
  description TEXT,
  enabled BOOLEAN DEFAULT true,
  icon_url VARCHAR(255),
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**voice_models 表**

```sql
CREATE TABLE voice_models (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  provider_id VARCHAR(50) NOT NULL,
  language VARCHAR(20) NOT NULL,
  gender VARCHAR(20) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  tags JSON,
  preview_url VARCHAR(255),
  is_premium BOOLEAN DEFAULT false,
  voice_params JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (provider_id) REFERENCES voice_providers(id)
);
```

### 示例数据插入

```sql
-- 插入提供商
INSERT INTO voice_providers (id, name, english_name, description, enabled) VALUES
('xunfei', '讯飞语音', 'iFLYTEK', '科大讯飞语音合成服务，支持多种音色', true),
('baidu', '百度语音', 'Baidu', '百度智能云语音合成服务', true),
('aliyun', '阿里云语音', 'Alibaba Cloud', '阿里云智能语音服务', false),
('tencent', '腾讯云语音', 'Tencent', '腾讯云语音合成服务', false);

-- 插入讯飞音色
INSERT INTO voice_models (id, name, provider_id, language, gender, description, category, tags, is_premium, voice_params) VALUES
('xiaoyan', '小燕', 'xunfei', 'zh_CN', 'female', '温柔女声，适合叙事', '播音员', '["温柔", "标准"]', false, '{"vcn": "xiaoyan"}'),
('aisjiuxu', '许久', 'xunfei', 'zh_CN', 'male', '磁性男声，适合情感类', '主播', '["磁性", "情感"]', true, '{"vcn": "aisjiuxu"}'),
('aisxping', '小萍', 'xunfei', 'zh_CN', 'female', '活泼女声，适合儿童内容', '儿童', '["活泼", "可爱"]', false, '{"vcn": "aisxping"}');

-- 插入百度音色
INSERT INTO voice_models (id, name, provider_id, language, gender, description, category, tags, is_premium, voice_params) VALUES
('duyy', '度逍遥', 'baidu', 'zh_CN', 'male', '情感男声', '播音员', '["情感", "磁性"]', false, '{"per": "5003"}'),
('duxiaoyao', '度小娇', 'baidu', 'zh_CN', 'female', '甜美女声', '主播', '["甜美", "活泼"]', false, '{"per": "5118"}');
```

---

## 注意事项

1. 所有字符串字段需要进行XSS防护
2. URL字段需要验证格式合法性
3. `voiceParams` 字段根据不同提供商有不同的结构，前端应灵活处理
4. 建议提供商图标使用CDN加速
5. 音色试听URL应支持跨域访问（CORS）
6. 考虑添加分页支持（当音色数量较多时）
7. 建议添加音色搜索和筛选功能

---

## 版本历史

- **v1.0** (2024-10-19): 初始版本，定义基础接口

