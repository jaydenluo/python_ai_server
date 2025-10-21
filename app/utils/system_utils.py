"""
系统工具
提供系统信息获取、健康检查、性能监控等功能
"""

import os
import psutil
import platform
import socket
import subprocess
import time
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime


def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        Dict: 系统信息
    """
    try:
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'hostname': socket.gethostname(),
            'python_version': platform.python_version(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'uptime_seconds': time.time() - psutil.boot_time()
        }
    except Exception:
        return {}


def get_memory_usage() -> Dict[str, Any]:
    """
    获取内存使用情况
    
    Returns:
        Dict: 内存使用信息
    """
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
    except Exception:
        return {}


def get_disk_usage(path: str = '/') -> Dict[str, Any]:
    """
    获取磁盘使用情况
    
    Args:
        path: 磁盘路径
        
    Returns:
        Dict: 磁盘使用信息
    """
    try:
        if platform.system() == 'Windows':
            path = 'C:\\'
        
        disk = psutil.disk_usage(path)
        
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': (disk.used / disk.total) * 100
        }
    except Exception:
        return {}


def get_cpu_usage(interval: float = 1.0) -> Dict[str, Any]:
    """
    获取CPU使用情况
    
    Args:
        interval: 采样间隔
        
    Returns:
        Dict: CPU使用信息
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=interval)
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        result = {
            'percent': cpu_percent,
            'count_physical': cpu_count,
            'count_logical': cpu_count_logical,
        }
        
        if cpu_freq:
            result.update({
                'freq_current': cpu_freq.current,
                'freq_min': cpu_freq.min,
                'freq_max': cpu_freq.max
            })
        
        # 获取每个CPU核心的使用率
        cpu_percents = psutil.cpu_percent(interval=interval, percpu=True)
        result['per_cpu'] = cpu_percents
        
        return result
    except Exception:
        return {}


def get_network_info() -> Dict[str, Any]:
    """
    获取网络信息
    
    Returns:
        Dict: 网络信息
    """
    try:
        # 网络接口信息
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        interfaces = {}
        for interface_name, addresses in net_if_addrs.items():
            interface_info = {
                'addresses': [],
                'is_up': False,
                'speed': 0
            }
            
            for addr in addresses:
                interface_info['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
            
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_info.update({
                    'is_up': stats.isup,
                    'duplex': str(stats.duplex),
                    'speed': stats.speed,
                    'mtu': stats.mtu
                })
            
            interfaces[interface_name] = interface_info
        
        # 网络IO统计
        net_io = psutil.net_io_counters()
        io_stats = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
        
        return {
            'interfaces': interfaces,
            'io_stats': io_stats
        }
    except Exception:
        return {}


def get_process_info(pid: Optional[int] = None) -> Dict[str, Any]:
    """
    获取进程信息
    
    Args:
        pid: 进程ID，None时获取当前进程
        
    Returns:
        Dict: 进程信息
    """
    try:
        if pid is None:
            process = psutil.Process()
        else:
            process = psutil.Process(pid)
        
        with process.oneshot():
            return {
                'pid': process.pid,
                'ppid': process.ppid(),
                'name': process.name(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
                'cpu_percent': process.cpu_percent(),
                'memory_info': process.memory_info()._asdict(),
                'memory_percent': process.memory_percent(),
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
                'cmdline': process.cmdline(),
                'cwd': process.cwd(),
                'username': process.username()
            }
    except Exception:
        return {}


def check_database_health(db_config: Dict[str, Any]) -> bool:
    """
    检查数据库健康状态
    
    Args:
        db_config: 数据库配置
        
    Returns:
        bool: 是否健康
    """
    try:
        # 这里需要根据实际的数据库类型实现
        # 示例：检查MySQL连接
        import pymysql
        
        connection = pymysql.connect(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 3306),
            user=db_config.get('user'),
            password=db_config.get('password'),
            database=db_config.get('database'),
            connect_timeout=5
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        connection.close()
        return True
    except Exception:
        return False


def check_redis_health(redis_config: Dict[str, Any]) -> bool:
    """
    检查Redis健康状态
    
    Args:
        redis_config: Redis配置
        
    Returns:
        bool: 是否健康
    """
    try:
        import redis
        
        client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            password=redis_config.get('password'),
            db=redis_config.get('db', 0),
            socket_timeout=5
        )
        
        client.ping()
        return True
    except Exception:
        return False


def check_external_api_health(url: str, timeout: int = 10) -> bool:
    """
    检查外部API健康状态
    
    Args:
        url: API地址
        timeout: 超时时间
        
    Returns:
        bool: 是否健康
    """
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 400
    except Exception:
        return False


def check_port_open(host: str, port: int, timeout: int = 5) -> bool:
    """
    检查端口是否开放
    
    Args:
        host: 主机地址
        port: 端口号
        timeout: 超时时间
        
    Returns:
        bool: 端口是否开放
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_environment_variables(prefix: str = "") -> Dict[str, str]:
    """
    获取环境变量
    
    Args:
        prefix: 变量名前缀过滤
        
    Returns:
        Dict: 环境变量字典
    """
    env_vars = {}
    
    for key, value in os.environ.items():
        if not prefix or key.startswith(prefix):
            env_vars[key] = value
    
    return env_vars


def execute_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """
    执行系统命令
    
    Args:
        command: 命令字符串
        timeout: 超时时间
        
    Returns:
        Dict: 执行结果
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            'success': result.returncode == 0,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': command
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'return_code': -1,
            'stdout': '',
            'stderr': 'Command timed out',
            'command': command
        }
    except Exception as e:
        return {
            'success': False,
            'return_code': -1,
            'stdout': '',
            'stderr': str(e),
            'command': command
        }


