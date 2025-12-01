"""
工业互联网机床状态监测平台 - Python 3.11兼容流处理器
使用纯Python实现流处理功能，替代Apache Flink
"""
import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

from config import settings

logger = logging.getLogger(__name__)

class StreamProcessor:
    """流处理器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_running = False
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        self.processors = []
        
    async def process(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理数据"""
        raise NotImplementedError
    
    async def start(self):
        """启动处理器"""
        self.is_running = True
        logger.info(f"流处理器 {self.name} 已启动")
    
    async def stop(self):
        """停止处理器"""
        self.is_running = False
        logger.info(f"流处理器 {self.name} 已停止")

class MachineDataProcessor(StreamProcessor):
    """机床数据处理器"""
    
    def __init__(self):
        super().__init__("MachineDataProcessor")
        
    async def process(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理机床数据"""
        try:
            if not isinstance(data, dict) or "machine_id" not in data:
                return None
            
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
            return None
    
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

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_windows = {}  # machine_id -> deque of historical data
        self.last_alert_times = {}  # machine_id -> last alert timestamp
        self.alert_cooldown = 300  # 5分钟冷却时间
    
    def detect_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测异常"""
        machine_id = data["machine_id"]
        current_time = time.time()
        
        # 初始化数据窗口
        if machine_id not in self.data_windows:
            self.data_windows[machine_id] = {
                "temperature": deque(maxlen=self.window_size),
                "vibration": deque(maxlen=self.window_size),
                "current": deque(maxlen=self.window_size),
                "speed": deque(maxlen=self.window_size)
            }
        
        # 添加新数据
        windows = self.data_windows[machine_id]
        windows["temperature"].append(data["temperature"])
        windows["vibration"].append(data["vibration"])
        windows["current"].append(data["current"])
        windows["speed"].append(data["speed"])
        
        anomalies = []
        
        # 检查是否在冷却期内
        last_alert = self.last_alert_times.get(machine_id, 0)
        if current_time - last_alert < self.alert_cooldown:
            return anomalies
        
        # 统计异常检测
        for param in ["temperature", "vibration", "current", "speed"]:
            if len(windows[param]) >= 10:  # 至少需要10个数据点
                values = list(windows[param])
                mean_val = statistics.mean(values)
                
                try:
                    std_val = statistics.stdev(values)
                except statistics.StatisticsError:
                    std_val = 0
                
                current_val = data[param]
                
                # 3-sigma规则检测异常
                if std_val > 0 and abs(current_val - mean_val) > 3 * std_val:
                    anomalies.append({
                        "type": f"{param}_anomaly",
                        "severity": "high" if abs(current_val - mean_val) > 4 * std_val else "medium",
                        "value": current_val,
                        "expected": mean_val,
                        "deviation": abs(current_val - mean_val),
                        "threshold": 3 * std_val
                    })
        
        # 如果检测到异常，更新最后报警时间
        if anomalies:
            self.last_alert_times[machine_id] = current_time
        
        return anomalies

class ThresholdChecker:
    """阈值检查器"""
    
    def check_thresholds(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查阈值"""
        alerts = []
        
        for param, config in settings.MONITORING_PARAMETERS.items():
            if param in data:
                value = data[param]
                
                if value > config["critical_threshold"]:
                    alerts.append({
                        "parameter": param,
                        "level": "CRITICAL",
                        "value": value,
                        "threshold": config["critical_threshold"],
                        "message": f"{param} 超过临界阈值"
                    })
                elif value > config["warning_threshold"]:
                    alerts.append({
                        "parameter": param,
                        "level": "WARNING",
                        "value": value,
                        "threshold": config["warning_threshold"],
                        "message": f"{param} 超过警告阈值"
                    })
        
        return alerts

class RealTimeAnalyzer:
    """实时分析器"""
    
    def __init__(self, window_duration: int = 60):
        self.window_duration = window_duration  # 窗口持续时间（秒）
        self.data_windows = {}  # machine_id -> time-based data window
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """实时分析"""
        machine_id = data["machine_id"]
        current_time = time.time()
        
        # 初始化数据窗口
        if machine_id not in self.data_windows:
            self.data_windows[machine_id] = deque()
        
        window = self.data_windows[machine_id]
        
        # 添加新数据点
        window.append({
            "timestamp": current_time,
            "data": data
        })
        
        # 移除过期数据
        cutoff_time = current_time - self.window_duration
        while window and window[0]["timestamp"] < cutoff_time:
            window.popleft()
        
        # 计算统计信息
        if not window:
            return {}
        
        values = [point["data"] for point in window]
        
        stats = {
            "machine_id": machine_id,
            "window_start": datetime.fromtimestamp(window[0]["timestamp"]).isoformat(),
            "window_end": datetime.fromtimestamp(current_time).isoformat(),
            "data_count": len(values),
            "avg_temperature": statistics.mean([v["temperature"] for v in values]),
            "max_temperature": max([v["temperature"] for v in values]),
            "avg_vibration": statistics.mean([v["vibration"] for v in values]),
            "max_vibration": max([v["vibration"] for v in values]),
            "avg_efficiency": statistics.mean([v.get("efficiency", 0) for v in values]),
            "min_health_score": min([v.get("health_score", 100) for v in values])
        }
        
        return stats

class StreamProcessingPipeline:
    """流处理管道"""
    
    def __init__(self):
        self.is_running = False
        self.data_processor = MachineDataProcessor()
        self.anomaly_detector = AnomalyDetector()
        self.threshold_checker = ThresholdChecker()
        self.real_time_analyzer = RealTimeAnalyzer()
        
        # 输出队列
        self.processed_data_queue = asyncio.Queue()
        self.anomaly_queue = asyncio.Queue()
        self.alert_queue = asyncio.Queue()
        self.stats_queue = asyncio.Queue()
        
        # 处理任务
        self.processing_tasks = []
    
    async def start(self):
        """启动流处理管道"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动处理任务
        self.processing_tasks = [
            asyncio.create_task(self._process_data_loop()),
            asyncio.create_task(self._output_processed_data()),
            asyncio.create_task(self._output_anomalies()),
            asyncio.create_task(self._output_alerts()),
            asyncio.create_task(self._output_stats())
        ]
        
        logger.info("流处理管道已启动")
    
    async def stop(self):
        """停止流处理管道"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消所有任务
        for task in self.processing_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        logger.info("流处理管道已停止")
    
    async def process_data(self, raw_data: Dict[str, Any]):
        """处理输入数据"""
        if not self.is_running:
            return
        
        try:
            # 数据处理
            processed_data = await self.data_processor.process(raw_data)
            if not processed_data:
                return
            
            # 异常检测
            anomalies = self.anomaly_detector.detect_anomalies(processed_data)
            if anomalies:
                await self.anomaly_queue.put({
                    "machine_id": processed_data["machine_id"],
                    "timestamp": datetime.now().isoformat(),
                    "anomalies": anomalies,
                    "data": processed_data,
                    "alert_type": "anomaly_detection"
                })
            
            # 阈值检查
            alerts = self.threshold_checker.check_thresholds(processed_data)
            if alerts:
                await self.alert_queue.put({
                    "machine_id": processed_data["machine_id"],
                    "timestamp": datetime.now().isoformat(),
                    "alerts": alerts,
                    "data": processed_data,
                    "alert_type": "threshold_violation"
                })
            
            # 实时分析
            stats = self.real_time_analyzer.analyze(processed_data)
            if stats:
                await self.stats_queue.put(stats)
            
            # 输出处理后的数据
            await self.processed_data_queue.put(processed_data)
            
        except Exception as e:
            logger.error(f"数据处理管道错误: {e}")
    
    async def _process_data_loop(self):
        """数据处理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(0.1)  # 避免CPU占用过高
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"数据处理循环错误: {e}")
                await asyncio.sleep(1)
    
    async def _output_processed_data(self):
        """输出处理后的数据"""
        while self.is_running:
            try:
                data = await asyncio.wait_for(self.processed_data_queue.get(), timeout=1.0)
                # 这里可以发送到Kafka或其他消息队列
                logger.debug(f"处理后的数据: {data['machine_id']}")
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"输出处理数据错误: {e}")
    
    async def _output_anomalies(self):
        """输出异常检测结果"""
        while self.is_running:
            try:
                anomaly = await asyncio.wait_for(self.anomaly_queue.get(), timeout=1.0)
                # 这里可以发送到报警系统
                logger.warning(f"检测到异常: {anomaly['machine_id']} - {len(anomaly['anomalies'])} 个异常")
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"输出异常数据错误: {e}")
    
    async def _output_alerts(self):
        """输出报警信息"""
        while self.is_running:
            try:
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                # 这里可以发送到报警系统
                logger.warning(f"阈值报警: {alert['machine_id']} - {len(alert['alerts'])} 个报警")
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"输出报警数据错误: {e}")
    
    async def _output_stats(self):
        """输出统计信息"""
        while self.is_running:
            try:
                stats = await asyncio.wait_for(self.stats_queue.get(), timeout=1.0)
                # 这里可以发送到监控系统
                logger.debug(f"实时统计: {stats['machine_id']} - {stats['data_count']} 个数据点")
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"输出统计数据错误: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取处理状态"""
        return {
            "is_running": self.is_running,
            "processor_type": "Python311StreamProcessor",
            "queues": {
                "processed_data": self.processed_data_queue.qsize(),
                "anomalies": self.anomaly_queue.qsize(),
                "alerts": self.alert_queue.qsize(),
                "stats": self.stats_queue.qsize()
            },
            "components": {
                "data_processor": True,
                "anomaly_detector": True,
                "threshold_checker": True,
                "real_time_analyzer": True
            }
        }

# 全局流处理管道实例
stream_pipeline = StreamProcessingPipeline()

async def start_stream_processing():
    """启动流处理（异步）"""
    try:
        await stream_pipeline.start()
        logger.info("Python 3.11兼容流处理已启动")
    except Exception as e:
        logger.error(f"启动流处理失败: {e}")

async def stop_stream_processing():
    """停止流处理（异步）"""
    try:
        await stream_pipeline.stop()
        logger.info("Python 3.11兼容流处理已停止")
    except Exception as e:
        logger.error(f"停止流处理失败: {e}")

async def process_machine_data(data: Dict[str, Any]):
    """处理机床数据"""
    await stream_pipeline.process_data(data)

def get_stream_processing_status() -> Dict[str, Any]:
    """获取流处理状态"""
    return stream_pipeline.get_status()
