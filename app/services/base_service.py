"""
⚠️ DEPRECATED - 已废弃

此文件已移动到 app/core/services/base_service.py

请更新导入：
- 旧: from app.services.base_service import BaseService
- 新: from app.core.services import BaseService

理由：
1. BaseService 是框架核心组件，应该放在 app/core 目录下
2. UserService 等具体业务服务应该单独放在各自的文件中
3. 更清晰的架构分层：core（框架）和 services（业务）分离

此文件将在下一个版本中删除。
"""

# 为了向后兼容，暂时保留导入
from app.core.services import BaseService

__all__ = ['BaseService']
