# TTS (文本转语音) API 文档

## 概述

TTS API 提供了强大的文本转语音功能，支持多种服务提供商，包括 OpenAI、百度、阶跃星辰、MiniMax 等。用户可以通过简单的 API 调用将文本转换为高质量的语音文件。

## 功能特性

- **多提供商支持**: 支持 OpenAI、百度、阶跃星辰、MiniMax、Azure、Google 等主流 TTS 服务
- **灵活的音色选择**: 每个提供商提供多种音色选择
- **多种音频格式**: 支持 MP3、WAV、AAC、FLAC、OPUS 等格式
- **参数可调**: 支持语速、音调、音量等参数调节
- **存储选项**: 可选择保存到服务器或直接返回音频数据
- **批量处理**: 支持批量生成语音文件
- **任务管理**: 完整的任务状态跟踪和管理
- **使用统计**: 详细的使用统计和监控

## API 端点

### 基础信息

- **基础URL**: `http://localhost:8000/api/tts`
- **认证方式**: Bearer Token (可选)
- **内容类型**: `application/json`

### 1. 生成语音

**POST** `/generate`

将文本转换为语音文件。

#### 请求参数

```json
{
  "text": "要合成的文本内容",
  "provider": "openai",
  "voice": "alloy",
  "format": "mp3",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "save_to_server": true
}
```

| 参数 | 类型 | 必填 | 说明 | 示例值 |
|------|------|------|------|--------|
| `text` | string | 是 | 要合成的文本内容 | "你好，世界！" |
| `provider` | string | 否 | TTS服务提供商 | "openai" |
| `voice` | string | 否 | 音色选择 | "alloy" |
| `format` | string | 否 | 音频格式 | "mp3" |
| `speed` | float | 否 | 语速 (0.25-4.0) | 1.0 |
| `pitch` | float | 否 | 音调 (0.5-2.0) | 1.0 |
| `volume` | float | 否 | 音量 (0.1-2.0) | 1.0 |
| `save_to_server` | boolean | 否 | 是否保存到服务器 | true |

#### 响应示例

