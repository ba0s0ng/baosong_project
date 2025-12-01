from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# 设备模型
class MachineBase(BaseModel):
    name: str
    type: str
    model: Optional[str] = None
    location: Optional[str] = None
    status: str = "offline"

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class Machine(MachineBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 设备数据模型 - 更新为新的字段结构
class MachineDataBase(BaseModel):
    machine_id: int
    temperature: Optional[float] = None
    vibration: Optional[float] = None
    noise: Optional[float] = None
    power_consumption: Optional[float] = None
    operating_hours: Optional[float] = None

class MachineDataCreate(MachineDataBase):
    pass

class MachineData(MachineDataBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# 报警模型 - 移除level字段
class AlarmBase(BaseModel):
    machine_id: int
    type: str
    message: str

class AlarmCreate(AlarmBase):
    pass

class AlarmUpdate(BaseModel):
    is_handled: Optional[bool] = None
    handled_by: Optional[str] = None
    handled_at: Optional[datetime] = None

class Alarm(AlarmBase):
    id: int
    timestamp: datetime
    is_handled: bool = False
    handled_by: Optional[str] = None
    handled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 报警规则模型 - 将operator改为comparison，移除level和message字段
class AlarmRuleBase(BaseModel):
    name: str
    parameter: str
    comparison: str
    threshold: float
    is_active: bool = True

class AlarmRuleCreate(AlarmRuleBase):
    pass

class AlarmRuleUpdate(BaseModel):
    name: Optional[str] = None
    parameter: Optional[str] = None
    comparison: Optional[str] = None
    threshold: Optional[float] = None
    is_active: Optional[bool] = None

class AlarmRule(AlarmRuleBase):
    id: int
    
    class Config:
        from_attributes = True

# 维护记录模型
class MaintenanceRecordBase(BaseModel):
    machine_id: int
    maintenance_type: str
    description: Optional[str] = None
    performed_by: Optional[str] = None
    status: str = "pending"

class MaintenanceRecordCreate(MaintenanceRecordBase):
    pass

class MaintenanceRecordUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    performed_by: Optional[str] = None
    status: Optional[str] = None

class MaintenanceRecord(MaintenanceRecordBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 仪表盘数据模型
class DashboardData(BaseModel):
    total_machines: int
    online_machines: int
    offline_machines: int
    total_alarms: int
    active_alarms: int
    high_priority_alarms: int
    recent_data: List[MachineData] = []

# 趋势数据模型
class TrendData(BaseModel):
    parameter: str
    machine_id: int
    timestamps: List[datetime]
    values: List[float]

# 统计数据模型
class MachineStatistics(BaseModel):
    machine_id: int
    machine_name: str
    avg_temperature: float
    max_temperature: float
    avg_vibration: float
    max_vibration: float
    total_alarms: int
    uptime_percentage: float