"""
模型状态枚举
"""

from enum import Enum


class ModelStatus(Enum):
    """模型状态枚举"""
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"
    
    @classmethod
    def get_display_name(cls, status: str) -> str:
        """获取状态显示名称"""
        status_map = {
            "training": "训练中",
            "trained": "已训练",
            "deployed": "已部署",
            "failed": "失败",
            "archived": "已归档"
        }
        return status_map.get(status, status)
    
    @classmethod
    def get_color(cls, status: str) -> str:
        """获取状态颜色"""
        color_map = {
            "training": "blue",
            "trained": "green",
            "deployed": "purple",
            "failed": "red",
            "archived": "gray"
        }
        return color_map.get(status, "gray")