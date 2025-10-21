"""
语音合成服务 (Text-to-Speech Service)
支持多种TTS服务提供商，包括OpenAI、百度、阶跃星辰等
"""

import uuid
import json
import asyncio
import base64
import os
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime
from enum import Enum
from pathlib import Path
from app.services.base_service import BaseService

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from app.utils.file_utils import FileUtils
    from app.utils.cache_utils import CacheUtils
except ImportError:
    # 如果工具类不存在，创建简单的替代实现
    class FileUtils:
        pass
    
    class CacheUtils:
        async def get(self, key):
            return None
        async def set(self, key, value, expire=None):
            pass


class TTSProvider(Enum):
    """TTS服务提供商枚举"""
    OPENAI = "openai"
    BAIDU = "baidu"
    STEP = "step"
    MINIMAX = "minimax"
    AZURE = "azure"
    GOOGLE = "google"


class AudioFormat(Enum):
    """音频格式枚举"""
    MP3 = "mp3"
    WAV = "wav"
    AAC = "aac"
    FLAC = "flac"
    OPUS = "opus"


class TTSVoice(Enum):
    """语音音色枚举"""
    # OpenAI TTS 音色
    OPENAI_ALLOY = "alloy"
    OPENAI_ECHO = "echo"
    OPENAI_FABLE = "fable"
    OPENAI_ONYX = "onyx"
    OPENAI_NOVA = "nova"
    OPENAI_SHIMMER = "shimmer"
    
    # 百度TTS音色
    BAIDU_FEMALE = "0"  # 度小美
    BAIDU_MALE = "1"    # 度小宇
    BAIDU_FEMALE_SWEET = "3"  # 度逍遥
    BAIDU_MALE_MAGNETIC = "4" # 度小娇
    
    # 阶跃星辰音色
    STEP_MAGNETIC_MALE = "cixingnansheng"
    STEP_SWEET_FEMALE = "tianmeinvxing"


class TTSStatus(Enum):
    """TTS任务状态枚举"""
    PENDING = "pending"     # 等待中
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"    # 取消


