"""
工业互联网机床状态监测平台 - Apache Flink流处理器
"""
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction, FilterFunction, KeyedProcessFunction
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common.time import Time

from config import settings

logger = logging.getLogger(__name__)

class MachineDataProcessor(MapFunction):
    """机床数据处理器"""
    
    def map(self, value: str) -> Dict[str, Any]:
        """处理机床数据"""
        try:
            data = json.loads(value)
            
            # 数据清洗和标准化
            processed_data = {
                "machine_id": data.get("machine_id"),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "temperature": float(data.get("temperature", 0)),
                "vibration": float(data.get("vibration", 0)),
                "current": float(data.get("current", 0)),
                "speed": float(data.get("speed", 0)),
                "pressure": float(data.get("pressure", 0)),
                "tool_wear": float(data.get("tool_wear", 0)),
                "power_consumption": float(data.get("power_consumption", 0)),
                "is_virtual": data.get("is_virtual", False),
                "processing_time": datetime.now().isoformat()
            }
            
            # 计算衍生指标
            processed_data["efficiency"] = self._calculate_efficiency(processed_data)
            processed_data["health_score"] = self._calculate_health_score(processed_data)
            processed_data["anomaly_score"] = self._calculate_anomaly_score(processed_data)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"数据处理错误: {e}")
            return {}
    
    def _calculate_efficiency(self, data: Dict[str, Any]) -> float:
        """计算设备效率"""
        if data["speed"] == 0:
            return 0.0
        
        # 基于转速、电流和功耗计算效率
        theoretical_power = data["speed"] * 0.01  # 理论功耗
        actual_power = data["power_consumption"]
        
        if actual_power == 0:
            return 0.0
        
        efficiency = min(100.0, (theoretical_power / actual_power) * 100)
        return round(efficiency, 2)
    
    def _calculate_health_score(self, data: Dict[str, Any]) -> float:
        """计算健康评分"""
        score = 100.0
        
        # 温度影响
        temp_params = settings.MONITORING_PARAMETERS["temperature"]
        if data["temperature"] > temp_params["critical_threshold"]:
            score -= 30
        elif data["temperature"] > temp_params["warning_threshold"]:
            score -= 15
        
        # 振动影响
        vib_params = settings.MONITORING_PARAMETERS["vibration"]
        if data["vibration"] > vib_params["critical_threshold"]:
            score -= 25
        elif data["vibration"] > vib_params["warning_threshold"]:
            score -= 10
        
        # 刀具磨损影响
        wear_params = settings.MONITORING_PARAMETERS["tool_wear"]
        if data["tool_wear"] > wear_params["critical_threshold"]:
            score -= 20
        elif data["tool_wear"] > wear_params["warning_threshold"]:
            score -= 10
        
        return max(0.0, round(score, 2))
    
    def _calculate_anomaly_score(self, data: Dict[str, Any]) -> float:
        """计算异常评分"""
        anomaly_score = 0.0
        
        # 基于历史数据的简单异常检测
        # 实际应用中应该使用更复杂的机器学习模型
        
        # 温度异常
        if data["temperature"] > 85 or data["temperature"] < 15:
            anomaly_score += 0.3
        
        # 振动异常
        if data["vibration"] > 12:
            anomaly_score += 0.4
        
        # 电流异常
        if data["current"] > 60 or (data["speed"] > 0 and data["current"] < 1):
            anomaly_score += 0.2
        
        # 转速异常
        if data["speed"] > 3500:
            anomaly_score += 0.1
        
        return min(1.0, round(anomaly_score, 3))

