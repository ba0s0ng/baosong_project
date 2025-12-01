import asyncio
import json
import paho.mqtt.client as mqtt
from datetime import datetime

from .db import execute_query, fetch_all

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.is_connected = False
        # 模拟数据生成器标志
        self.generate_mock_data = True
    
    async def connect(self):
        """连接到MQTT代理"""
        try:
            # 在实际环境中，这里应该连接到真实的MQTT代理
            # 这里我们模拟连接成功
            self.is_connected = True
            print("MQTT客户端已连接（模拟）")
            
            # 启动模拟数据生成任务
            if self.generate_mock_data:
                asyncio.create_task(self.generate_mock_data_loop())
                
        except Exception as e:
            print(f"MQTT连接失败: {e}")
    
    async def disconnect(self):
        """断开MQTT连接"""
        self.is_connected = False
        self.generate_mock_data = False
        print("MQTT客户端已断开连接")
    
    async def subscribe(self, topic):
        """订阅MQTT主题"""
        if self.is_connected:
            print(f"已订阅主题: {topic}")
    
    async def publish(self, topic, message):
        """发布MQTT消息"""
        if self.is_connected:
            print(f"发布消息到主题 {topic}: {message}")
    
    def on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        print(f"已连接到MQTT代理，返回码: {rc}")
    
    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        print(f"收到主题 {msg.topic} 的消息: {msg.payload.decode()}")
        # 在实际应用中，这里应该处理接收到的设备数据
    
    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        print(f"已断开MQTT连接，返回码: {rc}")
        self.is_connected = False
    
    async def generate_mock_data_loop(self):
        """生成模拟设备数据的循环"""
        import random
        import time
        
        while self.generate_mock_data:
            try:
                # 获取所有在线设备
                machines = await fetch_all("SELECT id FROM machines WHERE status = 'online'")
                
                for machine in machines:
                    machine_id = machine['id']
                    
                    # 生成模拟数据
                    data = {
                        'machine_id': machine_id,
                        'temperature': round(random.uniform(30.0, 75.0), 2),  # 温度在30-75度之间
                        'vibration': round(random.uniform(0.5, 4.5), 2),  # 振动在0.5-4.5之间
                        'current': round(random.uniform(50.0, 95.0), 2),  # 电流在50-95A之间
                        'rotation_speed': round(random.uniform(1000.0, 5000.0), 2),  # 转速在1000-5000RPM之间
                        'pressure': round(random.uniform(0.8, 1.5), 2),  # 压力在0.8-1.5MPa之间
                        'power': round(random.uniform(10.0, 50.0), 2)  # 功率在10-50kW之间
                    }
                    
                    # 保存到数据库
                    await execute_query('''
                    INSERT INTO machine_data (machine_id, timestamp, temperature, vibration, current, rotation_speed, pressure, power)
                    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)
                    ''', (data['machine_id'], data['temperature'], data['vibration'], 
                          data['current'], data['rotation_speed'], data['pressure'], data['power']))
                    
                    # 检查是否触发报警
                    await self.check_alarm_rules(machine_id, data)
                
                # 每5秒生成一次数据
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"生成模拟数据时出错: {e}")
                await asyncio.sleep(1)
    
    async def check_alarm_rules(self, machine_id, data):
        """检查是否触发报警规则"""
        rules = await fetch_all("SELECT * FROM alarm_rules WHERE is_active = TRUE")
        
        for rule in rules:
            param_value = data.get(rule['parameter'])
            if param_value is not None:
                threshold = rule['threshold']
                operator = rule['operator']
                
                # 检查是否触发规则
                trigger = False
                if operator == '>' and param_value > threshold:
                    trigger = True
                elif operator == '<' and param_value < threshold:
                    trigger = True
                elif operator == '>=' and param_value >= threshold:
                    trigger = True
                elif operator == '<=' and param_value <= threshold:
                    trigger = True
                elif operator == '==' and param_value == threshold:
                    trigger = True
                
                if trigger:
                    # 记录报警
                    await execute_query('''
                    INSERT INTO alarms (machine_id, timestamp, level, type, message)
                    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
                    ''', (machine_id, rule['level'], rule['parameter'], rule['message']))
                    print(f"触发报警: {rule['message']} (设备ID: {machine_id})")

# 创建全局MQTT客户端实例
mqtt_client = MQTTClient()