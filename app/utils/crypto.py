"""
加密与安全工具
提供密码哈希、JWT令牌、数据加密、API签名等功能
"""

import hashlib
import hmac
import secrets
import base64
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from passlib.context import CryptContext

# 密码上下文配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
JWT_SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该从环境变量读取
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """
    密码哈希加密
    
    Args:
        password: 原始密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码
    
    Args:
        password: 原始密码
        hashed: 哈希后的密码
        
    Returns:
        bool: 验证结果
    """
    return pwd_context.verify(password, hashed)


def generate_jwt_token(payload: Dict[str, Any], expire_hours: int = JWT_EXPIRE_HOURS) -> str:
    """
    生成JWT令牌
    
    Args:
        payload: 载荷数据
        expire_hours: 过期时间（小时）
        
    Returns:
        str: JWT令牌
    """
    expire = datetime.utcnow() + timedelta(hours=expire_hours)
    payload.update({"exp": expire})
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Dict: 解码后的载荷数据，失败返回None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_jwt_token(token: str) -> Optional[str]:
    """
    刷新JWT令牌
    
    Args:
        token: 原JWT令牌
        
    Returns:
        str: 新的JWT令牌，失败返回None
    """
    payload = decode_jwt_token(token)
    if payload:
        # 移除过期时间，重新生成
        payload.pop("exp", None)
        return generate_jwt_token(payload)
    return None


def generate_encryption_key() -> str:
    """
    生成加密密钥
    
    Returns:
        str: Base64编码的密钥
    """
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode()


def encrypt_data(data: str, key: str) -> str:
    """
    数据加密
    
    Args:
        data: 要加密的数据
        key: 加密密钥
        
    Returns:
        str: 加密后的数据
    """
    try:
        key_bytes = base64.urlsafe_b64decode(key.encode())
        f = Fernet(key_bytes)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception:
        raise ValueError("加密失败")


def decrypt_data(encrypted_data: str, key: str) -> str:
    """
    数据解密
    
    Args:
        encrypted_data: 加密的数据
        key: 解密密钥
        
    Returns:
        str: 解密后的数据
    """
    try:
        key_bytes = base64.urlsafe_b64decode(key.encode())
        f = Fernet(key_bytes)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    except Exception:
        raise ValueError("解密失败")


def generate_signature(data: Dict[str, Any], secret: str) -> str:
    """
    生成API签名
    
    Args:
        data: 要签名的数据
        secret: 签名密钥
        
    Returns:
        str: 签名字符串
    """
    # 对数据按key排序
    sorted_data = sorted(data.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_data])
    
    # 生成HMAC签名
    signature = hmac.new(
        secret.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_signature(data: Dict[str, Any], signature: str, secret: str) -> bool:
    """
    验证API签名
    
    Args:
        data: 原始数据
        signature: 签名字符串
        secret: 签名密钥
        
    Returns:
        bool: 验证结果
    """
    expected_signature = generate_signature(data, secret)
    return hmac.compare_digest(signature, expected_signature)


def generate_salt(length: int = 32) -> str:
    """
    生成随机盐值
    
    Args:
        length: 盐值长度
        
    Returns:
        str: 随机盐值
    """
    return secrets.token_hex(length)


def hash_with_salt(data: str, salt: str) -> str:
    """
    带盐值的哈希
    
    Args:
        data: 要哈希的数据
        salt: 盐值
        
    Returns:
        str: 哈希结果
    """
    return hashlib.sha256((data + salt).encode()).hexdigest()


def generate_api_key(length: int = 32) -> str:
    """
    生成API密钥
    
    Args:
        length: 密钥长度
        
    Returns:
        str: API密钥
    """
    return secrets.token_urlsafe(length)


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    敏感数据脱敏
    
    Args:
        data: 敏感数据
        mask_char: 掩码字符
        visible_chars: 可见字符数
        
    Returns:
        str: 脱敏后的数据
    """
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars * 2) + data[-visible_chars:]