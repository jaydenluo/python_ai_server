# 音色管理API文档

## 📋 概述

本文档定义音色管理相关的API接口，用于获取语音服务提供商和音色列表信息。

遵循 [API接口规范](./API_SPECIFICATION.md)。

---

## 🌐 基础信息

- **基础URL**: `http://your-backend.com/api`
- **响应格式**: 遵循统一响应格式（见API规范）

---

## 📚 接口列表

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
curl -X GET "http://localhost:8000/api/voice/providers" \
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
      "english_name": "iFLYTEK",
      "description": "科大讯飞超拟人语音合成服务，支持高质量中文语音合成",
      "enabled": true,
      "icon_url": null,
      "metadata": {
        "version": "v3.5",
        "supported_languages": ["zh_CN"],
        "features": ["tts", "super_tts"],
        "pricing": {
          "tts": "2元/万字符",
          "clone": "5元/个",
          "long_text": "3元/万字符（10万字超长文本）"
        }
      }
    }
  ],
  "errors": [],
  "meta": {},
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

#### 字段说明

**提供商对象 (data[])**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 提供商唯一标识 |
| name | String | 提供商中文名称 |
| english_name | String | 提供商英文名称 |
| description | String | 提供商描述信息 |
| enabled | Boolean | 是否启用 |
| icon_url | String/null | 提供商图标URL |
| metadata | Object | 元数据信息 |
| metadata.version | String | API版本 |
| metadata.supported_languages | Array | 支持的语言列表 |
| metadata.features | Array | 支持的功能列表 |
| metadata.pricing | Object | 价格信息 |

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
| provider | String | 是 | 提供商ID（如 'xunfei'） |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/voice/list?provider=xunfei" \
  -H "Content-Type: application/json"