class AnomalyDetectionFunction(KeyedProcessFunction):
    """异常检测函数"""
    
    def __init__(self):
        self.temperature_state = None
        self.vibration_state = None
        self.last_alert_time_state = None
    
    def open(self, runtime_context):
        """初始化状态"""
        self.temperature_state = runtime_context.get_state(
            ValueStateDescriptor("temperature_history", Types.LIST(Types.FLOAT()))
        )
        self.vibration_state = runtime_context.get_state(
            ValueStateDescriptor("vibration_history", Types.LIST(Types.FLOAT()))
        )
        self.last_alert_time_state = runtime_context.get_state(
            ValueStateDescriptor("last_alert_time", Types.LONG())
        )
    
    def process_element(self, value: Dict[str, Any], ctx, out):
        """处理数据元素"""
        try:
            machine_id = value["machine_id"]
            current_time = int(time.time() * 1000)
            
            # 获取历史数据
            temp_history = self.temperature_state.value() or []
            vib_history = self.vibration_state.value() or []
            last_alert_time = self.last_alert_time_state.value() or 0
            
            # 更新历史数据（保持最近100个数据点）
            temp_history.append(value["temperature"])
            vib_history.append(value["vibration"])
            
            if len(temp_history) > 100:
                temp_history = temp_history[-100:]
            if len(vib_history) > 100:
                vib_history = vib_history[-100:]
            
            # 更新状态
            self.temperature_state.update(temp_history)
            self.vibration_state.update(vib_history)
            
            # 异常检测
            anomalies = []
            
            # 温度异常检测
            if len(temp_history) >= 10:
                temp_avg = sum(temp_history[-10:]) / 10
                temp_std = (sum([(x - temp_avg) ** 2 for x in temp_history[-10:]]) / 10) ** 0.5
                
                if abs(value["temperature"] - temp_avg) > 3 * temp_std:
                    anomalies.append({
                        "type": "temperature_anomaly",
                        "severity": "high",
                        "value": value["temperature"],
                        "expected": temp_avg,
                        "deviation": abs(value["temperature"] - temp_avg)
                    })
            
            # 振动异常检测
            if len(vib_history) >= 10:
                vib_avg = sum(vib_history[-10:]) / 10
                vib_std = (sum([(x - vib_avg) ** 2 for x in vib_history[-10:]]) / 10) ** 0.5
                
                if abs(value["vibration"] - vib_avg) > 2 * vib_std:
                    anomalies.append({
                        "type": "vibration_anomaly",
                        "severity": "medium",
                        "value": value["vibration"],
                        "expected": vib_avg,
                        "deviation": abs(value["vibration"] - vib_avg)
                    })
            
            # 如果检测到异常且距离上次报警超过5分钟
            if anomalies and (current_time - last_alert_time) > 300000:  # 5分钟
                alert = {
                    "machine_id": machine_id,
                    "timestamp": datetime.now().isoformat(),
                    "anomalies": anomalies,
                    "data": value,
                    "alert_type": "anomaly_detection"
                }
                
                out.collect(json.dumps(alert))
                self.last_alert_time_state.update(current_time)
            
            # 输出处理后的数据
            out.collect(json.dumps(value))
            
        except Exception as e:
            logger.error(f"异常检测处理错误: {e}")

class ThresholdAlertFunction(FilterFunction):
    """阈值报警函数"""
    
    def filter(self, value: str) -> bool:
        """过滤需要报警的数据"""
        try:
            data = json.loads(value)
            
            # 检查各项参数是否超过阈值
            alerts = []
            
            for param, config in settings.MONITORING_PARAMETERS.items():
                if param in data:
                    value_param = data[param]
                    
                    if value_param > config["critical_threshold"]:
                        alerts.append({
                            "parameter": param,
                            "level": "CRITICAL",
                            "value": value_param,
                            "threshold": config["critical_threshold"]
                        })
                    elif value_param > config["warning_threshold"]:
                        alerts.append({
                            "parameter": param,
                            "level": "WARNING",
                            "value": value_param,
                            "threshold": config["warning_threshold"]
                        })
            
            return len(alerts) > 0
            
        except Exception as e:
            logger.error(f"阈值检查错误: {e}")
            return False

