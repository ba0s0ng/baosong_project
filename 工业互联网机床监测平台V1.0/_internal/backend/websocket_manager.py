"""
工业互联网机床状态监测平台 - WebSocket管理器
"""
import asyncio
import json
from typing import Dict, Set, Any, List
from datetime import datetime
from fastapi import WebSocket
from loguru import logger

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接
        self.active_connections: List[WebSocket] = []
        # 机床订阅映射 {machine_id: {websocket1, websocket2, ...}}
        self.machine_subscriptions: Dict[str, Set[WebSocket]] = {}
        # 连接订阅映射 {websocket: {machine_id1, machine_id2, ...}}
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_subscriptions[websocket] = set()
        
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")
        
        # 发送欢迎消息
        await self.send_personal_message(websocket, {
            "type": "welcome",
            "message": "欢迎连接到工业互联网机床监测平台",
            "timestamp": datetime.now().isoformat(),
            "connection_id": id(websocket)
        })
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 清理订阅关系
        if websocket in self.connection_subscriptions:
            subscribed_machines = self.connection_subscriptions[websocket]
            for machine_id in subscribed_machines:
                if machine_id in self.machine_subscriptions:
                    self.machine_subscriptions[machine_id].discard(websocket)
                    if not self.machine_subscriptions[machine_id]:
                        del self.machine_subscriptions[machine_id]
            
            del self.connection_subscriptions[websocket]
        
        logger.info(f"WebSocket连接已断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送个人消息"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False, default=str))
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息给所有连接"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message, ensure_ascii=False, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_machine_subscribers(self, machine_id: str, message: Dict[str, Any]):
        """向订阅特定机床的客户端广播消息"""
        if machine_id not in self.machine_subscriptions:
            return
        
        subscribers = self.machine_subscriptions[machine_id].copy()
        if not subscribers:
            return
        
        message_text = json.dumps(message, ensure_ascii=False, default=str)
        disconnected = []
        
        for connection in subscribers:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"向机床订阅者广播消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def subscribe(self, websocket: WebSocket, machine_id: str):
        """订阅机床数据"""
        if machine_id not in self.machine_subscriptions:
            self.machine_subscriptions[machine_id] = set()
        
        self.machine_subscriptions[machine_id].add(websocket)
        self.connection_subscriptions[websocket].add(machine_id)
        
        logger.info(f"WebSocket {id(websocket)} 订阅了机床 {machine_id}")
        
        # 发送订阅确认
        await self.send_personal_message(websocket, {
            "type": "subscription_confirmed",
            "machine_id": machine_id,
            "message": f"已订阅机床 {machine_id} 的数据",
            "timestamp": datetime.now().isoformat()
        })
    
    async def unsubscribe(self, websocket: WebSocket, machine_id: str):
        """取消订阅机床数据"""
        if machine_id in self.machine_subscriptions:
            self.machine_subscriptions[machine_id].discard(websocket)
            if not self.machine_subscriptions[machine_id]:
                del self.machine_subscriptions[machine_id]
        
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket].discard(machine_id)
        
        logger.info(f"WebSocket {id(websocket)} 取消订阅机床 {machine_id}")
        
        # 发送取消订阅确认
        await self.send_personal_message(websocket, {
            "type": "unsubscription_confirmed",
            "machine_id": machine_id,
            "message": f"已取消订阅机床 {machine_id} 的数据",
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_data(self, data: Dict[str, Any]):
        """广播机床数据"""
        machine_id = data.get("machine_id")
        if not machine_id:
            return
        
        message = {
            "type": "machine_data",
            "machine_id": machine_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 向订阅该机床的客户端广播
        await self.broadcast_to_machine_subscribers(machine_id, message)
        
        logger.debug(f"广播机床数据: {machine_id}")
    
    async def broadcast_alarm(self, alarm: Dict[str, Any]):
        """广播报警信息"""
        machine_id = alarm.get("machine_id")
        
        message = {
            "type": "alarm",
            "machine_id": machine_id,
            "alarm": alarm,
            "timestamp": datetime.now().isoformat()
        }
        
        # 报警信息广播给所有连接（高优先级）
        await self.broadcast(message)
        
        logger.warning(f"广播报警信息: {machine_id} - {alarm.get('message')}")
    
    async def broadcast_status_change(self, machine_id: str, old_status: str, new_status: str):
        """广播机床状态变化"""
        message = {
            "type": "status_change",
            "machine_id": machine_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        
        # 向订阅该机床的客户端广播
        await self.broadcast_to_machine_subscribers(machine_id, message)
        
        logger.info(f"广播状态变化: {machine_id} {old_status} -> {new_status}")
    
    async def broadcast_control_response(self, machine_id: str, command_id: str, response: Dict[str, Any]):
        """广播控制命令响应"""
        message = {
            "type": "control_response",
            "machine_id": machine_id,
            "command_id": command_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # 向订阅该机床的客户端广播
        await self.broadcast_to_machine_subscribers(machine_id, message)
        
        logger.info(f"广播控制响应: {machine_id} - {command_id}")
    
    async def send_system_notification(self, notification: Dict[str, Any]):
        """发送系统通知"""
        message = {
            "type": "system_notification",
            "notification": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast(message)
        
        logger.info(f"发送系统通知: {notification.get('title')}")
    
    async def send_maintenance_alert(self, machine_id: str, maintenance_info: Dict[str, Any]):
        """发送维护提醒"""
        message = {
            "type": "maintenance_alert",
            "machine_id": machine_id,
            "maintenance_info": maintenance_info,
            "timestamp": datetime.now().isoformat()
        }
        
        # 向订阅该机床的客户端广播
        await self.broadcast_to_machine_subscribers(machine_id, message)
        
        logger.info(f"发送维护提醒: {machine_id}")
    
    async def send_performance_report(self, machine_id: str, report: Dict[str, Any]):
        """发送性能报告"""
        message = {
            "type": "performance_report",
            "machine_id": machine_id,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
        # 向订阅该机床的客户端广播
        await self.broadcast_to_machine_subscribers(machine_id, message)
        
        logger.info(f"发送性能报告: {machine_id}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return {
            "total_connections": len(self.active_connections),
            "machine_subscriptions": {
                machine_id: len(subscribers) 
                for machine_id, subscribers in self.machine_subscriptions.items()
            },
            "total_subscriptions": sum(
                len(subscriptions) 
                for subscriptions in self.connection_subscriptions.values()
            )
        }
    
    def get_machine_subscribers(self, machine_id: str) -> int:
        """获取机床订阅者数量"""
        return len(self.machine_subscriptions.get(machine_id, set()))
    
    async def ping_all_connections(self):
        """向所有连接发送心跳"""
        if not self.active_connections:
            return
        
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast(ping_message)
    
    async def send_real_time_metrics(self, metrics: Dict[str, Any]):
        """发送实时指标"""
        message = {
            "type": "real_time_metrics",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast(message)
    
    async def handle_client_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """处理客户端消息"""
        message_type = message.get("type")
        
        try:
            if message_type == "subscribe":
                machine_id = message.get("machine_id")
                if machine_id:
                    await self.subscribe(websocket, machine_id)
                else:
                    await self.send_personal_message(websocket, {
                        "type": "error",
                        "message": "订阅请求缺少machine_id参数"
                    })
            
            elif message_type == "unsubscribe":
                machine_id = message.get("machine_id")
                if machine_id:
                    await self.unsubscribe(websocket, machine_id)
                else:
                    await self.send_personal_message(websocket, {
                        "type": "error",
                        "message": "取消订阅请求缺少machine_id参数"
                    })
            
            elif message_type == "get_subscriptions":
                subscriptions = list(self.connection_subscriptions.get(websocket, set()))
                await self.send_personal_message(websocket, {
                    "type": "subscriptions_list",
                    "subscriptions": subscriptions
                })
            
            elif message_type == "pong":
                # 客户端心跳响应
                logger.debug(f"收到客户端心跳响应: {id(websocket)}")
            
            else:
                await self.send_personal_message(websocket, {
                    "type": "error",
                    "message": f"未知的消息类型: {message_type}"
                })
        
        except Exception as e:
            logger.error(f"处理客户端消息失败: {e}")
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "处理消息时发生错误"
            })
