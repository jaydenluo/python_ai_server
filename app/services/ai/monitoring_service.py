"""
监控服务
负责AI工作流和智能体的实时监控、性能分析、告警管理
"""

import uuid
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from app.services.base_service import BaseService


class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"         # 信息
    WARNING = "warning"   # 警告
    ERROR = "error"       # 错误
    CRITICAL = "critical" # 严重


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"     # 计数器
    GAUGE = "gauge"        # 仪表
    HISTOGRAM = "histogram" # 直方图
    SUMMARY = "summary"    # 摘要


class MonitoringService(BaseService):
    """监控服务"""
    
    def __init__(self):
        super().__init__()
        self.metrics = {}      # 指标缓存
        self.alerts = {}       # 告警缓存
        self.logs = {}         # 日志缓存
        self.dashboards = {}   # 仪表板缓存
    
    def create_metric(self, metric_config: Dict[str, Any]) -> str:
        """
        创建监控指标
        
        Args:
            metric_config: 指标配置
                {
                    "name": "指标名称",
                    "type": "counter|gauge|histogram|summary",
                    "description": "指标描述",
                    "labels": [...],  # 标签列表
                    "thresholds": {...}  # 阈值配置
                }
        
        Returns:
            str: 指标ID
        """
        metric_id = str(uuid.uuid4())
        
        metric = {
            "id": metric_id,
            "name": metric_config.get("name", "未命名指标"),
            "type": metric_config.get("type", "gauge"),
            "description": metric_config.get("description", ""),
            "labels": metric_config.get("labels", []),
            "thresholds": metric_config.get("thresholds", {}),
            "values": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.metrics[metric_id] = metric
        return metric_id
    
    def record_metric(self, metric_id: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None) -> bool:
        """
        记录指标值
        
        Args:
            metric_id: 指标ID
            value: 指标值
            labels: 标签
            
        Returns:
            bool: 是否记录成功
        """
        if metric_id not in self.metrics:
            return False
        
        metric = self.metrics[metric_id]
        
        # 创建数据点
        data_point = {
            "value": value,
            "labels": labels or {},
            "timestamp": datetime.now().isoformat()
        }
        
        metric["values"].append(data_point)
        metric["updated_at"] = datetime.now().isoformat()
        
        # 检查阈值
        self._check_thresholds(metric_id, value)
        
        return True
    
    def get_metric_data(self, metric_id: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取指标数据
        
        Args:
            metric_id: 指标ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[Dict]: 指标数据
        """
        if metric_id not in self.metrics:
            return []
        
        metric = self.metrics[metric_id]
        values = metric["values"]
        
        # 时间过滤
        if start_time or end_time:
            filtered_values = []
            for value in values:
                timestamp = datetime.fromisoformat(value["timestamp"])
                
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                
                filtered_values.append(value)
            
            return filtered_values
        
        return values
    
    def create_alert(self, alert_config: Dict[str, Any]) -> str:
        """
        创建告警规则
        
        Args:
            alert_config: 告警配置
                {
                    "name": "告警名称",
                    "description": "告警描述",
                    "metric_id": "指标ID",
                    "condition": "阈值条件",
                    "level": "info|warning|error|critical",
                    "enabled": true
                }
        
        Returns:
            str: 告警ID
        """
        alert_id = str(uuid.uuid4())
        
        alert = {
            "id": alert_id,
            "name": alert_config.get("name", "未命名告警"),
            "description": alert_config.get("description", ""),
            "metric_id": alert_config.get("metric_id"),
            "condition": alert_config.get("condition", "value > 0"),
            "level": alert_config.get("level", "info"),
            "enabled": alert_config.get("enabled", True),
            "triggered_count": 0,
            "last_triggered": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.alerts[alert_id] = alert
        return alert_id
    
    def check_alerts(self, metric_id: str) -> List[Dict[str, Any]]:
        """
        检查告警
        
        Args:
            metric_id: 指标ID
            
        Returns:
            List[Dict]: 触发的告警
        """
        triggered_alerts = []
        
        for alert_id, alert in self.alerts.items():
            if not alert["enabled"] or alert["metric_id"] != metric_id:
                continue
            
            # 获取最新指标值
            metric_data = self.get_metric_data(metric_id)
            if not metric_data:
                continue
            
            latest_value = metric_data[-1]["value"]
            
            # 检查条件
            if self._evaluate_condition(alert["condition"], latest_value):
                # 触发告警
                alert["triggered_count"] += 1
                alert["last_triggered"] = datetime.now().isoformat()
                
                triggered_alert = {
                    "alert_id": alert_id,
                    "name": alert["name"],
                    "description": alert["description"],
                    "level": alert["level"],
                    "value": latest_value,
                    "condition": alert["condition"],
                    "triggered_at": datetime.now().isoformat()
                }
                
                triggered_alerts.append(triggered_alert)
        
        return triggered_alerts
    
    def log_event(self, event: Dict[str, Any]) -> str:
        """
        记录事件日志
        
        Args:
            event: 事件信息
                {
                    "level": "info|warning|error|critical",
                    "message": "日志消息",
                    "source": "事件源",
                    "metadata": {...}  # 元数据
                }
        
        Returns:
            str: 日志ID
        """
        log_id = str(uuid.uuid4())
        
        log_entry = {
            "id": log_id,
            "level": event.get("level", "info"),
            "message": event.get("message", ""),
            "source": event.get("source", "system"),
            "metadata": event.get("metadata", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logs[log_id] = log_entry
        return log_id
    
    def get_logs(self, level: Optional[str] = None, source: Optional[str] = None, 
                 start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取日志
        
        Args:
            level: 日志级别筛选
            source: 事件源筛选
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[Dict]: 日志列表
        """
        logs = list(self.logs.values())
        
        # 级别筛选
        if level:
            logs = [log for log in logs if log["level"] == level]
        
        # 源筛选
        if source:
            logs = [log for log in logs if log["source"] == source]
        
        # 时间筛选
        if start_time or end_time:
            filtered_logs = []
            for log in logs:
                timestamp = datetime.fromisoformat(log["timestamp"])
                
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                
                filtered_logs.append(log)
            
            logs = filtered_logs
        
        # 按时间排序
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs
    
    def create_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """
        创建监控仪表板
        
        Args:
            dashboard_config: 仪表板配置
                {
                    "name": "仪表板名称",
                    "description": "仪表板描述",
                    "widgets": [...]  # 组件列表
                }
        
        Returns:
            str: 仪表板ID
        """
        dashboard_id = str(uuid.uuid4())
        
        dashboard = {
            "id": dashboard_id,
            "name": dashboard_config.get("name", "未命名仪表板"),
            "description": dashboard_config.get("description", ""),
            "widgets": dashboard_config.get("widgets", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.dashboards[dashboard_id] = dashboard
        return dashboard_id
    
    def get_dashboard_data(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        获取仪表板数据
        
        Args:
            dashboard_id: 仪表板ID
            
        Returns:
            Dict: 仪表板数据
        """
        if dashboard_id not in self.dashboards:
            return None
        
        dashboard = self.dashboards[dashboard_id]
        
        # 获取组件数据
        widgets_data = []
        for widget in dashboard["widgets"]:
            widget_data = self._get_widget_data(widget)
            widgets_data.append(widget_data)
        
        return {
            "dashboard": dashboard,
            "widgets_data": widgets_data
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        获取系统指标
        
        Returns:
            Dict: 系统指标
        """
        return {
            "total_metrics": len(self.metrics),
            "total_alerts": len(self.alerts),
            "total_logs": len(self.logs),
            "active_alerts": len([a for a in self.alerts.values() if a["enabled"]]),
            "recent_logs": len(self.get_logs(start_time=datetime.now() - timedelta(hours=1)))
        }
    
    def _check_thresholds(self, metric_id: str, value: Union[int, float]) -> None:
        """检查阈值"""
        metric = self.metrics[metric_id]
        thresholds = metric.get("thresholds", {})
        
        for threshold_name, threshold_value in thresholds.items():
            if threshold_name == "warning" and value > threshold_value:
                self.log_event({
                    "level": "warning",
                    "message": f"指标 {metric['name']} 超过警告阈值",
                    "source": "monitoring",
                    "metadata": {"metric_id": metric_id, "value": value, "threshold": threshold_value}
                })
            elif threshold_name == "critical" and value > threshold_value:
                self.log_event({
                    "level": "critical",
                    "message": f"指标 {metric['name']} 超过严重阈值",
                    "source": "monitoring",
                    "metadata": {"metric_id": metric_id, "value": value, "threshold": threshold_value}
                })
    
    def _evaluate_condition(self, condition: str, value: Union[int, float]) -> bool:
        """评估条件"""
        try:
            # 简单的条件评估
            # 支持: value > 10, value < 5, value == 0 等
            return eval(condition.replace("value", str(value)))
        except:
            return False
    
    def _get_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """获取组件数据"""
        widget_type = widget.get("type", "metric")
        
        if widget_type == "metric":
            return self._get_metric_widget_data(widget)
        elif widget_type == "chart":
            return self._get_chart_widget_data(widget)
        elif widget_type == "alert":
            return self._get_alert_widget_data(widget)
        else:
            return {"error": f"不支持的组件类型: {widget_type}"}
    
    def _get_metric_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """获取指标组件数据"""
        metric_id = widget.get("metric_id")
        if not metric_id or metric_id not in self.metrics:
            return {"error": "指标不存在"}
        
        metric_data = self.get_metric_data(metric_id)
        if not metric_data:
            return {"value": 0, "trend": "stable"}
        
        latest_value = metric_data[-1]["value"]
        
        # 计算趋势
        if len(metric_data) >= 2:
            previous_value = metric_data[-2]["value"]
            if latest_value > previous_value:
                trend = "up"
            elif latest_value < previous_value:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "value": latest_value,
            "trend": trend,
            "timestamp": metric_data[-1]["timestamp"]
        }
    
    def _get_chart_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """获取图表组件数据"""
        metric_id = widget.get("metric_id")
        if not metric_id or metric_id not in self.metrics:
            return {"error": "指标不存在"}
        
        # 获取时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)  # 默认24小时
        
        metric_data = self.get_metric_data(metric_id, start_time, end_time)
        
        return {
            "data": metric_data,
            "chart_type": widget.get("chart_type", "line")
        }
    
    def _get_alert_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """获取告警组件数据"""
        # 获取最近的告警
        recent_alerts = []
        for alert in self.alerts.values():
            if alert["last_triggered"]:
                recent_alerts.append(alert)
        
        # 按触发时间排序
        recent_alerts.sort(key=lambda x: x["last_triggered"], reverse=True)
        
        return {
            "alerts": recent_alerts[:10],  # 最近10个告警
            "total_alerts": len(recent_alerts)
        }