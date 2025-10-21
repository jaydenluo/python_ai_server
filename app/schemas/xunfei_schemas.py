"""
讯飞语音服务Schema定义
用于API请求和响应的数据验证
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class XunfeiAuthRequest(BaseModel):
    """讯飞鉴权请求"""
    service: str = Field(..., description="服务类型: tts, asr, spark")
    user_id: Optional[str] = Field(None, description="用户ID")
    
    @validator('service')
    def validate_service(cls, v):
        if v not in ['tts', 'asr', 'spark']:
            raise ValueError('service必须是tts, asr或spark')
        return v


class XunfeiAuthResponse(BaseModel):
    """讯飞鉴权响应"""
    ws_url: str = Field(..., description="WebSocket连接URL")
    app_id: str = Field(..., description="应用ID")
    request_id: str = Field(..., description="请求ID")
    expires_at: str = Field(..., description="过期时间")
    service: str = Field(..., description="服务类型")
    message: str = Field(..., description="说明信息")


class XunfeiTTSRequest(BaseModel):
    """讯飞超拟人TTS生成请求"""
    text: str = Field(..., min_length=1, max_length=8000, description="要合成的文本")
    voice: str = Field(default="x5_lingfeiyi_flow", description="音色 (x5系列)")
    speed: int = Field(default=50, ge=0, le=100, description="语速(0-100)")
    volume: int = Field(default=50, ge=0, le=100, description="音量(0-100)")
    pitch: int = Field(default=50, ge=0, le=100, description="音调(0-100)")
    audio_format: str = Field(default="lame", description="音频格式: lame=MP3")
    oral_level: str = Field(default="mid", description="口语化等级: high/mid/low")
    
    @validator('audio_format')
    def validate_format(cls, v):
        if v not in ['lame', 'raw', 'speex', 'speex-wb']:
            raise ValueError('audio_format必须是lame, raw, speex或speex-wb')
        return v
    
    @validator('oral_level')
    def validate_oral_level(cls, v):
        if v not in ['high', 'mid', 'low']:
            raise ValueError('oral_level必须是high, mid或low')
        return v


class XunfeiTTSResponse(BaseModel):
    """讯飞TTS生成响应"""
    ws_url: str = Field(..., description="WebSocket连接URL")
    app_id: str = Field(..., description="应用ID")
    request_id: str = Field(..., description="请求ID")
    params: Dict[str, Any] = Field(..., description="TTS参数")
    expires_at: str = Field(..., description="过期时间")


class XunfeiASRRequest(BaseModel):
    """讯飞ASR识别请求"""
    audio_format: str = Field(default="raw", description="音频格式")
    sample_rate: int = Field(default=16000, description="采样率")
    language: str = Field(default="zh_cn", description="语言")
    domain: str = Field(default="iat", description="领域")
    
    @validator('audio_format')
    def validate_format(cls, v):
        if v not in ['raw', 'speex', 'speex-wb']:
            raise ValueError('audio_format必须是raw, speex或speex-wb')
        return v
    
    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        if v not in [8000, 16000]:
            raise ValueError('sample_rate必须是8000或16000')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ['zh_cn', 'en_us']:
            raise ValueError('language必须是zh_cn或en_us')
        return v


class XunfeiASRResponse(BaseModel):
    """讯飞ASR识别响应"""
    ws_url: str = Field(..., description="WebSocket连接URL")
    app_id: str = Field(..., description="应用ID")
    request_id: str = Field(..., description="请求ID")
    params: Dict[str, Any] = Field(..., description="ASR参数")
    expires_at: str = Field(..., description="过期时间")


class XunfeiSparkRequest(BaseModel):
    """讯飞星火大模型请求"""
    user_id: Optional[str] = Field(None, description="用户ID")


class XunfeiSparkResponse(BaseModel):
    """讯飞星火大模型响应"""
    ws_url: str = Field(..., description="WebSocket连接URL")
    app_id: str = Field(..., description="应用ID")
    request_id: str = Field(..., description="请求ID")
    expires_at: str = Field(..., description="过期时间")


class XunfeiQuotaResponse(BaseModel):
    """讯飞配额查询响应"""
    service: str = Field(..., description="服务类型")
    used: int = Field(..., description="已使用次数")
    limit: int = Field(..., description="总限额")
    remaining: int = Field(..., description="剩余次数")
    date: str = Field(..., description="统计日期")


class XunfeiVoiceInfo(BaseModel):
    """音色信息"""
    name: str = Field(..., description="音色名称")
    value: str = Field(..., description="音色值")
    gender: str = Field(..., description="性别")


class XunfeiVoicesResponse(BaseModel):
    """音色列表响应"""
    voices: Dict[str, List[XunfeiVoiceInfo]] = Field(..., description="按语言分类的音色列表")


class XunfeiFormatsResponse(BaseModel):
    """音频格式列表响应"""
    formats: Dict[str, str] = Field(..., description="音频格式说明")


# WebSocket消息格式定义（供前端参考）
class XunfeiTTSWSMessage(BaseModel):
    """TTS WebSocket消息格式"""
    common: Dict[str, str] = Field(..., description="公共参数")
    business: Dict[str, Any] = Field(..., description="业务参数")
    data: Dict[str, str] = Field(..., description="数据参数")


class XunfeiASRWSMessage(BaseModel):
    """ASR WebSocket消息格式"""
    common: Dict[str, str] = Field(..., description="公共参数")
    business: Dict[str, Any] = Field(..., description="业务参数")
    data: Dict[str, str] = Field(..., description="数据参数")


class XunfeiErrorResponse(BaseModel):
    """错误响应"""
    code: int = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
    service: Optional[str] = Field(None, description="服务类型")

