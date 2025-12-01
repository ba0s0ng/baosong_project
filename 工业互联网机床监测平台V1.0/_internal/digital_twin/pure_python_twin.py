"""
工业互联网机床状态监测平台 - 纯Python数字孪生实现
不依赖PyMunk等外部物理引擎，使用纯Python实现物理仿真
"""
import asyncio
import json
import time
import math
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class MachineState(Enum):
    """机床状态"""
    IDLE = "idle"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class PhysicsState:
    """物理状态"""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    acceleration: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    angular_velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)

@dataclass
class MachineParameters:
    """机床参数"""
    max_speed: float = 3000.0
    max_temperature: float = 80.0
    max_vibration: float = 10.0
    max_current: float = 50.0
    max_pressure: float = 10.0
    thermal_capacity: float = 1000.0  # 热容量
    cooling_rate: float = 0.1  # 冷却速率
    friction_coefficient: float = 0.02  # 摩擦系数
    inertia: float = 10.0  # 转动惯量

class PurePythonTwin:
    """纯Python数字孪生实现"""
    
    def __init__(self, machine_id: str, machine_type: str):
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.state = MachineState.IDLE
        self.physics_state = PhysicsState()
        self.parameters = MachineParameters()
        
        # 当前数据
        self.current_data = {
            "machine_id": machine_id,
            "timestamp": datetime.now().isoformat(),
            "temperature": 25.0,
            "vibration": 0.0,
            "current": 0.0,
            "speed": 0.0,
            "pressure": 2.0,
            "tool_wear": 0.0,
            "power_consumption": 0.0,
            "is_virtual": True
        }
        
        # 目标值
        self.target_speed = 0.0
        self.target_temperature = 25.0
        
        # 历史数据
        self.history = []
        self.max_history = 1000
        
        # 仿真参数
        self.dt = 0.1  # 时间步长（秒）
        self.last_update = time.time()
        
        # 噪声参数
        self.noise_level = 0.05
        
        # 磨损模型
        self.wear_rate = 0.001  # 每分钟磨损率
        self.wear_acceleration = 1.0  # 磨损加速因子
        
        logger.info(f"创建纯Python数字孪生: {machine_id} ({machine_type})")
    
    def update_physics(self, dt: float):
        """更新物理状态"""
        try:
            # 转速物理模拟
            self._update_speed_physics(dt)
            
            # 温度物理模拟
            self._update_temperature_physics(dt)
            
            # 振动物理模拟
            self._update_vibration_physics(dt)
            
            # 电流物理模拟
            self._update_current_physics(dt)
            
            # 压力物理模拟
            self._update_pressure_physics(dt)
            
            # 刀具磨损模拟
            self._update_tool_wear(dt)
            
            # 功耗计算
            self._calculate_power_consumption()
            
            # 添加噪声
            self._add_noise()
            
            # 更新时间戳
            self.current_data["timestamp"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"物理更新错误: {e}")
    
    def _update_speed_physics(self, dt: float):
        """更新转速物理"""
        current_speed = self.current_data["speed"]
        speed_diff = self.target_speed - current_speed
        
        # 简单的PID控制器
        kp = 0.5  # 比例系数
        max_acceleration = 500.0  # 最大加速度 rpm/s
        
        acceleration = kp * speed_diff
        acceleration = max(-max_acceleration, min(max_acceleration, acceleration))
        
        # 考虑摩擦阻力
        friction_force = -self.parameters.friction_coefficient * current_speed
        acceleration += friction_force
        
        # 更新速度
        new_speed = current_speed + acceleration * dt
        new_speed = max(0, min(self.parameters.max_speed, new_speed))
        
        self.current_data["speed"] = new_speed
    
    def _update_temperature_physics(self, dt: float):
        """更新温度物理"""
        current_temp = self.current_data["temperature"]
        speed = self.current_data["speed"]
        
        # 热量产生（基于转速和负载）
        heat_generation = (speed / self.parameters.max_speed) * 30.0  # 最大30度升温
        
        # 环境温度
        ambient_temp = 25.0
        
        # 冷却（牛顿冷却定律）
        cooling = self.parameters.cooling_rate * (current_temp - ambient_temp)
        
        # 温度变化率
        temp_change = (heat_generation - cooling) * dt / self.parameters.thermal_capacity
        
        new_temp = current_temp + temp_change
        new_temp = max(ambient_temp, min(self.parameters.max_temperature * 1.2, new_temp))
        
        self.current_data["temperature"] = new_temp
    
    def _update_vibration_physics(self, dt: float):
        """更新振动物理"""
        speed = self.current_data["speed"]
        temperature = self.current_data["temperature"]
        tool_wear = self.current_data["tool_wear"]
        
        # 基础振动（与转速相关）
        base_vibration = (speed / self.parameters.max_speed) * 2.0
        
        # 温度影响（高温增加振动）
        temp_factor = max(0, (temperature - 50) / 30) * 1.5
        
        # 磨损影响（磨损增加振动）
        wear_factor = (tool_wear / 100) * 3.0
        
        # 共振频率影响（特定转速下振动增大）
        resonance_speeds = [800, 1200, 1800, 2400]  # 共振转速
        resonance_factor = 0
        for res_speed in resonance_speeds:
            if abs(speed - res_speed) < 50:
                resonance_factor = 2.0 * (1 - abs(speed - res_speed) / 50)
        
        total_vibration = base_vibration + temp_factor + wear_factor + resonance_factor
        total_vibration = max(0, min(self.parameters.max_vibration, total_vibration))
        
        # 添加随机波动
        vibration_noise = random.uniform(-0.2, 0.2)
        total_vibration += vibration_noise
        
        self.current_data["vibration"] = max(0, total_vibration)
    
    def _update_current_physics(self, dt: float):
        """更新电流物理"""
        speed = self.current_data["speed"]
        temperature = self.current_data["temperature"]
        
        if speed == 0:
            # 待机电流
            self.current_data["current"] = 2.0
        else:
            # 负载电流（与转速和温度相关）
            base_current = (speed / self.parameters.max_speed) * 40.0
            
            # 温度影响（高温增加电阻，降低效率）
            temp_factor = 1.0 + (temperature - 25) / 100
            
            total_current = base_current * temp_factor + 2.0  # 加上待机电流
            total_current = max(2.0, min(self.parameters.max_current, total_current))
            
            self.current_data["current"] = total_current
    
    def _update_pressure_physics(self, dt: float):
        """更新压力物理"""
        speed = self.current_data["speed"]
        
        if speed == 0:
            # 待机压力
            target_pressure = 2.0
        else:
            # 工作压力（与转速相关）
            target_pressure = 2.0 + (speed / self.parameters.max_speed) * 6.0
        
        current_pressure = self.current_data["pressure"]
        pressure_diff = target_pressure - current_pressure
        
        # 压力变化（有延迟）
        pressure_change = pressure_diff * 0.1 * dt
        new_pressure = current_pressure + pressure_change
        new_pressure = max(0, min(self.parameters.max_pressure, new_pressure))
        
        self.current_data["pressure"] = new_pressure
    
    def _update_tool_wear(self, dt: float):
        """更新刀具磨损"""
        speed = self.current_data["speed"]
        temperature = self.current_data["temperature"]
        vibration = self.current_data["vibration"]
        
        if speed > 0:
            # 基础磨损率
            base_wear = self.wear_rate * dt / 60  # 转换为每秒
            
            # 转速影响
            speed_factor = (speed / self.parameters.max_speed) ** 1.5
            
            # 温度影响（高温加速磨损）
            temp_factor = 1.0 + max(0, (temperature - 60) / 20)
            
            # 振动影响（高振动加速磨损）
            vib_factor = 1.0 + (vibration / 10) * 0.5
            
            total_wear = base_wear * speed_factor * temp_factor * vib_factor * self.wear_acceleration
            
            current_wear = self.current_data["tool_wear"]
            new_wear = min(100.0, current_wear + total_wear)
            
            self.current_data["tool_wear"] = new_wear
    
    def _calculate_power_consumption(self):
        """计算功耗"""
        speed = self.current_data["speed"]
        current = self.current_data["current"]
        
        # 简化的功耗计算（基于电流和转速）
        if speed == 0:
            power = 1.0  # 待机功耗
        else:
            # 机械功率 + 电气损耗
            mechanical_power = (speed / self.parameters.max_speed) * 50.0
            electrical_loss = current * 0.5
            power = mechanical_power + electrical_loss + 1.0
        
        self.current_data["power_consumption"] = power
    
    def _add_noise(self):
        """添加测量噪声"""
        noise_params = {
            "temperature": 0.5,
            "vibration": 0.1,
            "current": 0.2,
            "speed": 5.0,
            "pressure": 0.1,
            "power_consumption": 0.5
        }
        
        for param, noise_std in noise_params.items():
            if param in self.current_data:
                noise = random.gauss(0, noise_std * self.noise_level)
                self.current_data[param] += noise
                
                # 确保值在合理范围内
                if param == "temperature":
                    self.current_data[param] = max(15, min(100, self.current_data[param]))
                elif param == "vibration":
                    self.current_data[param] = max(0, min(15, self.current_data[param]))
                elif param == "current":
                    self.current_data[param] = max(0, min(70, self.current_data[param]))
                elif param == "speed":
                    self.current_data[param] = max(0, min(3500, self.current_data[param]))
                elif param == "pressure":
                    self.current_data[param] = max(0, min(15, self.current_data[param]))
                elif param == "power_consumption":
                    self.current_data[param] = max(0, min(120, self.current_data[param]))
    
    def set_target_speed(self, speed: float):
        """设置目标转速"""
        self.target_speed = max(0, min(self.parameters.max_speed, speed))
        if speed > 0:
            self.state = MachineState.RUNNING
        else:
            self.state = MachineState.IDLE
    
    def start_machine(self, speed: float = 1000.0):
        """启动机床"""
        self.set_target_speed(speed)
        self.state = MachineState.RUNNING
        logger.info(f"启动机床 {self.machine_id}，目标转速: {speed}")
    
    def stop_machine(self):
        """停止机床"""
        self.set_target_speed(0)
        self.state = MachineState.IDLE
        logger.info(f"停止机床 {self.machine_id}")
    
    def emergency_stop(self):
        """紧急停机"""
        self.target_speed = 0
        self.current_data["speed"] = 0
        self.state = MachineState.ERROR
        logger.warning(f"紧急停机 {self.machine_id}")
    
    def reset_tool_wear(self):
        """重置刀具磨损（换刀）"""
        self.current_data["tool_wear"] = 0.0
        logger.info(f"重置刀具磨损 {self.machine_id}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "machine_id": self.machine_id,
            "machine_type": self.machine_type,
            "state": self.state.value,
            "physics_state": asdict(self.physics_state),
            "current_data": self.current_data.copy(),
            "target_speed": self.target_speed,
            "parameters": asdict(self.parameters)
        }
    
    def get_health_score(self) -> float:
        """计算健康评分"""
        score = 100.0
        
        # 温度影响
        temp = self.current_data["temperature"]
        if temp > 80:
            score -= (temp - 80) * 2
        elif temp > 70:
            score -= (temp - 70) * 1
        
        # 振动影响
        vib = self.current_data["vibration"]
        if vib > 8:
            score -= (vib - 8) * 5
        elif vib > 5:
            score -= (vib - 5) * 2
        
        # 刀具磨损影响
        wear = self.current_data["tool_wear"]
        if wear > 80:
            score -= (wear - 80) * 1
        elif wear > 60:
            score -= (wear - 60) * 0.5
        
        return max(0.0, min(100.0, score))
    
    def predict_remaining_life(self) -> Optional[float]:
        """预测剩余寿命（小时）"""
        if self.state != MachineState.RUNNING:
            return None
        
        current_wear = self.current_data["tool_wear"]
        if current_wear >= 95:
            return 0.0
        
        # 基于当前磨损率预测
        remaining_wear = 95 - current_wear
        current_wear_rate = self.wear_rate * 60  # 每小时磨损率
        
        # 考虑当前工况影响
        speed_factor = (self.current_data["speed"] / self.parameters.max_speed) ** 1.5
        temp_factor = 1.0 + max(0, (self.current_data["temperature"] - 60) / 20)
        vib_factor = 1.0 + (self.current_data["vibration"] / 10) * 0.5
        
        effective_wear_rate = current_wear_rate * speed_factor * temp_factor * vib_factor
        
        if effective_wear_rate <= 0:
            return None
        
        remaining_hours = remaining_wear / effective_wear_rate
        return max(0.0, remaining_hours)
    
    async def update(self):
        """异步更新"""
        current_time = time.time()
        dt = current_time - self.last_update
        
        if dt >= self.dt:
            self.update_physics(dt)
            
            # 保存历史数据
            if len(self.history) >= self.max_history:
                self.history.pop(0)
            
            self.history.append({
                "timestamp": current_time,
                "data": self.current_data.copy()
            })
            
            self.last_update = current_time

