"""
OpenAPI文档生成器
自动生成API文档
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class OpenAPISpec:
    """OpenAPI规范"""
    openapi: str = "3.0.3"
    info: Dict[str, Any] = None
    servers: List[Dict[str, str]] = None
    paths: Dict[str, Any] = None
    components: Dict[str, Any] = None
    tags: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.info is None:
            self.info = {
                "title": "AI Framework API",
                "version": "1.0.0",
                "description": "Python AI开发框架API文档"
            }
        if self.servers is None:
            self.servers = [
                {"url": "http://localhost:8000", "description": "开发环境"},
                {"url": "https://api.example.com", "description": "生产环境"}
            ]
        if self.paths is None:
            self.paths = {}
        if self.components is None:
            self.components = {
                "schemas": {},
                "securitySchemes": {}
            }
        if self.tags is None:
            self.tags = []


class OpenAPIGenerator:
    """OpenAPI文档生成器"""
    
    def __init__(self):
        self.spec = OpenAPISpec()
        self._register_components()
        self._register_tags()
    
    def _register_components(self):
        """注册组件"""
        # 安全方案
        self.spec.components["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
        
        # 数据模型
        self.spec.components["schemas"] = {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "username": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "status": {"type": "string", "enum": ["active", "inactive"]},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            },
            "AIModel": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "type": {"type": "string", "enum": ["classification", "regression", "clustering", "nlp", "computer_vision"]},
                    "framework": {"type": "string"},
                    "status": {"type": "string", "enum": ["training", "trained", "deployed", "failed", "archived"]},
                    "accuracy": {"type": "number", "format": "float"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            },
            "APIResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "data": {"type": "object"},
                    "errors": {"type": "array", "items": {"type": "string"}},
                    "meta": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "status_code": {"type": "integer"}
                }
            },
            "PaginationMeta": {
                "type": "object",
                "properties": {
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "per_page": {"type": "integer"},
                            "total": {"type": "integer"},
                            "pages": {"type": "integer"},
                            "has_next": {"type": "boolean"},
                            "has_prev": {"type": "boolean"}
                        }
                    }
                }
            }
        }
    
    def _register_tags(self):
        """注册标签"""
        self.spec.tags = [
            {"name": "用户管理", "description": "用户相关的API接口"},
            {"name": "AI模型", "description": "AI模型相关的API接口"},
            {"name": "认证", "description": "用户认证相关的API接口"},
            {"name": "系统", "description": "系统相关的API接口"}
        ]
    
    def add_path(self, path: str, method: str, operation: Dict[str, Any]):
        """添加路径操作"""
        if path not in self.spec.paths:
            self.spec.paths[path] = {}
        
        self.spec.paths[path][method.lower()] = operation
    
    def generate_user_paths(self):
        """生成用户相关路径"""
        # 获取用户列表
        self.add_path("/api/v1/users", "get", {
            "tags": ["用户管理"],
            "summary": "获取用户列表",
            "description": "获取系统中的所有用户列表",
            "parameters": [
                {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 15}},
                {"name": "search", "in": "query", "schema": {"type": "string"}},
                {"name": "role", "in": "query", "schema": {"type": "string"}},
                {"name": "status", "in": "query", "schema": {"type": "string"}}
            ],
            "responses": {
                "200": {
                    "description": "成功获取用户列表",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/User"}
                                            },
                                            "meta": {"$ref": "#/components/schemas/PaginationMeta"}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        })
        
        # 获取单个用户
        self.add_path("/api/v1/users/{id}", "get", {
            "tags": ["用户管理"],
            "summary": "获取单个用户",
            "description": "根据用户ID获取用户详细信息",
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "responses": {
                "200": {
                    "description": "成功获取用户信息",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                "404": {
                    "description": "用户不存在",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/APIResponse"}
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        })
        
        # 创建用户
        self.add_path("/api/v1/users", "post", {
            "tags": ["用户管理"],
            "summary": "创建用户",
            "description": "创建新的用户账户",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["username", "email", "password"],
                            "properties": {
                                "username": {"type": "string"},
                                "email": {"type": "string", "format": "email"},
                                "password": {"type": "string", "minLength": 8},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "用户创建成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                "400": {
                    "description": "请求数据无效",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/APIResponse"}
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        })
    
    def generate_auth_paths(self):
        """生成认证相关路径"""
        # 用户登录
        self.add_path("/api/v1/auth/login", "post", {
            "tags": ["认证"],
            "summary": "用户登录",
            "description": "用户登录获取访问令牌",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["username", "password"],
                            "properties": {
                                "username": {"type": "string"},
                                "password": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "登录成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "user": {"$ref": "#/components/schemas/User"},
                                                    "token": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                "401": {
                    "description": "认证失败",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/APIResponse"}
                        }
                    }
                }
            }
        })
        
        # 用户注册
        self.add_path("/api/v1/auth/register", "post", {
            "tags": ["认证"],
            "summary": "用户注册",
            "description": "注册新的用户账户",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["username", "email", "password"],
                            "properties": {
                                "username": {"type": "string"},
                                "email": {"type": "string", "format": "email"},
                                "password": {"type": "string", "minLength": 8},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "注册成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                "400": {
                    "description": "注册失败",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/APIResponse"}
                        }
                    }
                }
            }
        })
    
    def generate_ai_model_paths(self):
        """生成AI模型相关路径"""
        # 获取AI模型列表
        self.add_path("/api/v1/models", "get", {
            "tags": ["AI模型"],
            "summary": "获取AI模型列表",
            "description": "获取系统中的所有AI模型列表",
            "parameters": [
                {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 15}},
                {"name": "search", "in": "query", "schema": {"type": "string"}},
                {"name": "type", "in": "query", "schema": {"type": "string"}},
                {"name": "status", "in": "query", "schema": {"type": "string"}}
            ],
            "responses": {
                "200": {
                    "description": "成功获取AI模型列表",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/AIModel"}
                                            },
                                            "meta": {"$ref": "#/components/schemas/PaginationMeta"}
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        })
        
        # 模型预测
        self.add_path("/api/v1/models/{id}/predict", "post", {
            "tags": ["AI模型"],
            "summary": "模型预测",
            "description": "使用指定的AI模型进行预测",
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["input"],
                            "properties": {
                                "input": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "输入数据"
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "预测成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {"$ref": "#/components/schemas/APIResponse"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "model_id": {"type": "integer"},
                                                    "model_name": {"type": "string"},
                                                    "predictions": {
                                                        "type": "array",
                                                        "items": {"type": "object"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        })
    
    def generate_system_paths(self):
        """生成系统相关路径"""
        # 健康检查
        self.add_path("/api/v1/health", "get", {
            "tags": ["系统"],
            "summary": "健康检查",
            "description": "检查API服务状态",
            "responses": {
                "200": {
                    "description": "服务正常",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "version": {"type": "string"},
                                    "timestamp": {"type": "string", "format": "date-time"}
                                }
                            }
                        }
                    }
                }
            }
        })
        
        # API信息
        self.add_path("/api/v1/info", "get", {
            "tags": ["系统"],
            "summary": "API信息",
            "description": "获取API基本信息",
            "responses": {
                "200": {
                    "description": "API信息",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "version": {"type": "string"},
                                    "description": {"type": "string"},
                                    "endpoints": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        })
    
    def generate_documentation(self) -> Dict[str, Any]:
        """生成完整文档"""
        # 生成所有路径
        self.generate_user_paths()
        self.generate_auth_paths()
        self.generate_ai_model_paths()
        self.generate_system_paths()
        
        # 转换为字典
        return {
            "openapi": self.spec.openapi,
            "info": self.spec.info,
            "servers": self.spec.servers,
            "paths": self.spec.paths,
            "components": self.spec.components,
            "tags": self.spec.tags
        }
    
    def save_documentation(self, file_path: str):
        """保存文档到文件"""
        doc = self.generate_documentation()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    
    def get_json_documentation(self) -> str:
        """获取JSON格式的文档"""
        doc = self.generate_documentation()
        return json.dumps(doc, ensure_ascii=False, indent=2)


# 创建文档生成器实例
openapi_generator = OpenAPIGenerator()