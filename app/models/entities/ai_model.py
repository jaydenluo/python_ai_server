"""
AI模型实体
提供AI模型相关的数据模型和关系
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.core.orm.models import Model, Relationship
from app.core.orm.query import ModelQuery


class AIModel(Model):
    """AI模型"""
    
    __table__ = "ai_models"
    __fillable__ = [
        "user_id", "name", "description", "type", "framework", "version",
        "status", "file_path", "file_size", "accuracy", "precision",
        "recall", "f1_score", "training_data_size", "training_time",
        "hyperparameters", "metrics", "tags", "is_public"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def is_trained(self) -> bool:
        """是否已训练"""
        return self.status == "trained"
    
    @property
    def is_deployed(self) -> bool:
        """是否已部署"""
        return self.status == "deployed"
    
    @property
    def is_public(self) -> bool:
        """是否公开"""
        return getattr(self, 'is_public', False)
    
    @property
    def file_size_mb(self) -> float:
        """文件大小（MB）"""
        if hasattr(self, 'file_size') and self.file_size:
            return self.file_size / (1024 * 1024)
        return 0.0
    
    @property
    def training_time_hours(self) -> float:
        """训练时间（小时）"""
        if hasattr(self, 'training_time') and self.training_time:
            return self.training_time / 3600
        return 0.0
    
    def get_user(self) -> 'User':
        """获取模型所有者"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取AI模型 {self.name} 的所有者")
        return None
    
    def get_training_logs(self) -> List['TrainingLog']:
        """获取训练日志"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取AI模型 {self.name} 的训练日志")
        return []
    
    def get_predictions(self) -> List['Prediction']:
        """获取预测结果"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取AI模型 {self.name} 的预测结果")
        return []
    
    def deploy(self):
        """部署模型"""
        self.status = "deployed"
        self.save()
    
    def archive(self):
        """归档模型"""
        self.status = "archived"
        self.save()
    
    def make_public(self):
        """设为公开"""
        self.is_public = True
        self.save()
    
    def make_private(self):
        """设为私有"""
        self.is_public = False
        self.save()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'framework': self.framework,
            'version': self.version,
            'status': self.status,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'training_data_size': self.training_data_size,
            'training_time': self.training_time,
            'training_time_hours': self.training_time_hours,
            'hyperparameters': self.hyperparameters,
            'metrics': self.metrics,
            'tags': self.tags,
            'is_public': self.is_public,
            'is_trained': self.is_trained,
            'is_deployed': self.is_deployed,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }