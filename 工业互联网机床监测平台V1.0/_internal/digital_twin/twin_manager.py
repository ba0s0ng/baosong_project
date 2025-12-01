"""
工业互联网机床状态监测平台 - 数字孪生管理器
"""
import asyncio
import json
import math
import random
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import time

import pymunk
import numpy as np
from loguru import logger

from config import settings
from backend.models import MachineData, MachineType, DigitalTwinState

class MachinePhysicsModel:
    """机床物理模型"""
    
    def __init__(self, machine_id: str, machine_type: MachineType):
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.space = pymunk.Space()
        self.space.gravity = settings.PHYSICS_ENGINE_GRAVITY
        
        # 物理组件
        self.main_body = None
        self.spindle = None
        self.tool = None
        self.workpiece = None
        
        # 状态变量
        self.temperature = 25.0  # 初始温度
        self.vibration = 0.0
        self.current = 0.0
        self.speed = 0.0
        self.pressure = 0.0
        self.tool_wear = 0.0
        self.power_consumption = 0.0
        
        # 物理参数
        self.thermal_capacity = 1000.0  # 热容量
        self.heat_dissipation = 0.1  # 散热系数
        self.friction_coefficient = 0.02
        self.wear_rate = 0.001
        
        # 运行状态
        self.is_running = False
        self.target_speed = 0.0
        self.load_factor = 0.0
        
        self._initialize_physics()
    
    def _initialize_physics(self):
        """初始化物理模型"""
        try:
            # 创建主体
            main_mass = 1000  # kg
            main_moment = pymunk.moment_for_box(main_mass, (200, 100))
            self.main_body = pymunk.Body(main_mass, main_moment)
            main_shape = pymunk.Poly.create_box(self.main_body, (200, 100))
            main_shape.friction = 0.7
            self.space.add(self.main_body, main_shape)
            
            # 创建主轴
            spindle_mass = 50  # kg
            spindle_moment = pymunk.moment_for_circle(spindle_mass, 0, 20)
            self.spindle = pymunk.Body(spindle_mass, spindle_moment)
            spindle_shape = pymunk.Circle(self.spindle, 20)
            spindle_shape.friction = 0.1
            self.space.add(self.spindle, spindle_shape)
            
            # 连接主体和主轴
            joint = pymunk.PivotJoint(self.main_body, self.spindle, (0, 0), (0, 0))
            joint.collide_bodies = False
            self.space.add(joint)
            
            logger.info(f"机床 {self.machine_id} 物理模型初始化完成")
            
        except Exception as e:
            logger.error(f"初始化物理模型失败: {e}")
    
    def update_physics(self, dt: float):
        """更新物理仿真"""
        try:
            # 更新物理空间
            self.space.step(dt)
            
            # 更新温度模型
            self._update_temperature(dt)
            
            # 更新振动模型
            self._update_vibration(dt)
            
            # 更新电流模型
            self._update_current(dt)
            
            # 更新转速模型
            self._update_speed(dt)
            
            # 更新压力模型
            self._update_pressure(dt)
            
            # 更新刀具磨损
            self._update_tool_wear(dt)
            
            # 更新功耗
            self._update_power_consumption(dt)
            
        except Exception as e:
            logger.error(f"更新物理仿真失败: {e}")
    
    def _update_temperature(self, dt: float):
        """更新温度模型"""
        # 基于功耗和转速计算热量产生
        heat_generation = self.power_consumption * 0.3 + self.speed * 0.001
        
        # 环境温度
        ambient_temp = 25.0
        
        # 热量散失
        heat_loss = self.heat_dissipation * (self.temperature - ambient_temp)
        
        # 温度变化
        temp_change = (heat_generation - heat_loss) / self.thermal_capacity * dt
        self.temperature += temp_change
        
        # 添加随机噪声
        self.temperature += random.gauss(0, 0.1)
        
        # 限制温度范围
        self.temperature = max(20.0, min(150.0, self.temperature))
    
    def _update_vibration(self, dt: float):
        """更新振动模型"""
        # 基础振动（与转速相关）
        base_vibration = self.speed * 0.001
        
        # 不平衡引起的振动
        imbalance_vibration = math.sin(time.time() * self.speed * 0.1) * 0.5
        
        # 磨损引起的振动
        wear_vibration = self.tool_wear * 0.05
        
        # 总振动
        self.vibration = base_vibration + imbalance_vibration + wear_vibration
        
        # 添加随机噪声
        self.vibration += random.gauss(0, 0.05)
        
        # 限制振动范围
        self.vibration = max(0.0, min(20.0, abs(self.vibration)))
    
    def _update_current(self, dt: float):
        """更新电流模型"""
        if self.is_running:
            # 基础电流（与转速和负载相关）
            base_current = 5.0 + self.speed * 0.01 + self.load_factor * 20.0
            
            # 启动电流冲击
            if self.speed < self.target_speed * 0.9:
                base_current *= 1.5
            
            self.current = base_current
        else:
            # 待机电流
            self.current = 2.0
        
        # 添加随机噪声
        self.current += random.gauss(0, 0.2)
        
        # 限制电流范围
        self.current = max(0.0, min(100.0, self.current))
    
    def _update_speed(self, dt: float):
        """更新转速模型"""
        if self.is_running:
            # 转速变化（考虑惯性）
            speed_diff = self.target_speed - self.speed
            acceleration = speed_diff * 2.0  # 加速度系数
            
            self.speed += acceleration * dt
            
            # 考虑负载对转速的影响
            load_effect = self.load_factor * 50.0
            self.speed = max(0, self.speed - load_effect * dt)
        else:
            # 停机时转速逐渐降低
            self.speed *= (1.0 - 5.0 * dt)  # 减速系数
        
        # 添加随机噪声
        self.speed += random.gauss(0, 1.0)
        
        # 限制转速范围
        self.speed = max(0.0, min(5000.0, self.speed))
    
    def _update_pressure(self, dt: float):
        """更新压力模型"""
        if self.is_running:
            # 基础压力（与负载相关）
            base_pressure = 3.0 + self.load_factor * 5.0
            
            # 压力波动
            pressure_fluctuation = math.sin(time.time() * 2.0) * 0.2
            
            self.pressure = base_pressure + pressure_fluctuation
        else:
            # 待机压力
            self.pressure = 1.0
        
        # 添加随机噪声
        self.pressure += random.gauss(0, 0.05)
        
        # 限制压力范围
        self.pressure = max(0.0, min(15.0, self.pressure))
    
    def _update_tool_wear(self, dt: float):
        """更新刀具磨损"""
        if self.is_running and self.speed > 100:
            # 磨损率与转速、负载、温度相关
            wear_rate = self.wear_rate * (1.0 + self.speed * 0.0001) * (1.0 + self.load_factor) * (1.0 + (self.temperature - 25) * 0.01)
            
            self.tool_wear += wear_rate * dt
        
        # 限制磨损范围
        self.tool_wear = max(0.0, min(100.0, self.tool_wear))
    
    def _update_power_consumption(self, dt: float):
        """更新功耗"""
        if self.is_running:
            # 基础功耗
            base_power = 5.0
            
            # 转速相关功耗
            speed_power = self.speed * 0.005
            
            # 负载相关功耗
            load_power = self.load_factor * 15.0
            
            # 效率损失（温度相关）
            efficiency_loss = (self.temperature - 25) * 0.01
            
            self.power_consumption = (base_power + speed_power + load_power) * (1.0 + efficiency_loss)
        else:
            # 待机功耗
            self.power_consumption = 1.0
        
        # 添加随机噪声
        self.power_consumption += random.gauss(0, 0.1)
        
        # 限制功耗范围
        self.power_consumption = max(0.0, min(100.0, self.power_consumption))
    
    def set_running_state(self, running: bool, target_speed: float = 0.0, load_factor: float = 0.0):
        """设置运行状态"""
        self.is_running = running
        self.target_speed = target_speed
        self.load_factor = max(0.0, min(1.0, load_factor))
        
        logger.info(f"机床 {self.machine_id} 状态更新: 运行={running}, 目标转速={target_speed}, 负载={load_factor}")
    
    def get_current_data(self) -> Dict[str, Any]:
        """获取当前数据"""
        return {
            "machine_id": self.machine_id,
            "timestamp": datetime.now().isoformat(),
            "temperature": round(self.temperature, 2),
            "vibration": round(self.vibration, 3),
            "current": round(self.current, 2),
            "speed": round(self.speed, 1),
            "pressure": round(self.pressure, 2),
            "tool_wear": round(self.tool_wear, 1),
            "power_consumption": round(self.power_consumption, 2),
            "is_virtual": True
        }
    
    def get_physics_state(self) -> Dict[str, Any]:
        """获取物理状态"""
        return {
            "main_body_position": list(self.main_body.position) if self.main_body else [0, 0],
            "main_body_velocity": list(self.main_body.velocity) if self.main_body else [0, 0],
            "spindle_position": list(self.spindle.position) if self.spindle else [0, 0],
            "spindle_angular_velocity": self.spindle.angular_velocity if self.spindle else 0,
            "is_running": self.is_running,
            "target_speed": self.target_speed,
            "load_factor": self.load_factor
        }

class DigitalTwinManager:
    """数字孪生管理器"""
    
    def __init__(self):
        self.twins: Dict[str, MachinePhysicsModel] = {}
        self.is_running = False
        self.update_task = None
        self.last_update_time = time.time()
        
    async def initialize(self):
        """初始化数字孪生管理器"""
        try:
            # 创建默认的虚拟机床
            await self._create_default_twins()
            
            self.is_running = True
            logger.success("数字孪生管理器初始化完成")
            
        except Exception as e:
            logger.error(f"数字孪生管理器初始化失败: {e}")
            raise
    
    async def _create_default_twins(self):
        """创建默认的虚拟机床"""
        default_machines = [
            {
                "machine_id": "CNC001",
                "machine_type": MachineType.CNC_LATHE,
                "name": "数控车床-001"
            },
            {
                "machine_id": "MILL001", 
                "machine_type": MachineType.MILLING_MACHINE,
                "name": "铣床-001"
            },
            {
                "machine_id": "DRILL001",
                "machine_type": MachineType.DRILLING_MACHINE,
                "name": "钻床-001"
            }
        ]
        
        for machine_config in default_machines:
            await self.create_twin(
                machine_config["machine_id"],
                machine_config["machine_type"]
            )
            
            # 设置初始运行状态
            await self.set_twin_state(
                machine_config["machine_id"],
                running=True,
                target_speed=random.uniform(800, 1500),
                load_factor=random.uniform(0.3, 0.8)
            )
        
        logger.info(f"创建了 {len(default_machines)} 个默认虚拟机床")
    
    async def create_twin(self, machine_id: str, machine_type: MachineType) -> bool:
        """创建数字孪生"""
        try:
            if machine_id in self.twins:
                logger.warning(f"数字孪生 {machine_id} 已存在")
                return False
            
            twin = MachinePhysicsModel(machine_id, machine_type)
            self.twins[machine_id] = twin
            
            logger.info(f"创建数字孪生: {machine_id} ({machine_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"创建数字孪生失败: {e}")
            return False
    
    async def remove_twin(self, machine_id: str) -> bool:
        """移除数字孪生"""
        if machine_id in self.twins:
            del self.twins[machine_id]
            logger.info(f"移除数字孪生: {machine_id}")
            return True
        return False
    
    async def update_physics(self):
        """更新所有数字孪生的物理仿真"""
        if not self.is_running:
            return
        
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 限制时间步长
        dt = min(dt, 0.1)
        
        for twin in self.twins.values():
            twin.update_physics(dt)
    
    async def update_from_real_data(self, data: Dict[str, Any]):
        """从真实数据更新数字孪生"""
        machine_id = data.get("machine_id")
        if not machine_id or machine_id not in self.twins:
            return
        
        twin = self.twins[machine_id]
        
        # 使用真实数据校准虚拟模型
        if "temperature" in data:
            twin.temperature = data["temperature"]
        if "vibration" in data:
            twin.vibration = data["vibration"]
        if "current" in data:
            twin.current = data["current"]
        if "speed" in data:
            twin.speed = data["speed"]
        if "pressure" in data:
            twin.pressure = data["pressure"]
        
        logger.debug(f"使用真实数据更新数字孪生: {machine_id}")
    
    async def generate_virtual_data(self) -> List[Dict[str, Any]]:
        """生成虚拟数据"""
        virtual_data = []
        
        for twin in self.twins.values():
            data = twin.get_current_data()
            virtual_data.append(data)
        
        return virtual_data
    
    async def set_twin_state(self, machine_id: str, running: bool, target_speed: float = 0.0, load_factor: float = 0.0) -> bool:
        """设置数字孪生状态"""
        if machine_id not in self.twins:
            return False
        
        twin = self.twins[machine_id]
        twin.set_running_state(running, target_speed, load_factor)
        return True
    
    async def get_twin_state(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """获取数字孪生状态"""
        if machine_id not in self.twins:
            return None
        
        twin = self.twins[machine_id]
        
        return {
            "machine_id": machine_id,
            "timestamp": datetime.now().isoformat(),
            "physics_state": twin.get_physics_state(),
            "current_data": twin.get_current_data(),
            "simulation_parameters": {
                "thermal_capacity": twin.thermal_capacity,
                "heat_dissipation": twin.heat_dissipation,
                "friction_coefficient": twin.friction_coefficient,
                "wear_rate": twin.wear_rate
            },
            "predicted_values": await self._predict_values(twin),
            "health_score": self._calculate_health_score(twin),
            "remaining_life": self._estimate_remaining_life(twin)
        }
    
    async def _predict_values(self, twin: MachinePhysicsModel) -> Dict[str, float]:
        """预测未来值"""
        # 简单的线性预测（实际应用中可以使用更复杂的机器学习模型）
        predictions = {}
        
        # 预测温度趋势
        temp_trend = (twin.temperature - 25.0) * 0.1
        predictions["temperature_1h"] = twin.temperature + temp_trend
        
        # 预测刀具磨损
        wear_rate = twin.wear_rate * (1.0 + twin.speed * 0.0001) if twin.is_running else 0
        predictions["tool_wear_1h"] = min(100.0, twin.tool_wear + wear_rate * 3600)
        
        # 预测振动
        vibration_trend = twin.vibration * 0.05 if twin.tool_wear > 50 else 0
        predictions["vibration_1h"] = twin.vibration + vibration_trend
        
        return predictions
    
    def _calculate_health_score(self, twin: MachinePhysicsModel) -> float:
        """计算健康评分"""
        score = 100.0
        
        # 温度影响
        if twin.temperature > 80:
            score -= (twin.temperature - 80) * 2
        elif twin.temperature > 70:
            score -= (twin.temperature - 70) * 1
        
        # 振动影响
        if twin.vibration > 8:
            score -= (twin.vibration - 8) * 5
        elif twin.vibration > 5:
            score -= (twin.vibration - 5) * 2
        
        # 刀具磨损影响
        score -= twin.tool_wear * 0.5
        
        # 电流异常影响
        if twin.current > 45:
            score -= (twin.current - 45) * 1
        
        return max(0.0, min(100.0, score))
    
    def _estimate_remaining_life(self, twin: MachinePhysicsModel) -> Optional[float]:
        """估算剩余寿命（小时）"""
        if not twin.is_running:
            return None
        
        # 基于刀具磨损估算
        if twin.tool_wear >= 95:
            return 0.0
        
        wear_rate = twin.wear_rate * (1.0 + twin.speed * 0.0001)
        if wear_rate <= 0:
            return None
        
        remaining_wear = 95.0 - twin.tool_wear
        remaining_hours = remaining_wear / wear_rate / 3600  # 转换为小时
        
        return max(0.0, remaining_hours)
    
    async def simulate_fault(self, machine_id: str, fault_type: str, severity: float = 1.0):
        """模拟故障"""
        if machine_id not in self.twins:
            return False
        
        twin = self.twins[machine_id]
        
        if fault_type == "overheat":
            twin.temperature += 20 * severity
        elif fault_type == "vibration":
            twin.vibration += 5 * severity
        elif fault_type == "tool_wear":
            twin.tool_wear += 20 * severity
        elif fault_type == "pressure_drop":
            twin.pressure -= 2 * severity
        
        logger.warning(f"模拟故障: {machine_id} - {fault_type} (严重程度: {severity})")
        return True
    
    async def get_all_twins_status(self) -> Dict[str, Any]:
        """获取所有数字孪生状态"""
        status = {
            "total_twins": len(self.twins),
            "running_twins": sum(1 for twin in self.twins.values() if twin.is_running),
            "twins": {}
        }
        
        for machine_id, twin in self.twins.items():
            status["twins"][machine_id] = {
                "machine_type": twin.machine_type.value,
                "is_running": twin.is_running,
                "temperature": twin.temperature,
                "speed": twin.speed,
                "health_score": self._calculate_health_score(twin)
            }
        
        return status
    
    async def shutdown(self):
        """关闭数字孪生管理器"""
        self.is_running = False
        
        if self.update_task:
            self.update_task.cancel()
        
        # 清理物理空间
        for twin in self.twins.values():
            if twin.space:
                twin.space = None
        
        self.twins.clear()
        logger.info("数字孪生管理器已关闭")
    
    def is_running(self) -> bool:
        """检查管理器是否运行中"""
        return self.is_running
    
    async def export_twin_data(self, machine_id: str, hours: int = 24) -> Optional[Dict[str, Any]]:
        """导出数字孪生数据"""
        if machine_id not in self.twins:
            return None
        
        twin = self.twins[machine_id]
        
        # 生成历史数据（模拟）
        historical_data = []
        current_time = datetime.now()
        
        for i in range(hours * 60):  # 每分钟一个数据点
            timestamp = current_time - timedelta(minutes=i)
            
            # 添加一些历史变化
            temp_variation = math.sin(i * 0.1) * 5
            vibration_variation = math.sin(i * 0.05) * 0.5
            
            data_point = {
                "timestamp": timestamp.isoformat(),
                "temperature": twin.temperature + temp_variation,
                "vibration": twin.vibration + vibration_variation,
                "current": twin.current + random.gauss(0, 1),
                "speed": twin.speed + random.gauss(0, 10),
                "pressure": twin.pressure + random.gauss(0, 0.1)
            }
            historical_data.append(data_point)
        
        return {
            "machine_id": machine_id,
            "export_time": datetime.now().isoformat(),
            "period_hours": hours,
            "current_state": await self.get_twin_state(machine_id),
            "historical_data": historical_data
        }
