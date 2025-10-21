"""
认证服务
提供用户认证、权限验证等功能
"""

import jwt
import hashlib
import secrets
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.models.entities.system.user_management import User
from app.core.config.settings import config


class AuthResult(Enum):
    """认证结果枚举"""
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_DISABLED = "account_disabled"
    EMAIL_NOT_VERIFIED = "email_not_verified"
    TOO_MANY_ATTEMPTS = "too_many_attempts"


@dataclass
class AuthResponse:
    """认证响应"""
    success: bool
    result: AuthResult
    user: Optional[User] = None
    token: Optional[str] = None
    message: Optional[str] = None


class AuthService:
    """认证服务"""
    
    def __init__(self):
        self.secret_key = config.get("security.secret_key", "your-secret-key")
        self.jwt_algorithm = config.get("security.jwt_algorithm", "HS256")
        self.jwt_expire_hours = config.get("security.jwt_expire_hours", 24)
        self.max_login_attempts = config.get("security.max_login_attempts", 5)
        self.lockout_duration = config.get("security.lockout_duration", 30)
    
    def authenticate(self, username: str, password: str) -> AuthResponse:
        """用户认证"""
        try:
            # 查找用户
            user = User.query().where("username", username).or_where("email", username).first()
            
            if not user:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="用户名或密码错误"
                )
            
            # 检查账户状态
            if not user.is_active:
                return AuthResponse(
                    success=False,
                    result=AuthResult.ACCOUNT_DISABLED,
                    message="账户已被禁用"
                )
            
            # 检查登录尝试次数
            if self._is_account_locked(user):
                return AuthResponse(
                    success=False,
                    result=AuthResult.ACCOUNT_LOCKED,
                    message="账户已被锁定，请稍后再试"
                )
            
            # 验证密码
            if not user.check_password(password):
                self._record_failed_attempt(user)
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="用户名或密码错误"
                )
            
            # 检查邮箱验证
            if not user.is_verified:
                return AuthResponse(
                    success=False,
                    result=AuthResult.EMAIL_NOT_VERIFIED,
                    message="请先验证邮箱"
                )
            
            # 认证成功
            self._clear_failed_attempts(user)
            token = self._generate_token(user)
            
            return AuthResponse(
                success=True,
                result=AuthResult.SUCCESS,
                user=user,
                token=token,
                message="登录成功"
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"认证失败: {str(e)}"
            )
    
    def register(self, user_data: Dict[str, Any]) -> AuthResponse:
        """用户注册"""
        try:
            # 检查用户名是否已存在
            if User.query().where("username", user_data["username"]).exists():
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="用户名已存在"
                )
            
            # 检查邮箱是否已存在
            if User.query().where("email", user_data["email"]).exists():
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="邮箱已存在"
                )
            
            # 创建用户
            user = User(**user_data)
            user.set_password(user_data["password"])
            user.status = "active"
            
            if user.save():
                # 分配默认角色
                self._assign_default_role(user)
                
                # 生成验证令牌
                verification_token = self._generate_verification_token(user)
                
                return AuthResponse(
                    success=True,
                    result=AuthResult.SUCCESS,
                    user=user,
                    message="注册成功"
                )
            else:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="注册失败"
                )
                
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"注册失败: {str(e)}"
            )
    
    def verify_email(self, token: str) -> AuthResponse:
        """验证邮箱"""
        try:
            # 验证令牌
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            user_id = payload.get("user_id")
            
            if not user_id:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="无效的验证令牌"
                )
            
            # 查找用户
            user = User.query().find(user_id)
            if not user:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="用户不存在"
                )
            
            # 验证邮箱
            user.verify_email()
            user.save()
            
            return AuthResponse(
                success=True,
                result=AuthResult.SUCCESS,
                user=user,
                message="邮箱验证成功"
            )
            
        except jwt.InvalidTokenError:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message="无效的验证令牌"
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"验证失败: {str(e)}"
            )
    
    def refresh_token(self, token: str) -> AuthResponse:
        """刷新令牌"""
        try:
            # 验证令牌
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            user_id = payload.get("user_id")
            
            if not user_id:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="无效的令牌"
                )
            
            # 查找用户
            user = User.query().find(user_id)
            if not user or not user.is_active:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="用户不存在或已被禁用"
                )
            
            # 生成新令牌
            new_token = self._generate_token(user)
            
            return AuthResponse(
                success=True,
                result=AuthResult.SUCCESS,
                user=user,
                token=new_token,
                message="令牌刷新成功"
            )
            
        except jwt.InvalidTokenError:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message="无效的令牌"
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"刷新失败: {str(e)}"
            )
    
    def logout(self, token: str) -> AuthResponse:
        """用户登出"""
        try:
            # 这里可以将令牌加入黑名单
            # 或者更新用户的最后登出时间
            
            return AuthResponse(
                success=True,
                result=AuthResult.SUCCESS,
                message="登出成功"
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"登出失败: {str(e)}"
            )
    
    def change_password(self, user: User, old_password: str, new_password: str) -> AuthResponse:
        """修改密码"""
        try:
            # 验证旧密码
            if not user.check_password(old_password):
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="旧密码错误"
                )
            
            # 设置新密码
            user.set_password(new_password)
            user.save()
            
            return AuthResponse(
                success=True,
                result=AuthResult.SUCCESS,
                message="密码修改成功"
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"密码修改失败: {str(e)}"
            )
    
    def reset_password(self, email: str) -> AuthResponse:
        """重置密码"""
        try:
            # 查找用户
            user = User.query().where("email", email).first()
            if not user:
                return AuthResponse(
                    success=False,
                    result=AuthResult.INVALID_CREDENTIALS,
                    message="邮箱不存在"
                )
            
            # 生成重置令牌
            reset_token = self._generate_reset_token(user)
            
            # 这里应该发送重置邮件
            # send_reset_email(user.email, reset_token)
            
            return AuthResponse(
                success=True,
                result=AuthResult.SUCCESS,
                message="重置密码邮件已发送"
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                result=AuthResult.INVALID_CREDENTIALS,
                message=f"重置失败: {str(e)}"
            )
    
    def _generate_token(self, user: User) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [],  # 这里应该获取用户角色
            "permissions": [],  # 这里应该获取用户权限
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expire_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
    
    def _generate_verification_token(self, user: User) -> str:
        """生成验证令牌"""
        payload = {
            "user_id": user.id,
            "type": "email_verification",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
    
    def _generate_reset_token(self, user: User) -> str:
        """生成重置令牌"""
        payload = {
            "user_id": user.id,
            "type": "password_reset",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
    
    def _is_account_locked(self, user: User) -> bool:
        """检查账户是否被锁定"""
        # 这里应该检查用户的登录尝试记录
        # 为了示例，我们返回False
        return False
    
    def _record_failed_attempt(self, user: User):
        """记录失败尝试"""
        # 这里应该记录用户的登录尝试
        pass
    
    def _clear_failed_attempts(self, user: User):
        """清除失败尝试"""
        # 这里应该清除用户的登录尝试记录
        pass
    
    def _assign_default_role(self, user: User):
        """分配默认角色"""
        # 这里应该分配默认角色
        pass


# 全局认证服务实例
auth_service = AuthService()