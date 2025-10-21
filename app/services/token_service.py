"""
通用临时令牌生成服务 (Token Service)
支持多个AI平台的临时鉴权令牌生成，包括讯飞、阿里云、腾讯云等
"""

import time
import hmac
import hashlib
import base64
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Type
from urllib.parse import urlencode, urlparse, quote
from enum import Enum

try:
    from app.utils.cache_utils import CacheUtils
except ImportError:
    class CacheUtils:
        async def get(self, key):
            return None
        async def set(self, key, value, expire=None):
            pass
        async def incr(self, key):
            return 1
        async def expire(self, key, seconds):
            pass


class PlatformType(Enum):
    """AI平台类型"""
    XUNFEI = "xunfei"           # 讯飞
    ALIYUN = "aliyun"           # 阿里云
    TENCENT = "tencent"         # 腾讯云
    BAIDU = "baidu"             # 百度
    HUAWEI = "huawei"           # 华为云
    VOLCENGINE = "volcengine"   # 火山引擎


class ServiceType(Enum):
    """服务类型"""
    TTS = "tts"         # 语音合成
    ASR = "asr"         # 语音识别
    LLM = "llm"         # 大语言模型
    IMAGE = "image"     # 图片生成
    VIDEO = "video"     # 视频生成


class TokenProvider(ABC):
    """令牌提供者抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = CacheUtils()
    
    @abstractmethod
    def generate_auth_url(self, service: ServiceType, **kwargs) -> str:
        """生成鉴权URL"""
        pass
    
    @abstractmethod
    def create_request_params(self, service: ServiceType, **kwargs) -> Dict[str, Any]:
        """创建请求参数"""
        pass
    
    async def check_quota(self, user_id: str, service: ServiceType) -> bool:
        """检查用户配额"""
        quota_key = f"{self.__class__.__name__}:quota:{user_id}:{service.value}:{datetime.now().date()}"
        
        try:
            usage = await self.cache.get(quota_key) or 0
            usage = int(usage)
        except:
            usage = 0
        
        limit = self.config.get('quota', {}).get(service.value, 100)
        
        if usage >= limit:
            raise Exception(f"今日{service.value}服务配额已用完 ({usage}/{limit})")
        
        # 增加使用计数
        try:
            await self.cache.incr(quota_key)
            tomorrow = datetime.combine(datetime.now().date() + timedelta(days=1), datetime.min.time())
            expire_seconds = int((tomorrow - datetime.now()).total_seconds())
            await self.cache.expire(quota_key, expire_seconds)
        except:
            pass
        
        return True
    
    async def get_quota_info(self, user_id: str, service: ServiceType) -> Dict[str, Any]:
        """获取配额信息"""
        quota_key = f"{self.__class__.__name__}:quota:{user_id}:{service.value}:{datetime.now().date()}"
        
        try:
            usage = await self.cache.get(quota_key) or 0
            usage = int(usage)
        except:
            usage = 0
        
        limit = self.config.get('quota', {}).get(service.value, 100)
        
        return {
            'platform': self.__class__.__name__.replace('TokenProvider', '').lower(),
            'service': service.value,
            'used': usage,
            'limit': limit,
            'remaining': max(0, limit - usage),
            'date': str(datetime.now().date())
        }


class XunfeiTokenProvider(TokenProvider):
    """讯飞令牌提供者"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config['app_id']
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']
        
        # 讯飞服务端点
        self.endpoints = {
            ServiceType.TTS: config.get('super_tts_endpoint', 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6'),  # 超拟人TTS
            ServiceType.ASR: 'wss://iat-api.xfyun.cn/v2/iat',
            ServiceType.LLM: 'wss://spark-api.xf-yun.com/v3.5/chat'
        }
    
    def generate_auth_url(self, service: ServiceType, **kwargs) -> str:
        """生成讯飞WebSocket鉴权URL"""
        base_url = self.endpoints.get(service)
        if not base_url:
            raise ValueError(f"讯飞不支持的服务类型: {service.value}")
        
        # 解析URL
        url_parts = urlparse(base_url)
        host = url_parts.netloc
        path = url_parts.path
        
        # 生成RFC1123格式的时间戳
        now = datetime.utcnow()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 构建签名原文
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # 使用HMAC-SHA256生成签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构建authorization
        authorization_origin = (
            f'api_key="{self.api_key}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # 构建最终URL
        params = {
            'authorization': authorization,
            'date': date,
            'host': host
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    def create_request_params(self, service: ServiceType, **kwargs) -> Dict[str, Any]:
        """创建讯飞请求参数"""
        if service == ServiceType.TTS:
            return self._create_tts_params(**kwargs)
        elif service == ServiceType.ASR:
            return self._create_asr_params(**kwargs)
        else:
            return {}
    
    def _create_tts_params(self, text: str, voice: str = "x5_lingfeiyi_flow", speed: int = 50, 
                          volume: int = 50, pitch: int = 50, audio_format: str = "lame",
                          oral_level: str = "mid") -> Dict[str, Any]:
        """
        创建超拟人TTS参数
        
        参考文档：https://www.xfyun.cn/doc/spark/super%20smart-tts.html
        
        Args:
            text: 要合成的文本
            voice: 音色 (x5系列，需要在控制台开通权限)
            speed: 语速 (0-100)
            volume: 音量 (0-100)
            pitch: 音调 (0-100)
            audio_format: 音频格式 (lame=MP3)
            oral_level: 口语化等级 (high/mid/low)
            
        Returns:
            Dict: 超拟人TTS参数
        """
        # 超拟人TTS格式
        return {
            "header": {
                "app_id": self.app_id,
                "status": 2  # 0:开始, 1:中间, 2:结束
            },
            "parameter": {
                "oral": {
                    "oral_level": oral_level  # 口语化等级：high, mid, low
                },
                "tts": {
                    "vcn": voice,  # x5系列发音人，需要在控制台开通权限
                    "speed": speed,
                    "volume": volume,
                    "pitch": pitch,
                    "bgs": 0,   # 背景音乐
                    "reg": 0,   # 感情程度
                    "rdn": 0,   # 数字发音方式
                    "rhy": 0,   # 韵律
                    "audio": {
                        "encoding": audio_format,  # lame=MP3
                        "sample_rate": 24000,
                        "channels": 1,
                        "bit_depth": 16,
                        "frame_size": 0
                    }
                }
            },
            "payload": {
                "text": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 2,  # 0:开始, 1:中间, 2:结束
                    "seq": 0,
                    "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
                }
            }
        }
    
    def _create_asr_params(self, audio_format: str = "raw", sample_rate: int = 16000,
                          language: str = "zh_cn", domain: str = "iat") -> Dict[str, Any]:
        """创建ASR参数"""
        return {
            "common": {"app_id": self.app_id},
            "business": {
                "language": language,
                "domain": domain,
                "accent": "mandarin",
                "vad_eos": 10000,
                "dwa": "wpgs"
            },
            "data": {
                "status": 0,
                "format": audio_format,
                "encoding": "raw",
                "audio": ""
            }
        }


class AliyunTokenProvider(TokenProvider):
    """阿里云令牌提供者"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_key_id = config['access_key_id']
        self.access_key_secret = config['access_key_secret']
        self.app_key = config.get('app_key', '')
        
        self.endpoints = {
            ServiceType.TTS: 'wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1',
            ServiceType.ASR: 'wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1'
        }
    
    def generate_auth_url(self, service: ServiceType, **kwargs) -> str:
        """生成阿里云鉴权URL"""
        base_url = self.endpoints.get(service)
        if not base_url:
            raise ValueError(f"阿里云不支持的服务类型: {service.value}")
        
        # 阿里云使用Token方式鉴权
        token = self._generate_token()
        return f"{base_url}?token={token}"
    
    def _generate_token(self) -> str:
        """生成阿里云临时Token（示例，实际需要调用阿里云API）"""
        # 实际实现需要调用阿里云NLS Token接口
        # https://nls-meta.cn-shanghai.aliyuncs.com/
        timestamp = int(time.time())
        signature = hmac.new(
            self.access_key_secret.encode('utf-8'),
            f"{self.access_key_id}:{timestamp}".encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return f"{self.access_key_id}:{timestamp}:{signature}"
    
    def create_request_params(self, service: ServiceType, **kwargs) -> Dict[str, Any]:
        """创建阿里云请求参数"""
        return {
            "app_key": self.app_key,
            "format": kwargs.get('format', 'pcm'),
            "sample_rate": kwargs.get('sample_rate', 16000)
        }


class TencentTokenProvider(TokenProvider):
    """腾讯云令牌提供者"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secret_id = config['secret_id']
        self.secret_key = config['secret_key']
        self.app_id = config['app_id']
        
        self.endpoints = {
            ServiceType.TTS: 'wss://tts.cloud.tencent.com/stream',
            ServiceType.ASR: 'wss://asr.cloud.tencent.com/asr/v2'
        }
    
    def generate_auth_url(self, service: ServiceType, **kwargs) -> str:
        """生成腾讯云鉴权URL"""
        base_url = self.endpoints.get(service)
        if not base_url:
            raise ValueError(f"腾讯云不支持的服务类型: {service.value}")
        
        # 腾讯云使用签名方式
        timestamp = int(time.time())
        signature = self._generate_signature(timestamp)
        
        params = {
            'secretid': self.secret_id,
            'timestamp': timestamp,
            'expired': timestamp + 600,  # 10分钟过期
            'signature': signature
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    def _generate_signature(self, timestamp: int) -> str:
        """生成腾讯云签名"""
        signature_str = f"{self.secret_id}{timestamp}"
        return hmac.new(
            self.secret_key.encode('utf-8'),
            signature_str.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
    
    def create_request_params(self, service: ServiceType, **kwargs) -> Dict[str, Any]:
        """创建腾讯云请求参数"""
        return {
            "app_id": self.app_id,
            "voice_type": kwargs.get('voice', '1'),
            "speed": kwargs.get('speed', 0),
            "volume": kwargs.get('volume', 0)
        }


class TokenService:
    """通用令牌服务"""
    
    def __init__(self):
        self.providers: Dict[PlatformType, TokenProvider] = {}
        self.cache = CacheUtils()
    
    def register_provider(self, platform: PlatformType, provider: TokenProvider):
        """注册令牌提供者"""
        self.providers[platform] = provider
    
    def get_provider(self, platform: PlatformType) -> Optional[TokenProvider]:
        """获取令牌提供者"""
        return self.providers.get(platform)
    
    async def generate_auth(
        self,
        platform: PlatformType,
        service: ServiceType,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成鉴权信息
        
        Args:
            platform: AI平台类型
            service: 服务类型
            user_id: 用户ID
            **kwargs: 其他参数
            
        Returns:
            Dict: 鉴权信息
        """
        provider = self.get_provider(platform)
        if not provider:
            raise ValueError(f"未注册的平台: {platform.value}")
        
        # 检查配额
        await provider.check_quota(user_id, service)
        
        # 生成鉴权URL
        auth_url = provider.generate_auth_url(service, **kwargs)
        
        # 创建请求参数
        params = provider.create_request_params(service, **kwargs)
        
        # 生成请求ID
        request_id = f"{user_id}_{int(time.time() * 1000)}"
        
        # 计算过期时间
        expires_at = datetime.now() + timedelta(minutes=10)
        
        return {
            'platform': platform.value,
            'service': service.value,
            'ws_url': auth_url,
            'request_id': request_id,
            'params': params,
            'expires_at': int(expires_at.timestamp()),  # 返回时间戳（秒）
            'message': '请使用ws_url建立WebSocket连接'
        }
    
    async def get_quota(
        self,
        platform: PlatformType,
        service: ServiceType,
        user_id: str
    ) -> Dict[str, Any]:
        """获取配额信息"""
        provider = self.get_provider(platform)
        if not provider:
            raise ValueError(f"未注册的平台: {platform.value}")
        
        return await provider.get_quota_info(user_id, service)
    
    def get_supported_platforms(self) -> list:
        """获取支持的平台列表"""
        return [platform.value for platform in self.providers.keys()]
    
    def get_supported_services(self, platform: PlatformType) -> list:
        """获取平台支持的服务列表"""
        provider = self.get_provider(platform)
        if not provider:
            return []
        
        return [service.value for service in ServiceType if hasattr(provider, 'endpoints') 
                and service in provider.endpoints]


# 全局令牌服务实例
token_service = TokenService()

