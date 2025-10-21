"""
搜索与过滤工具
提供模糊搜索、全文搜索、数据过滤等功能
"""

import re
from typing import List, Dict, Any, Optional, Callable
from difflib import SequenceMatcher
import operator


def fuzzy_search(query: str, data_list: List[Dict[str, Any]], 
                fields: List[str], threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    模糊搜索
    
    Args:
        query: 搜索查询
        data_list: 数据列表
        fields: 搜索字段
        threshold: 相似度阈值
        
    Returns:
        List[Dict]: 搜索结果，按相似度排序
    """
    if not query.strip():
        return data_list
    
    results = []
    query_lower = query.lower()
    
    for item in data_list:
        max_similarity = 0
        
        for field in fields:
            field_value = str(item.get(field, '')).lower()
            
            # 计算相似度
            similarity = SequenceMatcher(None, query_lower, field_value).ratio()
            
            # 检查是否包含查询词
            if query_lower in field_value:
                similarity = max(similarity, 0.8)
            
            max_similarity = max(max_similarity, similarity)
        
        if max_similarity >= threshold:
            results.append({
                'item': item,
                'similarity': max_similarity
            })
    
    # 按相似度排序
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return [result['item'] for result in results]


def full_text_search(query: str, content: str, case_sensitive: bool = False) -> bool:
    """
    全文搜索
    
    Args:
        query: 搜索查询
        content: 搜索内容
        case_sensitive: 是否区分大小写
        
    Returns:
        bool: 是否匹配
    """
    if not query or not content:
        return False
    
    if not case_sensitive:
        query = query.lower()
        content = content.lower()
    
    # 支持多个关键词搜索（AND逻辑）
    keywords = query.split()
    
    return all(keyword in content for keyword in keywords)


def regex_search(pattern: str, data_list: List[Dict[str, Any]], 
                fields: List[str], flags: int = 0) -> List[Dict[str, Any]]:
    """
    正则表达式搜索
    
    Args:
        pattern: 正则表达式模式
        data_list: 数据列表
        fields: 搜索字段
        flags: 正则表达式标志
        
    Returns:
        List[Dict]: 匹配的结果
    """
    try:
        regex = re.compile(pattern, flags)
    except re.error:
        return []
    
    results = []
    
    for item in data_list:
        for field in fields:
            field_value = str(item.get(field, ''))
            
            if regex.search(field_value):
                results.append(item)
                break
    
    return results


def build_search_conditions(search_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    构建搜索条件
    
    Args:
        search_params: 搜索参数
        
    Returns:
        Dict: 标准化的搜索条件
    """
    conditions = {}
    
    for key, value in search_params.items():
        if value is None or value == '':
            continue
        
        # 处理特殊搜索操作符
        if key.endswith('__like'):
            field = key[:-6]
            conditions[field] = {'like': f'%{value}%'}
        elif key.endswith('__gt'):
            field = key[:-4]
            conditions[field] = {'gt': value}
        elif key.endswith('__gte'):
            field = key[:-5]
            conditions[field] = {'gte': value}
        elif key.endswith('__lt'):
            field = key[:-4]
            conditions[field] = {'lt': value}
        elif key.endswith('__lte'):
            field = key[:-5]
            conditions[field] = {'lte': value}
        elif key.endswith('__in'):
            field = key[:-4]
            if isinstance(value, str):
                value = value.split(',')
            conditions[field] = {'in': value}
        elif key.endswith('__ne'):
            field = key[:-4]
            conditions[field] = {'ne': value}
        else:
            conditions[key] = value
    
    return conditions


def filter_data(data_list: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    过滤数据
    
    Args:
        data_list: 数据列表
        filters: 过滤条件
        
    Returns:
        List[Dict]: 过滤后的数据
    """
    if not filters:
        return data_list
    
    results = []
    
    for item in data_list:
        match = True
        
        for field, condition in filters.items():
            item_value = item.get(field)
            
            if isinstance(condition, dict):
                # 处理复杂条件
                for op, op_value in condition.items():
                    if not _apply_filter_operation(item_value, op, op_value):
                        match = False
                        break
            else:
                # 简单相等比较
                if item_value != condition:
                    match = False
                    break
        
        if match:
            results.append(item)
    
    return results


def _apply_filter_operation(item_value: Any, operation: str, op_value: Any) -> bool:
    """
    应用过滤操作
    
    Args:
        item_value: 项目值
        operation: 操作类型
        op_value: 操作值
        
    Returns:
        bool: 是否匹配
    """
    if item_value is None:
        return operation in ['is_null', 'ne'] and op_value is None
    
    try:
        if operation == 'gt':
            return item_value > op_value
        elif operation == 'gte':
            return item_value >= op_value
        elif operation == 'lt':
            return item_value < op_value
        elif operation == 'lte':
            return item_value <= op_value
        elif operation == 'ne':
            return item_value != op_value
        elif operation == 'in':
            return item_value in op_value
        elif operation == 'not_in':
            return item_value not in op_value
        elif operation == 'like':
            return str(op_value).replace('%', '.*') in str(item_value)
        elif operation == 'ilike':
            pattern = str(op_value).replace('%', '.*')
            return re.search(pattern, str(item_value), re.IGNORECASE) is not None
        elif operation == 'startswith':
            return str(item_value).startswith(str(op_value))
        elif operation == 'endswith':
            return str(item_value).endswith(str(op_value))
        elif operation == 'contains':
            return str(op_value) in str(item_value)
        elif operation == 'regex':
            return re.search(str(op_value), str(item_value)) is not None
        else:
            return item_value == op_value
    except (TypeError, ValueError):
        return False


def sort_data(data_list: List[Dict[str, Any]], sort_by: str, 
             order: str = 'asc', key_func: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    排序数据
    
    Args:
        data_list: 数据列表
        sort_by: 排序字段
        order: 排序方向 ('asc' 或 'desc')
        key_func: 自定义排序键函数
        
    Returns:
        List[Dict]: 排序后的数据
    """
    if not data_list:
        return data_list
    
    reverse = order.lower() == 'desc'
    
    if key_func:
        return sorted(data_list, key=key_func, reverse=reverse)
    else:
        return sorted(data_list, key=lambda x: x.get(sort_by, ''), reverse=reverse)


def multi_sort_data(data_list: List[Dict[str, Any]], 
                   sort_rules: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    多字段排序
    
    Args:
        data_list: 数据列表
        sort_rules: 排序规则列表 [{"field": "name", "order": "asc"}]
        
    Returns:
        List[Dict]: 排序后的数据
    """
    if not data_list or not sort_rules:
        return data_list
    
    # 从后往前应用排序规则
    for rule in reversed(sort_rules):
        field = rule.get('field')
        order = rule.get('order', 'asc')
        
        if field:
            data_list = sort_data(data_list, field, order)
    
    return data_list


def paginate_search_results(results: List[Dict[str, Any]], page: int, 
                          per_page: int) -> Dict[str, Any]:
    """
    搜索结果分页
    
    Args:
        results: 搜索结果
        page: 页码
        per_page: 每页数量
        
    Returns:
        Dict: 分页结果
    """
    total = len(results)
    total_pages = (total + per_page - 1) // per_page
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    page_results = results[start_index:end_index]
    
    return {
        'results': page_results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


def highlight_search_terms(text: str, terms: List[str], 
                          highlight_tag: str = 'mark') -> str:
    """
    高亮搜索词
    
    Args:
        text: 原始文本
        terms: 搜索词列表
        highlight_tag: 高亮标签
        
    Returns:
        str: 高亮后的文本
    """
    if not terms:
        return text
    
    highlighted_text = text
    
    for term in terms:
        if not term.strip():
            continue
        
        # 使用正则表达式进行不区分大小写的替换
        pattern = re.escape(term)
        replacement = f'<{highlight_tag}>{term}</{highlight_tag}>'
        
        highlighted_text = re.sub(
            pattern, 
            replacement, 
            highlighted_text, 
            flags=re.IGNORECASE
        )
    
    return highlighted_text


def extract_search_suggestions(data_list: List[Dict[str, Any]], 
                             fields: List[str], limit: int = 10) -> List[str]:
    """
    提取搜索建议
    
    Args:
        data_list: 数据列表
        fields: 提取字段
        limit: 建议数量限制
        
    Returns:
        List[str]: 搜索建议列表
    """
    suggestions = set()
    
    for item in data_list:
        for field in fields:
            value = item.get(field)
            if value:
                # 提取单词
                words = re.findall(r'\b\w+\b', str(value).lower())
                suggestions.update(words)
    
    # 过滤太短的词
    suggestions = [s for s in suggestions if len(s) >= 2]
    
    return sorted(list(suggestions))[:limit]


def search_with_autocomplete(query: str, suggestions: List[str], 
                           max_suggestions: int = 5) -> List[str]:
    """
    自动完成搜索
    
    Args:
        query: 搜索查询
        suggestions: 建议列表
        max_suggestions: 最大建议数
        
    Returns:
        List[str]: 匹配的建议
    """
    if not query.strip():
        return []
    
    query_lower = query.lower()
    matches = []
    
    for suggestion in suggestions:
        if suggestion.lower().startswith(query_lower):
            matches.append(suggestion)
        elif query_lower in suggestion.lower():
            matches.append(suggestion)
    
    # 去重并限制数量
    unique_matches = list(dict.fromkeys(matches))
    
    return unique_matches[:max_suggestions]


def advanced_search(data_list: List[Dict[str, Any]], 
                   search_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    高级搜索
    
    Args:
        data_list: 数据列表
        search_config: 搜索配置
            {
                "query": "搜索词",
                "fields": ["field1", "field2"],
                "filters": {"field": "value"},
                "sort": [{"field": "name", "order": "asc"}],
                "fuzzy": True,
                "threshold": 0.6
            }
        
    Returns:
        List[Dict]: 搜索结果
    """
    results = data_list
    
    # 应用过滤器
    filters = search_config.get('filters', {})
    if filters:
        results = filter_data(results, filters)
    
    # 应用搜索
    query = search_config.get('query', '').strip()
    if query:
        fields = search_config.get('fields', [])
        fuzzy = search_config.get('fuzzy', False)
        
        if fuzzy:
            threshold = search_config.get('threshold', 0.6)
            results = fuzzy_search(query, results, fields, threshold)
        else:
            # 精确搜索
            filtered_results = []
            for item in results:
                for field in fields:
                    field_value = str(item.get(field, '')).lower()
                    if query.lower() in field_value:
                        filtered_results.append(item)
                        break
            results = filtered_results
    
    # 应用排序
    sort_rules = search_config.get('sort', [])
    if sort_rules:
        results = multi_sort_data(results, sort_rules)
    
    return results