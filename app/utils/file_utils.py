"""
文件与路径处理工具
提供文件操作、路径处理、上传下载等功能
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import Optional, List, Tuple
import hashlib
import uuid
from datetime import datetime


def safe_join(*paths) -> str:
    """
    安全的路径拼接，防止路径遍历攻击
    
    Args:
        *paths: 路径组件
        
    Returns:
        str: 安全的路径
    """
    base_path = Path(paths[0]).resolve()
    
    for path in paths[1:]:
        # 移除可能的路径遍历字符
        clean_path = str(path).replace('..', '').replace('/', '').replace('\\', '')
        base_path = base_path / clean_path
    
    return str(base_path)


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名（不包含点号）
    """
    return Path(filename).suffix.lstrip('.')


def get_filename_without_ext(filepath: str) -> str:
    """
    获取不带扩展名的文件名
    
    Args:
        filepath: 文件路径
        
    Returns:
        str: 不带扩展名的文件名
    """
    return Path(filepath).stem


def ensure_dir_exists(path: str) -> None:
    """
    确保目录存在，不存在则创建
    
    Args:
        path: 目录路径
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_size(filepath: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        filepath: 文件路径
        
    Returns:
        int: 文件大小
    """
    try:
        return Path(filepath).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def get_file_mime_type(filepath: str) -> str:
    """
    获取文件MIME类型
    
    Args:
        filepath: 文件路径
        
    Returns:
        str: MIME类型
    """
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type or 'application/octet-stream'


def is_allowed_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    检查文件类型是否允许
    
    Args:
        filename: 文件名
        allowed_types: 允许的文件类型列表
        
    Returns:
        bool: 是否允许
    """
    ext = get_file_extension(filename).lower()
    return ext in [t.lower() for t in allowed_types]


def generate_unique_filename(filename: str, upload_dir: str = None) -> str:
    """
    生成唯一文件名
    
    Args:
        filename: 原文件名
        upload_dir: 上传目录（用于检查重复）
        
    Returns:
        str: 唯一文件名
    """
    name = get_filename_without_ext(filename)
    ext = get_file_extension(filename)
    
    # 生成基于时间戳和UUID的唯一名称
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    new_filename = f"{name}_{timestamp}_{unique_id}"
    if ext:
        new_filename += f".{ext}"
    
    # 如果指定了上传目录，检查是否重复
    if upload_dir and Path(upload_dir, new_filename).exists():
        counter = 1
        while True:
            test_name = f"{name}_{timestamp}_{unique_id}_{counter}"
            if ext:
                test_name += f".{ext}"
            
            if not Path(upload_dir, test_name).exists():
                new_filename = test_name
                break
            counter += 1
    
    return new_filename


def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """
    保存上传的文件
    
    Args:
        file_content: 文件内容
        filename: 文件名
        upload_dir: 上传目录
        
    Returns:
        str: 保存的文件路径
    """
    ensure_dir_exists(upload_dir)
    
    # 生成唯一文件名
    unique_filename = generate_unique_filename(filename, upload_dir)
    filepath = Path(upload_dir) / unique_filename
    
    # 保存文件
    with open(filepath, 'wb') as f:
        f.write(file_content)
    
    return str(filepath)


def delete_file_safe(filepath: str) -> bool:
    """
    安全删除文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        bool: 是否删除成功
    """
    try:
        if Path(filepath).exists():
            Path(filepath).unlink()
            return True
        return False
    except (OSError, PermissionError):
        return False


def copy_file(src: str, dst: str) -> bool:
    """
    复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        
    Returns:
        bool: 是否复制成功
    """
    try:
        # 确保目标目录存在
        ensure_dir_exists(str(Path(dst).parent))
        shutil.copy2(src, dst)
        return True
    except (OSError, shutil.Error):
        return False


def move_file(src: str, dst: str) -> bool:
    """
    移动文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        
    Returns:
        bool: 是否移动成功
    """
    try:
        # 确保目标目录存在
        ensure_dir_exists(str(Path(dst).parent))
        shutil.move(src, dst)
        return True
    except (OSError, shutil.Error):
        return False


def get_file_hash(filepath: str, algorithm: str = 'md5') -> Optional[str]:
    """
    计算文件哈希值
    
    Args:
        filepath: 文件路径
        algorithm: 哈希算法（md5, sha1, sha256）
        
    Returns:
        str: 文件哈希值，失败返回None
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    except (OSError, ValueError):
        return None


def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
    """
    列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        recursive: 是否递归搜索
        
    Returns:
        List[str]: 文件路径列表
    """
    try:
        path = Path(directory)
        if recursive:
            files = path.rglob(pattern)
        else:
            files = path.glob(pattern)
        
        return [str(f) for f in files if f.is_file()]
    except OSError:
        return []


def get_directory_size(directory: str) -> int:
    """
    计算目录大小
    
    Args:
        directory: 目录路径
        
    Returns:
        int: 目录大小（字节）
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    continue
    except OSError:
        pass
    
    return total_size


def clean_directory(directory: str, older_than_days: int = 30) -> int:
    """
    清理目录中的旧文件
    
    Args:
        directory: 目录路径
        older_than_days: 保留天数
        
    Returns:
        int: 删除的文件数量
    """
    deleted_count = 0
    cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 3600)
    
    try:
        for filepath in list_files(directory, recursive=True):
            try:
                file_mtime = Path(filepath).stat().st_mtime
                if file_mtime < cutoff_time:
                    Path(filepath).unlink()
                    deleted_count += 1
            except (OSError, FileNotFoundError):
                continue
    except OSError:
        pass
    
    return deleted_count


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def is_binary_file(filepath: str) -> bool:
    """
    检查是否为二进制文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        bool: 是否为二进制文件
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except (OSError, FileNotFoundError):
        return False


def get_file_info(filepath: str) -> dict:
    """
    获取文件详细信息
    
    Args:
        filepath: 文件路径
        
    Returns:
        dict: 文件信息字典
    """
    try:
        path = Path(filepath)
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'extension': get_file_extension(filepath),
            'mime_type': get_file_mime_type(filepath),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'is_binary': is_binary_file(filepath),
            'hash_md5': get_file_hash(filepath, 'md5'),
        }
    except (OSError, FileNotFoundError):
        return {}