class FlinkStreamProcessor:
    """Flink流处理器主类"""
    
    def __init__(self):
        self.env = None
        self.table_env = None
        self.is_running = False
    
    def initialize(self):
        """初始化Flink环境"""
        try:
            # 创建流执行环境
            self.env = StreamExecutionEnvironment.get_execution_environment()
            self.env.set_parallelism(settings.FLINK_PARALLELISM)
            
            # 启用检查点
            self.env.enable_checkpointing(settings.FLINK_CHECKPOINT_INTERVAL)
            
            # 创建表环境
            env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
            self.table_env = StreamTableEnvironment.create(self.env, env_settings)
            
            logger.info("Flink流处理环境初始化完成")
            
        except Exception as e:
            logger.error(f"Flink环境初始化失败: {e}")
            raise
    
    def create_kafka_source(self, topic: str, group_id: str):
        """创建Kafka数据源"""
        try:
            properties = {
                'bootstrap.servers': ','.join(settings.KAFKA_BOOTSTRAP_SERVERS),
                'group.id': group_id
            }
            
            kafka_consumer = FlinkKafkaConsumer(
                topic,
                SimpleStringSchema(),
                properties
            )
            
            return kafka_consumer
            
        except Exception as e:
            logger.error(f"创建Kafka数据源失败: {e}")
            raise
    
    def create_kafka_sink(self, topic: str):
        """创建Kafka数据汇"""
        try:
            properties = {
                'bootstrap.servers': ','.join(settings.KAFKA_BOOTSTRAP_SERVERS)
            }
            
            kafka_producer = FlinkKafkaProducer(
                topic,
                SimpleStringSchema(),
                properties
            )
            
            return kafka_producer
            
        except Exception as e:
            logger.error(f"创建Kafka数据汇失败: {e}")
            raise
    
    def setup_machine_data_pipeline(self):
        """设置机床数据处理管道"""
        try:
            # 创建数据源
            kafka_source = self.create_kafka_source(
                settings.KAFKA_TOPIC_MACHINE_DATA,
                settings.KAFKA_CONSUMER_GROUP
            )
            
            # 创建数据流
            data_stream = self.env.add_source(kafka_source)
            
            # 数据处理
            processed_stream = data_stream.map(
                MachineDataProcessor(),
                output_type=Types.STRING()
            )
            
            # 按机床ID分组进行异常检测
            keyed_stream = processed_stream.key_by(
                lambda x: json.loads(x)["machine_id"]
            )
            
            anomaly_stream = keyed_stream.process(
                AnomalyDetectionFunction(),
                output_type=Types.STRING()
            )
            
            # 阈值报警
            alert_stream = processed_stream.filter(ThresholdAlertFunction())
            
            # 输出到不同的Kafka主题
            processed_sink = self.create_kafka_sink("processed-machine-data")
            anomaly_sink = self.create_kafka_sink(settings.KAFKA_TOPIC_ALARMS)
            alert_sink = self.create_kafka_sink("threshold-alerts")
            
            processed_stream.add_sink(processed_sink)
            anomaly_stream.add_sink(anomaly_sink)
            alert_stream.add_sink(alert_sink)
            
            logger.info("机床数据处理管道设置完成")
            
        except Exception as e:
            logger.error(f"设置数据处理管道失败: {e}")
            raise
    
    def setup_real_time_analytics(self):
        """设置实时分析"""
        try:
            # 创建机床数据表
            self.table_env.execute_sql("""
                CREATE TABLE machine_data (
                    machine_id STRING,
                    timestamp TIMESTAMP(3),
                    temperature DOUBLE,
                    vibration DOUBLE,
                    current DOUBLE,
                    speed DOUBLE,
                    pressure DOUBLE,
                    tool_wear DOUBLE,
                    power_consumption DOUBLE,
                    efficiency DOUBLE,
                    health_score DOUBLE,
                    WATERMARK FOR timestamp AS timestamp - INTERVAL '5' SECOND
                ) WITH (
                    'connector' = 'kafka',
                    'topic' = 'processed-machine-data',
                    'properties.bootstrap.servers' = '{}',
                    'format' = 'json'
                )
            """.format(','.join(settings.KAFKA_BOOTSTRAP_SERVERS)))
            
            # 创建实时统计表
            self.table_env.execute_sql("""
                CREATE TABLE machine_stats (
                    machine_id STRING,
                    window_start TIMESTAMP(3),
                    window_end TIMESTAMP(3),
                    avg_temperature DOUBLE,
                    max_temperature DOUBLE,
                    avg_vibration DOUBLE,
                    max_vibration DOUBLE,
                    avg_efficiency DOUBLE,
                    min_health_score DOUBLE,
                    data_count BIGINT
                ) WITH (
                    'connector' = 'kafka',
                    'topic' = 'machine-stats',
                    'properties.bootstrap.servers' = '{}',
                    'format' = 'json'
                )
            """.format(','.join(settings.KAFKA_BOOTSTRAP_SERVERS)))
            
            # 实时统计查询
            self.table_env.execute_sql("""
                INSERT INTO machine_stats
                SELECT 
                    machine_id,
                    TUMBLE_START(timestamp, INTERVAL '1' MINUTE) as window_start,
                    TUMBLE_END(timestamp, INTERVAL '1' MINUTE) as window_end,
                    AVG(temperature) as avg_temperature,
                    MAX(temperature) as max_temperature,
                    AVG(vibration) as avg_vibration,
                    MAX(vibration) as max_vibration,
                    AVG(efficiency) as avg_efficiency,
                    MIN(health_score) as min_health_score,
                    COUNT(*) as data_count
                FROM machine_data
                GROUP BY machine_id, TUMBLE(timestamp, INTERVAL '1' MINUTE)
            """)
            
            logger.info("实时分析设置完成")
            
        except Exception as e:
            logger.error(f"设置实时分析失败: {e}")
            raise
    
    def start_processing(self):
        """启动流处理"""
        try:
            if not self.env:
                self.initialize()
            
            # 设置处理管道
            self.setup_machine_data_pipeline()
            self.setup_real_time_analytics()
            
            # 启动执行
            self.is_running = True
            logger.info("启动Flink流处理...")
            
            # 异步执行
            job_result = self.env.execute("Industrial IoT Stream Processing")
            
            logger.info(f"流处理作业已启动: {job_result.get_job_id()}")
            
        except Exception as e:
            logger.error(f"启动流处理失败: {e}")
            self.is_running = False
            raise
    
    def stop_processing(self):
        """停止流处理"""
        try:
            self.is_running = False
            logger.info("Flink流处理已停止")
            
        except Exception as e:
            logger.error(f"停止流处理失败: {e}")
    
    def get_processing_status(self) -> Dict[str, Any]:
        """获取处理状态"""
        return {
            "is_running": self.is_running,
            "parallelism": settings.FLINK_PARALLELISM,
            "checkpoint_interval": settings.FLINK_CHECKPOINT_INTERVAL,
            "kafka_topics": {
                "input": settings.KAFKA_TOPIC_MACHINE_DATA,
                "output": ["processed-machine-data", "machine-stats", settings.KAFKA_TOPIC_ALARMS]
            }
        }

# 全局流处理器实例
stream_processor = FlinkStreamProcessor()

async def start_stream_processing():
    """启动流处理（异步）"""
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, stream_processor.start_processing
        )
    except Exception as e:
        logger.error(f"异步启动流处理失败: {e}")

async def stop_stream_processing():
    """停止流处理（异步）"""
    try:
        await asyncio.get_event_loop().run_in_executor(
            None, stream_processor.stop_processing
        )
    except Exception as e:
        logger.error(f"异步停止流处理失败: {e}")