```json
{
  "task_id": "uuid-string",
  "status": "success",
  "audio_url": "/api/tts/download/uuid-string",
  "audio_data": "base64-encoded-audio-data",
  "file_size": 1024000,
  "format": "mp3",
  "duration": 5.2,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. 获取任务状态

**GET** `/status/{task_id}`

获取指定任务的执行状态。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

#### 响应示例

```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "text": "要合成的文本内容",
  "provider": "openai",
  "voice": "alloy",
  "format": "mp3",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "save_to_server": true,
  "audio_url": "/api/tts/download/uuid-string",
  "file_size": 1024000,
  "duration": 5.2,
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": "2024-01-01T00:00:01Z",
  "completed_at": "2024-01-01T00:00:06Z"
}
```

### 3. 下载音频文件

**GET** `/download/{task_id}`

下载生成的音频文件。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

#### 响应

返回音频文件的二进制数据流。

### 4. 获取任务列表

**GET** `/tasks`

获取TTS任务列表。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 否 | 用户ID筛选 |
| `status` | string | 否 | 任务状态筛选 |
| `page` | integer | 否 | 页码 (默认: 1) |
| `per_page` | integer | 否 | 每页数量 (默认: 20) |

#### 响应示例

```json
{
  "tasks": [
    {
      "task_id": "uuid-string",
      "status": "completed",
      "text": "要合成的文本内容...",
      "provider": "openai",
      "voice": "alloy",
      "format": "mp3",
      "file_size": 1024000,
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:00:06Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

### 5. 删除任务

**DELETE** `/tasks/{task_id}`

删除指定的TTS任务。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

#### 响应示例

```json
{
  "task_id": "uuid-string",
  "message": "任务删除成功"
}
```

### 6. 获取服务提供商

**GET** `/providers`

获取支持的TTS服务提供商列表。

#### 响应示例

```json
[
  {
    "provider": "openai",
    "supported_formats": ["mp3", "opus", "aac", "flac"],
    "supported_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    "max_text_length": 4096
  },
  {
    "provider": "baidu",
    "supported_formats": ["mp3"],
    "supported_voices": ["0", "1", "3", "4"],
    "max_text_length": 1024
  }
]
```

### 7. 获取音色列表

**GET** `/voices?provider={provider}`

获取指定提供商的音色列表。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `provider` | string | 是 | 服务提供商 |

#### 响应示例

```json
{
  "provider": "openai",
  "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
}
```

### 8. 获取音频格式列表

**GET** `/formats?provider={provider}`

获取指定提供商支持的音频格式列表。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `provider` | string | 是 | 服务提供商 |

#### 响应示例

```json
{
  "provider": "openai",
  "formats": ["mp3", "opus", "aac", "flac"]
}
```

### 9. 批量生成语音

**POST** `/batch`

批量生成多个语音文件。

#### 请求参数

```json
{
  "texts": [
    "第一段文本",
    "第二段文本",
    "第三段文本"
  ],
  "provider": "openai",
  "voice": "alloy",
  "format": "mp3",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "save_to_server": true
}
```

#### 响应示例

```json
{
  "tasks": [
    {
      "task_id": "uuid-string-1",
      "status": "success"
    },
    {
      "task_id": "uuid-string-2",
      "status": "success"
    }
  ],
  "total": 3,
  "success_count": 2,
  "failed_count": 1
}
```

### 10. 健康检查

**GET** `/health`

检查TTS服务健康状态。

#### 响应示例

```json
{
  "status": "healthy",
  "service": "tts",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 11. 获取使用统计

**GET** `/stats`

获取TTS使用统计信息。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_date` | string | 否 | 开始日期 (YYYY-MM-DD) |
| `end_date` | string | 否 | 结束日期 (YYYY-MM-DD) |

#### 响应示例

```json
{
  "total_requests": 1000,
  "successful_requests": 950,
  "failed_requests": 50,
  "total_characters": 50000,
  "total_duration": 2500.5,
  "total_file_size": 50000000,
  "provider_stats": {
    "openai": {
      "requests": 600,
      "success_rate": 98.5
    },
    "baidu": {
      "requests": 400,
      "success_rate": 95.0
    }
  },
  "daily_stats": [
    {
      "date": "2024-01-01",
      "requests": 100,
      "characters": 5000
    }
  ]
}
```

## 服务提供商详情

### OpenAI TTS

- **提供商**: `openai`
- **音色**: alloy, echo, fable, onyx, nova, shimmer
- **格式**: mp3, opus, aac, flac
- **最大文本长度**: 4096字符
- **特点**: 高质量，多语言支持

### 百度TTS

- **提供商**: `baidu`
- **音色**: 0(度小美), 1(度小宇), 3(度逍遥), 4(度小娇)
- **格式**: mp3
- **最大文本长度**: 1024字符
- **特点**: 中文优化，价格便宜

### 阶跃星辰TTS

- **提供商**: `step`
- **音色**: cixingnansheng(磁性男声), tianmeinvxing(甜美女声)
- **格式**: mp3, wav
- **最大文本长度**: 2000字符
- **特点**: 国产化，中文支持好

### MiniMax TTS

- **提供商**: `minimax`
- **音色**: default
- **格式**: mp3, wav
- **最大文本长度**: 10000字符
- **特点**: 高质量合成，参数调节丰富

## 错误处理

### 常见错误码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式和值 |
| 401 | 认证失败 | 检查API密钥或Token |
| 404 | 资源不存在 | 检查任务ID或端点URL |
| 429 | 请求频率限制 | 降低请求频率 |
| 500 | 服务器内部错误 | 联系技术支持 |

### 错误响应格式

```json
{
  "error": "错误类型",
  "message": "详细错误信息",
  "code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 使用示例

### Python 示例

```python
import asyncio
import aiohttp

async def generate_speech():
    async with aiohttp.ClientSession() as session:
        url = "http://localhost:8000/api/tts/generate"
        payload = {
            "text": "你好，世界！",
            "provider": "openai",
            "voice": "alloy",
            "format": "mp3"
        }
        
        async with session.post(url, json=payload) as response:
            result = await response.json()
            print(f"任务ID: {result['task_id']}")
            
            # 检查任务状态
            status_url = f"http://localhost:8000/api/tts/status/{result['task_id']}"
            async with session.get(status_url) as status_response:
                status = await status_response.json()
                print(f"任务状态: {status['status']}")

asyncio.run(generate_speech())
```

### JavaScript 示例

```javascript
async function generateSpeech() {
    const response = await fetch('http://localhost:8000/api/tts/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: '你好，世界！',
            provider: 'openai',
            voice: 'alloy',
            format: 'mp3'
        })
    });
    
    const result = await response.json();
    console.log('任务ID:', result.task_id);
    
    // 检查任务状态
    const statusResponse = await fetch(`http://localhost:8000/api/tts/status/${result.task_id}`);
    const status = await statusResponse.json();
    console.log('任务状态:', status.status);
}

generateSpeech();
```

### cURL 示例

```bash
# 生成语音
curl -X POST "http://localhost:8000/api/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界！",
    "provider": "openai",
    "voice": "alloy",
    "format": "mp3"
  }'

# 获取任务状态
curl "http://localhost:8000/api/tts/status/{task_id}"

# 下载音频文件
curl "http://localhost:8000/api/tts/download/{task_id}" -o speech.mp3
```

## 最佳实践

### 1. 性能优化

- 使用批量API处理多个文本
- 合理设置缓存策略
- 选择合适的音频格式和参数

### 2. 错误处理

- 实现重试机制
- 监控任务状态
- 处理网络超时

### 3. 成本控制

- 选择合适的服务提供商
- 监控使用量统计
- 设置使用限制

### 4. 安全考虑

- 保护API密钥
- 验证输入文本
- 限制请求频率

## 配置说明

### 环境变量

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key

# 百度
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key

# 阶跃星辰
STEP_API_KEY=your-step-api-key

# MiniMax
MINIMAX_API_KEY=your-minimax-api-key
```

### 配置文件

参考 `config.tts.example.yaml` 文件进行配置。

## 更新日志

### v1.0.0 (2024-01-01)

- 初始版本发布
- 支持 OpenAI、百度、阶跃星辰、MiniMax 提供商
- 实现基本的TTS功能
- 支持任务管理和状态跟踪
- 提供完整的API文档和示例
