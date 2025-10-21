"""
SQL注入防护
防止SQL注入攻击
"""

import re
import hashlib
from typing import Dict, List, Set, Optional, Any, Pattern
from dataclasses import dataclass
from enum import Enum

from app.core.middleware.base import Middleware, Request, Response


class SQLInjectionError(Exception):
    """SQL注入错误"""
    pass


class ThreatLevel(Enum):
    """威胁级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SQLInjectionPattern:
    """SQL注入模式"""
    pattern: Pattern
    threat_level: ThreatLevel
    description: str
    mitigation: str


class SQLInjectionProtection:
    """SQL注入防护类"""
    
    def __init__(self):
        self.patterns = self._load_sql_injection_patterns()
        self.whitelist_patterns = self._load_whitelist_patterns()
        self.blocked_ips: Set[str] = set()
        self.suspicious_requests: Dict[str, int] = {}
        self.max_suspicious_requests = 5
        
    def _load_sql_injection_patterns(self) -> List[SQLInjectionPattern]:
        """加载SQL注入检测模式"""
        patterns = [
            # 基础SQL注入模式
            SQLInjectionPattern(
                pattern=re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)", re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description="SQL关键字检测",
                mitigation="使用参数化查询"
            ),
            
            # 注释符检测
            SQLInjectionPattern(
                pattern=re.compile(r"(--|#|\/\*|\*\/)", re.IGNORECASE),
                threat_level=ThreatLevel.MEDIUM,
                description="SQL注释符检测",
                mitigation="过滤注释符"
            ),
            
            # 引号检测
            SQLInjectionPattern(
                pattern=re.compile(r"['\"]", re.IGNORECASE),
                threat_level=ThreatLevel.LOW,
                description="引号字符检测",
                mitigation="转义引号字符"
            ),
            
            # 分号检测
            SQLInjectionPattern(
                pattern=re.compile(r";", re.IGNORECASE),
                threat_level=ThreatLevel.MEDIUM,
                description="SQL语句分隔符检测",
                mitigation="过滤分号字符"
            ),
            
            # 等号检测
            SQLInjectionPattern(
                pattern=re.compile(r"=", re.IGNORECASE),
                threat_level=ThreatLevel.LOW,
                description="等号字符检测",
                mitigation="验证等号使用"
            ),
            
            # 括号检测
            SQLInjectionPattern(
                pattern=re.compile(r"[()]", re.IGNORECASE),
                threat_level=ThreatLevel.LOW,
                description="括号字符检测",
                mitigation="验证括号使用"
            ),
            
            # 时间延迟检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(SLEEP|WAITFOR|DELAY)\b", re.IGNORECASE),
                threat_level=ThreatLevel.CRITICAL,
                description="时间延迟函数检测",
                mitigation="阻止时间延迟攻击"
            ),
            
            # 信息收集检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(VERSION|USER|DATABASE|SCHEMA|TABLE|COLUMN)\b", re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description="信息收集函数检测",
                mitigation="阻止信息收集"
            ),
            
            # 文件操作检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(LOAD_FILE|INTO\s+OUTFILE|INTO\s+DUMPFILE)\b", re.IGNORECASE),
                threat_level=ThreatLevel.CRITICAL,
                description="文件操作函数检测",
                mitigation="阻止文件操作"
            ),
            
            # 系统命令检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(SYSTEM|SHELL|CMD|EXEC)\b", re.IGNORECASE),
                threat_level=ThreatLevel.CRITICAL,
                description="系统命令检测",
                mitigation="阻止系统命令执行"
            ),
            
            # 盲注检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(AND|OR)\s+\d+\s*=\s*\d+", re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description="盲注模式检测",
                mitigation="阻止盲注攻击"
            ),
            
            # 联合查询检测
            SQLInjectionPattern(
                pattern=re.compile(r"\bUNION\s+(ALL\s+)?SELECT\b", re.IGNORECASE),
                threat_level=ThreatLevel.CRITICAL,
                description="联合查询检测",
                mitigation="阻止联合查询"
            ),
            
            # 子查询检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\s+.*\s+(SELECT|INSERT|UPDATE|DELETE)\b", re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description="子查询检测",
                mitigation="阻止子查询"
            ),
            
            # 存储过程检测
            SQLInjectionPattern(
                pattern=re.compile(r"\b(EXEC|EXECUTE|CALL|PROCEDURE)\b", re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description="存储过程检测",
                mitigation="阻止存储过程调用"
            ),
            
            # 十六进制检测
            SQLInjectionPattern(
                pattern=re.compile(r"0x[0-9a-fA-F]+", re.IGNORECASE),
                threat_level=ThreatLevel.MEDIUM,
                description="十六进制编码检测",
                mitigation="阻止十六进制编码"
            ),
            
            # Base64检测
            SQLInjectionPattern(
                pattern=re.compile(r"[A-Za-z0-9+/]{4,}={0,2}", re.IGNORECASE),
                threat_level=ThreatLevel.LOW,
                description="Base64编码检测",
                mitigation="验证Base64编码"
            ),
        ]
        
        return patterns
    
    def _load_whitelist_patterns(self) -> List[Pattern]:
        """加载白名单模式"""
        patterns = [
            # 允许的常见查询参数
            re.compile(r"^[a-zA-Z0-9_\-\.]+$"),
            # 允许的邮箱格式
            re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            # 允许的URL格式
            re.compile(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            # 允许的数字格式
            re.compile(r"^\d+$"),
            # 允许的日期格式
            re.compile(r"^\d{4}-\d{2}-\d{2}$"),
        ]
        
        return patterns
    
    def detect_sql_injection(self, input_data: str) -> List[Dict[str, Any]]:
        """检测SQL注入"""
        threats = []
        
        # 检查白名单
        if self._is_whitelisted(input_data):
            return threats
        
        # 检查SQL注入模式
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
    
    def _is_whitelisted(self, input_data: str) -> bool:
        """检查是否在白名单中"""
        for pattern in self.whitelist_patterns:
            if pattern.match(input_data):
                return True
        return False
    
    def sanitize_input(self, input_data: str) -> str:
        """清理输入数据"""
        # 移除SQL注释
        input_data = re.sub(r"--.*$", "", input_data, flags=re.MULTILINE)
        input_data = re.sub(r"#.*$", "", input_data, flags=re.MULTILINE)
        input_data = re.sub(r"/\*.*?\*/", "", input_data, flags=re.DOTALL)
        
        # 转义特殊字符
        input_data = input_data.replace("'", "''")
        input_data = input_data.replace('"', '""')
        input_data = input_data.replace("\\", "\\\\")
        
        # 移除危险字符
        dangerous_chars = [";", "--", "/*", "*/", "xp_", "sp_"]
        for char in dangerous_chars:
            input_data = input_data.replace(char, "")
        
        return input_data
    
    def validate_sql_query(self, query: str) -> bool:
        """验证SQL查询"""
        # 检查是否包含危险关键字
        dangerous_keywords = [
            "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
            "EXEC", "EXECUTE", "UNION", "SELECT", "INTO", "OUTFILE"
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        return True
    
    def log_suspicious_activity(self, client_ip: str, input_data: str, threats: List[Dict[str, Any]]):
        """记录可疑活动"""
        # 记录可疑请求
        if client_ip not in self.suspicious_requests:
            self.suspicious_requests[client_ip] = 0
        
        self.suspicious_requests[client_ip] += 1
        
        # 如果可疑请求过多，加入黑名单
        if self.suspicious_requests[client_ip] >= self.max_suspicious_requests:
            self.blocked_ips.add(client_ip)
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """检查IP是否被阻止"""
        return client_ip in self.blocked_ips
    
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


class SQLInjectionMiddleware(Middleware):
    """SQL注入防护中间件"""
    
    def __init__(self, 
                 protection: SQLInjectionProtection = None,
                 block_threats: bool = True,
                 log_threats: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.protection = protection or SQLInjectionProtection()
        self.block_threats = block_threats
        self.log_threats = log_threats
    
    async def handle(self, request: Request, next_handler) -> Response:
        """处理SQL注入防护"""
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 检查IP是否被阻止
        if self.protection.is_ip_blocked(client_ip):
            return self._create_blocked_response("IP address blocked due to suspicious activity")
        
        # 检查请求数据
        threats = []
        
        # 检查查询参数
        for param, value in request.query_params.items():
            if isinstance(value, str):
                param_threats = self.protection.detect_sql_injection(value)
                threats.extend(param_threats)
        
        # 检查请求体
        if hasattr(request, 'body') and request.body:
            if isinstance(request.body, str):
                body_threats = self.protection.detect_sql_injection(request.body)
                threats.extend(body_threats)
            elif isinstance(request.body, dict):
                for key, value in request.body.items():
                    if isinstance(value, str):
                        body_threats = self.protection.detect_sql_injection(value)
                        threats.extend(body_threats)
        
        # 检查请求头
        for header, value in request.headers.items():
            if isinstance(value, str):
                header_threats = self.protection.detect_sql_injection(value)
                threats.extend(header_threats)
        
        # 如果有威胁，记录并决定是否阻止
        if threats:
            if self.log_threats:
                self.protection.log_suspicious_activity(client_ip, str(request.body), threats)
            
            if self.block_threats:
                threat_summary = self.protection.get_threat_summary(threats)
                return self._create_threat_response(threat_summary)
        
        # 继续处理请求
        return await next_handler()
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 优先从代理头获取
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 从请求对象获取
        if hasattr(request, 'client_ip'):
            return request.client_ip
        
        return "unknown"
    
    def _create_blocked_response(self, message: str) -> Response:
        """创建阻止响应"""
        return Response(
            status_code=403,
            headers={"Content-Type": "application/json"},
            body={
                "error": "Access Denied",
                "message": message,
                "code": "IP_BLOCKED"
            }
        )
    
    def _create_threat_response(self, threat_summary: Dict[str, Any]) -> Response:
        """创建威胁响应"""
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            body={
                "error": "SQL Injection Detected",
                "message": f"Potential SQL injection attack detected (Level: {threat_summary['level']})",
                "code": "SQL_INJECTION_DETECTED",
                "threat_count": threat_summary["count"]
            }
        )


# 全局SQL注入防护实例
sql_injection_protection = None


def init_sql_injection_protection():
    """初始化SQL注入防护"""
    global sql_injection_protection
    sql_injection_protection = SQLInjectionProtection()
    return sql_injection_protection


def get_sql_injection_protection() -> SQLInjectionProtection:
    """获取SQL注入防护实例"""
    if sql_injection_protection is None:
        raise RuntimeError("SQL injection protection not initialized")
    return sql_injection_protection