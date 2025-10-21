"""
数据处理工具
提供数据转换、清洗、格式化等功能
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from io import StringIO
import pandas as pd
from datetime import datetime


def dict_to_json(data: Dict[str, Any], indent: Optional[int] = None, 
                ensure_ascii: bool = False) -> str:
    """
    字典转JSON字符串
    
    Args:
        data: 字典数据
        indent: 缩进空格数
        ensure_ascii: 是否确保ASCII编码
        
    Returns:
        str: JSON字符串
    """
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)


def json_to_dict(json_str: str) -> Optional[Dict[str, Any]]:
    """
    JSON字符串转字典
    
    Args:
        json_str: JSON字符串
        
    Returns:
        Dict: 字典数据，失败返回None
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def csv_to_dict_list(csv_content: str, delimiter: str = ',') -> List[Dict[str, Any]]:
    """
    CSV内容转字典列表
    
    Args:
        csv_content: CSV内容
        delimiter: 分隔符
        
    Returns:
        List[Dict]: 字典列表
    """
    try:
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        return list(reader)
    except Exception:
        return []


def dict_list_to_csv(data_list: List[Dict[str, Any]], delimiter: str = ',') -> str:
    """
    字典列表转CSV字符串
    
    Args:
        data_list: 字典列表
        delimiter: 分隔符
        
    Returns:
        str: CSV字符串
    """
    if not data_list:
        return ""
    
    output = StringIO()
    fieldnames = data_list[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
    
    writer.writeheader()
    writer.writerows(data_list)
    
    return output.getvalue()


def excel_to_dict_list(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Excel文件转字典列表
    
    Args:
        file_path: Excel文件路径
        sheet_name: 工作表名称
        
    Returns:
        List[Dict]: 字典列表
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.to_dict('records')
    except Exception:
        return []


def dict_list_to_excel(data_list: List[Dict[str, Any]], file_path: str, 
                      sheet_name: str = 'Sheet1') -> bool:
    """
    字典列表转Excel文件
    
    Args:
        data_list: 字典列表
        file_path: 输出文件路径
        sheet_name: 工作表名称
        
    Returns:
        bool: 是否成功
    """
    try:
        df = pd.DataFrame(data_list)
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        return True
    except Exception:
        return False


def xml_to_dict(xml_str: str) -> Optional[Dict[str, Any]]:
    """
    XML字符串转字典
    
    Args:
        xml_str: XML字符串
        
    Returns:
        Dict: 字典数据，失败返回None
    """
    def _xml_element_to_dict(element):
        result = {}
        
        # 处理属性
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # 处理文本内容
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            else:
                result['#text'] = element.text.strip()
        
        # 处理子元素
        for child in element:
            child_data = _xml_element_to_dict(child)
            
            if child.tag in result:
                # 如果已存在同名元素，转为列表
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    try:
        root = ET.fromstring(xml_str)
        return {root.tag: _xml_element_to_dict(root)}
    except ET.ParseError:
        return None


def dict_to_xml(data: Dict[str, Any], root_name: str = 'root') -> str:
    """
    字典转XML字符串
    
    Args:
        data: 字典数据
        root_name: 根元素名称
        
    Returns:
        str: XML字符串
    """
    def _dict_to_xml_element(parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '@attributes':
                    # 处理属性
                    for attr_key, attr_value in value.items():
                        parent.set(attr_key, str(attr_value))
                elif key == '#text':
                    # 处理文本内容
                    parent.text = str(value)
                else:
                    # 处理子元素
                    if isinstance(value, list):
                        for item in value:
                            child = ET.SubElement(parent, key)
                            _dict_to_xml_element(child, item)
                    else:
                        child = ET.SubElement(parent, key)
                        _dict_to_xml_element(child, value)
        else:
            parent.text = str(data)
    
    root = ET.Element(root_name)
    _dict_to_xml_element(root, data)
    
    return ET.tostring(root, encoding='unicode')


def remove_empty_values(data: Dict[str, Any], remove_none: bool = True, 
                       remove_empty_str: bool = True, remove_empty_list: bool = True) -> Dict[str, Any]:
    """
    移除空值
    
    Args:
        data: 原始数据
        remove_none: 是否移除None值
        remove_empty_str: 是否移除空字符串
        remove_empty_list: 是否移除空列表
        
    Returns:
        Dict: 清理后的数据
    """
    result = {}
    
    for key, value in data.items():
        skip = False
        
        if remove_none and value is None:
            skip = True
        elif remove_empty_str and value == '':
            skip = True
        elif remove_empty_list and isinstance(value, list) and len(value) == 0:
            skip = True
        
        if not skip:
            if isinstance(value, dict):
                # 递归处理嵌套字典
                nested_result = remove_empty_values(value, remove_none, remove_empty_str, remove_empty_list)
                if nested_result:  # 只有非空字典才保留
                    result[key] = nested_result
            else:
                result[key] = value
    
    return result


def normalize_phone_number(phone: str, country_code: str = '+86') -> str:
    """
    标准化手机号格式
    
    Args:
        phone: 原始手机号
        country_code: 国家代码
        
    Returns:
        str: 标准化后的手机号
    """
    # 移除所有非数字字符
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # 中国大陆手机号处理
    if country_code == '+86':
        if len(digits_only) == 11 and digits_only.startswith('1'):
            return f"+86{digits_only}"
        elif len(digits_only) == 13 and digits_only.startswith('86'):
            return f"+{digits_only}"
    
    return phone  # 无法标准化时返回原值


def clean_text(text: str, remove_extra_spaces: bool = True, 
              remove_special_chars: bool = False) -> str:
    """
    清理文本
    
    Args:
        text: 原始文本
        remove_extra_spaces: 是否移除多余空格
        remove_special_chars: 是否移除特殊字符
        
    Returns:
        str: 清理后的文本
    """
    if not isinstance(text, str):
        return str(text)
    
    result = text
    
    if remove_extra_spaces:
        # 替换多个空白字符为单个空格
        import re
        result = re.sub(r'\s+', ' ', result).strip()
    
    if remove_special_chars:
        # 只保留字母、数字、中文和基本标点
        import re
        result = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]', '', result)
    
    return result


def remove_duplicates(data_list: List[Dict[str, Any]], key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    移除重复项
    
    Args:
        data_list: 原始数据列表
        key: 用于判断重复的键，None时比较整个字典
        
    Returns:
        List[Dict]: 去重后的列表
    """
    if not data_list:
        return []
    
    seen = set()
    result = []
    
    for item in data_list:
        if key:
            # 根据指定键去重
            identifier = item.get(key)
        else:
            # 根据整个字典去重
            identifier = json.dumps(item, sort_keys=True, default=str)
        
        if identifier not in seen:
            seen.add(identifier)
            result.append(item)
    
    return result


def merge_dicts(*dicts: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
        deep: 是否深度合并
        
    Returns:
        Dict: 合并后的字典
    """
    result = {}
    
    for d in dicts:
        if not isinstance(d, dict):
            continue
        
        for key, value in d.items():
            if deep and key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 深度合并嵌套字典
                result[key] = merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
    
    return result


def flatten_dict(data: Dict[str, Any], separator: str = '.', prefix: str = '') -> Dict[str, Any]:
    """
    扁平化字典
    
    Args:
        data: 嵌套字典
        separator: 分隔符
        prefix: 前缀
        
    Returns:
        Dict: 扁平化后的字典
    """
    result = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            # 递归处理嵌套字典
            result.update(flatten_dict(value, separator, new_key))
        elif isinstance(value, list):
            # 处理列表
            for i, item in enumerate(value):
                list_key = f"{new_key}{separator}{i}"
                if isinstance(item, dict):
                    result.update(flatten_dict(item, separator, list_key))
                else:
                    result[list_key] = item
        else:
            result[new_key] = value
    
    return result


def unflatten_dict(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
    """
    反扁平化字典
    
    Args:
        data: 扁平化的字典
        separator: 分隔符
        
    Returns:
        Dict: 嵌套字典
    """
    result = {}
    
    for key, value in data.items():
        keys = key.split(separator)
        current = result
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    return result


def convert_data_types(data: Dict[str, Any], type_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    转换数据类型
    
    Args:
        data: 原始数据
        type_mapping: 类型映射 {"field": "int|float|str|bool|datetime"}
        
    Returns:
        Dict: 转换后的数据
    """
    result = data.copy()
    
    for field, target_type in type_mapping.items():
        if field not in result:
            continue
        
        value = result[field]
        
        try:
            if target_type == 'int':
                result[field] = int(value)
            elif target_type == 'float':
                result[field] = float(value)
            elif target_type == 'str':
                result[field] = str(value)
            elif target_type == 'bool':
                if isinstance(value, str):
                    result[field] = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    result[field] = bool(value)
            elif target_type == 'datetime':
                if isinstance(value, str):
                    result[field] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                elif isinstance(value, (int, float)):
                    result[field] = datetime.fromtimestamp(value)
        except (ValueError, TypeError):
            # 转换失败时保持原值
            pass
    
    return result


def group_by_field(data_list: List[Dict[str, Any]], field: str) -> Dict[Any, List[Dict[str, Any]]]:
    """
    按字段分组
    
    Args:
        data_list: 数据列表
        field: 分组字段
        
    Returns:
        Dict: 分组结果
    """
    groups = {}
    
    for item in data_list:
        key = item.get(field)
        
        if key not in groups:
            groups[key] = []
        
        groups[key].append(item)
    
    return groups


def calculate_statistics(data_list: List[Union[int, float]]) -> Dict[str, float]:
    """
    计算统计信息
    
    Args:
        data_list: 数值列表
        
    Returns:
        Dict: 统计信息
    """
    if not data_list:
        return {}
    
    data_list = [x for x in data_list if isinstance(x, (int, float))]
    
    if not data_list:
        return {}
    
    sorted_data = sorted(data_list)
    n = len(sorted_data)
    
    # 基本统计
    total = sum(sorted_data)
    mean = total / n
    
    # 中位数
    if n % 2 == 0:
        median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        median = sorted_data[n//2]
    
    # 方差和标准差
    variance = sum((x - mean) ** 2 for x in sorted_data) / n
    std_dev = variance ** 0.5
    
    return {
        'count': n,
        'sum': total,
        'mean': mean,
        'median': median,
        'min': min(sorted_data),
        'max': max(sorted_data),
        'variance': variance,
        'std_dev': std_dev,
        'range': max(sorted_data) - min(sorted_data)
    }