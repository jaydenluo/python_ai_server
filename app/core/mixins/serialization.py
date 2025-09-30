"""
序列化混入
提供通用的数据序列化功能
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime, date
from decimal import Decimal
import json
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped


class SerializationMixin:
    """序列化混入"""
    
    # 序列化配置
    __serialize_fields__: Optional[List[str]] = None  # 指定要序列化的字段
    __exclude_fields__: Optional[List[str]] = None    # 排除的字段
    __hidden_fields__: Optional[List[str]] = None     # 隐藏字段
    __datetime_format__: str = "iso"                  # 日期时间格式
    __json_ensure_ascii__: bool = False               # JSON编码设置
    
    def to_dict(self, include_hidden: bool = False, **kwargs) -> Dict[str, Any]:
        """转换为字典"""
        # 获取字段配置
        serialize_fields = self.__serialize_fields__
        exclude_fields = self.__exclude_fields__ or []
        hidden_fields = self.__hidden_fields__ or []
        
        # 如果没有指定字段，获取所有列
        if serialize_fields is None:
            mapper = inspect(self.__class__)
            serialize_fields = [column.name for column in mapper.columns]
        
        # 过滤字段
        if not include_hidden:
            serialize_fields = [f for f in serialize_fields if f not in hidden_fields]
        
        # 排除字段
        serialize_fields = [f for f in serialize_fields if f not in exclude_fields]
        
        # 构建字典
        result = {}
        for field in serialize_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                result[field] = self._serialize_value(value)
        
        # 添加计算属性
        result.update(self._get_computed_properties())
        
        return result
    
    def to_json(self, include_hidden: bool = False, **kwargs) -> str:
        """转换为JSON字符串"""
        data = self.to_dict(include_hidden=include_hidden, **kwargs)
        return json.dumps(
            data, 
            ensure_ascii=self.__json_ensure_ascii__,
            indent=kwargs.get('indent', 2),
            default=self._json_serializer
        )
    
    def to_public_dict(self) -> Dict[str, Any]:
        """转换为公开字典（隐藏敏感信息）"""
        return self.to_dict(include_hidden=False)
    
    def to_admin_dict(self) -> Dict[str, Any]:
        """转换为管理员字典（包含所有信息）"""
        return self.to_dict(include_hidden=True)
    
    def _serialize_value(self, value: Any) -> Any:
        """序列化单个值"""
        if value is None:
            return None
        elif isinstance(value, datetime):
            return self._serialize_datetime(value)
        elif isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        else:
            return value
    
    def _serialize_datetime(self, dt: datetime) -> str:
        """序列化日期时间"""
        if self.__datetime_format__ == "iso":
            return dt.isoformat()
        elif self.__datetime_format__ == "timestamp":
            return dt.timestamp()
        else:
            return dt.strftime(self.__datetime_format__)
    
    def _get_computed_properties(self) -> Dict[str, Any]:
        """获取计算属性"""
        computed = {}
        
        # 获取所有属性方法
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(self.__class__, attr_name, None)
            if attr and isinstance(attr, property):
                try:
                    computed[attr_name] = getattr(self, attr_name)
                except Exception:
                    pass  # 忽略无法计算的属性
        
        return computed
    
    def _json_serializer(self, obj: Any) -> Any:
        """JSON序列化器"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return str(obj)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs):
        """从字典创建实例"""
        # 过滤掉非列字段
        mapper = inspect(cls)
        column_names = {column.name for column in mapper.columns}
        
        filtered_data = {
            key: value for key, value in data.items() 
            if key in column_names
        }
        
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str, **kwargs):
        """从JSON字符串创建实例"""
        data = json.loads(json_str)
        return cls.from_dict(data, **kwargs)


class TimestampMixin:
    """时间戳混入"""
    
    def to_dict(self, include_hidden: bool = False, **kwargs) -> Dict[str, Any]:
        """重写to_dict方法，添加时间戳处理"""
        data = super().to_dict(include_hidden=include_hidden, **kwargs)
        
        # 添加时间戳字段
        if hasattr(self, 'created_at') and self.created_at:
            data['created_at'] = self._serialize_datetime(self.created_at)
        
        if hasattr(self, 'updated_at') and self.updated_at:
            data['updated_at'] = self._serialize_datetime(self.updated_at)
        
        return data


class SoftDeleteMixin:
    """软删除混入"""
    
    def to_dict(self, include_hidden: bool = False, **kwargs) -> Dict[str, Any]:
        """重写to_dict方法，添加软删除处理"""
        data = super().to_dict(include_hidden=include_hidden, **kwargs)
        
        # 添加软删除字段
        if hasattr(self, 'deleted_at') and self.deleted_at:
            data['deleted_at'] = self._serialize_datetime(self.deleted_at)
        
        if hasattr(self, 'is_deleted'):
            data['is_deleted'] = self.is_deleted
        
        return data


class AuditMixin:
    """审计混入"""
    
    def to_dict(self, include_hidden: bool = False, **kwargs) -> Dict[str, Any]:
        """重写to_dict方法，添加审计信息"""
        data = super().to_dict(include_hidden=include_hidden, **kwargs)
        
        # 添加审计字段
        if hasattr(self, 'created_by') and self.created_by:
            data['created_by'] = self.created_by
        
        if hasattr(self, 'updated_by') and self.updated_by:
            data['updated_by'] = self.updated_by
        
        return data