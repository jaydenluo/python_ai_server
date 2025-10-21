"""
数据验证工具
提供各种数据验证功能
"""

import re
import json
import xml.etree.ElementTree as ET
from typing import Any, List, Dict, Optional, Union
from datetime import datetime
import ipaddress


def is_valid_json(json_str: str) -> bool:
    """
    验证JSON格式
    
    Args:
        json_str: JSON字符串
        
    Returns:
        bool: 是否为有效JSON
    """
    try:
        json.loads(json_str)
        return True
    except (ValueError, TypeError):
        return False


def is_valid_xml(xml_str: str) -> bool:
    """
    验证XML格式
    
    Args:
        xml_str: XML字符串
        
    Returns:
        bool: 是否为有效XML
    """
    try:
        ET.fromstring(xml_str)
        return True
    except ET.ParseError:
        return False


def validate_required_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
    """
    验证必需字段
    
    Args:
        data: 数据字典
        required: 必需字段列表
        
    Returns:
        List[str]: 缺失的字段列表
    """
    missing_fields = []
    
    for field in required:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return missing_fields


def is_integer(value: Any) -> bool:
    """
    验证是否为整数
    
    Args:
        value: 要验证的值
        
    Returns:
        bool: 是否为整数
    """
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def is_float(value: Any) -> bool:
    """
    验证是否为浮点数
    
    Args:
        value: 要验证的值
        
    Returns:
        bool: 是否为浮点数
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def is_boolean(value: Any) -> bool:
    """
    验证是否为布尔值
    
    Args:
        value: 要验证的值
        
    Returns:
        bool: 是否为布尔值
    """
    return isinstance(value, bool) or str(value).lower() in ['true', 'false', '1', '0']


def is_list(value: Any) -> bool:
    """
    验证是否为列表
    
    Args:
        value: 要验证的值
        
    Returns:
        bool: 是否为列表
    """
    return isinstance(value, list)


def is_dict(value: Any) -> bool:
    """
    验证是否为字典
    
    Args:
        value: 要验证的值
        
    Returns:
        bool: 是否为字典
    """
    return isinstance(value, dict)


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否为有效邮箱
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str, country: str = 'CN') -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        country: 国家代码
        
    Returns:
        bool: 是否为有效手机号
    """
    phone = re.sub(r'\D', '', phone)  # 移除非数字字符
    
    if country == 'CN':
        # 中国大陆手机号
        pattern = r'^1[3-9]\d{9}$'
    elif country == 'US':
        # 美国手机号
        pattern = r'^[2-9]\d{2}[2-9]\d{2}\d{4}$'
    else:
        # 通用格式：7-15位数字
        pattern = r'^\d{7,15}$'
    
    return bool(re.match(pattern, phone))


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL地址
        
    Returns:
        bool: 是否为有效URL
    """
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return bool(re.match(pattern, url.strip()))


def validate_ip_address(ip: str) -> bool:
    """
    验证IP地址格式
    
    Args:
        ip: IP地址
        
    Returns:
        bool: 是否为有效IP地址
    """
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False


def validate_id_card(id_card: str) -> bool:
    """
    验证身份证号码（中国大陆）
    
    Args:
        id_card: 身份证号码
        
    Returns:
        bool: 是否为有效身份证号码
    """
    id_card = id_card.strip().upper()
    
    # 18位身份证号码
    if len(id_card) == 18:
        # 前17位必须是数字
        if not id_card[:17].isdigit():
            return False
        
        # 最后一位可以是数字或X
        if not (id_card[17].isdigit() or id_card[17] == 'X'):
            return False
        
        # 验证校验码
        coefficients = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        sum_val = sum(int(id_card[i]) * coefficients[i] for i in range(17))
        check_code = check_codes[sum_val % 11]
        
        return id_card[17] == check_code
    
    # 15位身份证号码（旧格式）
    elif len(id_card) == 15:
        return id_card.isdigit()
    
    return False


def validate_bank_card(card_number: str) -> bool:
    """
    验证银行卡号（Luhn算法）
    
    Args:
        card_number: 银行卡号
        
    Returns:
        bool: 是否为有效银行卡号
    """
    card_number = re.sub(r'\D', '', card_number)  # 移除非数字字符
    
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Luhn算法验证
    def luhn_check(num_str):
        digits = [int(d) for d in num_str]
        checksum = 0
        
        # 从右到左，每隔一位数字乘以2
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        return sum(digits) % 10 == 0
    
    return luhn_check(card_number)


def validate_license_plate(plate: str, country: str = 'CN') -> bool:
    """
    验证车牌号格式
    
    Args:
        plate: 车牌号
        country: 国家代码
        
    Returns:
        bool: 是否为有效车牌号
    """
    plate = plate.strip().upper()
    
    if country == 'CN':
        # 中国车牌号格式
        patterns = [
            r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{4}[A-Z0-9挂学警港澳]$',  # 普通车牌
            r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][0-9]{5}$',  # 新能源车牌
        ]
        
        return any(re.match(pattern, plate) for pattern in patterns)
    
    return False


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        Dict: 密码强度信息
    """
    result = {
        'is_valid': False,
        'score': 0,
        'strength': 'weak',
        'issues': []
    }
    
    # 长度检查
    if len(password) < 8:
        result['issues'].append('密码长度至少8位')
    else:
        result['score'] += 1
    
    # 包含小写字母
    if re.search(r'[a-z]', password):
        result['score'] += 1
    else:
        result['issues'].append('缺少小写字母')
    
    # 包含大写字母
    if re.search(r'[A-Z]', password):
        result['score'] += 1
    else:
        result['issues'].append('缺少大写字母')
    
    # 包含数字
    if re.search(r'\d', password):
        result['score'] += 1
    else:
        result['issues'].append('缺少数字')
    
    # 包含特殊字符
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['score'] += 1
    else:
        result['issues'].append('缺少特殊字符')
    
    # 评估强度
    if result['score'] >= 4:
        result['strength'] = 'strong'
        result['is_valid'] = True
    elif result['score'] >= 3:
        result['strength'] = 'medium'
        result['is_valid'] = True
    else:
        result['strength'] = 'weak'
    
    return result


