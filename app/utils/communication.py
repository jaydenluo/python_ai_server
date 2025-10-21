"""
通信工具
提供邮件发送、短信发送、推送通知等功能
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
import requests
import json


class EmailService:
    """邮件服务"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, 
                 password: str, use_tls: bool = True):
        """
        初始化邮件服务
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 用户名
            password: 密码
            use_tls: 是否使用TLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
    
    def send_email(self, to_email: str, subject: str, content: str, 
                  content_type: str = 'plain', attachments: Optional[List[str]] = None,
                  cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 ('plain' 或 'html')
            attachments: 附件文件路径列表
            cc: 抄送列表
            bcc: 密送列表
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # 添加邮件内容
            msg.attach(MIMEText(content, content_type, 'utf-8'))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                    except Exception:
                        continue
            
            # 发送邮件
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                
                # 构建收件人列表
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(self.username, recipients, msg.as_string())
            
            return True
        except Exception:
            return False
    
    def send_bulk_email(self, recipients: List[str], subject: str, content: str,
                       content_type: str = 'plain') -> Dict[str, Any]:
        """
        批量发送邮件
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型
            
        Returns:
            Dict: 发送结果统计
        """
        success_count = 0
        failed_count = 0
        failed_emails = []
        
        for email in recipients:
            if self.send_email(email, subject, content, content_type):
                success_count += 1
            else:
                failed_count += 1
                failed_emails.append(email)
        
        return {
            'total': len(recipients),
            'success': success_count,
            'failed': failed_count,
            'failed_emails': failed_emails
        }


class SMSService:
    """短信服务"""
    
    def __init__(self, api_url: str, api_key: str, api_secret: str):
        """
        初始化短信服务
        
        Args:
            api_url: API地址
            api_key: API密钥
            api_secret: API秘钥
        """
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
    
    def send_sms(self, phone: str, message: str, template_id: Optional[str] = None,
                params: Optional[Dict[str, str]] = None) -> bool:
        """
        发送短信
        
        Args:
            phone: 手机号
            message: 短信内容
            template_id: 模板ID
            params: 模板参数
            
        Returns:
            bool: 是否发送成功
        """
        try:
            payload = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'phone': phone,
                'message': message
            }
            
            if template_id:
                payload['template_id'] = template_id
            
            if params:
                payload['params'] = params
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def send_verification_sms(self, phone: str, code: str, 
                            template_id: Optional[str] = None) -> bool:
        """
        发送验证码短信
        
        Args:
            phone: 手机号
            code: 验证码
            template_id: 模板ID
            
        Returns:
            bool: 是否发送成功
        """
        if template_id:
            return self.send_sms(phone, '', template_id, {'code': code})
        else:
            message = f"您的验证码是：{code}，请在5分钟内使用。"
            return self.send_sms(phone, message)


class PushNotificationService:
    """推送通知服务"""
    
    def __init__(self, api_url: str, api_key: str):
        """
        初始化推送服务
        
        Args:
            api_url: API地址
            api_key: API密钥
        """
        self.api_url = api_url
        self.api_key = api_key
    
    def send_push_notification(self, user_id: str, title: str, content: str,
                             data: Optional[Dict[str, Any]] = None,
                             badge: Optional[int] = None) -> bool:
        """
        发送推送通知
        
        Args:
            user_id: 用户ID
            title: 通知标题
            content: 通知内容
            data: 附加数据
            badge: 角标数量
            
        Returns:
            bool: 是否发送成功
        """
        try:
            payload = {
                'api_key': self.api_key,
                'user_id': user_id,
                'title': title,
                'content': content
            }
            
            if data:
                payload['data'] = data
            
            if badge is not None:
                payload['badge'] = badge
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def send_bulk_push(self, user_ids: List[str], title: str, content: str,
                      data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量发送推送通知
        
        Args:
            user_ids: 用户ID列表
            title: 通知标题
            content: 通知内容
            data: 附加数据
            
        Returns:
            Dict: 发送结果统计
        """
        success_count = 0
        failed_count = 0
        failed_users = []
        
        for user_id in user_ids:
            if self.send_push_notification(user_id, title, content, data):
                success_count += 1
            else:
                failed_count += 1
                failed_users.append(user_id)
        
        return {
            'total': len(user_ids),
            'success': success_count,
            'failed': failed_count,
            'failed_users': failed_users
        }


# 便捷函数
def send_email(smtp_config: Dict[str, Any], to_email: str, subject: str, 
              content: str, **kwargs) -> bool:
    """
    发送邮件的便捷函数
    
    Args:
        smtp_config: SMTP配置
        to_email: 收件人
        subject: 主题
        content: 内容
        **kwargs: 其他参数
        
    Returns:
        bool: 是否成功
    """
    email_service = EmailService(**smtp_config)
    return email_service.send_email(to_email, subject, content, **kwargs)


def send_sms(sms_config: Dict[str, Any], phone: str, message: str, **kwargs) -> bool:
    """
    发送短信的便捷函数
    
    Args:
        sms_config: 短信配置
        phone: 手机号
        message: 消息内容
        **kwargs: 其他参数
        
    Returns:
        bool: 是否成功
    """
    sms_service = SMSService(**sms_config)
    return sms_service.send_sms(phone, message, **kwargs)


def send_push_notification(push_config: Dict[str, Any], user_id: str, 
                          title: str, content: str, **kwargs) -> bool:
    """
    发送推送通知的便捷函数
    
    Args:
        push_config: 推送配置
        user_id: 用户ID
        title: 标题
        content: 内容
        **kwargs: 其他参数
        
    Returns:
        bool: 是否成功
    """
    push_service = PushNotificationService(**push_config)
    return push_service.send_push_notification(user_id, title, content, **kwargs)


# 模板管理
class MessageTemplate:
    """消息模板"""
    
    def __init__(self):
        self.templates = {}
    
    def add_template(self, template_id: str, template: str) -> None:
        """
        添加模板
        
        Args:
            template_id: 模板ID
            template: 模板内容
        """
        self.templates[template_id] = template
    
    def render_template(self, template_id: str, **kwargs) -> str:
        """
        渲染模板
        
        Args:
            template_id: 模板ID
            **kwargs: 模板变量
            
        Returns:
            str: 渲染后的内容
        """
        if template_id not in self.templates:
            return ""
        
        template = self.templates[template_id]
        
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    def get_template(self, template_id: str) -> Optional[str]:
        """
        获取模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            str: 模板内容
        """
        return self.templates.get(template_id)


# 全局模板实例
message_templates = MessageTemplate()

# 预定义模板
message_templates.add_template('verification_code', '您的验证码是：{code}，请在{minutes}分钟内使用。')
message_templates.add_template('welcome_email', '欢迎注册{app_name}！您的账号是：{username}')
message_templates.add_template('password_reset', '您的密码重置链接：{reset_url}，链接将在{hours}小时后失效。')
message_templates.add_template('order_notification', '您的订单{order_id}已{status}，请及时查看。')