"""
时间日期工具
提供时间格式化、计算、转换等功能
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Union
import pytz
from dateutil import parser


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        str: 格式化后的时间字符串
    """
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: Optional[str] = None) -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_str: 日期时间字符串
        format_str: 格式字符串，None时自动解析
        
    Returns:
        datetime: 解析后的日期时间对象，失败返回None
    """
    try:
        if format_str:
            return datetime.strptime(date_str, format_str)
        else:
            # 使用 dateutil 进行智能解析
            return parser.parse(date_str)
    except (ValueError, TypeError, parser.ParserError):
        return None


def get_timestamp(dt: Optional[datetime] = None) -> int:
    """
    获取时间戳
    
    Args:
        dt: 日期时间对象，None时使用当前时间
        
    Returns:
        int: 时间戳（秒）
    """
    if dt is None:
        dt = datetime.now()
    return int(dt.timestamp())


def get_millisecond_timestamp(dt: Optional[datetime] = None) -> int:
    """
    获取毫秒时间戳
    
    Args:
        dt: 日期时间对象，None时使用当前时间
        
    Returns:
        int: 毫秒时间戳
    """
    if dt is None:
        dt = datetime.now()
    return int(dt.timestamp() * 1000)


def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """
    时间戳转日期时间
    
    Args:
        timestamp: 时间戳
        
    Returns:
        datetime: 日期时间对象
    """
    # 处理毫秒时间戳
    if timestamp > 1e10:
        timestamp = timestamp / 1000
    
    return datetime.fromtimestamp(timestamp)


def get_iso_datetime(dt: Optional[datetime] = None) -> str:
    """
    获取ISO格式的日期时间字符串
    
    Args:
        dt: 日期时间对象，None时使用当前时间
        
    Returns:
        str: ISO格式的时间字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def get_utc_datetime(dt: Optional[datetime] = None) -> datetime:
    """
    获取UTC时间
    
    Args:
        dt: 本地时间，None时使用当前时间
        
    Returns:
        datetime: UTC时间
    """
    if dt is None:
        dt = datetime.now()
    
    if dt.tzinfo is None:
        # 假设是本地时间
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(timezone.utc)


def add_days(dt: datetime, days: int) -> datetime:
    """
    增加天数
    
    Args:
        dt: 原始日期时间
        days: 要增加的天数（可为负数）
        
    Returns:
        datetime: 新的日期时间
    """
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """
    增加小时数
    
    Args:
        dt: 原始日期时间
        hours: 要增加的小时数（可为负数）
        
    Returns:
        datetime: 新的日期时间
    """
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """
    增加分钟数
    
    Args:
        dt: 原始日期时间
        minutes: 要增加的分钟数（可为负数）
        
    Returns:
        datetime: 新的日期时间
    """
    return dt + timedelta(minutes=minutes)


def get_time_diff(start: datetime, end: datetime) -> Dict[str, int]:
    """
    计算时间差
    
    Args:
        start: 开始时间
        end: 结束时间
        
    Returns:
        Dict: 时间差信息
    """
    diff = end - start
    
    total_seconds = int(diff.total_seconds())
    days = diff.days
    hours = total_seconds // 3600 % 24
    minutes = total_seconds // 60 % 60
    seconds = total_seconds % 60
    
    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'total_seconds': total_seconds,
        'total_minutes': total_seconds // 60,
        'total_hours': total_seconds // 3600,
        'total_days': days
    }


def is_expired(expire_time: datetime, current_time: Optional[datetime] = None) -> bool:
    """
    检查是否已过期
    
    Args:
        expire_time: 过期时间
        current_time: 当前时间，None时使用系统当前时间
        
    Returns:
        bool: 是否已过期
    """
    if current_time is None:
        current_time = datetime.now()
    
    return current_time > expire_time


def get_relative_time(dt: datetime, current_time: Optional[datetime] = None) -> str:
    """
    获取相对时间描述
    
    Args:
        dt: 目标时间
        current_time: 当前时间，None时使用系统当前时间
        
    Returns:
        str: 相对时间描述
    """
    if current_time is None:
        current_time = datetime.now()
    
    diff = current_time - dt
    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 0:
        # 未来时间
        diff = dt - current_time
        total_seconds = int(diff.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}秒后"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}分钟后"
        elif total_seconds < 86400:
            return f"{total_seconds // 3600}小时后"
        else:
            return f"{total_seconds // 86400}天后"
    
    # 过去时间
    if total_seconds < 60:
        return f"{total_seconds}秒前"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}分钟前"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600}小时前"
    elif total_seconds < 2592000:  # 30天
        return f"{total_seconds // 86400}天前"
    elif total_seconds < 31536000:  # 365天
        return f"{total_seconds // 2592000}个月前"
    else:
        return f"{total_seconds // 31536000}年前"