class TTSService(BaseService):
    """语音合成服务"""
    
    def __init__(self):
        super().__init__()
        self.tasks = {}  # TTS任务缓存
        self.providers_config = self._load_providers_config()
        self.cache = CacheUtils()
        self.file_utils = FileUtils()
        
        # 创建音频文件存储目录
        self.audio_storage_path = Path("storage/audio")
        self.audio_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _load_providers_config(self) -> Dict[str, Any]:
        """加载TTS服务提供商配置"""
        return {
            TTSProvider.OPENAI.value: {
                "api_url": "https://api.openai.com/v1/audio/speech",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}",
                    "Content-Type": "application/json"
                },
                "supported_formats": [AudioFormat.MP3.value, AudioFormat.OPUS.value, AudioFormat.AAC.value, AudioFormat.FLAC.value],
                "supported_voices": [v.value for v in TTSVoice if v.name.startswith('OPENAI_')],
                "max_text_length": 4096
            },
            TTSProvider.BAIDU.value: {
                "api_url": "https://tsn.baidu.com/text2audio",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                "supported_formats": [AudioFormat.MP3.value],
                "supported_voices": [v.value for v in TTSVoice if v.name.startswith('BAIDU_')],
                "max_text_length": 1024
            },
            TTSProvider.STEP.value: {
                "api_url": "https://api.stepfun.com/v1/tts",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('STEP_API_KEY', '')}",
                    "Content-Type": "application/json"
                },
                "supported_formats": [AudioFormat.MP3.value, AudioFormat.WAV.value],
                "supported_voices": [v.value for v in TTSVoice if v.name.startswith('STEP_')],
                "max_text_length": 2000
            },
            TTSProvider.MINIMAX.value: {
                "api_url": "https://api.minimax.chat/v1/text_to_speech",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('MINIMAX_API_KEY', '')}",
                    "Content-Type": "application/json"
                },
                "supported_formats": [AudioFormat.MP3.value, AudioFormat.WAV.value],
                "supported_voices": ["default"],
                "max_text_length": 10000
            }
        }
    
    async def generate_speech(
        self,
        text: str,
        provider: str = TTSProvider.OPENAI.value,
        voice: str = TTSVoice.OPENAI_ALLOY.value,
        format: str = AudioFormat.MP3.value,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        save_to_server: bool = True,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成语音
        
        Args:
            text: 要合成的文本
            provider: TTS服务提供商
            voice: 音色选择
            format: 音频格式
            speed: 语速 (0.25-4.0)
            pitch: 音调 (0.5-2.0)
            volume: 音量 (0.1-2.0)
            save_to_server: 是否保存到服务器
            user_id: 用户ID
            
        Returns:
            Dict: 生成结果
        """
        # 创建TTS任务
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "text": text,
            "provider": provider,
            "voice": voice,
            "format": format,
            "speed": speed,
            "pitch": pitch,
            "volume": volume,
            "save_to_server": save_to_server,
            "user_id": user_id,
            "status": TTSStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "audio_url": None,
            "audio_path": None,
            "file_size": None,
            "duration": None,
            "error": None
        }
        
        self.tasks[task_id] = task
        
        try:
            # 验证参数
            self._validate_tts_params(task)
            
            # 更新状态
            task["status"] = TTSStatus.PROCESSING.value
            task["started_at"] = datetime.now().isoformat()
            
            # 调用相应的TTS服务
            audio_data = await self._call_tts_provider(task)
            
            # 处理音频数据
            if save_to_server:
                # 保存到服务器
                audio_path, file_size = await self._save_audio_to_server(task_id, audio_data, format)
                task["audio_path"] = audio_path
                task["file_size"] = file_size
                task["audio_url"] = f"/api/audio/download/{task_id}"
            else:
                # 直接返回音频数据
                task["audio_data"] = base64.b64encode(audio_data).decode('utf-8')
            
            # 更新任务状态
            task["status"] = TTSStatus.COMPLETED.value
            task["completed_at"] = datetime.now().isoformat()
            
            return {
                "task_id": task_id,
                "status": "success",
                "audio_url": task.get("audio_url"),
                "audio_data": task.get("audio_data"),
                "file_size": task.get("file_size"),
                "format": format,
                "duration": task.get("duration"),
                "created_at": task["created_at"]
            }
            
        except Exception as e:
            # 更新错误状态
            task["status"] = TTSStatus.FAILED.value
            task["error"] = str(e)
            task["completed_at"] = datetime.now().isoformat()
            
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "created_at": task["created_at"]
            }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取TTS任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态信息
        """
        return self.tasks.get(task_id)
    
    async def download_audio(self, task_id: str) -> Optional[bytes]:
        """
        下载音频文件
        
        Args:
            task_id: 任务ID
            
        Returns:
            bytes: 音频文件数据
        """
        task = self.tasks.get(task_id)
        if not task or task["status"] != TTSStatus.COMPLETED.value:
            return None
        
        if task.get("audio_path"):
            try:
                with open(task["audio_path"], "rb") as f:
                    return f.read()
            except FileNotFoundError:
                return None
        
        return None
    
    def list_tasks(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取TTS任务列表
        
        Args:
            user_id: 用户ID筛选
            status: 状态筛选
            
        Returns:
            List[Dict]: 任务列表
        """
        tasks = list(self.tasks.values())
        
        if user_id:
            tasks = [t for t in tasks if t.get("user_id") == user_id]
        
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        
        # 按创建时间倒序排列
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tasks
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除TTS任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # 删除音频文件
        if task.get("audio_path") and os.path.exists(task["audio_path"]):
            try:
                os.remove(task["audio_path"])
            except OSError:
                pass
        
        # 删除任务记录
        del self.tasks[task_id]
        
        return True
    
    def _validate_tts_params(self, task: Dict[str, Any]) -> None:
        """验证TTS参数"""
        provider = task["provider"]
        config = self.providers_config.get(provider)
        
        if not config:
            raise ValueError(f"不支持的TTS服务提供商: {provider}")
        
        # 验证文本长度
        if len(task["text"]) > config["max_text_length"]:
            raise ValueError(f"文本长度超过限制: {len(task['text'])} > {config['max_text_length']}")
        
        # 验证音频格式
        if task["format"] not in config["supported_formats"]:
            raise ValueError(f"不支持的音频格式: {task['format']}")
        
        # 验证音色
        if task["voice"] not in config["supported_voices"]:
            raise ValueError(f"不支持的音色: {task['voice']}")
        
        # 验证参数范围
        if not 0.25 <= task["speed"] <= 4.0:
            raise ValueError("语速必须在0.25-4.0之间")
        
        if not 0.5 <= task["pitch"] <= 2.0:
            raise ValueError("音调必须在0.5-2.0之间")
        
        if not 0.1 <= task["volume"] <= 2.0:
            raise ValueError("音量必须在0.1-2.0之间")
    
    async def _call_tts_provider(self, task: Dict[str, Any]) -> bytes:
        """调用TTS服务提供商"""
        provider = task["provider"]
        
        if provider == TTSProvider.OPENAI.value:
            return await self._call_openai_tts(task)
        elif provider == TTSProvider.BAIDU.value:
            return await self._call_baidu_tts(task)
        elif provider == TTSProvider.STEP.value:
            return await self._call_step_tts(task)
        elif provider == TTSProvider.MINIMAX.value:
            return await self._call_minimax_tts(task)
        else:
            raise ValueError(f"不支持的TTS服务提供商: {provider}")
    
    async def _call_openai_tts(self, task: Dict[str, Any]) -> bytes:
        """调用OpenAI TTS API"""
        config = self.providers_config[TTSProvider.OPENAI.value]
        
        payload = {
            "model": "tts-1",
            "input": task["text"],
            "voice": task["voice"],
            "response_format": task["format"],
            "speed": task["speed"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["api_url"],
                headers=config["headers"],
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI TTS API错误: {response.status} - {error_text}")
    
    async def _call_baidu_tts(self, task: Dict[str, Any]) -> bytes:
        """调用百度TTS API"""
        config = self.providers_config[TTSProvider.BAIDU.value]
        
        # 百度TTS需要先获取access_token
        access_token = await self._get_baidu_access_token()
        
        payload = {
            "tex": task["text"],
            "tok": access_token,
            "cuid": "python_tts_client",
            "ctp": 1,
            "lan": "zh",
            "spd": int(task["speed"] * 5),  # 百度语速范围0-15
            "pit": int((task["pitch"] - 1) * 20),  # 百度音调范围-20到+20
            "vol": int(task["volume"] * 50),  # 百度音量范围0-100
            "per": task["voice"],
            "aue": 3 if task["format"] == "mp3" else 6  # 3=mp3, 6=wav
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["api_url"],
                headers=config["headers"],
                data=payload
            ) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'audio' in content_type:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        raise Exception(f"百度TTS API错误: {error_text}")
                else:
                    error_text = await response.text()
                    raise Exception(f"百度TTS API错误: {response.status} - {error_text}")
    
    async def _call_step_tts(self, task: Dict[str, Any]) -> bytes:
        """调用阶跃星辰TTS API"""
        config = self.providers_config[TTSProvider.STEP.value]
        
        payload = {
            "model": "step-tts-mini",
            "input": task["text"],
            "voice": task["voice"],
            "volume": task["volume"],
            "speed": task["speed"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["api_url"],
                headers=config["headers"],
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "audio" in result:
                        return base64.b64decode(result["audio"])
                    else:
                        raise Exception(f"阶跃星辰TTS API返回格式错误: {result}")
                else:
                    error_text = await response.text()
                    raise Exception(f"阶跃星辰TTS API错误: {response.status} - {error_text}")
    
    async def _call_minimax_tts(self, task: Dict[str, Any]) -> bytes:
        """调用MiniMax TTS API"""
        config = self.providers_config[TTSProvider.MINIMAX.value]
        
        payload = {
            "text": task["text"],
            "speed": task["speed"],
            "vol": task["volume"],
            "pitch": int((task["pitch"] - 1) * 12)  # MiniMax音调范围-12到12
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["api_url"],
                headers=config["headers"],
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "audio" in result:
                        return base64.b64decode(result["audio"])
                    else:
                        raise Exception(f"MiniMax TTS API返回格式错误: {result}")
                else:
                    error_text = await response.text()
                    raise Exception(f"MiniMax TTS API错误: {response.status} - {error_text}")
    
    async def _get_baidu_access_token(self) -> str:
        """获取百度API访问令牌"""
        # 从缓存中获取
        cached_token = await self.cache.get("baidu_access_token")
        if cached_token:
            return cached_token
        
        # 获取新的访问令牌
        api_key = os.getenv('BAIDU_API_KEY', '')
        secret_key = os.getenv('BAIDU_SECRET_KEY', '')
        
        if not api_key or not secret_key:
            raise Exception("百度API密钥未配置")
        
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url) as response:
                if response.status == 200:
                    result = await response.json()
                    access_token = result.get("access_token")
                    if access_token:
                        # 缓存访问令牌（有效期通常为30天）
                        await self.cache.set("baidu_access_token", access_token, expire=25*24*3600)
                        return access_token
                    else:
                        raise Exception(f"获取百度访问令牌失败: {result}")
                else:
                    error_text = await response.text()
                    raise Exception(f"获取百度访问令牌失败: {response.status} - {error_text}")
    
    async def _save_audio_to_server(self, task_id: str, audio_data: bytes, format: str) -> tuple[str, int]:
        """保存音频文件到服务器"""
        filename = f"{task_id}.{format}"
        file_path = self.audio_storage_path / filename
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        file_size = len(audio_data)
        return str(file_path), file_size
    
    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """获取支持的TTS服务提供商列表"""
        providers = []
        for provider, config in self.providers_config.items():
            providers.append({
                "provider": provider,
                "supported_formats": config["supported_formats"],
                "supported_voices": config["supported_voices"],
                "max_text_length": config["max_text_length"]
            })
        return providers
    
    def get_supported_voices(self, provider: str) -> List[str]:
        """获取指定提供商的音色列表"""
        config = self.providers_config.get(provider)
        if config:
            return config["supported_voices"]
        return []
    
    def get_supported_formats(self, provider: str) -> List[str]:
        """获取指定提供商的音频格式列表"""
        config = self.providers_config.get(provider)
        if config:
            return config["supported_formats"]
        return []
