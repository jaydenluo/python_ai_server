"""
AI服务统一鉴权控制器
提供多平台AI服务的WebSocket鉴权接口
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Query, Path
from app.core.controllers.base_controller import *
from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.token_service import TokenService, PlatformType, ServiceType
from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    """统一鉴权请求"""
    platform: str = Field(..., description="平台名称: xunfei/baidu/aliyun/openai等")
    service: str = Field(..., description="服务类型: tts/asr/llm")
    user_id: Optional[str] = Field(None, description="用户ID")
    params: Dict[str, Any] = Field(default_factory=dict, description="服务参数(不同平台不同)")


class AuthResponse(BaseModel):
    """统一鉴权响应"""
    platform: str = Field(..., description="平台名称")
    service: str = Field(..., description="服务类型")
    ws_url: str = Field(..., description="WebSocket连接地址")
    request_id: str = Field(..., description="请求ID")
    expires_at: int = Field(..., description="过期时间戳")
    params: Optional[Dict[str, Any]] = Field(None, description="额外参数(如需要)")


@api_controller(prefix="/api/auth", tags=["API - 鉴权服务"])
class AuthController(BaseController):
    """统一鉴权控制器"""
    
    def __init__(self):
        super().__init__()
        self.token_service = TokenService()
        self._init_providers()
    
    def _init_providers(self):
        """初始化所有平台的token提供者"""
        from app.core.config.settings import config
        
        # 初始化讯飞
        xunfei_config = config.get('xunfei', {})
        if all([xunfei_config.get('app_id'), xunfei_config.get('api_key'), xunfei_config.get('api_secret')]):
            from app.services.token_service import XunfeiTokenProvider
            xunfei_provider = XunfeiTokenProvider({
                'app_id': xunfei_config['app_id'],
                'api_key': xunfei_config['api_key'],
                'api_secret': xunfei_config['api_secret'],
                'super_tts_endpoint': config.get('xunfei.endpoints.super_tts'),
                'quota': {
                    'tts': config.get('xunfei.quota.tts', 100),
                    'asr': config.get('xunfei.quota.asr', 100),
                    'llm': config.get('xunfei.quota.spark', 50)
                }
            })
            self.token_service.register_provider(PlatformType.XUNFEI, xunfei_provider)
        
        # TODO: 初始化百度
        # baidu_config = config.get('baidu', {})
        # if baidu_config.get('api_key'):
        #     from app.services.token_service import BaiduTokenProvider
        #     baidu_provider = BaiduTokenProvider(baidu_config)
        #     self.token_service.register_provider(PlatformType.BAIDU, baidu_provider)
        
        # TODO: 初始化阿里云
        # aliyun_config = config.get('aliyun', {})
        # if aliyun_config.get('access_key_id'):
        #     from app.services.token_service import AliyunTokenProvider
        #     aliyun_provider = AliyunTokenProvider(aliyun_config)
        #     self.token_service.register_provider(PlatformType.ALIYUN, aliyun_provider)
    
    @post("/generate")
    async def generate_auth(self, auth_request: AuthRequest, request: Request = None):
        """
            生成AI服务WebSocket连接鉴权
            POST /api/auth/generate
            支持的平台：
            - xunfei: 讯飞语音
            - baidu: 百度AI
            - aliyun: 阿里云
            - openai: OpenAI (如需WebSocket)
            支持的服务：
            - tts: 语音合成
            - asr: 语音识别
            - llm: 大语言模型
            参数示例（讯飞TTS）：
            {
                "platform": "xunfei",
                "service": "tts",
                "user_id": "user123",
                "params": {
                    "text": "你好，世界",
                    "voice": "x5_lingfeiyi_flow",
                    "speed": 50,
                    "volume": 50,
                    "pitch": 50,
                    "audio_format": "lame",
                    "oral_level": "mid"
                }
            }
            参数示例（讯飞ASR）：
            {
                "platform": "xunfei",
                "service": "asr",
                "user_id": "user123",
                "params": {
                    "audio_format": "raw",
                    "sample_rate": 16000,
                    "language": "zh_cn"
                }
            }
        """
        print(f"\n[DEBUG] generate_auth 开始执行")
        print(f"[DEBUG] 收到请求参数: platform={auth_request.platform}, service={auth_request.service}, user_id={auth_request.user_id}")
        print(f"[DEBUG] params: {auth_request.params}")
        
        try:
            print(f"[DEBUG] 开始转换平台类型...")
            # 转换平台类型
            platform_map = {
                'xunfei': PlatformType.XUNFEI,
                'baidu': PlatformType.BAIDU,
                'aliyun': PlatformType.ALIYUN
            }
            
            platform = platform_map.get(auth_request.platform.lower())
            print(f"[DEBUG] 平台转换结果: {platform}")
            
            if not platform:
                print(f"[DEBUG] 平台不支持，返回错误")
                resp_data = self.error_response(
                    message=f"不支持的平台: {auth_request.platform}，支持的平台: {', '.join(platform_map.keys())}",
                    status_code=400
                )
                return JSONResponse(content=resp_data.to_dict(), status_code=resp_data.status_code)
            
            print(f"[DEBUG] 开始转换服务类型...")
            # 转换服务类型
            service_map = {
                'tts': ServiceType.TTS,
                'asr': ServiceType.ASR,
                'llm': ServiceType.LLM
            }
            
            service = service_map.get(auth_request.service.lower())
            print(f"[DEBUG] 服务转换结果: {service}")
            
            if not service:
                print(f"[DEBUG] 服务类型不支持，返回错误")
                resp_data = self.error_response(
                    message=f"不支持的服务类型: {auth_request.service}，支持的服务: {', '.join(service_map.keys())}",
                    status_code=400
                )
                return JSONResponse(content=resp_data.to_dict(), status_code=resp_data.status_code)
            
            # 获取用户ID
            user_id = auth_request.user_id or getattr(request, 'user_id', None) or 'anonymous'
            print(f"[DEBUG] 用户ID: {user_id}")
            
            # 生成鉴权信息
            print(f"[DEBUG] 调用token_service.generate_auth...")
            auth_info = await self.token_service.generate_auth(
                platform=platform,
                service=service,
                user_id=user_id,
                **auth_request.params
            )
            print(f"[DEBUG] token_service.generate_auth 返回: {auth_info}")
            
            # 构建响应
            print(f"[DEBUG] 构建响应数据...")
            response_data = AuthResponse(
                platform=auth_request.platform,
                service=auth_request.service,
                ws_url=auth_info['ws_url'],
                request_id=auth_info['request_id'],
                expires_at=auth_info['expires_at'],
                params=auth_info.get('params')
            )
            
            resp_data = self.success_response(
                data=response_data.model_dump(),  # Pydantic 2.x 使用 model_dump() 而不是 dict()
                message=f"{auth_request.platform} {auth_request.service} 鉴权信息生成成功"
            )
            print(f"[DEBUG] 生成成功，返回响应")
            return JSONResponse(content=resp_data.to_dict(), status_code=resp_data.status_code)
            
        except ValueError as e:
            print(f"[ERROR] ValueError: {e}")
            import traceback
            traceback.print_exc()
            resp_data = self.error_response(
                message=f"参数验证失败: {str(e)}",
                status_code=400
            )
            return JSONResponse(content=resp_data.to_dict(), status_code=resp_data.status_code)
        except KeyError as e:
            print(f"[ERROR] KeyError: {e}")
            import traceback
            traceback.print_exc()
            resp_data = self.error_response(
                message=f"平台未配置或未注册: {str(e)}",
                status_code=404
            )
            return JSONResponse(content=resp_data.to_dict(), status_code=resp_data.status_code)
        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()
            resp_data = self.error_response(
                message=f"生成鉴权信息失败: {str(e)}",
                status_code=500
            )
            return JSONResponse(content=resp_data.to_dict(), status_code=resp_data.status_code)
    
    @get("/platforms")
    async def get_platforms(self, request: Request):
        """
        获取已配置的平台列表
        
        GET /api/auth/platforms
        """
        print(f"\n[DEBUG] get_platforms 开始执行")
        try:
            platforms = []
            print(f"[DEBUG] 开始遍历平台类型...")
            
            for platform_type in PlatformType:
                if platform_type in self.token_service.providers:
                    platforms.append({
                        "id": platform_type.value,
                        "name": self._get_platform_name(platform_type),
                        "enabled": True,
                        "services": ["tts", "asr", "llm"]  # TODO: 从provider获取支持的服务
                    })
            
            print(f"[DEBUG] 找到 {len(platforms)} 个平台")
            response_data = self.success_response(
                data={"platforms": platforms},
                message="获取平台列表成功"
            )
            print(f"[DEBUG] 返回成功响应")
            return JSONResponse(content=response_data.to_dict(), status_code=response_data.status_code)
            
        except Exception as e:
            print(f"[ERROR] get_platforms Exception: {e}")
            import traceback
            traceback.print_exc()
            response_data = self.error_response(
                message=f"获取平台列表失败: {str(e)}",
                status_code=500
            )
            return JSONResponse(content=response_data.to_dict(), status_code=response_data.status_code)
    
    def _get_platform_name(self, platform: PlatformType) -> str:
        """获取平台中文名称"""
        name_map = {
            PlatformType.XUNFEI: "讯飞语音",
            PlatformType.BAIDU: "百度AI",
            PlatformType.ALIYUN: "阿里云"
        }
        return name_map.get(platform, platform.value)