class PurePythonTwinManager:
    """纯Python数字孪生管理器"""
    
    def __init__(self):
        self.twins: Dict[str, PurePythonTwin] = {}
        self.is_running = False
        self.update_task = None
        self.update_interval = 0.1  # 100ms
    
    async def create_twin(self, machine_id: str, machine_type: str) -> PurePythonTwin:
        """创建数字孪生"""
        if machine_id in self.twins:
            logger.warning(f"数字孪生 {machine_id} 已存在")
            return self.twins[machine_id]
        
        twin = PurePythonTwin(machine_id, machine_type)
        self.twins[machine_id] = twin
        
        logger.info(f"创建数字孪生: {machine_id}")
        return twin
    
    async def remove_twin(self, machine_id: str) -> bool:
        """移除数字孪生"""
        if machine_id in self.twins:
            del self.twins[machine_id]
            logger.info(f"移除数字孪生: {machine_id}")
            return True
        return False
    
    async def get_twin(self, machine_id: str) -> Optional[PurePythonTwin]:
        """获取数字孪生"""
        return self.twins.get(machine_id)
    
    async def get_twin_state(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """获取数字孪生状态"""
        twin = await self.get_twin(machine_id)
        if twin:
            return twin.get_current_state()
        return None
    
    async def start_all_twins(self):
        """启动所有数字孪生"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_task = asyncio.create_task(self._update_loop())
        logger.info("启动所有数字孪生")
    
    async def stop_all_twins(self):
        """停止所有数字孪生"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        logger.info("停止所有数字孪生")
    
    async def _update_loop(self):
        """更新循环"""
        while self.is_running:
            try:
                # 并行更新所有孪生
                update_tasks = [twin.update() for twin in self.twins.values()]
                if update_tasks:
                    await asyncio.gather(*update_tasks, return_exceptions=True)
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"数字孪生更新循环错误: {e}")
                await asyncio.sleep(1)
    
    def get_all_twins_status(self) -> Dict[str, Any]:
        """获取所有数字孪生状态"""
        return {
            "total_twins": len(self.twins),
            "is_running": self.is_running,
            "twins": {
                machine_id: twin.get_current_state()
                for machine_id, twin in self.twins.items()
            }
        }

# 全局数字孪生管理器实例
pure_python_twin_manager = PurePythonTwinManager()
