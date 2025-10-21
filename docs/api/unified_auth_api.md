# AI服务统一鉴权API文档

## 概述

统一鉴权接口提供跨平台的AI服务WebSocket连接鉴权，支持多个平台（讯飞、百度、阿里云等）的语音合成(TTS)、语音识别(ASR)、大语言模型(LLM)等服务。

**基础路径**: `/api/auth`

**优势**:
- ✅ 统一接口，多平台支持
- ✅ 参数灵活，适配不同平台
- ✅ 易于扩展新平台
- ✅ 统一的响应格式

---

## 1. 生成鉴权信息

### 接口信息

- **路径**: `POST /api/auth/generate`
- **描述**: 为指定平台和服务生成WebSocket连接鉴权信息
- **认证**: 可选（建议携带用户认证）

### 请求参数

```json
{
  "platform": "string",      // 平台名称: xunfei/baidu/aliyun/openai
  "service": "string",       // 服务类型: tts/asr/llm
  "user_id": "string",       // 用户ID（可选）
  "params": {                // 服务参数（根据平台和服务不同而不同）
    // 具体参数见下方平台说明
  }
}
```

### 响应格式

```json
{
  "success": true,
  "message": "xunfei tts 鉴权信息生成成功",
  "data": {
    "platform": "xunfei",
    "service": "tts",
    "ws_url": "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6?authorization=...",
    "request_id": "req_123456",
    "expires_at": 1698765432,
    "params": {
      // 额外参数（如需要）
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 2. 平台参数说明

### 2.1 讯飞语音 (xunfei)

#### TTS 参数

```json
{
  "platform": "xunfei",
  "service": "tts",
  "params": {
    "text": "要合成的文本",
    "voice": "x5_lingfeiyi_flow",  // 音色ID
    "speed": 50,                    // 语速 0-100
    "volume": 50,                   // 音量 0-100
    "pitch": 50,                    // 音调 0-100
    "audio_format": "lame",         // 音频格式: lame(MP3)
    "oral_level": "mid"             // 口语化等级: high/mid/low
  }
}
```

**可用音色**:
- `x5_lingfeiyi_flow` - 凌飞易（男声，流畅）
- `x5_lingfeizhe` - 凌飞哲（男声，沉稳）
- `x5_yuxia` - 语夏（女声，温柔）
- `x5_yeting` - 叶婷（女声，甜美）
- `x5_yewang` - 叶望（男声，阳光）

#### ASR 参数

```json
{
  "platform": "xunfei",
  "service": "asr",
  "params": {
    "audio_format": "raw",      // 音频格式
    "sample_rate": 16000,       // 采样率
    "language": "zh_cn",        // 语言
    "domain": "iat"             // 领域
  }
}
```

#### LLM 参数（星火大模型）

```json
{
  "platform": "xunfei",
  "service": "llm",
  "params": {
    // 星火大模型参数
  }
}
```

---

### 2.2 百度AI (baidu)

#### TTS 参数

```json
{
  "platform": "baidu",
  "service": "tts",
  "params": {
    "text": "要合成的文本",
    "voice": "0",               // 音色：0=度小宇，1=度小美，3=度逍遥，4=度丫丫
    "speed": 5,                 // 语速 0-15
    "volume": 5,                // 音量 0-15
    "pitch": 5                  // 音调 0-15
  }
}
```

> 注：百度平台配置和实现待完成

---

### 2.3 阿里云 (aliyun)

#### TTS 参数

```json
{
  "platform": "aliyun",
  "service": "tts",
  "params": {
    "text": "要合成的文本",
    "voice": "xiaoyun",         // 音色
    "format": "mp3",            // 格式：mp3/wav/pcm
    "sample_rate": 16000,       // 采样率
    "volume": 50,               // 音量 0-100
    "speech_rate": 0,           // 语速 -500~500
    "pitch_rate": 0             // 音调 -500~500
  }
}
```

> 注：阿里云平台配置和实现待完成

---

## 3. 获取平台列表

### 接口信息

- **路径**: `GET /api/auth/platforms`
- **描述**: 获取已配置的平台列表
- **认证**: 可选

### 响应格式

```json
{
  "success": true,
  "message": "获取平台列表成功",
  "data": {
    "platforms": [
      {
        "id": "xunfei",
        "name": "讯飞语音",
        "enabled": true,
        "services": ["tts", "asr", "llm"]
      },
      {
        "id": "baidu",
        "name": "百度AI",
        "enabled": false,
        "services": ["tts", "asr"]
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 4. 完整示例

### 示例1: 讯飞TTS

**请求**:
```bash
curl -X POST http://localhost:8000/api/auth/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xunfei",
    "service": "tts",
    "user_id": "user123",
    "params": {
      "text": "你好，欢迎使用AI语音服务！",
      "voice": "x5_lingfeiyi_flow",
      "speed": 50,
      "volume": 70,
      "pitch": 50,
      "audio_format": "lame",
      "oral_level": "mid"
    }
  }'
```

**响应**:
```json
{
  "success": true,
  "message": "xunfei tts 鉴权信息生成成功",
  "data": {
    "platform": "xunfei",
    "service": "tts",
    "ws_url": "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6?authorization=...",
    "request_id": "req_20240101000000_abc123",
    "expires_at": 1704067200,
    "params": {
      "header": {
        "app_id": "4f4d5a39",
        "status": 2
      },
      "parameter": {
        "oral": {"oral_level": "mid"},
        "tts": {
          "vcn": "x5_lingfeiyi_flow",
          "speed": 50,
          "volume": 70,
          "pitch": 50,
          "audio": {
            "encoding": "lame",
            "sample_rate": 24000,
            "channels": 1,
            "bit_depth": 16
          }
        }
      },
      "payload": {
        "text": {
          "encoding": "utf8",
          "text": "5L2g5aW977yM5qyi6L+O5L2/55SoQUnor63pn7PmnI3liqEh"
        }
      }
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**前端使用**:
```javascript
// 1. 获取鉴权信息
const authData = response.data;

// 2. 建立WebSocket连接
const ws = new WebSocket(authData.ws_url);

// 3. 发送请求参数（讯飞需要）
ws.onopen = () => {
  ws.send(JSON.stringify(authData.params));
};

// 4. 接收音频数据
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 处理音频数据
};
```

---

### 示例2: 讯飞ASR

**请求**:
```bash
curl -X POST http://localhost:8000/api/auth/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xunfei",
    "service": "asr",
    "params": {
      "audio_format": "raw",
      "sample_rate": 16000,
      "language": "zh_cn"
    }
  }'
```

---

## 5. 错误码

| HTTP状态码 | 错误说明 |
|-----------|---------|
| 400 | 参数验证失败 |
| 404 | 平台未配置或未注册 |
| 500 | 服务器内部错误 |

**错误响应示例**:
```json
{
  "success": false,
  "message": "不支持的平台: unknown，支持的平台: xunfei, baidu, aliyun, openai",
  "errors": [],
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 6. 旧接口迁移指南

### 旧接口（讯飞专用）
```
POST /api/xunfei/tts/auth
POST /api/xunfei/asr/auth
POST /api/xunfei/spark/auth
```

### 新接口（统一）
```
POST /api/auth/generate
```

**迁移示例**:

旧代码：
```javascript
fetch('/api/xunfei/tts/auth', {
  method: 'POST',
  body: JSON.stringify({
    text: "你好",
    voice: "x5_lingfeiyi_flow",
    speed: 50
  })
})
```

新代码：
```javascript
fetch('/api/auth/generate', {
  method: 'POST',
  body: JSON.stringify({
    platform: "xunfei",
    service: "tts",
    params: {
      text: "你好",
      voice: "x5_lingfeiyi_flow",
      speed: 50
    }
  })
})
```

---

## 7. 配置说明

在 `config.yaml` 中配置各平台的密钥：

```yaml
# 讯飞配置
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

# 百度配置（待实现）
# baidu:
#   api_key: "your_api_key"
#   secret_key: "your_secret_key"

# 阿里云配置（待实现）
# aliyun:
#   access_key_id: "your_access_key_id"
#   access_key_secret: "your_access_key_secret"
```

---

## 8. 开发计划

- [x] 讯飞语音支持
- [ ] 百度AI支持
- [ ] 阿里云支持
- [ ] OpenAI支持
- [ ] 腾讯云支持
- [ ] 微软Azure支持

