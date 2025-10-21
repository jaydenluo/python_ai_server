"""
通用 Schema 定义
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from pydantic import BaseModel, Field, EmailStr, create_model
from fastapi import Query
from datetime import datetime, date


# ============================================================
# 通用响应模型
# ============================================================

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================
# 查询参数 Schema 生成器
# ============================================================

def create_query_schema_from_response(
    response_schema: Type[BaseModel],
    name: str = "QuerySchema",
    extra_fields: Optional[Dict[str, Any]] = None
) -> Type[BaseModel]:
    """
    从 ResponseSchema 创建查询参数 Schema
    
    Args:
        response_schema: 响应 Schema（如 User.ResponseSchema）
        name: 生成的 Schema 名称
        extra_fields: 额外的查询字段（如 keyword）
    
    Returns:
        查询参数 Schema（所有字段都是 Optional）
    
    示例:
        UserQuerySchema = create_query_schema_from_response(
            User.ResponseSchema,
            name="UserQuerySchema",
            extra_fields={
                'keyword': (Optional[str], Field(None, description="搜索关键词"))
            }
        )
    """
    extra_fields = extra_fields or {}
    
    # 从 ResponseSchema 提取所有字段，都设为 Optional
    fields = {}
    for field_name, field_info in response_schema.__fields__.items():
        # 获取原始类型
        original_type = field_info.annotation
        
        # 设为 Optional
        optional_type = Optional[original_type]
        
        # 使用原始的 description
        description = field_info.field_info.description or f"{field_name} 过滤条件"
        
        fields[field_name] = (optional_type, Field(None, description=description))
    
    # 添加额外字段
    fields.update(extra_fields)
    
    # 创建新 Schema
    QuerySchema = create_model(name, **fields)
    
    return QuerySchema


# ============================================================
# 通用查询参数（用于 Depends）
# ============================================================

class BaseQueryParams(BaseModel):
    """基础查询参数"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    
    class Config:
        # 允许从查询字符串初始化
        from_attributes = True


class UserListParams(BaseQueryParams):
    """用户列表查询参数"""
    # 继承 keyword
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_staff: Optional[bool] = Field(None, description="是否员工")
    dept_id: Optional[int] = Field(None, description="部门ID", gt=0)
    role_id: Optional[int] = Field(None, description="角色ID", gt=0)
    email: Optional[EmailStr] = Field(None, description="邮箱")
    mobile: Optional[str] = Field(None, description="手机号")
    created_after: Optional[date] = Field(None, description="创建时间起始")
    created_before: Optional[date] = Field(None, description="创建时间结束")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向", pattern="^(asc|desc)$")


# ============================================================
# 批量操作
# ============================================================

class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_items=1, description="要删除的ID列表")


class BatchUpdateRequest(BaseModel):
    """批量更新请求"""
    ids: List[int] = Field(..., min_items=1, description="要更新的ID列表")
    data: Dict[str, Any] = Field(..., description="更新的数据")


# ============================================================
# 密码重置
# ============================================================

class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")
    confirm_password: str = Field(..., description="确认密码")
    
    def validate_passwords_match(self) -> bool:
        """验证两次密码是否一致"""
        return self.new_password == self.confirm_password
