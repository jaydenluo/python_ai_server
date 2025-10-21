"""
讯飞语音服务 (iFlytek Speech Service)
使用通用Token服务提供讯飞语音合成、语音识别等功能
"""

from typing import Dict, Optional, Any
from app.services.token_service import (
    TokenService,
    PlatformType,
    ServiceType,
    XunfeiTokenProvider
)


class XunfeiService:
    """讯飞语音服务 - 第三方API服务，不涉及数据库操作"""
    
    def __init__(self, app_id: str, api_key: str, api_secret: str):
        """初始化讯飞服务"""
        self.app_id = app_id
        
        # 初始化Token服务
        self.token_service = TokenService()
        
        # 注册讯飞Token提供者
        xunfei_config = {
            'app_id': app_id,
            'api_key': api_key,
            'api_secret': api_secret,
            'quota': {
                'tts': 100,
                'asr': 100,
                'llm': 50
            }
        }
        xunfei_provider = XunfeiTokenProvider(xunfei_config)
        self.token_service.register_provider(PlatformType.XUNFEI, xunfei_provider)
        
        # 讯飞API端点配置（用于前端参考）
        self.endpoints = {
            'tts': 'wss://tts-api.xfyun.cn/v2/tts',
            'asr': 'wss://iat-api.xfyun.cn/v2/iat',
            'spark': 'wss://spark-api.xf-yun.com/v3.5/chat'
        }
    
    async def generate_tts_auth(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        生成TTS WebSocket连接鉴权信息
        
        Args:
            user_id: 用户ID（用于配额控制）
            **kwargs: TTS参数
            
        Returns:
            Dict: 包含WebSocket URL和鉴权信息
        """
        # 使用通用Token服务生成鉴权
        return await self.token_service.generate_auth(
            platform=PlatformType.XUNFEI,
            service=ServiceType.TTS,
            user_id=user_id,
            **kwargs
        )
    
    async def generate_asr_auth(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        生成ASR WebSocket连接鉴权信息
        
        Args:
            user_id: 用户ID（用于配额控制）
            **kwargs: ASR参数
            
        Returns:
            Dict: 包含WebSocket URL和鉴权信息
        """
        # 使用通用Token服务生成鉴权
        return await self.token_service.generate_auth(
            platform=PlatformType.XUNFEI,
            service=ServiceType.ASR,
            user_id=user_id,
            **kwargs
        )
    
    async def generate_spark_auth(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        生成讯飞星火大模型WebSocket连接鉴权信息
        
        Args:
            user_id: 用户ID（用于配额控制）
            **kwargs: 星火参数
            
        Returns:
            Dict: 包含WebSocket URL和鉴权信息
        """
        # 使用通用Token服务生成鉴权
        return await self.token_service.generate_auth(
            platform=PlatformType.XUNFEI,
            service=ServiceType.LLM,
            user_id=user_id,
            **kwargs
        )
    
    async def get_user_quota(self, user_id: str, service: str) -> Dict[str, Any]:
        """
        获取用户配额使用情况
        
        Args:
            user_id: 用户ID
            service: 服务类型
            
        Returns:
            Dict: 配额信息
        """
        # 映射服务类型
        service_map = {
            'tts': ServiceType.TTS,
            'asr': ServiceType.ASR,
            'spark': ServiceType.LLM
        }
        
        service_type = service_map.get(service)
        if not service_type:
            raise ValueError(f"不支持的服务类型: {service}")
        
        # 使用通用Token服务查询配额
        return await self.token_service.get_quota(
            platform=PlatformType.XUNFEI,
            service=service_type,
            user_id=user_id
        )
    
    def create_tts_params(
        self,
        text: str,
        voice: str = "xiaoyan",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
        audio_format: str = "lame"
    ) -> Dict[str, Any]:
        """
        创建TTS请求参数
        
        Args:
            text: 要合成的文本
            voice: 音色 (xiaoyan, aisjiuxu, aisxping等)
            speed: 语速 (0-100, 默认50)
            volume: 音量 (0-100, 默认50)
            pitch: 音调 (0-100, 默认50)
            audio_format: 音频格式 (lame=mp3, raw=pcm, speex等)
            
        Returns:
            Dict: TTS参数字典
        """
        return {
            "common": {
                "app_id": self.app_id
            },
            "business": {
                "aue": audio_format,
                "sfl": 1,
                "auf": "audio/L16;rate=16000",
                "vcn": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "bgs": 0,
                "tte": "UTF8"
            },
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
            }
        }
    
    def create_asr_params(
        self,
        audio_format: str = "raw",
        sample_rate: int = 16000,
        language: str = "zh_cn",
        domain: str = "iat"
    ) -> Dict[str, Any]:
        """
        创建ASR请求参数
        
        Args:
            audio_format: 音频格式 (raw=pcm, speex, speex-wb)
            sample_rate: 采样率 (8000, 16000)
            language: 语言 (zh_cn, en_us)
            domain: 领域 (iat=通用, medical=医疗等)
            
        Returns:
            Dict: ASR参数字典
        """
        return {
            "common": {
                "app_id": self.app_id
            },
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
                "audio": ""  # Base64编码的音频数据
            }
        }
    
    @staticmethod
    def get_available_voices() -> Dict[str, list]:
        """
        获取可用的超拟人TTS音色列表 (x5系列)
        
        注意：需要在讯飞控制台开通对应发音人的权限
        参考：https://www.xfyun.cn/doc/spark/super%20smart-tts.html
        
        Returns:
            Dict: 按类型分类的音色列表
        """
        return {
            "超拟人音色": [
                {"name": "凌飞易_流畅版", "value": "x5_lingfeiyi_flow", "gender": "male", "description": "流畅自然的男声"},
                {"name": "凌飞易_情感版", "value": "x5_lingfeiyi", "gender": "male", "description": "富有情感的男声"},
                {"name": "小研_流畅版", "value": "x5_xiaoyan_flow", "gender": "female", "description": "流畅自然的女声"},
                {"name": "小研_情感版", "value": "x5_xiaoyan", "gender": "female", "description": "富有情感的女声"},
                {"name": "小雨_流畅版", "value": "x5_xiaoyu_flow", "gender": "female", "description": "清新温柔的女声"},
                {"name": "小雨_情感版", "value": "x5_xiaoyu", "gender": "female", "description": "活泼生动的女声"},
                {"name": "晓辰_流畅版", "value": "x5_xiaochen_flow", "gender": "female", "description": "知性优雅的女声"},
                {"name": "晓辰_情感版", "value": "x5_xiaochen", "gender": "female", "description": "温暖亲切的女声"}
            ]
        }
    
    @staticmethod
    def get_audio_formats() -> Dict[str, str]:
        """
        获取支持的音频格式
        
        Returns:
            Dict: 音频格式说明
        """
        return {
            "lame": "MP3格式 (压缩音频, 推荐)",
            "raw": "PCM格式 (原始音频)",
            "speex": "Speex格式 (窄带, 8kHz)",
            "speex-wb": "Speex格式 (宽带, 16kHz)"
        }

