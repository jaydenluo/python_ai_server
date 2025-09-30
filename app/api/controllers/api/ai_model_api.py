"""
API AI模型控制器
负责AI模型管理功能
"""

from typing import Dict, Any, List
from app.api.controllers.base import ResourceController, APIResponse
from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, rate_limit, cache, validate, api_doc
)
from app.models.ai_model import AIModel
from app.core.middleware.base import Request, Response


@api_controller(prefix="/api", version="v1", middleware=["auth"])
class APIAIModelController(ResourceController):
    """API AI模型控制器 - AI模型管理功能"""
    
    def __init__(self):
        super().__init__(AIModel)
    
    @get("/ai-models", name="api.ai_models.index")
    @auth_required
    @rate_limit(requests_per_minute=60, requests_per_hour=1000)
    @cache(ttl=300)
    @api_doc(
        summary="获取AI模型列表",
        description="获取可用的AI模型列表",
        tags=["API-AI模型管理"],
        responses={
            "200": {"description": "成功获取AI模型列表"},
            "401": {"description": "未授权访问"},
            "429": {"description": "请求过于频繁"}
        }
    )
    async def index(self, request: Request) -> Response:
        """获取AI模型列表 - API专用"""
        try:
            # 获取查询参数
            page = int(request.query_params.get("page", 1))
            per_page = int(request.query_params.get("per_page", 15))
            category = request.query_params.get("category", "")
            status = request.query_params.get("status", "")
            
            # 构建查询
            query = self.query
            
            # 分类筛选
            if category:
                query = query.where("category", category)
            
            # 状态筛选
            if status:
                query = query.where("status", status)
            
            # 分页
            models = query.paginate(page, per_page)
            
            # 转换数据格式
            models_data = []
            for model in models:
                model_dict = model.to_dict()
                models_data.append(model_dict)
            
            return self._create_response(
                self.success_response(
                    data={
                        "ai_models": models_data,
                        "pagination": {
                            "page": page,
                            "per_page": per_page,
                            "total": query.count()
                        }
                    },
                    message="获取AI模型列表成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"获取AI模型列表失败: {str(e)}")
            )
    
    @get("/ai-models/{id}", name="api.ai_models.show")
    @auth_required
    @cache(ttl=600)
    @api_doc(
        summary="获取AI模型详细信息",
        description="获取指定AI模型的详细信息",
        tags=["API-AI模型管理"],
        responses={
            "200": {"description": "成功获取AI模型信息"},
            "404": {"description": "AI模型不存在"},
            "401": {"description": "未授权访问"}
        }
    )
    async def show(self, request: Request) -> Response:
        """获取AI模型详细信息 - API专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            model_id = path_parts[-1]
            
            # 查找AI模型
            model = self.query.find(model_id)
            
            if not model:
                return self._create_response(
                    self.not_found_response("AI模型不存在")
                )
            
            # 转换数据格式
            model_dict = model.to_dict()
            
            return self._create_response(
                self.success_response(
                    data=model_dict,
                    message="获取AI模型信息成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"获取AI模型信息失败: {str(e)}")
            )
    
    @post("/ai-models", name="api.ai_models.store")
    @auth_required
    @validate({
        "name": "required|unique:ai_models,name",
        "description": "required",
        "category": "required|in:nlp,vision,audio,multimodal",
        "framework": "required|in:pytorch,tensorflow,onnx,huggingface"
    })
    @api_doc(
        summary="创建AI模型",
        description="创建新的AI模型",
        tags=["API-AI模型管理"],
        responses={
            "201": {"description": "AI模型创建成功"},
            "400": {"description": "请求参数错误"},
            "401": {"description": "未授权访问"}
        }
    )
    async def store(self, request: Request) -> Response:
        """创建AI模型 - API专用"""
        try:
            # 获取请求数据
            data = request.json
            
            # 创建AI模型
            model = AIModel()
            model.name = data.get("name")
            model.description = data.get("description")
            model.category = data.get("category")
            model.framework = data.get("framework")
            model.status = "active"
            
            # 保存AI模型
            model.save()
            
            return self._create_response(
                self.success_response(
                    data=model.to_dict(),
                    message="AI模型创建成功",
                    status_code=201
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"创建AI模型失败: {str(e)}")
            )
    
    @post("/ai-models/{id}/predict", name="api.ai_models.predict")
    @auth_required
    @rate_limit(requests_per_minute=30, requests_per_hour=500)
    @validate({
        "input": "required",
        "parameters": "array"
    })
    @api_doc(
        summary="AI模型预测",
        description="使用AI模型进行预测",
        tags=["API-AI模型管理"],
        responses={
            "200": {"description": "预测成功"},
            "400": {"description": "请求参数错误"},
            "401": {"description": "未授权访问"},
            "404": {"description": "AI模型不存在"}
        }
    )
    async def predict(self, request: Request) -> Response:
        """AI模型预测 - API专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            model_id = path_parts[-2]  # 因为路径是 /ai-models/{id}/predict
            
            # 查找AI模型
            model = self.query.find(model_id)
            
            if not model:
                return self._create_response(
                    self.not_found_response("AI模型不存在")
                )
            
            # 获取请求数据
            data = request.json
            input_data = data.get("input")
            parameters = data.get("parameters", {})
            
            # 模拟AI模型预测
            prediction_result = {
                "model_id": model_id,
                "model_name": model.name,
                "input": input_data,
                "output": "预测结果",
                "confidence": 0.95,
                "processing_time": 0.5,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            return self._create_response(
                self.success_response(
                    data=prediction_result,
                    message="AI模型预测成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"AI模型预测失败: {str(e)}")
            )
    
    @put("/ai-models/{id}", name="api.ai_models.update")
    @auth_required
    @validate({
        "name": "required",
        "description": "required",
        "category": "required|in:nlp,vision,audio,multimodal"
    })
    @api_doc(
        summary="更新AI模型信息",
        description="更新AI模型信息",
        tags=["API-AI模型管理"],
        responses={
            "200": {"description": "AI模型更新成功"},
            "404": {"description": "AI模型不存在"},
            "401": {"description": "未授权访问"}
        }
    )
    async def update(self, request: Request) -> Response:
        """更新AI模型信息 - API专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            model_id = path_parts[-1]
            
            # 查找AI模型
            model = self.query.find(model_id)
            
            if not model:
                return self._create_response(
                    self.not_found_response("AI模型不存在")
                )
            
            # 获取请求数据
            data = request.json
            
            # 更新AI模型信息
            model.name = data.get("name", model.name)
            model.description = data.get("description", model.description)
            model.category = data.get("category", model.category)
            
            # 保存更新
            model.save()
            
            return self._create_response(
                self.success_response(
                    data=model.to_dict(),
                    message="AI模型更新成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"更新AI模型失败: {str(e)}")
            )
    
    @delete("/ai-models/{id}", name="api.ai_models.destroy")
    @auth_required
    @api_doc(
        summary="删除AI模型",
        description="删除AI模型",
        tags=["API-AI模型管理"],
        responses={
            "200": {"description": "AI模型删除成功"},
            "404": {"description": "AI模型不存在"},
            "401": {"description": "未授权访问"}
        }
    )
    async def destroy(self, request: Request) -> Response:
        """删除AI模型 - API专用"""
        try:
            # 从路径中提取ID
            path_parts = request.path.split("/")
            model_id = path_parts[-1]
            
            # 查找AI模型
            model = self.query.find(model_id)
            
            if not model:
                return self._create_response(
                    self.not_found_response("AI模型不存在")
                )
            
            # 删除AI模型
            model.delete()
            
            return self._create_response(
                self.success_response(
                    message="AI模型删除成功"
                )
            )
            
        except Exception as e:
            return self._create_response(
                self.server_error_response(f"删除AI模型失败: {str(e)}")
            )