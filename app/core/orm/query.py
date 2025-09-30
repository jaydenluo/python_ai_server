"""
查询构建器
提供类似Laravel Eloquent的查询功能
"""

from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import json

T = TypeVar('T', bound='Model')


class QueryOperator(Enum):
    """查询操作符"""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


@dataclass
class QueryCondition:
    """查询条件"""
    column: str
    operator: QueryOperator
    value: Any
    boolean: str = "AND"  # AND, OR


@dataclass
class QueryJoin:
    """查询连接"""
    table: str
    first: str
    operator: str
    second: str
    type: str = "INNER"  # INNER, LEFT, RIGHT, OUTER


class ModelQuery:
    """模型查询构建器"""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.table = model_class.__table__ or model_class.__name__.lower()
        self.conditions: List[QueryCondition] = []
        self.joins: List[QueryJoin] = []
        self.select_columns: List[str] = []
        self.order_by: List[str] = []
        self.group_by: List[str] = []
        self.having_conditions: List[QueryCondition] = []
        self.limit_value: Optional[int] = None
        self.offset_value: Optional[int] = None
        self.distinct: bool = False
    
    def select(self, *columns: str) -> 'ModelQuery':
        """选择列"""
        self.select_columns.extend(columns)
        return self
    
    def distinct(self) -> 'ModelQuery':
        """去重"""
        self.distinct = True
        return self
    
    def where(self, column: str, operator: Union[str, QueryOperator], value: Any = None, boolean: str = "AND") -> 'ModelQuery':
        """添加WHERE条件"""
        if isinstance(operator, str):
            operator = QueryOperator(operator)
        
        condition = QueryCondition(
            column=column,
            operator=operator,
            value=value,
            boolean=boolean
        )
        self.conditions.append(condition)
        return self
    
    def or_where(self, column: str, operator: Union[str, QueryOperator], value: Any = None) -> 'ModelQuery':
        """添加OR WHERE条件"""
        return self.where(column, operator, value, "OR")
    
    def where_in(self, column: str, values: List[Any], boolean: str = "AND") -> 'ModelQuery':
        """IN条件"""
        return self.where(column, QueryOperator.IN, values, boolean)
    
    def where_not_in(self, column: str, values: List[Any], boolean: str = "AND") -> 'ModelQuery':
        """NOT IN条件"""
        return self.where(column, QueryOperator.NOT_IN, values, boolean)
    
    def where_between(self, column: str, values: List[Any], boolean: str = "AND") -> 'ModelQuery':
        """BETWEEN条件"""
        return self.where(column, QueryOperator.BETWEEN, values, boolean)
    
    def where_not_between(self, column: str, values: List[Any], boolean: str = "AND") -> 'ModelQuery':
        """NOT BETWEEN条件"""
        return self.where(column, QueryOperator.NOT_BETWEEN, values, boolean)
    
    def where_null(self, column: str, boolean: str = "AND") -> 'ModelQuery':
        """IS NULL条件"""
        return self.where(column, QueryOperator.IS_NULL, None, boolean)
    
    def where_not_null(self, column: str, boolean: str = "AND") -> 'ModelQuery':
        """IS NOT NULL条件"""
        return self.where(column, QueryOperator.IS_NOT_NULL, None, boolean)
    
    def where_like(self, column: str, value: str, boolean: str = "AND") -> 'ModelQuery':
        """LIKE条件"""
        return self.where(column, QueryOperator.LIKE, value, boolean)
    
    def where_not_like(self, column: str, value: str, boolean: str = "AND") -> 'ModelQuery':
        """NOT LIKE条件"""
        return self.where(column, QueryOperator.NOT_LIKE, value, boolean)
    
    def where_date(self, column: str, date: str, boolean: str = "AND") -> 'ModelQuery':
        """日期条件"""
        return self.where(column, QueryOperator.EQUALS, date, boolean)
    
    def where_year(self, column: str, year: int, boolean: str = "AND") -> 'ModelQuery':
        """年份条件"""
        return self.where(column, QueryOperator.EQUALS, year, boolean)
    
    def where_month(self, column: str, month: int, boolean: str = "AND") -> 'ModelQuery':
        """月份条件"""
        return self.where(column, QueryOperator.EQUALS, month, boolean)
    
    def where_day(self, column: str, day: int, boolean: str = "AND") -> 'ModelQuery':
        """日期条件"""
        return self.where(column, QueryOperator.EQUALS, day, boolean)
    
    def where_time(self, column: str, time: str, boolean: str = "AND") -> 'ModelQuery':
        """时间条件"""
        return self.where(column, QueryOperator.EQUALS, time, boolean)
    
    def where_column(self, first: str, operator: str, second: str, boolean: str = "AND") -> 'ModelQuery':
        """列比较条件"""
        condition = QueryCondition(
            column=f"{first} {operator} {second}",
            operator=QueryOperator.EQUALS,
            value=None,
            boolean=boolean
        )
        self.conditions.append(condition)
        return self
    
    def where_raw(self, sql: str, bindings: List[Any] = None, boolean: str = "AND") -> 'ModelQuery':
        """原始SQL条件"""
        condition = QueryCondition(
            column=sql,
            operator=QueryOperator.EQUALS,
            value=bindings or [],
            boolean=boolean
        )
        self.conditions.append(condition)
        return self
    
    def join(self, table: str, first: str, operator: str, second: str, type: str = "INNER") -> 'ModelQuery':
        """添加JOIN"""
        join = QueryJoin(
            table=table,
            first=first,
            operator=operator,
            second=second,
            type=type
        )
        self.joins.append(join)
        return self
    
    def left_join(self, table: str, first: str, operator: str, second: str) -> 'ModelQuery':
        """LEFT JOIN"""
        return self.join(table, first, operator, second, "LEFT")
    
    def right_join(self, table: str, first: str, operator: str, second: str) -> 'ModelQuery':
        """RIGHT JOIN"""
        return self.join(table, first, operator, second, "RIGHT")
    
    def outer_join(self, table: str, first: str, operator: str, second: str) -> 'ModelQuery':
        """OUTER JOIN"""
        return self.join(table, first, operator, second, "OUTER")
    
    def order_by(self, column: str, direction: str = "ASC") -> 'ModelQuery':
        """排序"""
        self.order_by.append(f"{column} {direction}")
        return self
    
    def order_by_desc(self, column: str) -> 'ModelQuery':
        """降序排序"""
        return self.order_by(column, "DESC")
    
    def order_by_asc(self, column: str) -> 'ModelQuery':
        """升序排序"""
        return self.order_by(column, "ASC")
    
    def group_by(self, *columns: str) -> 'ModelQuery':
        """分组"""
        self.group_by.extend(columns)
        return self
    
    def having(self, column: str, operator: Union[str, QueryOperator], value: Any, boolean: str = "AND") -> 'ModelQuery':
        """HAVING条件"""
        if isinstance(operator, str):
            operator = QueryOperator(operator)
        
        condition = QueryCondition(
            column=column,
            operator=operator,
            value=value,
            boolean=boolean
        )
        self.having_conditions.append(condition)
        return self
    
    def limit(self, count: int) -> 'ModelQuery':
        """限制数量"""
        self.limit_value = count
        return self
    
    def offset(self, count: int) -> 'ModelQuery':
        """偏移量"""
        self.offset_value = count
        return self
    
    def skip(self, count: int) -> 'ModelQuery':
        """跳过记录"""
        return self.offset(count)
    
    def take(self, count: int) -> 'ModelQuery':
        """获取记录"""
        return self.limit(count)
    
    def paginate(self, page: int, per_page: int = 15) -> 'ModelQuery':
        """分页"""
        offset = (page - 1) * per_page
        return self.limit(per_page).offset(offset)
    
    def get(self) -> List[T]:
        """获取所有记录"""
        # 这里应该实现查询逻辑
        # 实际实现需要数据库连接
        print(f"执行查询: {self._build_sql()}")
        return []
    
    def first(self) -> Optional[T]:
        """获取第一条记录"""
        results = self.limit(1).get()
        return results[0] if results else None
    
    def find(self, id: Any) -> Optional[T]:
        """根据主键查找"""
        return self.where(self.model_class.__primary_key__, QueryOperator.EQUALS, id).first()
    
    def count(self) -> int:
        """统计记录数"""
        # 这里应该实现统计逻辑
        # 实际实现需要数据库连接
        print(f"执行统计查询: {self._build_count_sql()}")
        return 0
    
    def exists(self) -> bool:
        """检查是否存在"""
        return self.count() > 0
    
    def sum(self, column: str) -> float:
        """求和"""
        # 这里应该实现求和逻辑
        # 实际实现需要数据库连接
        print(f"执行求和查询: {self._build_sum_sql(column)}")
        return 0.0
    
    def avg(self, column: str) -> float:
        """平均值"""
        # 这里应该实现平均值逻辑
        # 实际实现需要数据库连接
        print(f"执行平均值查询: {self._build_avg_sql(column)}")
        return 0.0
    
    def max(self, column: str) -> Any:
        """最大值"""
        # 这里应该实现最大值逻辑
        # 实际实现需要数据库连接
        print(f"执行最大值查询: {self._build_max_sql(column)}")
        return None
    
    def min(self, column: str) -> Any:
        """最小值"""
        # 这里应该实现最小值逻辑
        # 实际实现需要数据库连接
        print(f"执行最小值查询: {self._build_min_sql(column)}")
        return None
    
    def update(self, attributes: Dict[str, Any]) -> int:
        """更新记录"""
        # 这里应该实现更新逻辑
        # 实际实现需要数据库连接
        print(f"执行更新: {self._build_update_sql(attributes)}")
        return 0
    
    def delete(self) -> int:
        """删除记录"""
        # 这里应该实现删除逻辑
        # 实际实现需要数据库连接
        print(f"执行删除: {self._build_delete_sql()}")
        return 0
    
    def _build_sql(self) -> str:
        """构建SQL查询"""
        sql_parts = ["SELECT"]
        
        # 选择列
        if self.select_columns:
            sql_parts.append(", ".join(self.select_columns))
        else:
            sql_parts.append("*")
        
        # 表名
        sql_parts.append(f"FROM {self.table}")
        
        # JOIN
        for join in self.joins:
            sql_parts.append(f"{join.type} JOIN {join.table} ON {join.first} {join.operator} {join.second}")
        
        # WHERE条件
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        # GROUP BY
        if self.group_by:
            sql_parts.append(f"GROUP BY {', '.join(self.group_by)}")
        
        # HAVING
        if self.having_conditions:
            having_clause = self._build_having_clause()
            sql_parts.append(f"HAVING {having_clause}")
        
        # ORDER BY
        if self.order_by:
            sql_parts.append(f"ORDER BY {', '.join(self.order_by)}")
        
        # LIMIT
        if self.limit_value:
            sql_parts.append(f"LIMIT {self.limit_value}")
        
        # OFFSET
        if self.offset_value:
            sql_parts.append(f"OFFSET {self.offset_value}")
        
        return " ".join(sql_parts)
    
    def _build_where_clause(self) -> str:
        """构建WHERE子句"""
        conditions = []
        for condition in self.conditions:
            if condition.operator == QueryOperator.IS_NULL:
                conditions.append(f"{condition.column} IS NULL")
            elif condition.operator == QueryOperator.IS_NOT_NULL:
                conditions.append(f"{condition.column} IS NOT NULL")
            elif condition.operator == QueryOperator.IN:
                values = ", ".join([f"'{v}'" for v in condition.value])
                conditions.append(f"{condition.column} IN ({values})")
            elif condition.operator == QueryOperator.NOT_IN:
                values = ", ".join([f"'{v}'" for v in condition.value])
                conditions.append(f"{condition.column} NOT IN ({values})")
            elif condition.operator == QueryOperator.BETWEEN:
                conditions.append(f"{condition.column} BETWEEN '{condition.value[0]}' AND '{condition.value[1]}'")
            elif condition.operator == QueryOperator.NOT_BETWEEN:
                conditions.append(f"{condition.column} NOT BETWEEN '{condition.value[0]}' AND '{condition.value[1]}'")
            else:
                value = f"'{condition.value}'" if isinstance(condition.value, str) else condition.value
                conditions.append(f"{condition.column} {condition.operator.value} {value}")
        
        return f" {conditions[0].boolean} ".join(conditions)
    
    def _build_having_clause(self) -> str:
        """构建HAVING子句"""
        conditions = []
        for condition in self.having_conditions:
            value = f"'{condition.value}'" if isinstance(condition.value, str) else condition.value
            conditions.append(f"{condition.column} {condition.operator.value} {value}")
        
        return f" {conditions[0].boolean} ".join(conditions)
    
    def _build_count_sql(self) -> str:
        """构建统计SQL"""
        sql_parts = ["SELECT COUNT(*) FROM", self.table]
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    def _build_sum_sql(self, column: str) -> str:
        """构建求和SQL"""
        sql_parts = ["SELECT SUM(", column, ") FROM", self.table]
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    def _build_avg_sql(self, column: str) -> str:
        """构建平均值SQL"""
        sql_parts = ["SELECT AVG(", column, ") FROM", self.table]
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    def _build_max_sql(self, column: str) -> str:
        """构建最大值SQL"""
        sql_parts = ["SELECT MAX(", column, ") FROM", self.table]
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    def _build_min_sql(self, column: str) -> str:
        """构建最小值SQL"""
        sql_parts = ["SELECT MIN(", column, ") FROM", self.table]
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    def _build_update_sql(self, attributes: Dict[str, Any]) -> str:
        """构建更新SQL"""
        sql_parts = ["UPDATE", self.table, "SET"]
        
        set_clauses = []
        for key, value in attributes.items():
            if isinstance(value, str):
                set_clauses.append(f"{key} = '{value}'")
            else:
                set_clauses.append(f"{key} = {value}")
        
        sql_parts.append(", ".join(set_clauses))
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    def _build_delete_sql(self) -> str:
        """构建删除SQL"""
        sql_parts = ["DELETE FROM", self.table]
        
        if self.conditions:
            where_clause = self._build_where_clause()
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)