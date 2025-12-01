"""
工业互联网机床状态监测平台 - 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MachineType(str, Enum):
    """机床类型枚举"""
    CNC_LATHE = "CNC_LATHE"
    MILLING_MACHINE = "MILLING_MACHINE"
    DRILLING_MACHINE = "DRILLING_MACHINE"
    GRINDING_MACHINE = "GRINDING_MACHINE"

class MachineStatus(str, Enum):
    """机床状态枚举"""
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"

class AlarmLevel(str, Enum):
    """报警级别枚举"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class MachineData(BaseModel):
    """机床数据模型"""
    machine_id: str = Field(..., description="机床ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    temperature: float = Field(..., ge=0, le=200, description="温度(°C)")
    vibration: float = Field(..., ge=0, le=50, description="振动(mm/s)")
    current: float = Field(..., ge=0, le=100, description="电流(A)")
    speed: float = Field(..., ge=0, le=5000, description="转速(rpm)")
    pressure: float = Field(..., ge=0, le=20, description="压力(bar)")
    position_x: Optional[float] = Field(None, description="X轴位置(mm)")
    position_y: Optional[float] = Field(None, description="Y轴位置(mm)")
    position_z: Optional[float] = Field(None, description="Z轴位置(mm)")
    tool_wear: Optional[float] = Field(None, ge=0, le=100, description="刀具磨损(%)")
    power_consumption: Optional[float] = Field(None, ge=0, description="功耗(kW)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MachineInfo(BaseModel):
    """机床信息模型"""
    machine_id: str = Field(..., description="机床ID")
    name: str = Field(..., description="机床名称")
    type: MachineType = Field(..., description="机床类型")
    model: str = Field(..., description="机床型号")
    manufacturer: str = Field(..., description="制造商")
    location: str = Field(..., description="位置")
    installation_date: datetime = Field(..., description="安装日期")
    status: MachineStatus = Field(default=MachineStatus.OFFLINE, description="当前状态")
    is_virtual: bool = Field(default=False, description="是否为虚拟设备")
    last_maintenance: Optional[datetime] = Field(None, description="上次维护时间")
    next_maintenance: Optional[datetime] = Field(None, description="下次维护时间")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="技术规格")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AlarmEvent(BaseModel):
    """报警事件模型"""
    alarm_id: str = Field(..., description="报警ID")
    machine_id: str = Field(..., description="机床ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="报警时间")
    level: AlarmLevel = Field(..., description="报警级别")
    type: str = Field(..., description="报警类型")
    message: str = Field(..., description="报警消息")
    parameter: str = Field(..., description="相关参数")
    value: float = Field(..., description="参数值")
    threshold: float = Field(..., description="阈值")
    is_acknowledged: bool = Field(default=False, description="是否已确认")
    acknowledged_by: Optional[str] = Field(None, description="确认人")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    is_resolved: bool = Field(default=False, description="是否已解决")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ControlCommand(BaseModel):
    """控制命令模型"""
    command_id: str = Field(..., description="命令ID")
    machine_id: str = Field(..., description="机床ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="命令时间")
    command_type: str = Field(..., description="命令类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="命令参数")
    operator: str = Field(..., description="操作员")
    status: str = Field(default="PENDING", description="执行状态")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DigitalTwinState(BaseModel):
    """数字孪生状态模型"""
    machine_id: str = Field(..., description="机床ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    physics_state: Dict[str, Any] = Field(default_factory=dict, description="物理状态")
    simulation_parameters: Dict[str, Any] = Field(default_factory=dict, description="仿真参数")
    predicted_values: Dict[str, float] = Field(default_factory=dict, description="预测值")
    health_score: float = Field(..., ge=0, le=100, description="健康评分")
    remaining_life: Optional[float] = Field(None, description="剩余寿命(小时)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProductionOrder(BaseModel):
    """生产订单模型"""
    order_id: str = Field(..., description="订单ID")
    machine_id: str = Field(..., description="机床ID")
    product_name: str = Field(..., description="产品名称")
    quantity: int = Field(..., gt=0, description="数量")
    start_time: datetime = Field(..., description="开始时间")
    estimated_end_time: datetime = Field(..., description="预计结束时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    status: str = Field(default="PENDING", description="订单状态")
    progress: float = Field(default=0.0, ge=0, le=100, description="完成进度(%)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QualityData(BaseModel):
    """质量数据模型"""
    quality_id: str = Field(..., description="质量记录ID")
    machine_id: str = Field(..., description="机床ID")
    order_id: str = Field(..., description="订单ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="检测时间")
    dimensions: Dict[str, float] = Field(default_factory=dict, description="尺寸数据")
    surface_roughness: Optional[float] = Field(None, description="表面粗糙度")
    hardness: Optional[float] = Field(None, description="硬度")
    is_qualified: bool = Field(..., description="是否合格")
    defect_types: List[str] = Field(default_factory=list, description="缺陷类型")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MaintenanceRecord(BaseModel):
    """维护记录模型"""
    maintenance_id: str = Field(..., description="维护记录ID")
    machine_id: str = Field(..., description="机床ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="维护时间")
    type: str = Field(..., description="维护类型")
    description: str = Field(..., description="维护描述")
    technician: str = Field(..., description="技术员")
    duration: float = Field(..., gt=0, description="维护时长(小时)")
    cost: Optional[float] = Field(None, description="维护成本")
    parts_replaced: List[str] = Field(default_factory=list, description="更换部件")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EnergyData(BaseModel):
    """能耗数据模型"""
    machine_id: str = Field(..., description="机床ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    power_consumption: float = Field(..., ge=0, description="功耗(kW)")
    energy_efficiency: float = Field(..., ge=0, le=100, description="能效(%)")
    carbon_emission: float = Field(..., ge=0, description="碳排放(kg)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 响应模型
class APIResponse(BaseModel):
    """API响应基础模型"""
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(default_factory=list, description="数据项")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    size: int = Field(default=10, description="每页大小")
    pages: int = Field(default=0, description="总页数")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.total > 0 and self.size > 0:
            self.pages = (self.total + self.size - 1) // self.size
