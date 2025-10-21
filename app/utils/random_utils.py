"""
随机生成工具
提供ID生成、随机字符串、随机数据等功能
"""

import random
import string
import uuid
import secrets
from typing import Dict, Any, List, Optional


def generate_uuid() -> str:
    """
    生成UUID
    
    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    生成短ID
    
    Args:
        length: ID长度
        
    Returns:
        str: 短ID
    """
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_numeric_id(length: int = 6) -> str:
    """
    生成数字ID
    
    Args:
        length: ID长度
        
    Returns:
        str: 数字ID
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_random_string(length: int, chars: Optional[str] = None) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        chars: 字符集，默认为字母和数字
        
    Returns:
        str: 随机字符串
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """
    生成随机密码
    
    Args:
        length: 密码长度
        include_symbols: 是否包含特殊字符
        
    Returns:
        str: 随机密码
    """
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*"
    
    # 确保密码包含各种类型的字符
    password = []
    
    # 至少包含一个小写字母
    password.append(secrets.choice(string.ascii_lowercase))
    # 至少包含一个大写字母
    password.append(secrets.choice(string.ascii_uppercase))
    # 至少包含一个数字
    password.append(secrets.choice(string.digits))
    
    if include_symbols:
        # 至少包含一个特殊字符
        password.append(secrets.choice("!@#$%^&*"))
    
    # 填充剩余长度
    for _ in range(length - len(password)):
        password.append(secrets.choice(chars))
    
    # 随机打乱顺序
    random.shuffle(password)
    
    return ''.join(password)


def generate_verification_code(length: int = 6, code_type: str = 'numeric') -> str:
    """
    生成验证码
    
    Args:
        length: 验证码长度
        code_type: 验证码类型 ('numeric', 'alpha', 'alphanumeric')
        
    Returns:
        str: 验证码
    """
    if code_type == 'numeric':
        chars = string.digits
    elif code_type == 'alpha':
        chars = string.ascii_uppercase
    elif code_type == 'alphanumeric':
        chars = string.ascii_uppercase + string.digits
    else:
        chars = string.digits
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_random_color(format_type: str = 'hex') -> str:
    """
    生成随机颜色
    
    Args:
        format_type: 颜色格式 ('hex', 'rgb', 'hsl')
        
    Returns:
        str: 颜色值
    """
    if format_type == 'hex':
        return f"#{random.randint(0, 0xFFFFFF):06x}"
    elif format_type == 'rgb':
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return f"rgb({r}, {g}, {b})"
    elif format_type == 'hsl':
        h = random.randint(0, 360)
        s = random.randint(0, 100)
        l = random.randint(0, 100)
        return f"hsl({h}, {s}%, {l}%)"
    else:
        return f"#{random.randint(0, 0xFFFFFF):06x}"


def generate_random_avatar_url(size: int = 200) -> str:
    """
    生成随机头像URL
    
    Args:
        size: 头像尺寸
        
    Returns:
        str: 头像URL
    """
    # 使用 Gravatar 的随机头像服务
    random_hash = generate_random_string(32)
    return f"https://www.gravatar.com/avatar/{random_hash}?s={size}&d=identicon"


def generate_mock_name(gender: Optional[str] = None) -> str:
    """
    生成模拟姓名
    
    Args:
        gender: 性别 ('male', 'female', None为随机)
        
    Returns:
        str: 模拟姓名
    """
    surnames = ['张', '王', '李', '赵', '陈', '刘', '杨', '黄', '周', '吴']
    
    male_names = ['伟', '强', '磊', '军', '勇', '涛', '明', '超', '辉', '华']
    female_names = ['丽', '娜', '敏', '静', '秀', '慧', '美', '雅', '芳', '莉']
    
    surname = random.choice(surnames)
    
    if gender == 'male':
        given_name = random.choice(male_names)
    elif gender == 'female':
        given_name = random.choice(female_names)
    else:
        given_name = random.choice(male_names + female_names)
    
    return surname + given_name


def generate_mock_phone() -> str:
    """
    生成模拟手机号
    
    Returns:
        str: 模拟手机号
    """
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    
    prefix = random.choice(prefixes)
    suffix = ''.join(random.choices(string.digits, k=8))
    
    return prefix + suffix


def generate_mock_email(domain: Optional[str] = None) -> str:
    """
    生成模拟邮箱
    
    Args:
        domain: 邮箱域名，默认随机选择
        
    Returns:
        str: 模拟邮箱
    """
    if domain is None:
        domains = ['gmail.com', 'qq.com', '163.com', 'sina.com', 'hotmail.com']
        domain = random.choice(domains)
    
    username = generate_random_string(random.randint(5, 12), string.ascii_lowercase + string.digits)
    return f"{username}@{domain}"


def generate_mock_data(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据模式生成模拟数据
    
    Args:
        schema: 数据模式定义
        
    Returns:
        Dict: 模拟数据
    """
    result = {}
    
    for field, config in schema.items():
        field_type = config.get('type', 'string')
        
        if field_type == 'string':
            length = config.get('length', 10)
            result[field] = generate_random_string(length)
        
        elif field_type == 'int':
            min_val = config.get('min', 0)
            max_val = config.get('max', 100)
            result[field] = random.randint(min_val, max_val)
        
        elif field_type == 'float':
            min_val = config.get('min', 0.0)
            max_val = config.get('max', 100.0)
            result[field] = round(random.uniform(min_val, max_val), 2)
        
        elif field_type == 'bool':
            result[field] = random.choice([True, False])
        
        elif field_type == 'choice':
            choices = config.get('choices', [])
            result[field] = random.choice(choices) if choices else None
        
        elif field_type == 'email':
            result[field] = generate_mock_email()
        
        elif field_type == 'phone':
            result[field] = generate_mock_phone()
        
        elif field_type == 'name':
            result[field] = generate_mock_name()
        
        elif field_type == 'uuid':
            result[field] = generate_uuid()
        
        elif field_type == 'color':
            result[field] = generate_random_color()
        
        else:
            result[field] = None
    
    return result


def random_sample(items: List[Any], count: int) -> List[Any]:
    """
    随机抽样
    
    Args:
        items: 原始列表
        count: 抽样数量
        
    Returns:
        List: 抽样结果
    """
    if count >= len(items):
        return items.copy()
    
    return random.sample(items, count)


def weighted_random_choice(choices: Dict[Any, float]) -> Any:
    """
    加权随机选择
    
    Args:
        choices: 选择项及其权重的字典
        
    Returns:
        Any: 选择的项
    """
    items = list(choices.keys())
    weights = list(choices.values())
    
    return random.choices(items, weights=weights, k=1)[0]


def shuffle_list(items: List[Any]) -> List[Any]:
    """
    随机打乱列表
    
    Args:
        items: 原始列表
        
    Returns:
        List: 打乱后的列表
    """
    shuffled = items.copy()
    random.shuffle(shuffled)
    return shuffled


def generate_random_date(start_year: int = 2020, end_year: int = 2024) -> str:
    """
    生成随机日期
    
    Args:
        start_year: 开始年份
        end_year: 结束年份
        
    Returns:
        str: 随机日期字符串 (YYYY-MM-DD)
    """
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    
    # 处理不同月份的天数
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # 2月
        max_day = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    
    day = random.randint(1, max_day)
    
    return f"{year:04d}-{month:02d}-{day:02d}"