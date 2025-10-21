"""
语音服务音色管理控制器
提供语音服务提供商和音色列表查询接口
"""

from typing import Dict, List, Any
from app.core.controllers.base_controller import *
from app.core.middleware.base import Request, Response
from app.services.ai.voice_service import VoiceService


@api_controller(prefix="/api/voice", tags=["API - 语音服务"])
class VoiceController(BaseController):
    """语音服务控制器"""
    
    def __init__(self):
        super().__init__()
        self.voice_service = VoiceService()
    
    @get("/providers")
    async def get_providers(self, request: Request) -> Response:
        """
        获取语音服务提供商列表
        
        GET /api/voice/providers
        """
        try:
            providers = self.voice_service.get_providers()
            
            return self._create_response(
                self.success_response(
                    data=providers,
                    message="获取提供商列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取提供商列表失败: {str(e)}",
                    code=500
                )
            )
    
    @get("/list")
    async def get_voice_list(self, request: Request) -> Response:
        """
        获取指定提供商的音色列表
        
        GET /api/voice/list?provider={provider_id}
        """
        try:
            # 获取提供商ID参数
            provider_id = request.query_params.get('provider')
            
            if not provider_id:
                return self._create_response(
                    self.error_response(
                        message="缺少provider参数",
                        errors=["provider参数不能为空"],
                        code=400
                    )
                )
            
            # 获取音色列表
            voice_data = self.voice_service.get_voice_list(provider_id)
            
            if voice_data is None:
                return self._create_response(
                    self.error_response(
                        message="提供商不存在或未启用",
                        errors=[f"提供商 '{provider_id}' 不存在"],
                        code=404
                    )
                )
            
            return self._create_response(
                self.success_response(
                    data=voice_data,
                    message="获取音色列表成功"
                )
            )
            
        except ValueError as e:
            return self._create_response(
                self.error_response(
                    message="参数验证失败",
                    errors=[str(e)],
                    code=400
                )
            )
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取音色列表失败: {str(e)}",
                    code=500
                )
            )
    
    @get("/detail/{voice_id}")
    async def get_voice_detail(self, request: Request, voice_id: str) -> Response:
        """
        获取音色详情
        
        GET /api/voice/detail/{voice_id}
        """
        try:
            # 获取提供商ID参数（可选）
            provider_id = request.query_params.get('provider')
            
            voice_detail = self.voice_service.get_voice_detail(voice_id, provider_id)
            
            if voice_detail is None:
                return self._create_response(
                    self.error_response(
                        message="音色不存在",
                        errors=[f"音色 '{voice_id}' 不存在"],
                        code=404
                    )
                )
            
            return self._create_response(
                self.success_response(
                    data=voice_detail,
                    message="获取音色详情成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.error_response(
                    message=f"获取音色详情失败: {str(e)}",
                    code=500
                )
            )

