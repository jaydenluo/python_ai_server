"""
XSS防护
防止跨站脚本攻击
"""

import re
import html
import urllib.parse
from typing import Dict, List, Set, Optional, Any, Pattern
from dataclasses import dataclass
from enum import Enum

from app.core.middleware.base import Middleware, Request, Response


class XSSError(Exception):
    """XSS错误"""
    pass


class XSSThreatLevel(Enum):
    """XSS威胁级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class XSSPattern:
    """XSS模式"""
    pattern: Pattern
    threat_level: XSSThreatLevel
    description: str
    mitigation: str


class XSSProtection:
    """XSS防护类"""
    
    def __init__(self):
        self.patterns = self._load_xss_patterns()
        self.allowed_tags = {"p", "br", "strong", "em", "u", "i", "b", "span", "div"}
        self.allowed_attributes = {"class", "id", "style"}
        self.max_input_length = 10000
        
    def _load_xss_patterns(self) -> List[XSSPattern]:
        """加载XSS检测模式"""
        patterns = [
            # 脚本标签检测
            XSSPattern(
                pattern=re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
                threat_level=XSSThreatLevel.CRITICAL,
                description="脚本标签检测",
                mitigation="移除脚本标签"
            ),
            
            # JavaScript事件检测
            XSSPattern(
                pattern=re.compile(r"on\w+\s*=", re.IGNORECASE),
                threat_level=XSSThreatLevel.CRITICAL,
                description="JavaScript事件检测",
                mitigation="移除事件属性"
            ),
            
            # JavaScript协议检测
            XSSPattern(
                pattern=re.compile(r"javascript\s*:", re.IGNORECASE),
                threat_level=XSSThreatLevel.CRITICAL,
                description="JavaScript协议检测",
                mitigation="移除JavaScript协议"
            ),
            
            # 数据协议检测
            XSSPattern(
                pattern=re.compile(r"data\s*:", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="数据协议检测",
                mitigation="移除数据协议"
            ),
            
            # VBScript检测
            XSSPattern(
                pattern=re.compile(r"vbscript\s*:", re.IGNORECASE),
                threat_level=XSSThreatLevel.CRITICAL,
                description="VBScript协议检测",
                mitigation="移除VBScript协议"
            ),
            
            # 表达式检测
            XSSPattern(
                pattern=re.compile(r"expression\s*\(", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="CSS表达式检测",
                mitigation="移除CSS表达式"
            ),
            
            # 内联样式检测
            XSSPattern(
                pattern=re.compile(r"style\s*=\s*[^>]*", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="内联样式检测",
                mitigation="清理内联样式"
            ),
            
            # 表单检测
            XSSPattern(
                pattern=re.compile(r"<form[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="表单标签检测",
                mitigation="移除表单标签"
            ),
            
            # 输入标签检测
            XSSPattern(
                pattern=re.compile(r"<input[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="输入标签检测",
                mitigation="移除输入标签"
            ),
            
            # 链接标签检测
            XSSPattern(
                pattern=re.compile(r"<a[^>]*href\s*=\s*[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="链接标签检测",
                mitigation="清理链接属性"
            ),
            
            # 图片标签检测
            XSSPattern(
                pattern=re.compile(r"<img[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="图片标签检测",
                mitigation="清理图片属性"
            ),
            
            # 对象标签检测
            XSSPattern(
                pattern=re.compile(r"<object[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="对象标签检测",
                mitigation="移除对象标签"
            ),
            
            # 嵌入标签检测
            XSSPattern(
                pattern=re.compile(r"<embed[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="嵌入标签检测",
                mitigation="移除嵌入标签"
            ),
            
            # 应用标签检测
            XSSPattern(
                pattern=re.compile(r"<applet[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="应用标签检测",
                mitigation="移除应用标签"
            ),
            
            # 框架标签检测
            XSSPattern(
                pattern=re.compile(r"<iframe[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="框架标签检测",
                mitigation="移除框架标签"
            ),
            
            # 框架集标签检测
            XSSPattern(
                pattern=re.compile(r"<frameset[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="框架集标签检测",
                mitigation="移除框架集标签"
            ),
            
            # 框架标签检测
            XSSPattern(
                pattern=re.compile(r"<frame[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.HIGH,
                description="框架标签检测",
                mitigation="移除框架标签"
            ),
            
            # 元标签检测
            XSSPattern(
                pattern=re.compile(r"<meta[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="元标签检测",
                mitigation="移除元标签"
            ),
            
            # 链接标签检测
            XSSPattern(
                pattern=re.compile(r"<link[^>]*>", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="链接标签检测",
                mitigation="移除链接标签"
            ),
            
            # 样式标签检测
            XSSPattern(
                pattern=re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL),
                threat_level=XSSThreatLevel.HIGH,
                description="样式标签检测",
                mitigation="移除样式标签"
            ),
            
            # 字符编码检测
            XSSPattern(
                pattern=re.compile(r"&#\d+;", re.IGNORECASE),
                threat_level=XSSThreatLevel.LOW,
                description="字符编码检测",
                mitigation="验证字符编码"
            ),
            
            # 十六进制编码检测
            XSSPattern(
                pattern=re.compile(r"\\x[0-9a-fA-F]{2}", re.IGNORECASE),
                threat_level=XSSThreatLevel.MEDIUM,
                description="十六进制编码检测",
                mitigation="阻止十六进制编码"
            ),
            
            # URL编码检测
            XSSPattern(
                pattern=re.compile(r"%[0-9a-fA-F]{2}", re.IGNORECASE),
                threat_level=XSSThreatLevel.LOW,
                description="URL编码检测",
                mitigation="验证URL编码"
            ),
        ]
        
        return patterns
    
    def detect_xss(self, input_data: str) -> List[Dict[str, Any]]:
        """检测XSS攻击"""
        threats = []
        
        # 检查输入长度
        if len(input_data) > self.max_input_length:
            threat = {
                "pattern": "input_length",
                "threat_level": XSSThreatLevel.MEDIUM.value,
                "description": "输入长度超限",
                "mitigation": "限制输入长度",
                "input": input_data[:100] + "..."
            }
            threats.append(threat)
        
        # 检查XSS模式
        for pattern_info in self.patterns:
            matches = pattern_info.pattern.findall(input_data)
            if matches:
                threat = {
                    "pattern": pattern_info.pattern.pattern,
                    "threat_level": pattern_info.threat_level.value,
                    "description": pattern_info.description,
                    "mitigation": pattern_info.mitigation,
                    "matches": matches,
                    "input": input_data
                }
                threats.append(threat)
        
        return threats
    
    def sanitize_html(self, html_content: str) -> str:
        """清理HTML内容"""
        # 移除脚本标签
        html_content = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # 移除事件属性
        html_content = re.sub(r"on\w+\s*=\s*[^>]*", "", html_content, flags=re.IGNORECASE)
        
        # 移除JavaScript协议
        html_content = re.sub(r"javascript\s*:", "", html_content, flags=re.IGNORECASE)
        
        # 移除VBScript协议
        html_content = re.sub(r"vbscript\s*:", "", html_content, flags=re.IGNORECASE)
        
        # 移除数据协议
        html_content = re.sub(r"data\s*:", "", html_content, flags=re.IGNORECASE)
        
        # 移除CSS表达式
        html_content = re.sub(r"expression\s*\(", "", html_content, flags=re.IGNORECASE)
        
        # 移除危险标签
        dangerous_tags = ["script", "object", "embed", "applet", "iframe", "frame", "frameset", "form", "input", "meta", "link", "style"]
        for tag in dangerous_tags:
            html_content = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", html_content, flags=re.IGNORECASE | re.DOTALL)
            html_content = re.sub(rf"<{tag}[^>]*>", "", html_content, flags=re.IGNORECASE)
        
        # 清理内联样式
        html_content = re.sub(r"style\s*=\s*[^>]*", "", html_content, flags=re.IGNORECASE)
        
        return html_content
    
    def escape_html(self, text: str) -> str:
        """转义HTML字符"""
        return html.escape(text, quote=True)
    
    def unescape_html(self, text: str) -> str:
        """反转义HTML字符"""
        return html.unescape(text)
    
    def validate_url(self, url: str) -> bool:
        """验证URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ["http", "https", "ftp", "ftps"]:
                return False
            
            # 检查域名
            if not parsed.netloc:
                return False
            
            # 检查是否包含危险字符
            dangerous_chars = ["<", ">", "\"", "'", "&", "javascript:", "vbscript:", "data:"]
            for char in dangerous_chars:
                if char in url.lower():
                    return False
            
            return True
            
        except Exception:
            return False
    
    def clean_input(self, input_data: str) -> str:
        """清理输入数据"""
        # 转义HTML字符
        cleaned = self.escape_html(input_data)
        
        # 移除多余的空白字符
        cleaned = re.sub(r"\s+", " ", cleaned)
        
        # 移除首尾空白
        cleaned = cleaned.strip()
        
        return cleaned
    
    def get_threat_summary(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取威胁摘要"""
        if not threats:
            return {"level": "safe", "count": 0}
        
        threat_levels = [threat["threat_level"] for threat in threats]
        
        if "critical" in threat_levels:
            level = "critical"
        elif "high" in threat_levels:
            level = "high"
        elif "medium" in threat_levels:
            level = "medium"
        else:
            level = "low"
        
        return {
            "level": level,
            "count": len(threats),
            "threats": threats
        }


class XSSMiddleware(Middleware):
    """XSS防护中间件"""
    
    def __init__(self, 
                 protection: XSSProtection = None,
                 block_threats: bool = True,
                 log_threats: bool = True,
                 sanitize_output: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.protection = protection or XSSProtection()
        self.block_threats = block_threats
        self.log_threats = log_threats
        self.sanitize_output = sanitize_output
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理XSS防护"""
        # 检查请求数据
        threats = []
        
        # 检查查询参数
        for param, value in request.query_params.items():
            if isinstance(value, str):
                param_threats = self.protection.detect_xss(value)
                threats.extend(param_threats)
        
        # 检查请求体
        if hasattr(request, 'body') and request.body:
            if isinstance(request.body, str):
                body_threats = self.protection.detect_xss(request.body)
                threats.extend(body_threats)
            elif isinstance(request.body, dict):
                for key, value in request.body.items():
                    if isinstance(value, str):
                        body_threats = self.protection.detect_xss(value)
                        threats.extend(body_threats)
        
        # 检查请求头
        for header, value in request.headers.items():
            if isinstance(value, str):
                header_threats = self.protection.detect_xss(value)
                threats.extend(header_threats)
        
        # 如果有威胁，记录并决定是否阻止
        if threats:
            if self.log_threats:
                # 记录威胁日志
                pass
            
            if self.block_threats:
                threat_summary = self.protection.get_threat_summary(threats)
                return self._create_threat_response(threat_summary)
        
        # 继续处理请求
        response = await next_handler()
        
        # 清理响应内容
        if self.sanitize_output and response.body:
            if isinstance(response.body, str):
                response.body = self.protection.sanitize_html(response.body)
            elif isinstance(response.body, dict):
                response.body = self._sanitize_dict(response.body)
        
        return response
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理字典数据"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.protection.sanitize_html(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self._sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """清理列表数据"""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.protection.sanitize_html(item))
            elif isinstance(item, dict):
                sanitized.append(self._sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self._sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized
    
    def _create_threat_response(self, threat_summary: Dict[str, Any]) -> Response:
        """创建威胁响应"""
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            body={
                "error": "XSS Attack Detected",
                "message": f"Potential XSS attack detected (Level: {threat_summary['level']})",
                "code": "XSS_ATTACK_DETECTED",
                "threat_count": threat_summary["count"]
            }
        )


# 全局XSS防护实例
xss_protection = None


def init_xss_protection():
    """初始化XSS防护"""
    global xss_protection
    xss_protection = XSSProtection()
    return xss_protection


def get_xss_protection() -> XSSProtection:
    """获取XSS防护实例"""
    if xss_protection is None:
        raise RuntimeError("XSS protection not initialized")
    return xss_protection