def validate_date_range(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> bool:
    """
    验证日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        bool: 日期范围是否有效
    """
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        return start_date <= end_date
    except (ValueError, TypeError):
        return False


def validate_numeric_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None, 
                          max_val: Optional[Union[int, float]] = None) -> bool:
    """
    验证数值范围
    
    Args:
        value: 要验证的值
        min_val: 最小值
        max_val: 最大值
        
    Returns:
        bool: 是否在有效范围内
    """
    try:
        num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False
        
        if max_val is not None and num_value > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_string_length(text: str, min_length: Optional[int] = None, 
                          max_length: Optional[int] = None) -> bool:
    """
    验证字符串长度
    
    Args:
        text: 要验证的字符串
        min_length: 最小长度
        max_length: 最大长度
        
    Returns:
        bool: 长度是否有效
    """
    length = len(text)
    
    if min_length is not None and length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True


def validate_regex_pattern(text: str, pattern: str) -> bool:
    """
    使用正则表达式验证文本
    
    Args:
        text: 要验证的文本
        pattern: 正则表达式模式
        
    Returns:
        bool: 是否匹配模式
    """
    try:
        return bool(re.match(pattern, text))
    except re.error:
        return False


def sanitize_input(text: str, allowed_chars: Optional[str] = None) -> str:
    """
    清理输入文本
    
    Args:
        text: 输入文本
        allowed_chars: 允许的字符集，None时移除HTML标签和特殊字符
        
    Returns:
        str: 清理后的文本
    """
    if allowed_chars:
        # 只保留允许的字符
        return ''.join(c for c in text if c in allowed_chars)
    else:
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除潜在危险字符
        text = re.sub(r'[<>"\']', '', text)
        return text.strip()