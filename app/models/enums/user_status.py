"""
用户状态枚举
"""

from enum import Enum


class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    
    @classmethod
    def get_display_name(cls, status: str) -> str:
        """获取状态显示名称"""
        status_map = {
            "active": "活跃",
            "inactive": "非活跃",
            "suspended": "已暂停",
            "pending": "待审核"
        }
        return status_map.get(status, status)
    
    @classmethod
    def get_color(cls, status: str) -> str:
        """获取状态颜色"""
        color_map = {
            "active": "green",
            "inactive": "gray",
            "suspended": "red",
            "pending": "yellow"
        }
        return color_map.get(status, "gray")