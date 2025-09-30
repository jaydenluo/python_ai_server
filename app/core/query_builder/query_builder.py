"""
查询构建器
提供链式查询接口，充分利用SQLAlchemy的强大功能
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Tuple, Callable
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload
from sqlalchemy import and_, or_, not_, func, desc, asc, text, case, cast, extract
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date, timedelta
import json

T = TypeVar('T')


class QueryBuilder:
    """查询构建器 - 提供链式查询接口"""
    
    def __init__(self, model_class: Type[T], session: Session):
        self.model_class = model_class
        self.session = session
        self.query = session.query(model_class)
        self._conditions = []
        self._joins = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._limit_value = None
        self._offset_value = None
        self._distinct = False
        self._select_fields = None
    
    def where(self, field: str, operator: str = "eq", value: Any = None) -> 'QueryBuilder':
        """添加WHERE条件"""
        if not hasattr(self.model_class, field):
            raise AttributeError(f"Model {self.model_class.__name__} has no field '{field}'")
        
        field_attr = getattr(self.model_class, field)
        
        if operator == "eq":
            self._conditions.append(field_attr == value)
        elif operator == "ne":
            self._conditions.append(field_attr != value)
        elif operator == "gt":
            self._conditions.append(field_attr > value)
        elif operator == "gte":
            self._conditions.append(field_attr >= value)
        elif operator == "lt":
            self._conditions.append(field_attr < value)
        elif operator == "lte":
            self._conditions.append(field_attr <= value)
        elif operator == "like":
            self._conditions.append(field_attr.like(f"%{value}%"))
        elif operator == "ilike":
            self._conditions.append(field_attr.ilike(f"%{value}%"))
        elif operator == "in":
            self._conditions.append(field_attr.in_(value))
        elif operator == "not_in":
            self._conditions.append(field_attr.notin_(value))
        elif operator == "is_null":
            self._conditions.append(field_attr.is_(None))
        elif operator == "is_not_null":
            self._conditions.append(field_attr.isnot(None))
        elif operator == "between":
            self._conditions.append(field_attr.between(value[0], value[1]))
        elif operator == "contains":
            self._conditions.append(field_attr.contains(value))
        elif operator == "overlap":
            self._conditions.append(field_attr.overlap(value))
        elif operator == "json_contains":
            self._conditions.append(field_attr[value[0]] == value[1])
        elif operator == "date_extract":
            self._conditions.append(extract(value[0], field_attr) == value[1])
        else:
            raise ValueError(f"Unsupported operator: {operator}")
        
        return self
    
    def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """IN条件"""
        return self.where(field, "in", values)
    
    def where_not_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """NOT IN条件"""
        return self.where(field, "not_in", values)
    
    def where_like(self, field: str, value: str) -> 'QueryBuilder':
        """LIKE条件"""
        return self.where(field, "like", value)
    
    def where_ilike(self, field: str, value: str) -> 'QueryBuilder':
        """ILIKE条件"""
        return self.where(field, "ilike", value)
    
    def where_between(self, field: str, start: Any, end: Any) -> 'QueryBuilder':
        """BETWEEN条件"""
        return self.where(field, "between", [start, end])
    
    def where_null(self, field: str) -> 'QueryBuilder':
        """IS NULL条件"""
        return self.where(field, "is_null")
    
    def where_not_null(self, field: str) -> 'QueryBuilder':
        """IS NOT NULL条件"""
        return self.where(field, "is_not_null")
    
    def where_date_range(self, field: str, start_date: date, end_date: date) -> 'QueryBuilder':
        """日期范围条件"""
        return self.where(field, "between", [start_date, end_date])
    
    def where_this_week(self, field: str) -> 'QueryBuilder':
        """本周条件"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return self.where_date_range(field, start_of_week, end_of_week)
    
    def where_this_month(self, field: str) -> 'QueryBuilder':
        """本月条件"""
        today = date.today()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return self.where_date_range(field, start_of_month, end_of_month)
    
    def where_json(self, field: str, json_path: str, value: Any) -> 'QueryBuilder':
        """JSON字段条件"""
        return self.where(field, "json_contains", [json_path, value])
    
    def where_array_contains(self, field: str, value: Any) -> 'QueryBuilder':
        """数组包含条件"""
        return self.where(field, "contains", value)
    
    def where_array_overlap(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """数组重叠条件"""
        return self.where(field, "overlap", values)
    
    def where_date_part(self, field: str, part: str, value: Any) -> 'QueryBuilder':
        """日期部分条件"""
        return self.where(field, "date_extract", [part, value])
    
    def or_where(self, field: str, operator: str = "eq", value: Any = None) -> 'QueryBuilder':
        """OR条件"""
        if not hasattr(self.model_class, field):
            raise AttributeError(f"Model {self.model_class.__name__} has no field '{field}'")
        
        field_attr = getattr(self.model_class, field)
        
        if operator == "eq":
            condition = field_attr == value
        elif operator == "ne":
            condition = field_attr != value
        elif operator == "like":
            condition = field_attr.like(f"%{value}%")
        elif operator == "ilike":
            condition = field_attr.ilike(f"%{value}%")
        else:
            raise ValueError(f"Unsupported operator for OR: {operator}")
        
        if self._conditions:
            self._conditions = [or_(self._conditions[0], condition)]
        else:
            self._conditions.append(condition)
        
        return self
    
    def join(self, relation: str, join_type: str = "inner") -> 'QueryBuilder':
        """添加JOIN"""
        if not hasattr(self.model_class, relation):
            raise AttributeError(f"Model {self.model_class.__name__} has no relation '{relation}'")
        
        relation_attr = getattr(self.model_class, relation)
        
        if join_type.lower() == "left":
            self.query = self.query.outerjoin(relation_attr)
        elif join_type.lower() == "right":
            self.query = self.query.join(relation_attr, isouter=True)
        else:
            self.query = self.query.join(relation_attr)
        
        self._joins.append(relation)
        return self
    
    def with_relations(self, relations: List[str]) -> 'QueryBuilder':
        """预加载关联数据"""
        for relation in relations:
            if hasattr(self.model_class, relation):
                self.query = self.query.options(joinedload(getattr(self.model_class, relation)))
        return self
    
    def with_subquery_relations(self, relations: List[str]) -> 'QueryBuilder':
        """使用子查询加载关联数据"""
        for relation in relations:
            if hasattr(self.model_class, relation):
                self.query = self.query.options(selectinload(getattr(self.model_class, relation)))
        return self
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """选择特定字段"""
        field_attrs = [getattr(self.model_class, field) for field in fields]
        self.query = self.query.with_entities(*field_attrs)
        self._select_fields = fields
        return self
    
    def distinct(self) -> 'QueryBuilder':
        """去重"""
        self.query = self.query.distinct()
        self._distinct = True
        return self
    
    def order_by(self, field: str, direction: str = "asc") -> 'QueryBuilder':
        """排序"""
        if not hasattr(self.model_class, field):
            raise AttributeError(f"Model {self.model_class.__name__} has no field '{field}'")
        
        field_attr = getattr(self.model_class, field)
        
        if direction.lower() == "desc":
            self.query = self.query.order_by(desc(field_attr))
        else:
            self.query = self.query.order_by(asc(field_attr))
        
        self._order_by.append((field, direction))
        return self
    
    def order_by_multiple(self, order_fields: List[Tuple[str, str]]) -> 'QueryBuilder':
        """多字段排序"""
        for field, direction in order_fields:
            self.order_by(field, direction)
        return self
    
    def group_by(self, field: str) -> 'QueryBuilder':
        """分组"""
        if not hasattr(self.model_class, field):
            raise AttributeError(f"Model {self.model_class.__name__} has no field '{field}'")
        
        field_attr = getattr(self.model_class, field)
        self.query = self.query.group_by(field_attr)
        self._group_by.append(field)
        return self
    
    def having(self, field: str, operator: str = "eq", value: Any = None) -> 'QueryBuilder':
        """HAVING条件"""
        if not hasattr(self.model_class, field):
            raise AttributeError(f"Model {self.model_class.__name__} has no field '{field}'")
        
        field_attr = getattr(self.model_class, field)
        
        if operator == "eq":
            condition = field_attr == value
        elif operator == "gt":
            condition = field_attr > value
        elif operator == "gte":
            condition = field_attr >= value
        elif operator == "lt":
            condition = field_attr < value
        elif operator == "lte":
            condition = field_attr <= value
        else:
            raise ValueError(f"Unsupported HAVING operator: {operator}")
        
        self.query = self.query.having(condition)
        self._having.append((field, operator, value))
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """限制数量"""
        self.query = self.query.limit(count)
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """偏移量"""
        self.query = self.query.offset(count)
        self._offset_value = count
        return self
    
    def paginate(self, page: int, per_page: int) -> 'QueryBuilder':
        """分页"""
        offset = (page - 1) * per_page
        return self.offset(offset).limit(per_page)
    
    def raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> 'QueryBuilder':
        """原生SQL"""
        self.query = self.session.execute(text(sql), params or {})
        return self
    
    def aggregate(self, field: str, func_name: str) -> 'QueryBuilder':
        """聚合函数"""
        if not hasattr(self.model_class, field):
            raise AttributeError(f"Model {self.model_class.__name__} has no field '{field}'")
        
        field_attr = getattr(self.model_class, field)
        
        if func_name == "count":
            func_obj = func.count(field_attr)
        elif func_name == "sum":
            func_obj = func.sum(field_attr)
        elif func_name == "avg":
            func_obj = func.avg(field_attr)
        elif func_name == "max":
            func_obj = func.max(field_attr)
        elif func_name == "min":
            func_obj = func.min(field_attr)
        else:
            raise ValueError(f"Unsupported aggregate function: {func_name}")
        
        self.query = self.query.with_entities(func_obj)
        return self
    
    def count(self) -> int:
        """统计数量"""
        return self.query.count()
    
    def exists(self) -> bool:
        """检查是否存在"""
        return self.query.first() is not None
    
    def first(self) -> Optional[T]:
        """获取第一条记录"""
        return self._apply_conditions().first()
    
    def all(self) -> List[T]:
        """获取所有记录"""
        return self._apply_conditions().all()
    
    def get(self, id: Any) -> Optional[T]:
        """根据ID获取记录"""
        return self._apply_conditions().filter(self.model_class.id == id).first()
    
    def paginate_result(self, page: int, per_page: int) -> Dict[str, Any]:
        """分页结果"""
        total = self.count()
        items = self.paginate(page, per_page).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "has_prev": page > 1,
            "has_next": page < (total + per_page - 1) // per_page
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "conditions": len(self._conditions),
            "joins": self._joins,
            "order_by": self._order_by,
            "group_by": self._group_by,
            "having": self._having,
            "limit": self._limit_value,
            "offset": self._offset_value,
            "distinct": self._distinct,
            "select_fields": self._select_fields
        }
    
    def _apply_conditions(self):
        """应用条件"""
        if self._conditions:
            self.query = self.query.filter(and_(*self._conditions))
        return self.query
    
    def clone(self) -> 'QueryBuilder':
        """克隆查询构建器"""
        new_builder = QueryBuilder(self.model_class, self.session)
        new_builder._conditions = self._conditions.copy()
        new_builder._joins = self._joins.copy()
        new_builder._order_by = self._order_by.copy()
        new_builder._group_by = self._group_by.copy()
        new_builder._having = self._having.copy()
        new_builder._limit_value = self._limit_value
        new_builder._offset_value = self._offset_value
        new_builder._distinct = self._distinct
        new_builder._select_fields = self._select_fields
        return new_builder