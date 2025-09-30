"""
Web控制器模块
所有Web相关的控制器都放在这里
"""

from .home_controller import WebHomeController
from .user_web_api import WebUserController
from .ai_web_api import WebAIController

__all__ = [
    "WebHomeController",
    "WebUserController",
    "WebAIController"
]