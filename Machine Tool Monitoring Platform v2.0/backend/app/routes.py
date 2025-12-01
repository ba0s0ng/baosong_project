from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta

from .db import fetch_all, fetch_one, execute_query
from .schemas import (
    Machine, MachineCreate, MachineUpdate,
    MachineData, MachineDataCreate,
    Alarm, AlarmCreate, AlarmUpdate,
    AlarmRule, AlarmRuleCreate, AlarmRuleUpdate,
    MaintenanceRecord, MaintenanceRecordCreate, MaintenanceRecordUpdate,
    DashboardData, TrendData, MachineStatistics
)

router = APIRouter()

# 设备管理接口
@router.get("/machines", response_model=List[Machine])
def get_machines():
    """获取所有设备列表"""
    machines = fetch_all("SELECT * FROM machines")
    return machines

@router.get("/machines/{machine_id}", response_model=Machine)
def get_machine(machine_id: int):
    """获取单个设备详情"""
    machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    if not machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    return machine

@router.post("/machines", response_model=Machine)
def create_machine(machine: MachineCreate):
    """创建设备"""
    cursor = execute_query(
        "INSERT INTO machines (name, type, model, location, status) VALUES (?, ?, ?, ?, ?)",
        (machine.name, machine.type, machine.model, machine.location, machine.status)
    )
    new_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (cursor.lastrowid,))
    return new_machine

@router.put("/machines/{machine_id}", response_model=Machine)
def update_machine(machine_id: int, machine_update: MachineUpdate):
    """更新设备信息"""
    # 检查设备是否存在
    existing_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    if not existing_machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    # 构建更新字段
    update_fields = []
    update_values = []
    
    if machine_update.name is not None:
        update_fields.append("name = ?")
        update_values.append(machine_update.name)
    if machine_update.type is not None:
        update_fields.append("type = ?")
        update_values.append(machine_update.type)
    if machine_update.model is not None:
        update_fields.append("model = ?")
        update_values.append(machine_update.model)
    if machine_update.location is not None:
        update_fields.append("location = ?")
        update_values.append(machine_update.location)
    if machine_update.status is not None:
        update_fields.append("status = ?")
        update_values.append(machine_update.status)
    
    # 添加更新时间
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    
    # 构建更新SQL
    update_sql = f"UPDATE machines SET {', '.join(update_fields)} WHERE id = ?"
    update_values.append(machine_id)
    
    # 执行更新
    execute_query(update_sql, update_values)
    
    # 返回更新后的设备
    updated_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    return updated_machine

@router.delete("/machines/{machine_id}")
def delete_machine(machine_id: int):
    """删除设备"""
    # 检查设备是否存在
    existing_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    if not existing_machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    # 执行删除
    execute_query("DELETE FROM machines WHERE id = ?", (machine_id,))
    
    return {"message": "设备已成功删除"}

