"""
仓储类
提供完整的数据访问功能，整合基础和高级查询能力
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Tuple, Callable
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload, contains_eager
from sqlalchemy import and_, or_, not_, func, desc, asc, text, case, cast, extract
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import Select
from datetime import datetime, date, timedelta
import json
import threading
from queue import Queue, Empty

T = TypeVar('T')


class Repository:
    """仓储类 - 提供完整的数据访问功能"""
    
    def __init__(self, model_class: Type[T], session: Session):
        self.model_class = model_class
        self.session = session
    
    # ==================== 基础CRUD操作 ====================
    
    def create(self, **kwargs) -> T:
        """创建记录"""
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """根据ID获取记录"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """获取所有记录"""
        query = self.session.query(self.model_class)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """根据字段获取记录"""
        return self.session.query(self.model_class).filter(
            getattr(self.model_class, field) == value
        ).first()
    
    def get_many_by_field(self, field: str, value: Any) -> List[T]:
        """根据字段获取多条记录"""
        return self.session.query(self.model_class).filter(
            getattr(self.model_class, field) == value
        ).all()
    
    def update(self, id: Any, **kwargs) -> Optional[T]:
        """更新记录"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def delete(self, id: Any) -> bool:
        """删除记录"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            self.session.delete(instance)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def exists(self, id: Any) -> bool:
        """检查记录是否存在"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).exists()
    
    def count(self) -> int:
        """统计记录数量"""
        return self.session.query(self.model_class).count()
    
    # ==================== 查询构建器 ====================
    
    def query(self) -> Select:
        """获取查询对象"""
        return self.session.query(self.model_class)
    
    def filter_by_conditions(self, conditions: Dict[str, Any]) -> List[T]:
        """根据条件过滤"""
        query = self.query()
        
        for field, value in conditions.items():
            if hasattr(self.model_class, field):
                if isinstance(value, dict):
                    # 支持操作符
                    operator = value.get('operator', 'eq')
                    val = value.get('value')
                    
                    if operator == 'eq':
                        query = query.filter(getattr(self.model_class, field) == val)
                    elif operator == 'ne':
                        query = query.filter(getattr(self.model_class, field) != val)
                    elif operator == 'gt':
                        query = query.filter(getattr(self.model_class, field) > val)
                    elif operator == 'gte':
                        query = query.filter(getattr(self.model_class, field) >= val)
                    elif operator == 'lt':
                        query = query.filter(getattr(self.model_class, field) < val)
                    elif operator == 'lte':
                        query = query.filter(getattr(self.model_class, field) <= val)
                    elif operator == 'like':
                        query = query.filter(getattr(self.model_class, field).like(f"%{val}%"))
                    elif operator == 'ilike':
                        query = query.filter(getattr(self.model_class, field).ilike(f"%{val}%"))
                    elif operator == 'in':
                        query = query.filter(getattr(self.model_class, field).in_(val))
                    elif operator == 'not_in':
                        query = query.filter(getattr(self.model_class, field).notin_(val))
                    elif operator == 'is_null':
                        query = query.filter(getattr(self.model_class, field).is_(None))
                    elif operator == 'is_not_null':
                        query = query.filter(getattr(self.model_class, field).isnot(None))
                    elif operator == 'between':
                        query = query.filter(getattr(self.model_class, field).between(val[0], val[1]))
                else:
                    query = query.filter(getattr(self.model_class, field) == value)
        
        return query.all()
    
    def search_by_text(self, fields: List[str], search_text: str) -> List[T]:
        """全文搜索"""
        query = self.query()
        search_conditions = []
        
        for field in fields:
            if hasattr(self.model_class, field):
                search_conditions.append(
                    getattr(self.model_class, field).ilike(f"%{search_text}%")
                )
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        return query.all()
    
    def filter_by_date_range(self, field: str, start_date: date, end_date: date) -> List[T]:
        """根据日期范围过滤"""
        return self.query().filter(
            and_(
                getattr(self.model_class, field) >= start_date,
                getattr(self.model_class, field) <= end_date
            )
        ).all()
    
    def filter_by_this_week(self, field: str) -> List[T]:
        """获取本周的记录"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        return self.filter_by_date_range(field, start_of_week, end_of_week)
    
    def filter_by_this_month(self, field: str) -> List[T]:
        """获取本月的记录"""
        today = date.today()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        return self.filter_by_date_range(field, start_of_month, end_of_month)
    
    # ==================== 关联查询 ====================
    
    def get_with_relations(self, id: Any, relations: List[str]) -> Optional[T]:
        """获取记录及其关联数据"""
        query = self.query()
        
        for relation in relations:
            if hasattr(self.model_class, relation):
                query = query.options(joinedload(getattr(self.model_class, relation)))
        
        return query.filter(self.model_class.id == id).first()
    
    def get_all_with_relations(self, relations: List[str]) -> List[T]:
        """获取所有记录及其关联数据"""
        query = self.query()
        
        for relation in relations:
            if hasattr(self.model_class, relation):
                query = query.options(joinedload(getattr(self.model_class, relation)))
        
        return query.all()
    
    def get_with_subquery_relations(self, relations: List[str]) -> List[T]:
        """使用子查询加载关联数据"""
        query = self.query()
        
        for relation in relations:
            if hasattr(self.model_class, relation):
                query = query.options(selectinload(getattr(self.model_class, relation)))
        
        return query.all()
    
    # ==================== 聚合查询 ====================
    
    def count_by_field(self, field: str, value: Any) -> int:
        """根据字段统计数量"""
        return self.query().filter(getattr(self.model_class, field) == value).count()
    
    def count_by_conditions(self, conditions: Dict[str, Any]) -> int:
        """根据条件统计数量"""
        query = self.query()
        
        for field, value in conditions.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)
        
        return query.count()
    
    def get_field_values(self, field: str, distinct: bool = True) -> List[Any]:
        """获取字段的所有值"""
        query = self.query()
        
        if distinct:
            query = query.distinct()
        
        return [getattr(row, field) for row in query.all()]
    
    def get_field_stats(self, field: str) -> Dict[str, Any]:
        """获取字段统计信息"""
        result = self.query().with_entities(
            func.count(getattr(self.model_class, field)).label('count'),
            func.min(getattr(self.model_class, field)).label('min'),
            func.max(getattr(self.model_class, field)).label('max'),
            func.avg(getattr(self.model_class, field)).label('avg'),
            func.sum(getattr(self.model_class, field)).label('sum')
        ).first()
        
        return {
            'count': result.count,
            'min': result.min,
            'max': result.max,
            'avg': float(result.avg) if result.avg else 0,
            'sum': result.sum
        }
    
    def group_by_field(self, field: str, aggregate_func: str = 'count') -> List[Dict[str, Any]]:
        """根据字段分组统计"""
        query = self.query()
        
        if aggregate_func == 'count':
            func_obj = func.count(self.model_class.id)
        elif aggregate_func == 'sum':
            func_obj = func.sum(getattr(self.model_class, field))
        elif aggregate_func == 'avg':
            func_obj = func.avg(getattr(self.model_class, field))
        elif aggregate_func == 'max':
            func_obj = func.max(getattr(self.model_class, field))
        elif aggregate_func == 'min':
            func_obj = func.min(getattr(self.model_class, field))
        else:
            func_obj = func.count(self.model_class.id)
        
        results = query.with_entities(
            getattr(self.model_class, field),
            func_obj
        ).group_by(getattr(self.model_class, field)).all()
        
        return [
            {field: getattr(row, field), 'count': row[1]}
            for row in results
        ]
    
    # ==================== 排序和分页 ====================
    
    def order_by_field(self, field: str, direction: str = 'asc') -> List[T]:
        """根据字段排序"""
        query = self.query()
        
        if direction.lower() == 'desc':
            query = query.order_by(desc(getattr(self.model_class, field)))
        else:
            query = query.order_by(asc(getattr(self.model_class, field)))
        
        return query.all()
    
    def order_by_multiple(self, order_fields: List[Tuple[str, str]]) -> List[T]:
        """多字段排序"""
        query = self.query()
        
        for field, direction in order_fields:
            if direction.lower() == 'desc':
                query = query.order_by(desc(getattr(self.model_class, field)))
            else:
                query = query.order_by(asc(getattr(self.model_class, field)))
        
        return query.all()
    
    def paginate(self, page: int, per_page: int, order_by: Optional[str] = None, 
                 order_direction: str = 'asc') -> Dict[str, Any]:
        """分页查询"""
        query = self.query()
        
        # 排序
        if order_by and hasattr(self.model_class, order_by):
            if order_direction.lower() == 'desc':
                query = query.order_by(desc(getattr(self.model_class, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model_class, order_by)))
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * per_page
        items = query.offset(offset).limit(per_page).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page < (total + per_page - 1) // per_page
        }
    
    # ==================== 高级查询 ====================
    
    def get_by_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行原生SQL查询"""
        result = self.session.execute(text(sql), params or {})
        return [dict(row) for row in result]
    
    def get_by_case_statement(self, field: str, case_conditions: Dict[str, Any]) -> List[T]:
        """使用CASE语句查询"""
        case_stmt = case(
            *[getattr(self.model_class, field) == value for value in case_conditions.keys()],
            else_=None
        )
        
        return self.query().filter(case_stmt.isnot(None)).all()
    
    def get_by_date_extract(self, field: str, extract_part: str, value: Any) -> List[T]:
        """根据日期部分提取查询"""
        return self.query().filter(
            extract(extract_part, getattr(self.model_class, field)) == value
        ).all()
    
    def get_by_json_field(self, json_field: str, json_path: str, value: Any) -> List[T]:
        """根据JSON字段查询"""
        return self.query().filter(
            getattr(self.model_class, json_field)[json_path] == value
        ).all()
    
    def get_by_array_contains(self, field: str, value: Any) -> List[T]:
        """数组包含查询"""
        return self.query().filter(
            getattr(self.model_class, field).contains(value)
        ).all()
    
    def get_by_array_overlaps(self, field: str, values: List[Any]) -> List[T]:
        """数组重叠查询"""
        return self.query().filter(
            getattr(self.model_class, field).overlap(values)
        ).all()
    
    # ==================== 批量操作 ====================
    
    def bulk_update_by_conditions(self, conditions: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """根据条件批量更新"""
        query = self.query()
        
        for field, value in conditions.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)
        
        return query.update(updates, synchronize_session=False)
    
    def bulk_delete_by_conditions(self, conditions: Dict[str, Any]) -> int:
        """根据条件批量删除"""
        query = self.query()
        
        for field, value in conditions.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)
        
        return query.delete(synchronize_session=False)
    
    def bulk_insert(self, data: List[Dict[str, Any]]) -> List[T]:
        """批量插入"""
        try:
            instances = [self.model_class(**item) for item in data]
            self.session.add_all(instances)
            self.session.commit()
            return instances
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    # ==================== 事务管理 ====================
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """在事务中执行函数"""
        try:
            result = func(*args, **kwargs)
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            raise e
    
    def batch_operation(self, operations: List[Callable]) -> List[Any]:
        """批量操作"""
        results = []
        try:
            for operation in operations:
                result = operation()
                results.append(result)
            self.session.commit()
            return results
        except Exception as e:
            self.session.rollback()
            raise e