```

#### 响应示例

```json
{
  "success": true,
  "message": "获取音色列表成功",
  "data": {
    "provider_id": "xunfei",
    "voices": [
      {
        "id": "x5_lingfeiyi_flow",
        "name": "凌飞易",
        "provider_id": "xunfei",
        "language": "zh_CN",
        "gender": "male",
        "description": "流畅自然的男声，适合新闻播报、有声读物",
        "category": "超拟人",
        "tags": ["流畅", "自然", "专业", "标准"],
        "preview_url": null,
        "is_premium": true,
        "voice_params": {
          "vcn": "x5_lingfeiyi_flow",
          "speed": 50,
          "volume": 50,
          "pitch": 50,
          "oral_level": "mid"
        },
        "metadata": {
          "version": "x5系列",
          "recommended_scenarios": ["新闻播报", "有声读物", "教育培训"],
          "sample_rate": 24000,
          "audio_format": "MP3"
        }
      },
      {
        "id": "x5_xiaoyan_flow",
        "name": "小研",
        "provider_id": "xunfei",
        "language": "zh_CN",
        "gender": "female",
        "description": "流畅自然的女声，温柔清晰，适合客服、讲解",
        "category": "超拟人",
        "tags": ["温柔", "清晰", "亲和", "标准"],
        "preview_url": null,
        "is_premium": true,
        "voice_params": {
          "vcn": "x5_xiaoyan_flow",
          "speed": 50,
          "volume": 50,
          "pitch": 50,
          "oral_level": "mid"
        },
        "metadata": {
          "version": "x5系列",
          "recommended_scenarios": ["客服语音", "产品讲解", "导航提示"],
          "sample_rate": 24000,
          "audio_format": "MP3"
        }
      }
    ],
    "total": 8,
    "metadata": {
      "categories": ["超拟人"],
      "languages": ["zh_CN"],
      "premium_count": 8,
      "free_count": 0
    }
  },
  "errors": [],
  "meta": {},
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

#### 字段说明

**响应根对象 (data)**

| 字段 | 类型 | 说明 |
|------|------|------|
| provider_id | String | 提供商ID |
| voices | Array | 音色列表 |
| total | Number | 音色总数 |
| metadata | Object | 统计元数据 |

**音色对象 (voices[])**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 音色唯一标识 |
| name | String | 音色显示名称 |
| provider_id | String | 所属提供商ID |
| language | String | 支持的语言（ISO 639-1） |
| gender | String | 性别：'male', 'female', 'neutral' |
| description | String | 音色描述 |
| category | String | 音色类别 |
| tags | Array&lt;String&gt; | 音色标签 |
| preview_url | String/null | 试听音频URL |
| is_premium | Boolean | 是否为付费音色 |
| voice_params | Object | 音色参数（用于TTS请求） |
| metadata | Object | 额外元数据 |

**voice_params 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| vcn | String | 音色标识符（讯飞专用） |
| speed | Number | 默认语速 (0-100) |
| volume | Number | 默认音量 (0-100) |
| pitch | Number | 默认音调 (0-100) |
| oral_level | String | 默认口语化等级 (high/mid/low) |

**metadata 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| version | String | 音色版本 |
| recommended_scenarios | Array | 推荐使用场景 |
| sample_rate | Number | 采样率 (Hz) |
| audio_format | String | 音频格式 |

---

### 3. 获取音色详情

获取单个音色的详细信息。

#### 接口地址

```
GET /api/voice/detail/{voice_id}?provider={providerId}
```

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| voice_id | String | 是 | 音色ID（路径参数） |
| provider | String | 否 | 提供商ID（查询参数，可选） |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/api/voice/detail/x5_lingfeiyi_flow?provider=xunfei" \
  -H "Content-Type: application/json"
```

#### 响应示例

```json
{
  "success": true,
  "message": "获取音色详情成功",
  "data": {
    "id": "x5_lingfeiyi_flow",
    "name": "凌飞易",
    "provider_id": "xunfei",
    "language": "zh_CN",
    "gender": "male",
    "description": "流畅自然的男声，适合新闻播报、有声读物",
    "category": "超拟人",
    "tags": ["流畅", "自然", "专业", "标准"],
    "preview_url": null,
    "is_premium": true,
    "voice_params": {
      "vcn": "x5_lingfeiyi_flow",
      "speed": 50,
      "volume": 50,
      "pitch": 50,
      "oral_level": "mid"
    },
    "metadata": {
      "version": "x5系列",
      "recommended_scenarios": ["新闻播报", "有声读物", "教育培训"],
      "sample_rate": 24000,
      "audio_format": "MP3"
    }
  },
  "errors": [],
  "meta": {},
  "status_code": 200,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

---

## ⚠️ 错误响应

### 缺少provider参数

```json
{
  "success": false,
  "message": "缺少provider参数",
  "data": null,
  "errors": ["provider参数不能为空"],
  "meta": {},
  "status_code": 400,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 提供商不存在

```json
{
  "success": false,
  "message": "提供商不存在或未启用",
  "data": null,
  "errors": ["提供商 'invalid_provider' 不存在"],
  "meta": {},
  "status_code": 404,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

### 音色不存在

```json
{
  "success": false,
  "message": "音色不存在",
  "data": null,
  "errors": ["音色 'invalid_voice' 不存在"],
  "meta": {},
  "status_code": 404,
  "timestamp": "2024-10-19T12:00:00.000Z"
}
```

---

## 📊 音色分类说明

### 讯飞x5系列音色

| 音色ID | 名称 | 性别 | 特点 | 推荐场景 |
|--------|------|------|------|----------|
| x5_lingfeiyi_flow | 凌飞易 | 男 | 流畅自然 | 新闻播报、有声读物 |
| x5_lingfeiyi | 凌飞易（情感版） | 男 | 富有情感 | 情感故事、戏剧朗读 |
| x5_xiaoyan_flow | 小研 | 女 | 温柔清晰 | 客服语音、产品讲解 |
| x5_xiaoyan | 小研（情感版） | 女 | 甜美温暖 | 情感文章、儿童故事 |
| x5_xiaoyu_flow | 小雨 | 女 | 清新温柔 | 睡前故事、冥想引导 |
| x5_xiaoyu | 小雨（情感版） | 女 | 活泼生动 | 青春文学、活力广告 |
| x5_xiaochen_flow | 晓辰 | 女 | 知性优雅 | 商务演讲、专业讲座 |
| x5_xiaochen | 晓辰（情感版） | 女 | 温暖亲切 | 心灵鸡汤、情感电台 |

### 音色标签说明

- **流畅**: 语音自然流畅，适合长文本朗读
- **情感**: 富有情感表现力，适合情感内容
- **温柔**: 声音柔和，适合舒缓类内容
- **专业**: 发音标准清晰，适合正式场合
- **活泼**: 充满活力，适合轻松内容
- **知性**: 成熟稳重，适合专业内容

---

## 💡 使用建议

### 1. 前端展示

- 按性别分类展示音色
- 提供标签筛选功能
- 显示推荐使用场景
- 支持试听功能（如果有preview_url）

### 2. 音色选择

- 根据内容类型推荐合适的音色
- 新闻类 → 流畅版音色
- 情感类 → 情感版音色
- 专业类 → 知性音色

### 3. 参数调整

- 使用 `voice_params` 中的默认值
- 允许用户微调 speed、volume、pitch
- oral_level 根据内容特点选择

---

## 🔗 相关文档

- [API接口规范](./API_SPECIFICATION.md)
- [讯飞语音API文档](./xunfei_api.md)
- [Flutter前端集成指南](../guides/xunfei_flutter_guide.md)

---

## 📝 版本历史

- **v1.0** (2024-10-19): 初始版本，支持讯飞x5系列音色

