# 讯飞语音服务配置说明

## 📋 当前配置状态

✅ **已完成配置** - 可以直接使用

## 🔑 配置信息

所有配置已写入 `config.yaml`，无需额外的环境变量配置。

### 当前配置内容

```yaml
xunfei:
  # 应用ID
  app_id: "4f4d5a39"
  
  # API密钥
  api_key: "c3707fb39206d788d80ae13fa1ce82bc"
  
  # API密钥
  api_secret: "NjAzMmY5NDExMzBkODM4MjI0ODExOTA4"
  
  # 服务端点配置
  endpoints:
    # 超拟人TTS端点
    super_tts: "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6"
    asr: "wss://iat-api.xfyun.cn/v2/iat"
    spark: "wss://spark-api.xf-yun.com/v3.5/chat"
  
  # 配额限制 (每用户每天)
  quota:
    tts: 100      # 语音合成
    asr: 100      # 语音识别
    spark: 50     # 星火大模型
  
  # 默认配置
  defaults:
    tts:
      voice: "x5_lingfeiyi_flow"   # x5系列发音人
      speed: 50
      volume: 50
      pitch: 50
      audio_format: "lame"         # MP3格式
      oral_level: "mid"            # 口语化等级: high/mid/low
```

## 📦 服务功能

### 1. 超拟人语音合成 (TTS)

- **价格**: 2元/万字符
- **特点**: 超拟人合成，音质自然流畅
- **支持**: 克隆声音（5元/个）
- **超长文本**: 支持10万字（3元/万字符）

### 2. 可用音色 (x5系列)

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

## 🚀 快速测试

### 1. 启动服务

```bash
python main.py
```

### 2. 测试TTS接口

```bash
curl -X POST http://localhost:8000/api/xunfei/tts/auth \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是讯飞超拟人语音合成测试",
    "voice": "x5_lingfeiyi_flow",
    "speed": 50,
    "volume": 50,
    "pitch": 50,
    "oral_level": "mid"
  }'
```

### 3. 查看配额

```bash
curl http://localhost:8000/api/xunfei/quota?service=tts
```

### 4. 获取音色列表

```bash
curl http://localhost:8000/api/xunfei/voices
```

## 📖 文档链接

- [讯飞API接口文档](docs/api/xunfei_api.md)
- [Flutter前端集成指南](docs/guides/xunfei_flutter_guide.md)
- [快速开始指南](docs/guides/xunfei_quick_start.md)
- [讯飞官方文档](https://www.xfyun.cn/doc/spark/super%20smart-tts.html)

## ⚙️ 配置说明

### 配额调整

如需调整每日配额，修改 `config.yaml`:

```yaml
xunfei:
  quota:
    tts: 200  # 修改为200次/天
    asr: 200
    spark: 100
```

### 默认参数调整

修改默认的TTS参数:

```yaml
xunfei:
  defaults:
    tts:
      voice: "x5_xiaoyan_flow"  # 改为女声
      speed: 60                  # 加快语速
      oral_level: "high"         # 提高口语化程度
```

## 🔐 安全说明

- ✅ 所有密钥配置在 `config.yaml` 中
- ✅ 生产环境建议将 `config.yaml` 添加到 `.gitignore`
- ✅ 可以使用 `config.example.yaml` 作为模板
- ✅ 前端不会接触到任何密钥信息

## 📝 注意事项

1. **音色权限**: 使用前需在讯飞控制台开通x5系列发音人权限
2. **端点URL**: 超拟人TTS端点是专属的，每个应用不同
3. **配额管理**: 默认每用户每天100次TTS调用
4. **音频格式**: 推荐使用 `lame` (MP3格式)
5. **口语化等级**: `mid` 适合大多数场景

## ✅ 已完成功能

- ✅ 通用Token服务架构
- ✅ 超拟人TTS鉴权和参数生成
- ✅ WebSocket直连支持
- ✅ 配额管理
- ✅ 音色管理
- ✅ Flutter集成文档
- ✅ 完整的API文档

## 🎉 开始使用

配置已完成，可以直接启动服务开始使用！

```bash
python main.py
```

后端API地址: http://localhost:8000

查看API文档: http://localhost:8000/docs

