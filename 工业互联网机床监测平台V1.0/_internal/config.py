"""
工业互联网机床状态监测平台配置文件
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any

class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "工业互联网机床状态监测平台"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # FastAPI配置
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    
    # Django Channels配置
    CHANNELS_HOST: str = "0.0.0.0"
    CHANNELS_PORT: int = 8001
    ASGI_APPLICATION: str = "backend.asgi.application"
    
    # MQTT配置 - 支持EMQX集群
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_BROKER_WS_PORT: int = 8083
    MQTT_BROKER_WSS_PORT: int = 8084
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_KEEPALIVE: int = 60
    MQTT_QOS: int = 1
    MQTT_RETAIN: bool = False
    MQTT_CLEAN_SESSION: bool = True
    
    # 数据库配置
    # PostgreSQL - 关系型数据
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "industrial_iot"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 30
    
    # InfluxDB - 时序数据
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "industrial-iot-token"
    INFLUXDB_ORG: str = "industrial-iot"
    INFLUXDB_BUCKET: str = "machine-data"
    INFLUXDB_RETENTION_POLICY: str = "30d"
    
    # Redis配置 - 缓存和会话
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_POOL_SIZE: int = 10
    REDIS_CACHE_TTL: int = 3600  # 1小时
    
    # Kafka配置 - 流处理
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["localhost:9092"]
    KAFKA_TOPIC_MACHINE_DATA: str = "machine-data"
    KAFKA_TOPIC_ALARMS: str = "alarms"
    KAFKA_TOPIC_EVENTS: str = "events"
    KAFKA_CONSUMER_GROUP: str = "industrial-iot-group"
    
    # WebSocket配置
    WEBSOCKET_HOST: str = "localhost"
    WEBSOCKET_PORT: int = 8001
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    
    # 规则引擎配置
    RULE_ENGINE_TYPE: str = "custom"  # custom, drools
    RULE_ENGINE_RESPONSE_TIME: float = 2.0  # 响应时间要求 < 2秒
    RULE_ENGINE_MAX_THREADS: int = 10
    RULE_ENGINE_BATCH_SIZE: int = 100
    DROOLS_JVM_ARGS: List[str] = ["-Xmx2g", "-Xms1g"]
    
    # 数字孪生配置
    DIGITAL_TWIN_UPDATE_INTERVAL: float = 0.1  # 100ms更新间隔
    DIGITAL_TWIN_PHYSICS_ENGINE: str = "pymunk"  # pymunk, pybullet
    PHYSICS_ENGINE_GRAVITY: tuple = (0, -981)  # 重力加速度
    DIGITAL_TWIN_PREDICTION_HORIZON: int = 3600  # 预测时间窗口(秒)
    
    # 流处理配置
    STREAM_PROCESSING_ENGINE: str = "flink"  # flink, kafka_streams
    FLINK_JOBMANAGER_HOST: str = "localhost"
    FLINK_JOBMANAGER_PORT: int = 8081
    FLINK_PARALLELISM: int = 4
    FLINK_CHECKPOINT_INTERVAL: int = 60000  # 60秒
    
    # 机床设备配置
    MACHINE_TYPES: Dict[str, Dict[str, Any]] = {
        "CNC_LATHE": {
            "name": "数控车床",
            "max_speed": 3000,
            "max_temperature": 80,
            "max_vibration": 10,
            "max_current": 50,
            "max_pressure": 10
        },
        "MILLING_MACHINE": {
            "name": "铣床",
            "max_speed": 2500,
            "max_temperature": 75,
            "max_vibration": 8,
            "max_current": 45,
            "max_pressure": 8
        },
        "DRILLING_MACHINE": {
            "name": "钻床",
            "max_speed": 2000,
            "max_temperature": 70,
            "max_vibration": 6,
            "max_current": 40,
            "max_pressure": 6
        },
        "GRINDING_MACHINE": {
            "name": "磨床",
            "max_speed": 1800,
            "max_temperature": 85,
            "max_vibration": 12,
            "max_current": 55,
            "max_pressure": 12
        }
    }
    
    # 监测参数配置
    MONITORING_PARAMETERS: Dict[str, Dict[str, Any]] = {
        "temperature": {
            "min": 20, "max": 80, "unit": "°C",
            "warning_threshold": 70, "critical_threshold": 85,
            "sampling_rate": 1.0  # 每秒采样
        },
        "vibration": {
            "min": 0, "max": 10, "unit": "mm/s",
            "warning_threshold": 8, "critical_threshold": 12,
            "sampling_rate": 10.0  # 每秒10次采样
        },
        "current": {
            "min": 0, "max": 50, "unit": "A",
            "warning_threshold": 45, "critical_threshold": 55,
            "sampling_rate": 1.0
        },
        "speed": {
            "min": 0, "max": 3000, "unit": "rpm",
            "warning_threshold": 2800, "critical_threshold": 3200,
            "sampling_rate": 1.0
        },
        "pressure": {
            "min": 0, "max": 10, "unit": "bar",
            "warning_threshold": 9, "critical_threshold": 12,
            "sampling_rate": 1.0
        },
        "tool_wear": {
            "min": 0, "max": 100, "unit": "%",
            "warning_threshold": 80, "critical_threshold": 95,
            "sampling_rate": 0.1  # 每10秒采样
        },
        "power_consumption": {
            "min": 0, "max": 100, "unit": "kW",
            "warning_threshold": 90, "critical_threshold": 110,
            "sampling_rate": 1.0
        }
    }
    
    # 报警配置
    ALARM_LEVELS: Dict[str, int] = {
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4
    }
    
    ALARM_RESPONSE_ACTIONS: Dict[str, List[str]] = {
        "CRITICAL": ["stop_machine", "send_sms", "send_email", "trigger_alarm"],
        "ERROR": ["send_email", "trigger_alarm"],
        "WARNING": ["send_notification"],
        "INFO": ["log_event"]
    }
    
    # 机器学习配置
    ML_MODEL_UPDATE_INTERVAL: int = 3600  # 1小时更新一次模型
    ML_PREDICTION_MODELS: Dict[str, str] = {
        "temperature": "lstm",
        "vibration": "arima",
        "tool_wear": "xgboost",
        "failure_prediction": "random_forest"
    }
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # API限流配置
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 200
    
    # 监控配置
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    METRICS_EXPORT_INTERVAL: int = 15  # 15秒导出一次指标
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/industrial_iot.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    
    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".json", ".xml", ".txt"]
    
    # 3D可视化配置
    THREEJS_VERSION: str = "r158"
    WEBGL_RENDERER: bool = True
    ENABLE_VR_SUPPORT: bool = False
    MODEL_CACHE_SIZE: int = 100  # 缓存的3D模型数量
    
    # 硬件接口配置
    HARDWARE_INTERFACES: Dict[str, Dict[str, Any]] = {
        "modbus": {
            "enabled": True,
            "port": 502,
            "timeout": 5
        },
        "opcua": {
            "enabled": True,
            "port": 4840,
            "security_policy": "None"
        },
        "ethernet_ip": {
            "enabled": True,
            "port": 44818
        },
        "profinet": {
            "enabled": False,
            "port": 34962
        }
    }
    
    # 容器化配置
    DOCKER_REGISTRY: str = "localhost:5000"
    KUBERNETES_NAMESPACE: str = "industrial-iot"
    KUBERNETES_CONFIG_PATH: str = "~/.kube/config"
    
    # 性能配置
    MAX_CONCURRENT_REQUESTS: int = 1000
    DATABASE_POOL_SIZE: int = 20
    CACHE_SIZE: int = 1000
    WORKER_PROCESSES: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 全局设置实例
settings = Settings()

# 数据库连接字符串
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# SQLAlchemy异步连接字符串
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Redis连接字符串
REDIS_URL = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}" if settings.REDIS_PASSWORD else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

# MQTT主题配置
MQTT_TOPICS = {
    "machine_data": "industrial/machine/+/data",
    "machine_status": "industrial/machine/+/status",
    "machine_alarm": "industrial/machine/+/alarm",
    "machine_control": "industrial/machine/+/control",
    "machine_heartbeat": "industrial/machine/+/heartbeat",
    "system_events": "industrial/system/events",
    "digital_twin": "industrial/twin/+/state"
}

# Kafka主题配置
KAFKA_TOPICS = {
    "machine_data": settings.KAFKA_TOPIC_MACHINE_DATA,
    "alarms": settings.KAFKA_TOPIC_ALARMS,
    "events": settings.KAFKA_TOPIC_EVENTS
}

# 工业协议端口配置
INDUSTRIAL_PROTOCOLS = {
    "modbus_tcp": 502,
    "opcua": 4840,
    "ethernet_ip": 44818,
    "profinet": 34962,
    "bacnet": 47808,
    "dnp3": 20000
}
