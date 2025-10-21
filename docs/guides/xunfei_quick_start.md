# 讯飞超拟人TTS快速开始指南

> ⚠️ **重要更新**: 接口已升级为统一鉴权接口，请使用新接口
> 
> 新文档: [统一鉴权API文档](../api/unified_auth_api.md)
> 
> 新接口: `POST /api/auth/generate`

## 📝 简介

本项目已集成**讯飞超拟人语音合成（TTS）**服务，通过统一鉴权接口支持Flutter前端直连讯飞WebSocket，实现低延迟、高质量的语音合成。

## 🎯 架构特点

- ✅ **API密钥安全**: 密钥保存在后端，前端不可见
- ✅ **零后端压力**: 音频流直连讯飞，不经过后端转发  
- ✅ **低延迟**: 前端直连WebSocket，实时性最优
- ✅ **配额可控**: 后端统一管理使用配额
- ✅ **通用Token服务**: 可扩展支持阿里云、腾讯云等其他平台

## 🚀 快速开始

### 1. 获取讯飞密钥

1. 访问 [讯飞开放平台](https://www.xfyun.cn/)
2. 注册并登录
3. 创建新应用
4. 开通**超拟人语音合成**服务
5. 获取以下信息：
   - `APPID`
   - `APIKey`
   - `APISecret`
   - 超拟人TTS专属端点URL

### 2. 配置后端

在 `config.yaml` 中配置讯飞服务：

```yaml
xunfei:
  # 填入你的讯飞密钥
  app_id: "your_app_id"
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  
  endpoints:
    # 替换为你的超拟人TTS专属端点
    super_tts: "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/your_endpoint"
    asr: "wss://iat-api.xfyun.cn/v2/iat"
    spark: "wss://spark-api.xf-yun.com/v3.5/chat"
```

### 3. 启动后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端API地址: `http://localhost:8000`

### 4. 测试接口

#### 获取TTS鉴权信息（使用新的统一接口）

```bash
curl -X POST http://localhost:8000/api/auth/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xunfei",
    "service": "tts",
    "params": {
      "text": "你好，这是讯飞超拟人语音合成测试",
      "voice": "x5_lingfeiyi_flow",
      "speed": 50,
      "volume": 50,
      "pitch": 50,
      "oral_level": "mid"
    }
  }'
```

返回:

```json
{
  "success": true,
  "message": "xunfei tts 鉴权信息生成成功",
  "data": {
    "platform": "xunfei",
    "service": "tts",
    "ws_url": "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/xxx?authorization=xxx",
    "request_id": "req_123456",
    "expires_at": 1704067200,
    "params": {
      "header": {...},
      "parameter": {...},
      "payload": {...}
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 查询配额

```bash
curl http://localhost:8000/api/xunfei/quota?service=tts
```

#### 获取音色列表

```bash
curl http://localhost:8000/api/xunfei/voices
```

## 📱 Flutter前端集成

详细集成指南请查看: [Flutter前端实现文档](./xunfei_flutter_guide.md)

### 简要步骤:

1. **添加依赖包**
   ```yaml
   dependencies:
     http: ^1.1.0
     web_socket_channel: ^2.4.0
     audioplayers: ^5.2.0
   ```

2. **调用后端获取鉴权**
   ```dart
   final response = await http.post(
     Uri.parse('http://your-backend/api/xunfei/tts/auth'),
     body: jsonEncode({
       'text': '你好世界',
       'voice': 'x5_lingfeiyi_flow'
     })
   );
   ```

3. **建立WebSocket连接**
   ```dart
   final wsUrl = response['data']['ws_url'];
   final params = response['data']['params'];
   final channel = WebSocketChannel.connect(Uri.parse(wsUrl));
   ```

4. **发送参数并接收音频**
   ```dart
   channel.sink.add(jsonEncode(params));
   channel.stream.listen((data) {
     // 处理接收到的音频数据
   });
   ```

## 🎤 可用音色 (x5系列)

| 音色名称 | 音色值 | 性别 | 特点 |
|---------|--------|------|------|
| 凌飞易_流畅版 | x5_lingfeiyi_flow | 男 | 流畅自然 |
| 凌飞易_情感版 | x5_lingfeiyi | 男 | 富有情感 |
| 小研_流畅版 | x5_xiaoyan_flow | 女 | 流畅自然 |
| 小研_情感版 | x5_xiaoyan | 女 | 富有情感 |
| 小雨_流畅版 | x5_xiaoyu_flow | 女 | 清新温柔 |
| 小雨_情感版 | x5_xiaoyu | 女 | 活泼生动 |
| 晓辰_流畅版 | x5_xiaochen_flow | 女 | 知性优雅 |
| 晓辰_情感版 | x5_xiaochen | 女 | 温暖亲切 |

**注意**: 需要在讯飞控制台开通对应发音人的权限

## ⚙️ 参数说明

### TTS请求参数

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | 1-8000字符 | - | 要合成的文本 |
| voice | string | - | x5_lingfeiyi_flow | 音色（x5系列） |
| speed | int | 0-100 | 50 | 语速 |
| volume | int | 0-100 | 50 | 音量 |
| pitch | int | 0-100 | 50 | 音调 |
| audio_format | string | lame/raw | lame | 音频格式（lame=MP3） |
| oral_level | string | high/mid/low | mid | 口语化等级 |

### 口语化等级说明

- **high**: 高口语化，更接近自然对话
- **mid**: 中等口语化，平衡朗读与对话
- **low**: 低口语化，更接近朗读风格

## 📊 配额管理

### 默认配额

- TTS: 100次/用户/天
- ASR: 100次/用户/天
- Spark: 50次/用户/天

### 修改配额

在 `config.yaml` 中修改:

```yaml
xunfei:
  quota:
    tts: 200  # 修改为200次/天
```

## 🔧 通用Token服务

本项目使用通用Token服务架构，可轻松扩展支持其他AI平台：

### 已支持平台

- ✅ 讯飞（Xunfei）
- ⏳ 阿里云（Aliyun）- 预留接口
- ⏳ 腾讯云（Tencent）- 预留接口

### 扩展新平台

```python
# 在 app/services/token_service.py 中添加新的Provider
class NewPlatformTokenProvider(TokenProvider):
    def generate_auth_url(self, service: ServiceType, **kwargs) -> str:
        # 实现鉴权URL生成逻辑
        pass
    
    def create_request_params(self, service: ServiceType, **kwargs) -> Dict:
        # 实现请求参数生成逻辑
        pass

# 注册Provider
token_service.register_provider(PlatformType.NEW_PLATFORM, provider)
```

## 📖 详细文档

- [讯飞API接口文档](../api/xunfei_api.md)
- [Flutter前端集成指南](./xunfei_flutter_guide.md)
- [超拟人TTS官方文档](https://www.xfyun.cn/doc/spark/super%20smart-tts.html)
- [WebSocket鉴权文档](https://www.xfyun.cn/doc/spark/general_url_authentication.html)

## ❓ 常见问题

### Q: WebSocket连接失败？

**A**: 检查以下几点：
1. 超拟人TTS端点URL是否正确
2. API密钥是否正确配置
3. 是否在讯飞控制台开通了超拟人TTS服务

### Q: 音色无法使用？

**A**: 需要在讯飞控制台开通对应x5系列发音人的权限

### Q: 配额很快用完？

**A**: 在前端添加防抖/节流，或增加配额限制

### Q: 如何获取超拟人TTS端点URL？

**A**: 登录讯飞控制台 → 超拟人语音合成 → 服务接口信息 → 查看WebSocket地址

## 🎉 完成！

现在你已经成功集成了讯飞超拟人TTS服务，可以开始开发了！

如有问题，请参考详细文档或提交工单到讯飞开放平台。