def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """
    时区转换
    
    Args:
        dt: 日期时间对象
        from_tz: 源时区
        to_tz: 目标时区
        
    Returns:
        datetime: 转换后的时间
    """
    from_timezone = pytz.timezone(from_tz)
    to_timezone = pytz.timezone(to_tz)
    
    # 如果没有时区信息，假设是源时区
    if dt.tzinfo is None:
        dt = from_timezone.localize(dt)
    
    return dt.astimezone(to_timezone)


def get_local_time(utc_time: datetime, local_tz: str = 'Asia/Shanghai') -> datetime:
    """
    UTC时间转本地时间
    
    Args:
        utc_time: UTC时间
        local_tz: 本地时区
        
    Returns:
        datetime: 本地时间
    """
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    
    local_timezone = pytz.timezone(local_tz)
    return utc_time.astimezone(local_timezone)


def get_week_range(dt: Optional[datetime] = None) -> tuple:
    """
    获取指定日期所在周的开始和结束时间
    
    Args:
        dt: 指定日期，None时使用当前日期
        
    Returns:
        tuple: (周开始时间, 周结束时间)
    """
    if dt is None:
        dt = datetime.now()
    
    # 获取周一（weekday() 返回0-6，0是周一）
    days_since_monday = dt.weekday()
    monday = dt - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    
    # 设置为当天的开始和结束
    week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return week_start, week_end


def get_month_range(dt: Optional[datetime] = None) -> tuple:
    """
    获取指定日期所在月的开始和结束时间
    
    Args:
        dt: 指定日期，None时使用当前日期
        
    Returns:
        tuple: (月开始时间, 月结束时间)
    """
    if dt is None:
        dt = datetime.now()
    
    # 月初
    month_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 月末
    if dt.month == 12:
        next_month = dt.replace(year=dt.year + 1, month=1, day=1)
    else:
        next_month = dt.replace(month=dt.month + 1, day=1)
    
    month_end = next_month - timedelta(microseconds=1)
    
    return month_start, month_end


def is_weekend(dt: datetime) -> bool:
    """
    检查是否为周末
    
    Args:
        dt: 日期时间
        
    Returns:
        bool: 是否为周末
    """
    return dt.weekday() >= 5  # 5是周六，6是周日


def is_business_day(dt: datetime) -> bool:
    """
    检查是否为工作日
    
    Args:
        dt: 日期时间
        
    Returns:
        bool: 是否为工作日
    """
    return not is_weekend(dt)


def get_age(birth_date: datetime, current_date: Optional[datetime] = None) -> int:
    """
    计算年龄
    
    Args:
        birth_date: 出生日期
        current_date: 当前日期，None时使用系统当前日期
        
    Returns:
        int: 年龄
    """
    if current_date is None:
        current_date = datetime.now()
    
    age = current_date.year - birth_date.year
    
    # 检查是否还没到生日
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


def sleep_until(target_time: datetime) -> None:
    """
    休眠到指定时间
    
    Args:
        target_time: 目标时间
    """
    current_time = datetime.now()
    if target_time > current_time:
        sleep_seconds = (target_time - current_time).total_seconds()
        time.sleep(sleep_seconds)


def format_duration(seconds: int) -> str:
    """
    格式化时长显示
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时长字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}分{remaining_seconds}秒"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}小时{remaining_minutes}分钟"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        return f"{days}天{remaining_hours}小时"


def get_quarter(dt: datetime) -> int:
    """
    获取季度
    
    Args:
        dt: 日期时间
        
    Returns:
        int: 季度（1-4）
    """
    return (dt.month - 1) // 3 + 1


def get_quarter_range(year: int, quarter: int) -> tuple:
    """
    获取指定季度的开始和结束时间
    
    Args:
        year: 年份
        quarter: 季度（1-4）
        
    Returns:
        tuple: (季度开始时间, 季度结束时间)
    """
    if quarter not in [1, 2, 3, 4]:
        raise ValueError("季度必须是1-4之间的整数")
    
    start_month = (quarter - 1) * 3 + 1
    end_month = quarter * 3
    
    quarter_start = datetime(year, start_month, 1)
    
    if end_month == 12:
        quarter_end = datetime(year + 1, 1, 1) - timedelta(microseconds=1)
    else:
        quarter_end = datetime(year, end_month + 1, 1) - timedelta(microseconds=1)
    
    return quarter_start, quarter_end