# 设备数据接口
@router.get("/machines/{machine_id}/data", response_model=List[MachineData])
def get_machine_data(
    machine_id: int,
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """获取设备数据"""
    # 构建查询
    query = "SELECT * FROM machine_data WHERE machine_id = ?"
    params = [machine_id]
    
    if start_time:
        query += " AND timestamp >= ?"
        params.append(start_time)
    if end_time:
        query += " AND timestamp <= ?"
        params.append(end_time)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    data = fetch_all(query, params)
    return data

@router.post("/machines/{machine_id}/data", response_model=MachineData)
def create_machine_data(machine_id: int, data: MachineDataCreate):
    """添加设备数据"""
    # 检查设备是否存在
    existing_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    if not existing_machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    cursor = execute_query(
        """INSERT INTO machine_data 
        (machine_id, temperature, vibration, noise, power_consumption, operating_hours, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
        (machine_id, data.temperature, data.vibration, data.noise or 0, 
         data.power_consumption or 0, data.operating_hours or 0)
    )
    
    new_data = fetch_one("SELECT * FROM machine_data WHERE id = ?", (cursor.lastrowid,))
    return new_data

# 报警接口
@router.get("/alarms", response_model=List[Alarm])
def get_alarms(
    machine_id: Optional[int] = None,
    is_handled: Optional[bool] = None,
    limit: int = 100
):
    """获取报警列表"""
    # 构建查询
    query = "SELECT * FROM alarms WHERE 1=1"
    params = []
    
    if machine_id:
        query += " AND machine_id = ?"
        params.append(machine_id)
    if is_handled is not None:
        query += " AND is_handled = ?"
        params.append(is_handled)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    alarms = fetch_all(query, params)
    return alarms

@router.put("/alarms/{alarm_id}", response_model=Alarm)
def update_alarm(alarm_id: int, alarm_update: AlarmUpdate):
    """更新报警状态"""
    # 检查报警是否存在
    existing_alarm = fetch_one("SELECT * FROM alarms WHERE id = ?", (alarm_id,))
    if not existing_alarm:
        raise HTTPException(status_code=404, detail="报警未找到")
    
    # 构建更新字段
    update_fields = []
    update_values = []
    
    if alarm_update.is_handled is not None:
        update_fields.append("is_handled = ?")
        update_values.append(alarm_update.is_handled)
        if alarm_update.is_handled and not existing_alarm['is_handled']:
            update_fields.append("handled_at = CURRENT_TIMESTAMP")
    if alarm_update.handled_by is not None:
        update_fields.append("handled_by = ?")
        update_values.append(alarm_update.handled_by)
    if alarm_update.handled_at is not None:
        update_fields.append("handled_at = ?")
        update_values.append(alarm_update.handled_at)
    
    # 构建更新SQL
    update_sql = f"UPDATE alarms SET {', '.join(update_fields)} WHERE id = ?"
    update_values.append(alarm_id)
    
    # 执行更新
    execute_query(update_sql, update_values)
    
    # 返回更新后的报警
    updated_alarm = fetch_one("SELECT * FROM alarms WHERE id = ?", (alarm_id,))
    return updated_alarm

# 报警规则接口
@router.get("/alarm-rules", response_model=List[AlarmRule])
def get_alarm_rules(is_active: Optional[bool] = None):
    """获取报警规则列表"""
    query = "SELECT * FROM alarm_rules WHERE 1=1"
    params = []
    
    if is_active is not None:
        query += " AND is_active = ?"
        params.append(is_active)
    
    rules = fetch_all(query, params)
    return rules

@router.post("/alarm-rules", response_model=AlarmRule)
def create_alarm_rule(rule: AlarmRuleCreate):
    """创建报警规则"""
    cursor = execute_query(
        """INSERT INTO alarm_rules 
        (name, parameter, threshold, comparison, is_active) 
        VALUES (?, ?, ?, ?, ?)""",
        (rule.name, rule.parameter, rule.threshold, rule.comparison, rule.is_active)
    )
    
    new_rule = fetch_one("SELECT * FROM alarm_rules WHERE id = ?", (cursor.lastrowid,))
    return new_rule

@router.put("/alarm-rules/{rule_id}", response_model=AlarmRule)
def update_alarm_rule(rule_id: int, rule_update: AlarmRuleUpdate):
    """更新报警规则"""
    # 检查规则是否存在
    existing_rule = fetch_one("SELECT * FROM alarm_rules WHERE id = ?", (rule_id,))
    if not existing_rule:
        raise HTTPException(status_code=404, detail="报警规则未找到")
    
    # 构建更新字段
    update_fields = []
    update_values = []
    
    if rule_update.name is not None:
        update_fields.append("name = ?")
        update_values.append(rule_update.name)
    if rule_update.parameter is not None:
        update_fields.append("parameter = ?")
        update_values.append(rule_update.parameter)
    if rule_update.comparison is not None:
        update_fields.append("comparison = ?")
        update_values.append(rule_update.comparison)
    if rule_update.threshold is not None:
        update_fields.append("threshold = ?")
        update_values.append(rule_update.threshold)
    if rule_update.is_active is not None:
        update_fields.append("is_active = ?")
        update_values.append(rule_update.is_active)
    
    # 构建更新SQL
    update_sql = f"UPDATE alarm_rules SET {', '.join(update_fields)} WHERE id = ?"
    update_values.append(rule_id)
    
    # 执行更新
    execute_query(update_sql, update_values)
    
    # 返回更新后的规则
    updated_rule = fetch_one("SELECT * FROM alarm_rules WHERE id = ?", (rule_id,))
    return updated_rule

@router.delete("/alarm-rules/{rule_id}")
def delete_alarm_rule(rule_id: int):
    """删除报警规则"""
    # 检查规则是否存在
    existing_rule = fetch_one("SELECT * FROM alarm_rules WHERE id = ?", (rule_id,))
    if not existing_rule:
        raise HTTPException(status_code=404, detail="报警规则未找到")
    
    # 执行删除
    execute_query("DELETE FROM alarm_rules WHERE id = ?", (rule_id,))
    
    return {"message": "报警规则已成功删除"}

# 维护记录接口
@router.get("/maintenance", response_model=List[MaintenanceRecord])
def get_maintenance_records(
    machine_id: Optional[int] = None,
    status: Optional[str] = None
):
    """获取维护记录列表"""
    query = "SELECT * FROM maintenance_records WHERE 1=1"
    params = []
    
    if machine_id:
        query += " AND machine_id = ?"
        params.append(machine_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY start_time DESC"
    
    records = fetch_all(query, params)
    return records

@router.post("/maintenance", response_model=MaintenanceRecord)
def create_maintenance_record(record: MaintenanceRecordCreate):
    """创建维护记录"""
    # 检查设备是否存在
    existing_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (record.machine_id,))
    if not existing_machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    cursor = execute_query(
        """INSERT INTO maintenance_records 
        (machine_id, maintenance_type, description, performed_by, status) 
        VALUES (?, ?, ?, ?, ?)""",
        (record.machine_id, record.maintenance_type, record.description, 
         record.performed_by, record.status)
    )
    
    new_record = fetch_one("SELECT * FROM maintenance_records WHERE id = ?", (cursor.lastrowid,))
    return new_record

@router.put("/maintenance/{record_id}", response_model=MaintenanceRecord)
def update_maintenance_record(record_id: int, record_update: MaintenanceRecordUpdate):
    """更新维护记录"""
    # 检查记录是否存在
    existing_record = fetch_one("SELECT * FROM maintenance_records WHERE id = ?", (record_id,))
    if not existing_record:
        raise HTTPException(status_code=404, detail="维护记录未找到")
    
    # 构建更新字段
    update_fields = []
    update_values = []
    
    if record_update.maintenance_type is not None:
        update_fields.append("maintenance_type = ?")
        update_values.append(record_update.maintenance_type)
    if record_update.description is not None:
        update_fields.append("description = ?")
        update_values.append(record_update.description)
    if record_update.start_time is not None:
        update_fields.append("start_time = ?")
        update_values.append(record_update.start_time)
    if record_update.end_time is not None:
        update_fields.append("end_time = ?")
        update_values.append(record_update.end_time)
    if record_update.performed_by is not None:
        update_fields.append("performed_by = ?")
        update_values.append(record_update.performed_by)
    if record_update.status is not None:
        update_fields.append("status = ?")
        update_values.append(record_update.status)
    
    # 构建更新SQL
    update_sql = f"UPDATE maintenance_records SET {', '.join(update_fields)} WHERE id = ?"
    update_values.append(record_id)
    
    # 执行更新
    execute_query(update_sql, update_values)
    
    # 返回更新后的记录
    updated_record = fetch_one("SELECT * FROM maintenance_records WHERE id = ?", (record_id,))
    return updated_record

# 仪表盘数据接口
@router.get("/dashboard", response_model=DashboardData)
def get_dashboard_data():
    """获取仪表盘数据"""
    # 获取设备统计
    total_machines = fetch_one("SELECT COUNT(*) as count FROM machines")['count']
    online_machines = fetch_one("SELECT COUNT(*) as count FROM machines WHERE status = 'online'")['count']
    offline_machines = total_machines - online_machines
    
    # 获取报警统计
    total_alarms = fetch_one("SELECT COUNT(*) as count FROM alarms")['count']
    active_alarms = fetch_one("SELECT COUNT(*) as count FROM alarms WHERE is_handled = FALSE")['count']
    # 计算高优先级报警（基于温度>70, 振动>4等条件）
    high_priority_alarms = fetch_one(
        "SELECT COUNT(*) as count FROM alarms WHERE message LIKE '%temperature > 70%' OR message LIKE '%vibration > 4%'")['count']
    
    # 获取最近的设备数据
    recent_data = fetch_all(
        """SELECT md.* FROM machine_data md
        JOIN machines m ON md.machine_id = m.id
        WHERE m.status = 'online'
        ORDER BY md.timestamp DESC
        LIMIT 20"""
    )
    
    return DashboardData(
        total_machines=total_machines,
        online_machines=online_machines,
        offline_machines=offline_machines,
        total_alarms=total_alarms,
        active_alarms=active_alarms,
        high_priority_alarms=high_priority_alarms,
        recent_data=recent_data
    )

# 趋势数据接口
@router.get("/machines/{machine_id}/trends/{parameter}", response_model=TrendData)
def get_trend_data(
    machine_id: int,
    parameter: str,
    hours: int = 24
):
    """获取设备参数趋势数据"""
    # 检查设备是否存在
    existing_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    if not existing_machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    # 检查参数是否有效
    valid_parameters = ['temperature', 'vibration', 'noise', 'power_consumption', 'operating_hours']
    if parameter not in valid_parameters:
        raise HTTPException(status_code=400, detail=f"无效的参数类型，有效值为: {', '.join(valid_parameters)}")
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # 查询趋势数据
    data = fetch_all(
        f"""SELECT timestamp, {parameter} FROM machine_data 
        WHERE machine_id = ? AND timestamp BETWEEN ? AND ? 
        ORDER BY timestamp ASC""",
        (machine_id, start_time, end_time)
    )
    
    # 提取时间戳和值
    timestamps = [item['timestamp'] for item in data]
    values = [item[parameter] for item in data]
    
    return TrendData(
        parameter=parameter,
        machine_id=machine_id,
        timestamps=timestamps,
        values=values
    )

# 统计数据接口
@router.get("/machines/{machine_id}/statistics", response_model=MachineStatistics)
def get_machine_statistics(machine_id: int, days: int = 7):
    """获取设备统计数据"""
    # 检查设备是否存在
    existing_machine = fetch_one("SELECT * FROM machines WHERE id = ?", (machine_id,))
    if not existing_machine:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # 查询统计数据
    stats = fetch_one(
        """SELECT 
            AVG(temperature) as avg_temperature,
            MAX(temperature) as max_temperature,
            AVG(vibration) as avg_vibration,
            MAX(vibration) as max_vibration
        FROM machine_data 
        WHERE machine_id = ? AND timestamp BETWEEN ? AND ?""",
        (machine_id, start_time, end_time)
    )
    
    # 查询报警数量
    alarm_count = fetch_one(
        "SELECT COUNT(*) as count FROM alarms WHERE machine_id = ? AND timestamp BETWEEN ? AND ?",
        (machine_id, start_time, end_time)
    )['count']
    
    # 计算在线时间百分比（简化计算，实际应该基于状态变化记录）
    uptime_percentage = 95.0 if existing_machine['status'] == 'online' else 45.0
    
    return MachineStatistics(
        machine_id=machine_id,
        machine_name=existing_machine['name'],
        avg_temperature=float(stats['avg_temperature'] or 0),
        max_temperature=float(stats['max_temperature'] or 0),
        avg_vibration=float(stats['avg_vibration'] or 0),
        max_vibration=float(stats['max_vibration'] or 0),
        total_alarms=alarm_count,
        uptime_percentage=uptime_percentage
    )