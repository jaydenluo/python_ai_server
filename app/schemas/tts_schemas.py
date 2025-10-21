"""
语音合成相关的Pydantic模式定义
"""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TTSGenerateRequest(BaseModel):
    """语音生成请求模式"""
    
    text: str = Field(..., description="要合成的文本", min_length=1, max_length=10000)
    provider: str = Field(default="openai", description="TTS服务提供商")
    voice: str = Field(default="alloy", description="音色选择")
    format: str = Field(default="mp3", description="音频格式")
    speed: float = Field(default=1.0, description="语速", ge=0.25, le=4.0)
    pitch: float = Field(default=1.0, description="音调", ge=0.5, le=2.0)
    volume: float = Field(default=1.0, description="音量", ge=0.1, le=2.0)
    save_to_server: bool = Field(default=True, description="是否保存到服务器")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('文本内容不能为空')
        return v.strip()
    
    @validator('provider')
    def validate_provider(cls, v):
        valid_providers = ['openai', 'baidu', 'step', 'minimax', 'azure', 'google']
        if v not in valid_providers:
            raise ValueError(f'不支持的提供商: {v}')
        return v
    
    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['mp3', 'wav', 'aac', 'flac', 'opus']
        if v not in valid_formats:
            raise ValueError(f'不支持的音频格式: {v}')
        return v


class TTSGenerateResponse(BaseModel):
    """语音生成响应模式"""
    
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    audio_data: Optional[str] = Field(None, description="音频数据(Base64编码)")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    format: Optional[str] = Field(None, description="音频格式")
    duration: Optional[float] = Field(None, description="音频时长(秒)")
    created_at: str = Field(..., description="创建时间")
    error: Optional[str] = Field(None, description="错误信息")


class TTSStatusResponse(BaseModel):
    """TTS任务状态响应模式"""
    
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    text: str = Field(..., description="原始文本")
    provider: str = Field(..., description="服务提供商")
    voice: str = Field(..., description="音色")
    format: str = Field(..., description="音频格式")
    speed: float = Field(..., description="语速")
    pitch: float = Field(..., description="音调")
    volume: float = Field(..., description="音量")
    save_to_server: bool = Field(..., description="是否保存到服务器")
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    file_size: Optional[int] = Field(None, description="文件大小")
    duration: Optional[float] = Field(None, description="音频时长")
    created_at: str = Field(..., description="创建时间")
    started_at: Optional[str] = Field(None, description="开始时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    error: Optional[str] = Field(None, description="错误信息")


class TTSListResponse(BaseModel):
    """TTS任务列表响应模式"""
    
    tasks: List[Dict[str, Any]] = Field(..., description="任务列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class TTSProviderInfo(BaseModel):
    """TTS服务提供商信息模式"""
    
    provider: str = Field(..., description="提供商名称")
    supported_formats: List[str] = Field(..., description="支持的音频格式")
    supported_voices: List[str] = Field(..., description="支持的音色")
    max_text_length: int = Field(..., description="最大文本长度")


class TTSBatchRequest(BaseModel):
    """批量语音生成请求模式"""
    
    texts: List[str] = Field(..., description="文本列表", min_items=1, max_items=10)
    provider: str = Field(default="openai", description="TTS服务提供商")
    voice: str = Field(default="alloy", description="音色选择")
    format: str = Field(default="mp3", description="音频格式")
    speed: float = Field(default=1.0, description="语速", ge=0.25, le=4.0)
    pitch: float = Field(default=1.0, description="音调", ge=0.5, le=2.0)
    volume: float = Field(default=1.0, description="音量", ge=0.1, le=2.0)
    save_to_server: bool = Field(default=True, description="是否保存到服务器")
    
    @validator('texts')
    def validate_texts(cls, v):
        if not v:
            raise ValueError('文本列表不能为空')
        for text in v:
            if not text.strip():
                raise ValueError('文本内容不能为空')
        return [text.strip() for text in v]


class TTSBatchResponse(BaseModel):
    """批量语音生成响应模式"""
    
    tasks: List[Dict[str, Any]] = Field(..., description="任务列表")
    total: int = Field(..., description="总任务数")
    success_count: int = Field(..., description="成功任务数")
    failed_count: int = Field(..., description="失败任务数")


class TTSConfigRequest(BaseModel):
    """TTS配置请求模式"""
    
    provider: str = Field(..., description="服务提供商")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_secret: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    timeout: int = Field(default=30, description="请求超时时间(秒)", ge=5, le=300)
    retry_count: int = Field(default=3, description="重试次数", ge=0, le=10)
    enable_cache: bool = Field(default=True, description="是否启用缓存")
    cache_ttl: int = Field(default=3600, description="缓存过期时间(秒)", ge=60, le=86400)


class TTSConfigResponse(BaseModel):
    """TTS配置响应模式"""
    
    provider: str = Field(..., description="服务提供商")
    status: str = Field(..., description="配置状态")
    message: str = Field(..., description="配置信息")
    updated_at: str = Field(..., description="更新时间")


class TTSUsageStats(BaseModel):
    """TTS使用统计模式"""
    
    total_requests: int = Field(..., description="总请求数")
    successful_requests: int = Field(..., description="成功请求数")
    failed_requests: int = Field(..., description="失败请求数")
    total_characters: int = Field(..., description="总字符数")
    total_duration: float = Field(..., description="总音频时长(秒)")
    total_file_size: int = Field(..., description="总文件大小(字节)")
    provider_stats: Dict[str, Dict[str, Any]] = Field(..., description="各提供商统计")
    daily_stats: List[Dict[str, Any]] = Field(..., description="每日统计")
    created_at: str = Field(..., description="统计时间")


class TTSHealthCheck(BaseModel):
    """TTS健康检查模式"""
    
    status: str = Field(..., description="服务状态")
    providers: Dict[str, Dict[str, Any]] = Field(..., description="提供商状态")
    storage: Dict[str, Any] = Field(..., description="存储状态")
    cache: Dict[str, Any] = Field(..., description="缓存状态")
    uptime: float = Field(..., description="运行时间(秒)")
    version: str = Field(..., description="服务版本")
    timestamp: str = Field(..., description="检查时间")
