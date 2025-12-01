"""
工业互联网机床状态监测平台 - MQTT客户端
"""
import asyncio
import json
import uuid
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import paho.mqtt.client as mqtt
from loguru import logger

from config import settings, MQTT_TOPICS
from backend.models import MachineData, AlarmEvent

class MQTTClient:
    """MQTT客户端管理器"""
    
    def __init__(self):
        self.client = None
        self.is_connected_flag = False
        self.pending_data = asyncio.Queue()
        self.message_handlers = {}
        self.subscribed_topics = set()
        
    async def connect(self):
        """连接到MQTT代理"""
        try:
            self.client = mqtt.Client(client_id=f"industrial_iot_{uuid.uuid4().hex[:8]}")
            
            # 设置回调函数
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.on_subscribe = self._on_subscribe
            self.client.on_unsubscribe = self._on_unsubscribe
            
            # 设置认证信息
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
            
            # 连接到代理
            logger.info(f"正在连接到MQTT代理: {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                settings.MQTT_KEEPALIVE
            )
            
            # 启动网络循环
            self.client.loop_start()
            
            # 等待连接建立
            await self._wait_for_connection()
            
            # 订阅默认主题
            await self._subscribe_default_topics()
            
            logger.success("MQTT客户端连接成功")
            
        except Exception as e:
            logger.error(f"MQTT连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开MQTT连接"""
        if self.client:
            logger.info("正在断开MQTT连接...")
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected_flag = False
            logger.info("MQTT连接已断开")
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.is_connected_flag
    
    async def publish(self, topic: str, payload: str, qos: int = 1, retain: bool = False):
        """发布消息"""
        if not self.is_connected_flag:
            raise ConnectionError("MQTT客户端未连接")
        
        try:
            result = self.client.publish(topic, payload, qos, retain)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"发布消息失败: {mqtt.error_string(result.rc)}")
            
            logger.debug(f"消息已发布到主题 {topic}: {payload[:100]}...")
            
        except Exception as e:
            logger.error(f"发布消息失败: {e}")
            raise
    
    async def subscribe(self, topic: str, qos: int = 1):
        """订阅主题"""
        if not self.is_connected_flag:
            raise ConnectionError("MQTT客户端未连接")
        
        try:
            result, mid = self.client.subscribe(topic, qos)
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"订阅主题失败: {mqtt.error_string(result)}")
            
            self.subscribed_topics.add(topic)
            logger.info(f"已订阅主题: {topic}")
            
        except Exception as e:
            logger.error(f"订阅主题失败: {e}")
            raise
    
    async def unsubscribe(self, topic: str):
        """取消订阅主题"""
        if not self.is_connected_flag:
            raise ConnectionError("MQTT客户端未连接")
        
        try:
            result, mid = self.client.unsubscribe(topic)
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"取消订阅失败: {mqtt.error_string(result)}")
            
            self.subscribed_topics.discard(topic)
            logger.info(f"已取消订阅主题: {topic}")
            
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            raise
    
    def register_message_handler(self, topic_pattern: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[topic_pattern] = handler
        logger.info(f"已注册消息处理器: {topic_pattern}")
    
    def has_pending_data(self) -> bool:
        """检查是否有待处理数据"""
        return not self.pending_data.empty()
    
    async def get_pending_data(self) -> Optional[Dict[str, Any]]:
        """获取待处理数据"""
        try:
            return await asyncio.wait_for(self.pending_data.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return None
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.is_connected_flag = True
            logger.success(f"MQTT连接成功，返回码: {rc}")
        else:
            self.is_connected_flag = False
            logger.error(f"MQTT连接失败，返回码: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.is_connected_flag = False
        if rc != 0:
            logger.warning(f"MQTT意外断开连接，返回码: {rc}")
        else:
            logger.info("MQTT正常断开连接")
    
    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"收到消息 - 主题: {topic}, 负载: {payload[:100]}...")
            
            # 解析消息
            data = json.loads(payload)
            data['_topic'] = topic
            data['_timestamp'] = datetime.now().isoformat()
            
            # 处理不同类型的消息
            if '/data' in topic:
                self._handle_machine_data(topic, data)
            elif '/status' in topic:
                self._handle_machine_status(topic, data)
            elif '/alarm' in topic:
                self._handle_machine_alarm(topic, data)
            elif '/control' in topic:
                self._handle_control_response(topic, data)
            
            # 将数据放入队列
            asyncio.create_task(self.pending_data.put(data))
            
        except Exception as e:
            logger.error(f"处理MQTT消息失败: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """订阅成功回调"""
        logger.debug(f"订阅成功，消息ID: {mid}, QoS: {granted_qos}")
    
    def _on_unsubscribe(self, client, userdata, mid):
        """取消订阅回调"""
        logger.debug(f"取消订阅成功，消息ID: {mid}")
    
    async def _wait_for_connection(self, timeout: int = 10):
        """等待连接建立"""
        for _ in range(timeout * 10):  # 每100ms检查一次
            if self.is_connected_flag:
                return
            await asyncio.sleep(0.1)
        
        raise TimeoutError("MQTT连接超时")
    
    async def _subscribe_default_topics(self):
        """订阅默认主题"""
        for topic_name, topic_pattern in MQTT_TOPICS.items():
            await self.subscribe(topic_pattern)
    
    def _handle_machine_data(self, topic: str, data: Dict[str, Any]):
        """处理机床数据消息"""
        try:
            # 从主题中提取机床ID
            machine_id = self._extract_machine_id(topic)
            data['machine_id'] = machine_id
            data['message_type'] = 'machine_data'
            
            logger.debug(f"处理机床数据: {machine_id}")
            
        except Exception as e:
            logger.error(f"处理机床数据失败: {e}")
    
    def _handle_machine_status(self, topic: str, data: Dict[str, Any]):
        """处理机床状态消息"""
        try:
            machine_id = self._extract_machine_id(topic)
            data['machine_id'] = machine_id
            data['message_type'] = 'machine_status'
            
            logger.debug(f"处理机床状态: {machine_id} - {data.get('status')}")
            
        except Exception as e:
            logger.error(f"处理机床状态失败: {e}")
    
    def _handle_machine_alarm(self, topic: str, data: Dict[str, Any]):
        """处理机床报警消息"""
        try:
            machine_id = self._extract_machine_id(topic)
            data['machine_id'] = machine_id
            data['message_type'] = 'machine_alarm'
            
            logger.warning(f"收到机床报警: {machine_id} - {data.get('message')}")
            
        except Exception as e:
            logger.error(f"处理机床报警失败: {e}")
    
    def _handle_control_response(self, topic: str, data: Dict[str, Any]):
        """处理控制响应消息"""
        try:
            machine_id = self._extract_machine_id(topic)
            data['machine_id'] = machine_id
            data['message_type'] = 'control_response'
            
            logger.info(f"收到控制响应: {machine_id} - {data.get('status')}")
            
        except Exception as e:
            logger.error(f"处理控制响应失败: {e}")
    
    def _extract_machine_id(self, topic: str) -> str:
        """从主题中提取机床ID"""
        # 主题格式: industrial/machine/{machine_id}/data
        parts = topic.split('/')
        if len(parts) >= 3:
            return parts[2]
        return "unknown"
    
    async def publish_machine_data(self, machine_id: str, data: MachineData):
        """发布机床数据"""
        topic = f"industrial/machine/{machine_id}/data"
        payload = data.json()
        await self.publish(topic, payload)
    
    async def publish_machine_status(self, machine_id: str, status: str):
        """发布机床状态"""
        topic = f"industrial/machine/{machine_id}/status"
        payload = json.dumps({
            "machine_id": machine_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        await self.publish(topic, payload)
    
    async def publish_alarm(self, alarm: AlarmEvent):
        """发布报警信息"""
        topic = f"industrial/machine/{alarm.machine_id}/alarm"
        payload = alarm.json()
        await self.publish(topic, payload)
    
    async def send_control_command(self, machine_id: str, command: Dict[str, Any]):
        """发送控制命令"""
        topic = f"industrial/machine/{machine_id}/control"
        payload = json.dumps({
            "command_id": str(uuid.uuid4()),
            "machine_id": machine_id,
            "timestamp": datetime.now().isoformat(),
            **command
        })
        await self.publish(topic, payload)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            "broker_host": settings.MQTT_BROKER_HOST,
            "broker_port": settings.MQTT_BROKER_PORT,
            "is_connected": self.is_connected_flag,
            "subscribed_topics": list(self.subscribed_topics),
            "pending_messages": self.pending_data.qsize()
        }
