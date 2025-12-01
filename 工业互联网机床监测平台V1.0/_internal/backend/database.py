"""
工业互联网机床状态监测平台 - 数据库管理器
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import uuid

import asyncpg
import redis.asyncio as redis
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point
from loguru import logger

from config import settings, DATABASE_URL
from backend.models import (
    MachineData, MachineInfo, AlarmEvent, ControlCommand,
    DigitalTwinState, MachineStatus, AlarmLevel
)

class DatabaseManager:
    """数据库管理器 - 管理PostgreSQL、InfluxDB和Redis"""
    
    def __init__(self):
        self.postgres_pool = None
        self.influx_client = None
        self.redis_client = None
        self.is_initialized = False
    
    async def initialize(self):
        """初始化所有数据库连接"""
        try:
            logger.info("正在初始化数据库连接...")
            
            # 初始化PostgreSQL连接池
            await self._init_postgres()
            
            # 初始化InfluxDB客户端
            await self._init_influxdb()
            
            # 初始化Redis客户端
            await self._init_redis()
            
            # 创建数据库表
            await self._create_tables()
            
            self.is_initialized = True
            logger.success("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    async def close(self):
        """关闭所有数据库连接"""
        logger.info("正在关闭数据库连接...")
        
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.influx_client:
            await self.influx_client.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.is_initialized = False
        logger.info("数据库连接已关闭")
    
    def is_connected(self) -> bool:
        """检查数据库连接状态"""
        return self.is_initialized
    
    async def _init_postgres(self):
        """初始化PostgreSQL连接池"""
        try:
            self.postgres_pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("PostgreSQL连接池创建成功")
        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {e}")
            raise
    
    async def _init_influxdb(self):
        """初始化InfluxDB客户端"""
        try:
            self.influx_client = InfluxDBClientAsync(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG
            )
            
            # 测试连接
            health = await self.influx_client.health()
            if health.status == "pass":
                logger.info("InfluxDB连接成功")
            else:
                raise Exception(f"InfluxDB健康检查失败: {health.message}")
                
        except Exception as e:
            logger.error(f"InfluxDB连接失败: {e}")
            # InfluxDB连接失败不影响系统启动，只记录警告
            logger.warning("系统将在没有时序数据库的情况下运行")
            self.influx_client = None
    
    async def _init_redis(self):
        """初始化Redis客户端"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            # Redis连接失败不影响系统启动
            logger.warning("系统将在没有缓存的情况下运行")
            self.redis_client = None
    
    async def _create_tables(self):
        """创建PostgreSQL数据表"""
        async with self.postgres_pool.acquire() as conn:
            # 机床信息表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS machines (
                    machine_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    model VARCHAR(100),
                    manufacturer VARCHAR(100),
                    location VARCHAR(200),
                    installation_date TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'OFFLINE',
                    is_virtual BOOLEAN DEFAULT FALSE,
                    last_maintenance TIMESTAMP,
                    next_maintenance TIMESTAMP,
                    specifications JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 报警事件表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alarm_events (
                    alarm_id VARCHAR(50) PRIMARY KEY,
                    machine_id VARCHAR(50) REFERENCES machines(machine_id),
                    timestamp TIMESTAMP NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    parameter VARCHAR(50),
                    value FLOAT,
                    threshold FLOAT,
                    is_acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_by VARCHAR(100),
                    acknowledged_at TIMESTAMP,
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 控制命令表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS control_commands (
                    command_id VARCHAR(50) PRIMARY KEY,
                    machine_id VARCHAR(50) REFERENCES machines(machine_id),
                    timestamp TIMESTAMP NOT NULL,
                    command_type VARCHAR(50) NOT NULL,
                    parameters JSONB,
                    operator VARCHAR(100) NOT NULL,
                    status VARCHAR(20) DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 维护记录表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_records (
                    maintenance_id VARCHAR(50) PRIMARY KEY,
                    machine_id VARCHAR(50) REFERENCES machines(machine_id),
                    timestamp TIMESTAMP NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    description TEXT,
                    technician VARCHAR(100) NOT NULL,
                    duration FLOAT NOT NULL,
                    cost FLOAT,
                    parts_replaced JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_alarm_events_machine_id ON alarm_events(machine_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_alarm_events_timestamp ON alarm_events(timestamp)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_control_commands_machine_id ON control_commands(machine_id)")
            
            logger.info("PostgreSQL数据表创建完成")
    
    # 机床管理方法
    async def get_all_machines(self) -> List[Dict[str, Any]]:
        """获取所有机床信息"""
        async with self.postgres_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM machines ORDER BY name")
            return [dict(row) for row in rows]
    
    async def get_machine_info(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """获取指定机床信息"""
        async with self.postgres_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM machines WHERE machine_id = $1", machine_id)
            return dict(row) if row else None
    
    async def create_machine(self, machine_info: MachineInfo) -> bool:
        """创建机床记录"""
        try:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO machines (
                        machine_id, name, type, model, manufacturer, location,
                        installation_date, status, is_virtual, specifications
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                    machine_info.machine_id, machine_info.name, machine_info.type.value,
                    machine_info.model, machine_info.manufacturer, machine_info.location,
                    machine_info.installation_date, machine_info.status.value,
                    machine_info.is_virtual, json.dumps(machine_info.specifications)
                )
            return True
        except Exception as e:
            logger.error(f"创建机床记录失败: {e}")
            return False
    
    async def update_machine_status(self, machine_id: str, status: MachineStatus) -> bool:
        """更新机床状态"""
        try:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE machines SET status = $1, updated_at = CURRENT_TIMESTAMP 
                    WHERE machine_id = $2
                """, status.value, machine_id)
            
            # 缓存到Redis
            if self.redis_client:
                await self.redis_client.hset(
                    f"machine:{machine_id}:status", 
                    "status", status.value,
                    "timestamp", datetime.now().isoformat()
                )
            
            return True
        except Exception as e:
            logger.error(f"更新机床状态失败: {e}")
            return False
    
    async def get_machine_status(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """获取机床状态"""
        # 先从Redis缓存获取
        if self.redis_client:
            cached_status = await self.redis_client.hgetall(f"machine:{machine_id}:status")
            if cached_status:
                return cached_status
        
        # 从PostgreSQL获取
        async with self.postgres_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT machine_id, status, updated_at FROM machines WHERE machine_id = $1", 
                machine_id
            )
            return dict(row) if row else None
    
    # 时序数据管理方法
    async def store_machine_data(self, data: Dict[str, Any]) -> bool:
        """存储机床时序数据到InfluxDB"""
        if not self.influx_client:
            logger.warning("InfluxDB未连接，跳过时序数据存储")
            return False
        
        try:
            # 创建数据点
            point = Point("machine_data") \
                .tag("machine_id", data.get("machine_id")) \
                .field("temperature", float(data.get("temperature", 0))) \
                .field("vibration", float(data.get("vibration", 0))) \
                .field("current", float(data.get("current", 0))) \
                .field("speed", float(data.get("speed", 0))) \
                .field("pressure", float(data.get("pressure", 0)))
            
            # 添加可选字段
            if "position_x" in data:
                point = point.field("position_x", float(data["position_x"]))
            if "position_y" in data:
                point = point.field("position_y", float(data["position_y"]))
            if "position_z" in data:
                point = point.field("position_z", float(data["position_z"]))
            if "tool_wear" in data:
                point = point.field("tool_wear", float(data["tool_wear"]))
            if "power_consumption" in data:
                point = point.field("power_consumption", float(data["power_consumption"]))
            
            # 设置时间戳
            if "timestamp" in data:
                point = point.time(data["timestamp"])
            
            # 写入数据
            write_api = self.influx_client.write_api()
            await write_api.write(bucket=settings.INFLUXDB_BUCKET, record=point)
            
            return True
            
        except Exception as e:
            logger.error(f"存储时序数据失败: {e}")
            return False
    
    async def get_machine_data(self, machine_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取机床历史数据"""
        if not self.influx_client:
            return []
        
        try:
            query = f'''
                from(bucket: "{settings.INFLUXDB_BUCKET}")
                |> range(start: -24h)
                |> filter(fn: (r) => r["_measurement"] == "machine_data")
                |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
                |> limit(n: {limit})
                |> sort(columns: ["_time"], desc: true)
            '''
            
            query_api = self.influx_client.query_api()
            tables = await query_api.query(query)
            
            data = []
            for table in tables:
                for record in table.records:
                    data.append({
                        "timestamp": record.get_time().isoformat(),
                        "machine_id": record.values.get("machine_id"),
                        "field": record.get_field(),
                        "value": record.get_value()
                    })
            
            return data
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return []
    
    # 报警管理方法
    async def store_alarm(self, alarm: AlarmEvent) -> bool:
        """存储报警事件"""
        try:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO alarm_events (
                        alarm_id, machine_id, timestamp, level, type, message,
                        parameter, value, threshold
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    alarm.alarm_id, alarm.machine_id, alarm.timestamp,
                    alarm.level.value, alarm.type, alarm.message,
                    alarm.parameter, alarm.value, alarm.threshold
                )
            
            # 缓存最新报警到Redis
            if self.redis_client:
                await self.redis_client.lpush(
                    f"machine:{alarm.machine_id}:alarms",
                    json.dumps(alarm.dict(), default=str)
                )
                # 只保留最近100条报警
                await self.redis_client.ltrim(f"machine:{alarm.machine_id}:alarms", 0, 99)
            
            return True
            
        except Exception as e:
            logger.error(f"存储报警事件失败: {e}")
            return False
    
    async def get_alarms(self, limit: int = 50, machine_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取报警事件"""
        try:
            async with self.postgres_pool.acquire() as conn:
                if machine_id:
                    rows = await conn.fetch("""
                        SELECT * FROM alarm_events 
                        WHERE machine_id = $1 
                        ORDER BY timestamp DESC 
                        LIMIT $2
                    """, machine_id, limit)
                else:
                    rows = await conn.fetch("""
                        SELECT * FROM alarm_events 
                        ORDER BY timestamp DESC 
                        LIMIT $1
                    """, limit)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"获取报警事件失败: {e}")
            return []
    
    async def acknowledge_alarm(self, alarm_id: str, acknowledged_by: str) -> bool:
        """确认报警"""
        try:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE alarm_events 
                    SET is_acknowledged = TRUE, acknowledged_by = $1, acknowledged_at = CURRENT_TIMESTAMP
                    WHERE alarm_id = $2
                """, acknowledged_by, alarm_id)
            return True
        except Exception as e:
            logger.error(f"确认报警失败: {e}")
            return False
    
    # 控制命令管理方法
    async def log_control_command(self, machine_id: str, command: Dict[str, Any]) -> bool:
        """记录控制命令"""
        try:
            command_id = str(uuid.uuid4())
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO control_commands (
                        command_id, machine_id, timestamp, command_type, parameters, operator
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                    command_id, machine_id, datetime.now(),
                    command.get("type", "unknown"), json.dumps(command),
                    command.get("operator", "system")
                )
            return True
        except Exception as e:
            logger.error(f"记录控制命令失败: {e}")
            return False
    
    # 缓存管理方法
    async def cache_set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        if not self.redis_client:
            return False
        
        try:
            if isinstance(value, dict):
                value = json.dumps(value, default=str)
            await self.redis_client.setex(key, expire, value)
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    async def cache_delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    # 统计分析方法
    async def get_machine_statistics(self, machine_id: str, hours: int = 24) -> Dict[str, Any]:
        """获取机床统计信息"""
        stats = {
            "machine_id": machine_id,
            "period_hours": hours,
            "data_points": 0,
            "alarms_count": 0,
            "avg_temperature": 0,
            "avg_vibration": 0,
            "max_current": 0,
            "uptime_percentage": 0
        }
        
        try:
            # 从InfluxDB获取统计数据
            if self.influx_client:
                query = f'''
                    from(bucket: "{settings.INFLUXDB_BUCKET}")
                    |> range(start: -{hours}h)
                    |> filter(fn: (r) => r["_measurement"] == "machine_data")
                    |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
                    |> group(columns: ["_field"])
                    |> mean()
                '''
                
                query_api = self.influx_client.query_api()
                tables = await query_api.query(query)
                
                for table in tables:
                    for record in table.records:
                        field = record.get_field()
                        value = record.get_value()
                        if field == "temperature":
                            stats["avg_temperature"] = round(value, 2)
                        elif field == "vibration":
                            stats["avg_vibration"] = round(value, 2)
                        elif field == "current":
                            stats["max_current"] = round(value, 2)
            
            # 从PostgreSQL获取报警统计
            async with self.postgres_pool.acquire() as conn:
                alarm_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM alarm_events 
                    WHERE machine_id = $1 AND timestamp > $2
                """, machine_id, datetime.now() - timedelta(hours=hours))
                
                stats["alarms_count"] = alarm_count or 0
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return stats
