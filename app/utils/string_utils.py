"""
字符串处理工具
提供字符串转换、验证、处理等功能
"""

import re
import html
import unicodedata
from typing import Optional
from urllib.parse import quote, unquote


def to_snake_case(text: str) -> str:
    """
    转换为蛇形命名法
    
    Args:
        text: 输入文本
        
    Returns:
        str: 蛇形命名的文本
    """
    # 处理驼峰命名
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    # 处理连续大写字母
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def to_camel_case(text: str) -> str:
    """
    转换为驼峰命名法
    
    Args:
        text: 输入文本
        
    Returns:
        str: 驼峰命名的文本
    """
    components = text.replace('-', '_').split('_')
    return components[0].lower() + ''.join(word.capitalize() for word in components[1:])


def to_pascal_case(text: str) -> str:
    """
    转换为帕斯卡命名法
    
    Args:
        text: 输入文本
        
    Returns:
        str: 帕斯卡命名的文本
    """
    components = text.replace('-', '_').split('_')
    return ''.join(word.capitalize() for word in components)


def to_kebab_case(text: str) -> str:
    """
    转换为短横线命名法
    
    Args:
        text: 输入文本
        
    Returns:
        str: 短横线命名的文本
    """
    # 处理驼峰命名
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
    # 处理连续大写字母
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1)
    return s2.lower().replace('_', '-')


def is_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否为有效邮箱
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆）
    
    Args:
        phone: 手机号
        
    Returns:
        bool: 是否为有效手机号
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def is_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL地址
        
    Returns:
        bool: 是否为有效URL
    """
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return bool(re.match(pattern, url))


def is_chinese(text: str) -> bool:
    """
    检查是否包含中文字符
    
    Args:
        text: 输入文本
        
    Returns:
        bool: 是否包含中文
    """
    pattern = r'[\u4e00-\u9fff]'
    return bool(re.search(pattern, text))


def truncate_string(text: str, length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 输入文本
        length: 最大长度
        suffix: 后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def remove_html_tags(html_text: str) -> str:
    """
    移除HTML标签
    
    Args:
        html_text: HTML文本
        
    Returns:
        str: 纯文本
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)


def escape_html(text: str) -> str:
    """
    HTML转义
    
    Args:
        text: 输入文本
        
    Returns:
        str: 转义后的文本
    """
    return html.escape(text)


def unescape_html(text: str) -> str:
    """
    HTML反转义
    
    Args:
        text: HTML转义文本
        
    Returns:
        str: 原始文本
    """
    return html.unescape(text)


def slugify(text: str) -> str:
    """
    生成URL友好的slug
    
    Args:
        text: 输入文本
        
    Returns:
        str: slug字符串
    """
    # 转换为小写
    text = text.lower()
    # 移除重音符号
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # 替换非字母数字字符为连字符
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # 移除首尾连字符
    text = text.strip('-')
    return text


def extract_numbers(text: str) -> list:
    """
    提取文本中的数字
    
    Args:
        text: 输入文本
        
    Returns:
        list: 数字列表
    """
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return [float(num) if '.' in num else int(num) for num in numbers]


def extract_urls(text: str) -> list:
    """
    提取文本中的URL
    
    Args:
        text: 输入文本
        
    Returns:
        list: URL列表
    """
    pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?'
    return re.findall(pattern, text)


def extract_emails(text: str) -> list:
    """
    提取文本中的邮箱地址
    
    Args:
        text: 输入文本
        
    Returns:
        list: 邮箱列表
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def clean_whitespace(text: str) -> str:
    """
    清理多余的空白字符
    
    Args:
        text: 输入文本
        
    Returns:
        str: 清理后的文本
    """
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    return text.strip()


def mask_string(text: str, start: int = 0, end: int = 0, mask_char: str = '*') -> str:
    """
    字符串掩码
    
    Args:
        text: 输入文本
        start: 开始保留字符数
        end: 结尾保留字符数
        mask_char: 掩码字符
        
    Returns:
        str: 掩码后的文本
    """
    if len(text) <= start + end:
        return mask_char * len(text)
    
    if end == 0:
        return text[:start] + mask_char * (len(text) - start)
    else:
        return text[:start] + mask_char * (len(text) - start - end) + text[-end:]


def count_words(text: str) -> int:
    """
    统计单词数量
    
    Args:
        text: 输入文本
        
    Returns:
        int: 单词数量
    """
    # 移除HTML标签
    text = remove_html_tags(text)
    # 分割单词
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def reverse_string(text: str) -> str:
    """
    反转字符串
    
    Args:
        text: 输入文本
        
    Returns:
        str: 反转后的文本
    """
    return text[::-1]


def capitalize_words(text: str) -> str:
    """
    首字母大写
    
    Args:
        text: 输入文本
        
    Returns:
        str: 首字母大写的文本
    """
    return ' '.join(word.capitalize() for word in text.split())


def url_encode(text: str) -> str:
    """
    URL编码
    
    Args:
        text: 输入文本
        
    Returns:
        str: URL编码后的文本
    """
    return quote(text)


def url_decode(text: str) -> str:
    """
    URL解码
    
    Args:
        text: URL编码的文本
        
    Returns:
        str: 解码后的文本
    """
    return unquote(text)