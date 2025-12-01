"""
工业互联网机床状态监测平台 - 规则引擎
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time

from loguru import logger
from config import settings
from backend.models import AlarmEvent, AlarmLevel, MachineData

class RuleType(str, Enum):
    """规则类型"""
    THRESHOLD = "THRESHOLD"  # 阈值规则
    TREND = "TREND"  # 趋势规则
    PATTERN = "PATTERN"  # 模式规则
    COMPOSITE = "COMPOSITE"  # 复合规则

class OperatorType(str, Enum):
    """操作符类型"""
    GT = ">"  # 大于
    GTE = ">="  # 大于等于
    LT = "<"  # 小于
    LTE = "<="  # 小于等于
    EQ = "=="  # 等于
    NEQ = "!="  # 不等于
    IN = "in"  # 包含
    NOT_IN = "not_in"  # 不包含

@dataclass
class RuleCondition:
    """规则条件"""
    parameter: str  # 参数名
    operator: OperatorType  # 操作符
    value: Any  # 比较值
    weight: float = 1.0  # 权重

@dataclass
class Rule:
    """规则定义"""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: List[RuleCondition]
    alarm_level: AlarmLevel
    enabled: bool = True
    machine_types: List[str] = None  # 适用的机床类型
    cooldown_seconds: int = 60  # 冷却时间（秒）
    created_at: datetime = None
    updated_at: datetime = None

class RuleEngine:
    """规则引擎 - 实现异常检测和报警"""
    
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.rule_history: Dict[str, List[Dict[str, Any]]] = {}  # 规则执行历史
        self.alarm_cooldowns: Dict[str, datetime] = {}  # 报警冷却时间
        self.data_buffer: Dict[str, List[Dict[str, Any]]] = {}  # 数据缓冲区
        self.is_active = False
        
    def load_rules(self):
        """加载规则配置"""
        try:
            # 加载默认规则
            self._load_default_rules()
            
            # 尝试从文件加载自定义规则
            self._load_custom_rules()
            
            self.is_active = True
            logger.success(f"规则引擎启动成功，加载了 {len(self.rules)} 条规则")
            
        except Exception as e:
            logger.error(f"加载规则失败: {e}")
            raise
    
    def _load_default_rules(self):
        """加载默认规则"""
        default_rules = [
            # 温度过高报警
            Rule(
                rule_id="temp_high_critical",
                name="温度过高临界报警",
                description="机床温度超过80°C时触发临界报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("temperature", OperatorType.GT, 80.0)
                ],
                alarm_level=AlarmLevel.CRITICAL,
                cooldown_seconds=30
            ),
            
            Rule(
                rule_id="temp_high_warning",
                name="温度过高警告",
                description="机床温度超过70°C时触发警告",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("temperature", OperatorType.GT, 70.0)
                ],
                alarm_level=AlarmLevel.WARNING,
                cooldown_seconds=60
            ),
            
            # 振动异常报警
            Rule(
                rule_id="vibration_high",
                name="振动异常报警",
                description="机床振动超过8mm/s时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("vibration", OperatorType.GT, 8.0)
                ],
                alarm_level=AlarmLevel.ERROR,
                cooldown_seconds=45
            ),
            
            # 电流异常报警
            Rule(
                rule_id="current_high",
                name="电流过高报警",
                description="机床电流超过45A时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("current", OperatorType.GT, 45.0)
                ],
                alarm_level=AlarmLevel.ERROR,
                cooldown_seconds=30
            ),
            
            Rule(
                rule_id="current_low",
                name="电流异常低报警",
                description="机床运行时电流低于5A可能存在异常",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("current", OperatorType.LT, 5.0),
                    RuleCondition("speed", OperatorType.GT, 100.0)  # 运行状态
                ],
                alarm_level=AlarmLevel.WARNING,
                cooldown_seconds=120
            ),
            
            # 转速异常报警
            Rule(
                rule_id="speed_high",
                name="转速过高报警",
                description="机床转速超过2800rpm时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("speed", OperatorType.GT, 2800.0)
                ],
                alarm_level=AlarmLevel.WARNING,
                cooldown_seconds=60
            ),
            
            # 压力异常报警
            Rule(
                rule_id="pressure_high",
                name="压力过高报警",
                description="机床压力超过8bar时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("pressure", OperatorType.GT, 8.0)
                ],
                alarm_level=AlarmLevel.ERROR,
                cooldown_seconds=30
            ),
            
            Rule(
                rule_id="pressure_low",
                name="压力过低报警",
                description="机床压力低于1bar时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("pressure", OperatorType.LT, 1.0)
                ],
                alarm_level=AlarmLevel.WARNING,
                cooldown_seconds=60
            ),
            
            # 复合规则 - 综合异常
            Rule(
                rule_id="comprehensive_anomaly",
                name="综合异常报警",
                description="温度和振动同时异常时触发高级报警",
                rule_type=RuleType.COMPOSITE,
                conditions=[
                    RuleCondition("temperature", OperatorType.GT, 65.0, weight=0.6),
                    RuleCondition("vibration", OperatorType.GT, 6.0, weight=0.4)
                ],
                alarm_level=AlarmLevel.ERROR,
                cooldown_seconds=90
            ),
            
            # 刀具磨损报警
            Rule(
                rule_id="tool_wear_high",
                name="刀具磨损报警",
                description="刀具磨损超过85%时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("tool_wear", OperatorType.GT, 85.0)
                ],
                alarm_level=AlarmLevel.WARNING,
                cooldown_seconds=300  # 5分钟冷却
            ),
            
            # 功耗异常报警
            Rule(
                rule_id="power_consumption_high",
                name="功耗过高报警",
                description="功耗超过正常范围时触发报警",
                rule_type=RuleType.THRESHOLD,
                conditions=[
                    RuleCondition("power_consumption", OperatorType.GT, 50.0)
                ],
                alarm_level=AlarmLevel.WARNING,
                cooldown_seconds=120
            )
        ]
        
        for rule in default_rules:
            rule.created_at = datetime.now()
            rule.updated_at = datetime.now()
            self.rules[rule.rule_id] = rule
        
        logger.info(f"加载了 {len(default_rules)} 条默认规则")
    
    def _load_custom_rules(self):
        """从文件加载自定义规则"""
        try:
            # 这里可以从配置文件或数据库加载自定义规则
            # 暂时跳过，使用默认规则
            pass
        except Exception as e:
            logger.warning(f"加载自定义规则失败: {e}")
    
    async def process_data(self, data: Dict[str, Any]) -> Optional[AlarmEvent]:
        """处理数据并检查规则"""
        if not self.is_active:
            return None
        
        start_time = time.time()
        machine_id = data.get("machine_id")
        
        if not machine_id:
            return None
        
        try:
            # 将数据添加到缓冲区
            self._add_to_buffer(machine_id, data)
            
            # 检查所有规则
            alarm = await self._check_rules(machine_id, data)
            
            # 检查响应时间
            processing_time = time.time() - start_time
            if processing_time > settings.RULE_ENGINE_RESPONSE_TIME:
                logger.warning(f"规则引擎处理时间超标: {processing_time:.3f}s > {settings.RULE_ENGINE_RESPONSE_TIME}s")
            
            return alarm
            
        except Exception as e:
            logger.error(f"处理数据时发生错误: {e}")
            return None
    
    def _add_to_buffer(self, machine_id: str, data: Dict[str, Any]):
        """将数据添加到缓冲区"""
        if machine_id not in self.data_buffer:
            self.data_buffer[machine_id] = []
        
        self.data_buffer[machine_id].append(data)
        
        # 保持缓冲区大小（最多保留100条记录）
        if len(self.data_buffer[machine_id]) > 100:
            self.data_buffer[machine_id] = self.data_buffer[machine_id][-100:]
    
    async def _check_rules(self, machine_id: str, data: Dict[str, Any]) -> Optional[AlarmEvent]:
        """检查所有规则"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # 检查冷却时间
            cooldown_key = f"{machine_id}:{rule.rule_id}"
            if cooldown_key in self.alarm_cooldowns:
                if datetime.now() < self.alarm_cooldowns[cooldown_key]:
                    continue
            
            # 检查规则条件
            if await self._evaluate_rule(rule, machine_id, data):
                # 创建报警事件
                alarm = self._create_alarm_event(rule, machine_id, data)
                
                # 设置冷却时间
                self.alarm_cooldowns[cooldown_key] = datetime.now() + timedelta(seconds=rule.cooldown_seconds)
                
                # 记录规则执行历史
                self._record_rule_execution(rule.rule_id, machine_id, data, True)
                
                logger.warning(f"规则触发: {rule.name} - 机床: {machine_id}")
                return alarm
            else:
                # 记录规则执行历史（未触发）
                self._record_rule_execution(rule.rule_id, machine_id, data, False)
        
        return None
    
    async def _evaluate_rule(self, rule: Rule, machine_id: str, data: Dict[str, Any]) -> bool:
        """评估规则条件"""
        if rule.rule_type == RuleType.THRESHOLD:
            return self._evaluate_threshold_rule(rule, data)
        elif rule.rule_type == RuleType.COMPOSITE:
            return self._evaluate_composite_rule(rule, data)
        elif rule.rule_type == RuleType.TREND:
            return self._evaluate_trend_rule(rule, machine_id, data)
        elif rule.rule_type == RuleType.PATTERN:
            return self._evaluate_pattern_rule(rule, machine_id, data)
        
        return False
    
    def _evaluate_threshold_rule(self, rule: Rule, data: Dict[str, Any]) -> bool:
        """评估阈值规则"""
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, data):
                return False
        return True
    
    def _evaluate_composite_rule(self, rule: Rule, data: Dict[str, Any]) -> bool:
        """评估复合规则（加权评分）"""
        total_weight = 0
        satisfied_weight = 0
        
        for condition in rule.conditions:
            total_weight += condition.weight
            if self._evaluate_condition(condition, data):
                satisfied_weight += condition.weight
        
        # 如果满足条件的权重超过总权重的80%，则触发规则
        return satisfied_weight / total_weight >= 0.8
    
    def _evaluate_trend_rule(self, rule: Rule, machine_id: str, data: Dict[str, Any]) -> bool:
        """评估趋势规则"""
        # 获取历史数据
        history = self.data_buffer.get(machine_id, [])
        if len(history) < 5:  # 需要至少5个数据点
            return False
        
        # 简单的趋势检测（这里可以实现更复杂的算法）
        for condition in rule.conditions:
            parameter = condition.parameter
            values = [item.get(parameter, 0) for item in history[-5:] if parameter in item]
            
            if len(values) < 3:
                continue
            
            # 检查是否呈上升趋势
            if condition.operator == OperatorType.GT:
                if not all(values[i] > values[i-1] for i in range(1, len(values))):
                    return False
            # 检查是否呈下降趋势
            elif condition.operator == OperatorType.LT:
                if not all(values[i] < values[i-1] for i in range(1, len(values))):
                    return False
        
        return True
    
    def _evaluate_pattern_rule(self, rule: Rule, machine_id: str, data: Dict[str, Any]) -> bool:
        """评估模式规则"""
        # 这里可以实现复杂的模式匹配算法
        # 暂时返回False，表示未实现
        return False
    
    def _evaluate_condition(self, condition: RuleCondition, data: Dict[str, Any]) -> bool:
        """评估单个条件"""
        parameter_value = data.get(condition.parameter)
        if parameter_value is None:
            return False
        
        try:
            if condition.operator == OperatorType.GT:
                return parameter_value > condition.value
            elif condition.operator == OperatorType.GTE:
                return parameter_value >= condition.value
            elif condition.operator == OperatorType.LT:
                return parameter_value < condition.value
            elif condition.operator == OperatorType.LTE:
                return parameter_value <= condition.value
            elif condition.operator == OperatorType.EQ:
                return parameter_value == condition.value
            elif condition.operator == OperatorType.NEQ:
                return parameter_value != condition.value
            elif condition.operator == OperatorType.IN:
                return parameter_value in condition.value
            elif condition.operator == OperatorType.NOT_IN:
                return parameter_value not in condition.value
        except Exception as e:
            logger.error(f"评估条件时发生错误: {e}")
            return False
        
        return False
    
    def _create_alarm_event(self, rule: Rule, machine_id: str, data: Dict[str, Any]) -> AlarmEvent:
        """创建报警事件"""
        # 找到触发的参数和值
        triggered_condition = None
        for condition in rule.conditions:
            if self._evaluate_condition(condition, data):
                triggered_condition = condition
                break
        
        if not triggered_condition:
            triggered_condition = rule.conditions[0]  # 使用第一个条件作为默认
        
        return AlarmEvent(
            alarm_id=str(uuid.uuid4()),
            machine_id=machine_id,
            timestamp=datetime.now(),
            level=rule.alarm_level,
            type=rule.rule_type.value,
            message=f"{rule.name}: {rule.description}",
            parameter=triggered_condition.parameter,
            value=data.get(triggered_condition.parameter, 0),
            threshold=triggered_condition.value
        )
    
    def _record_rule_execution(self, rule_id: str, machine_id: str, data: Dict[str, Any], triggered: bool):
        """记录规则执行历史"""
        if rule_id not in self.rule_history:
            self.rule_history[rule_id] = []
        
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "machine_id": machine_id,
            "triggered": triggered,
            "data_snapshot": {k: v for k, v in data.items() if k in ["temperature", "vibration", "current", "speed", "pressure"]}
        }
        
        self.rule_history[rule_id].append(execution_record)
        
        # 保持历史记录大小
        if len(self.rule_history[rule_id]) > 1000:
            self.rule_history[rule_id] = self.rule_history[rule_id][-1000:]
    
    def add_rule(self, rule: Rule) -> bool:
        """添加新规则"""
        try:
            rule.created_at = datetime.now()
            rule.updated_at = datetime.now()
            self.rules[rule.rule_id] = rule
            logger.info(f"添加新规则: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"添加规则失败: {e}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新规则"""
        if rule_id not in self.rules:
            return False
        
        try:
            rule = self.rules[rule_id]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.now()
            logger.info(f"更新规则: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"更新规则失败: {e}")
            return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id not in self.rules:
            return False
        
        try:
            rule_name = self.rules[rule_id].name
            del self.rules[rule_id]
            
            # 清理相关历史记录
            if rule_id in self.rule_history:
                del self.rule_history[rule_id]
            
            logger.info(f"删除规则: {rule_name}")
            return True
        except Exception as e:
            logger.error(f"删除规则失败: {e}")
            return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"启用规则: {self.rules[rule_id].name}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"禁用规则: {self.rules[rule_id].name}")
            return True
        return False
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "rule_type": rule.rule_type.value,
                "alarm_level": rule.alarm_level.value,
                "enabled": rule.enabled,
                "conditions_count": len(rule.conditions),
                "cooldown_seconds": rule.cooldown_seconds,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
            }
            for rule in self.rules.values()
        ]
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        total_rules = len(self.rules)
        enabled_rules = sum(1 for rule in self.rules.values() if rule.enabled)
        
        rule_type_counts = {}
        alarm_level_counts = {}
        
        for rule in self.rules.values():
            rule_type = rule.rule_type.value
            alarm_level = rule.alarm_level.value
            
            rule_type_counts[rule_type] = rule_type_counts.get(rule_type, 0) + 1
            alarm_level_counts[alarm_level] = alarm_level_counts.get(alarm_level, 0) + 1
        
        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "disabled_rules": total_rules - enabled_rules,
            "rule_type_distribution": rule_type_counts,
            "alarm_level_distribution": alarm_level_counts,
            "active_cooldowns": len(self.alarm_cooldowns),
            "buffer_size": sum(len(buffer) for buffer in self.data_buffer.values())
        }
    
    def is_active(self) -> bool:
        """检查规则引擎是否活跃"""
        return self.is_active
    
    def clear_cooldowns(self):
        """清除所有冷却时间"""
        self.alarm_cooldowns.clear()
        logger.info("已清除所有报警冷却时间")
    
    def clear_history(self):
        """清除执行历史"""
        self.rule_history.clear()
        logger.info("已清除所有规则执行历史")