def get_load_average() -> Dict[str, float]:
    """
    获取系统负载平均值（仅Unix系统）
    
    Returns:
        Dict: 负载平均值
    """
    try:
        if hasattr(os, 'getloadavg'):
            load1, load5, load15 = os.getloadavg()
            return {
                'load_1min': load1,
                'load_5min': load5,
                'load_15min': load15
            }
        else:
            return {}
    except Exception:
        return {}


def monitor_system_resources(duration: int = 60, interval: int = 5) -> List[Dict[str, Any]]:
    """
    监控系统资源使用情况
    
    Args:
        duration: 监控持续时间（秒）
        interval: 采样间隔（秒）
        
    Returns:
        List[Dict]: 监控数据列表
    """
    monitoring_data = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        timestamp = datetime.now().isoformat()
        
        data_point = {
            'timestamp': timestamp,
            'cpu': get_cpu_usage(interval=1),
            'memory': get_memory_usage(),
            'disk': get_disk_usage(),
        }
        
        monitoring_data.append(data_point)
        time.sleep(interval)
    
    return monitoring_data


def cleanup_temp_files(temp_dir: str = "/tmp", max_age_hours: int = 24) -> int:
    """
    清理临时文件
    
    Args:
        temp_dir: 临时目录
        max_age_hours: 最大保留时间（小时）
        
    Returns:
        int: 清理的文件数量
    """
    if platform.system() == 'Windows':
        temp_dir = os.environ.get('TEMP', 'C:\\temp')
    
    cleaned_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        cleaned_count += 1
                except (OSError, FileNotFoundError):
                    continue
    except Exception:
        pass
    
    return cleaned_count


def get_service_status(service_name: str) -> Dict[str, Any]:
    """
    获取系统服务状态（仅Linux系统）
    
    Args:
        service_name: 服务名称
        
    Returns:
        Dict: 服务状态信息
    """
    if platform.system() != 'Linux':
        return {'error': 'Only supported on Linux systems'}
    
    try:
        # 使用systemctl检查服务状态
        result = execute_command(f"systemctl is-active {service_name}")
        
        if result['success']:
            status = result['stdout'].strip()
        else:
            status = 'unknown'
        
        # 获取详细信息
        detail_result = execute_command(f"systemctl status {service_name}")
        
        return {
            'service_name': service_name,
            'status': status,
            'is_running': status == 'active',
            'details': detail_result.get('stdout', '')
        }
    except Exception as e:
        return {
            'service_name': service_name,
            'status': 'error',
            'is_running': False,
            'error': str(e)
        }