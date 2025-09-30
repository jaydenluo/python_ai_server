"""
模型类型枚举
"""

from enum import Enum


class ModelType(Enum):
    """模型类型枚举"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    TIME_SERIES = "time_series"
    
    @classmethod
    def get_display_name(cls, type_name: str) -> str:
        """获取类型显示名称"""
        type_map = {
            "classification": "分类模型",
            "regression": "回归模型",
            "clustering": "聚类模型",
            "nlp": "自然语言处理",
            "computer_vision": "计算机视觉",
            "recommendation": "推荐模型",
            "time_series": "时间序列"
        }
        return type_map.get(type_name, type_name)
    
    @classmethod
    def get_icon(cls, type_name: str) -> str:
        """获取类型图标"""
        icon_map = {
            "classification": "📊",
            "regression": "📈",
            "clustering": "🔍",
            "nlp": "💬",
            "computer_vision": "👁️",
            "recommendation": "🎯",
            "time_series": "⏰"
        }
        return icon_map.get(type_name, "🤖")