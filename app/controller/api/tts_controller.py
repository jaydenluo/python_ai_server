"""
语音合成API控制器
提供文本转语音的REST API接口
"""

import asyncio
import io
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, UploadFile, File, Query, Path
from fastapi.responses import StreamingResponse, FileResponse
from app.core.controllers.base_controller import BaseController
from app.core.middleware.base import Request, Response
from app.services.ai.tts_service import TTSService, TTSProvider, TTSVoice, AudioFormat
from app.schemas.tts_schemas import (
    TTSGenerateRequest,
    TTSGenerateResponse,
    TTSStatusResponse,
    TTSListResponse,
    TTSProviderInfo
)


class TTSController(BaseController):
    """语音合成控制器"""
    
    def __init__(self):
        super().__init__()
        self.tts_service = TTSService()
    
    async def generate_speech(self, request: Request) -> Response:
        """
        生成语音
        
        POST /api/tts/generate
        """
        try:
            # 解析请求数据
            data = await request.json()
            
            # 验证请求参数
            tts_request = TTSGenerateRequest(**data)
            
            # 获取用户ID（从认证中间件）
            user_id = getattr(request, 'user_id', None)
            
            # 调用TTS服务生成语音
            result = await self.tts_service.generate_speech(
                text=tts_request.text,
                provider=tts_request.provider,
                voice=tts_request.voice,
                format=tts_request.format,
                speed=tts_request.speed,
                pitch=tts_request.pitch,
                volume=tts_request.volume,
                save_to_server=tts_request.save_to_server,
                user_id=user_id
            )
            
            # 构建响应
            response_data = TTSGenerateResponse(
                task_id=result["task_id"],
                status=result["status"],
                audio_url=result.get("audio_url"),
                audio_data=result.get("audio_data"),
                file_size=result.get("file_size"),
                format=result.get("format"),
                duration=result.get("duration"),
                created_at=result["created_at"],
                error=result.get("error")
            )
            
            return self._create_response(
                self.success_response(
                    data=response_data.dict(),
                    message="语音生成请求已提交"
                )
            )
            
        except ValueError as e:
            return self._create_response(
                self.error_response(
                    message=f"参数验证失败: {str(e)}",
                    code=400
                )
            )
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"语音生成失败: {str(e)}",
                    code=500
                )
            )
    
    async def get_task_status(self, request: Request, task_id: str = Path(..., description="任务ID")) -> Response:
        """
        获取TTS任务状态
        
        GET /api/tts/status/{task_id}
        """
        try:
            task = await self.tts_service.get_task_status(task_id)
            
            if not task:
                return self._create_response(
                    self.error_response(
                        message="任务不存在",
                        code=404
                    )
                )
            
            response_data = TTSStatusResponse(
                task_id=task["id"],
                status=task["status"],
                text=task["text"],
                provider=task["provider"],
                voice=task["voice"],
                format=task["format"],
                speed=task["speed"],
                pitch=task["pitch"],
                volume=task["volume"],
                save_to_server=task["save_to_server"],
                audio_url=task.get("audio_url"),
                file_size=task.get("file_size"),
                duration=task.get("duration"),
                created_at=task["created_at"],
                started_at=task.get("started_at"),
                completed_at=task.get("completed_at"),
                error=task.get("error")
            )
            
            return self._create_response(
                self.success_response(
                    data=response_data.dict(),
                    message="获取任务状态成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取任务状态失败: {str(e)}",
                    code=500
                )
            )
    
    async def download_audio(self, request: Request, task_id: str = Path(..., description="任务ID")) -> Response:
        """
        下载音频文件
        
        GET /api/tts/download/{task_id}
        """
        try:
            # 获取任务信息
            task = await self.tts_service.get_task_status(task_id)
            
            if not task:
                return self._create_response(
                    self.error_response(
                        message="任务不存在",
                        code=404
                    )
                )
            
            if task["status"] != "completed":
                return self._create_response(
                    self.error_response(
                        message="任务未完成",
                        code=400
                    )
                )
            
            # 获取音频数据
            audio_data = await self.tts_service.download_audio(task_id)
            
            if not audio_data:
                return self._create_response(
                    self.error_response(
                        message="音频文件不存在",
                        code=404
                    )
                )
            
            # 返回音频文件流
            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type=f"audio/{task['format']}",
                headers={
                    "Content-Disposition": f"attachment; filename=speech_{task_id}.{task['format']}",
                    "Content-Length": str(len(audio_data))
                }
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"下载音频失败: {str(e)}",
                    code=500
                )
            )
    
    async def list_tasks(self, request: Request) -> Response:
        """
        获取TTS任务列表
        
        GET /api/tts/tasks
        """
        try:
            # 获取查询参数
            user_id = request.query_params.get("user_id")
            status = request.query_params.get("status")
            page = int(request.query_params.get("page", 1))
            per_page = int(request.query_params.get("per_page", 20))
            
            # 获取任务列表
            tasks = self.tts_service.list_tasks(user_id=user_id, status=status)
            
            # 分页处理
            total = len(tasks)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_tasks = tasks[start:end]
            
            # 构建响应数据
            task_list = []
            for task in paginated_tasks:
                task_list.append({
                    "task_id": task["id"],
                    "status": task["status"],
                    "text": task["text"][:100] + "..." if len(task["text"]) > 100 else task["text"],
                    "provider": task["provider"],
                    "voice": task["voice"],
                    "format": task["format"],
                    "file_size": task.get("file_size"),
                    "created_at": task["created_at"],
                    "completed_at": task.get("completed_at")
                })
            
            response_data = TTSListResponse(
                tasks=task_list,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=(total + per_page - 1) // per_page
            )
            
            return self._create_response(
                self.success_response(
                    data=response_data.dict(),
                    message="获取任务列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取任务列表失败: {str(e)}",
                    code=500
                )
            )
    
    async def delete_task(self, request: Request, task_id: str = Path(..., description="任务ID")) -> Response:
        """
        删除TTS任务
        
        DELETE /api/tts/tasks/{task_id}
        """
        try:
            success = self.tts_service.delete_task(task_id)
            
            if not success:
                return self._create_response(
                    self.error_response(
                        message="任务不存在",
                        code=404
                    )
                )
            
            return self._create_response(
                self.success_response(
                    data={"task_id": task_id},
                    message="任务删除成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"删除任务失败: {str(e)}",
                    code=500
                )
            )
    
    async def get_providers(self, request: Request) -> Response:
        """
        获取支持的TTS服务提供商
        
        GET /api/tts/providers
        """
        try:
            providers = self.tts_service.get_supported_providers()
            
            provider_list = []
            for provider in providers:
                provider_list.append(TTSProviderInfo(
                    provider=provider["provider"],
                    supported_formats=provider["supported_formats"],
                    supported_voices=provider["supported_voices"],
                    max_text_length=provider["max_text_length"]
                ))
            
            return self._create_response(
                self.success_response(
                    data=[p.dict() for p in provider_list],
                    message="获取服务提供商列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取服务提供商列表失败: {str(e)}",
                    code=500
                )
            )
    
    async def get_voices(self, request: Request, provider: str = Query(..., description="服务提供商")) -> Response:
        """
        获取指定提供商的音色列表
        
        GET /api/tts/voices?provider={provider}
        """
        try:
            voices = self.tts_service.get_supported_voices(provider)
            
            if not voices:
                return self._create_response(
                    self.error_response(
                        message=f"不支持的提供商: {provider}",
                        code=400
                    )
                )
            
            return self._create_response(
                self.success_response(
                    data={"provider": provider, "voices": voices},
                    message="获取音色列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取音色列表失败: {str(e)}",
                    code=500
                )
            )
    
    async def get_formats(self, request: Request, provider: str = Query(..., description="服务提供商")) -> Response:
        """
        获取指定提供商的音频格式列表
        
        GET /api/tts/formats?provider={provider}
        """
        try:
            formats = self.tts_service.get_supported_formats(provider)
            
            if not formats:
                return self._create_response(
                    self.error_response(
                        message=f"不支持的提供商: {provider}",
                        code=400
                    )
                )
            
            return self._create_response(
                self.success_response(
                    data={"provider": provider, "formats": formats},
                    message="获取音频格式列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取音频格式列表失败: {str(e)}",
                    code=500
                )
            )
    
    async def batch_generate(self, request: Request) -> Response:
        """
        批量生成语音
        
        POST /api/tts/batch
        """
        try:
            # 解析请求数据
            data = await request.json()
            
            texts = data.get("texts", [])
            if not texts or len(texts) > 10:  # 限制批量数量
                return self._create_response(
                    self.error_response(
                        message="批量文本数量必须在1-10之间",
                        code=400
                    )
                )
            
            # 获取用户ID
            user_id = getattr(request, 'user_id', None)
            
            # 批量生成语音
            tasks = []
            for text in texts:
                result = await self.tts_service.generate_speech(
                    text=text,
                    provider=data.get("provider", TTSProvider.OPENAI.value),
                    voice=data.get("voice", TTSVoice.OPENAI_ALLOY.value),
                    format=data.get("format", AudioFormat.MP3.value),
                    speed=data.get("speed", 1.0),
                    pitch=data.get("pitch", 1.0),
                    volume=data.get("volume", 1.0),
                    save_to_server=data.get("save_to_server", True),
                    user_id=user_id
                )
                tasks.append(result)
            
            return self._create_response(
                self.success_response(
                    data={"tasks": tasks},
                    message="批量语音生成请求已提交"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"批量语音生成失败: {str(e)}",
                    code=500
                )
            )
