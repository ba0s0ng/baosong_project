"""
工业互联网机床状态监测平台 - 设备管理器
支持真实设备与虚拟设备的无缝切换
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

from config import settings

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """设备类型"""
    REAL = "real"
    VIRTUAL = "virtual"

class ConnectionStatus(Enum):
    """连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class DeviceInterface(ABC):
    """设备接口抽象基类"""
    
    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        self.device_id = device_id
        self.device_config = device_config
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.last_data_time = None
        self.error_count = 0
        self.max_errors = 5
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接设备"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开设备连接"""
        pass
    
    @abstractmethod
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """读取设备数据"""
        pass
    
    @abstractmethod
    async def write_command(self, command: Dict[str, Any]) -> bool:
        """向设备发送命令"""
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        pass
    
    def is_connected(self) -> bool:
        """检查设备是否连接"""
        return self.connection_status == ConnectionStatus.CONNECTED
    
    def get_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        return {
            "device_id": self.device_id,
            "connection_status": self.connection_status.value,
            "last_data_time": self.last_data_time.isoformat() if self.last_data_time else None,
            "error_count": self.error_count,
            "device_config": self.device_config
        }

class ModbusDevice(DeviceInterface):
    """Modbus设备接口"""
    
    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        super().__init__(device_id, device_config)
        self.client = None
        self.host = device_config.get("host", "localhost")
        self.port = device_config.get("port", 502)
        self.unit_id = device_config.get("unit_id", 1)
        self.timeout = device_config.get("timeout", 5)
        self.register_map = device_config.get("register_map", {})
    
    async def connect(self) -> bool:
        """连接Modbus设备"""
        try:
            from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient
            
            self.connection_status = ConnectionStatus.CONNECTING
            
            self.client = AsyncModbusTCPClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            
            connected = await self.client.connect()
            
            if connected:
                self.connection_status = ConnectionStatus.CONNECTED
                self.error_count = 0
                logger.info(f"Modbus设备 {self.device_id} 连接成功")
                return True
            else:
                self.connection_status = ConnectionStatus.ERROR
                self.error_count += 1
                logger.error(f"Modbus设备 {self.device_id} 连接失败")
                return False
                
        except Exception as e:
            logger.error(f"关闭设备管理器失败: {e}")
            self.connection_status = ConnectionStatus.ERROR
            self.error_count += 1
            logger.error(f"Modbus设备 {self.device_id} 连接异常: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开Modbus设备连接"""
        try:
            if self.client:
                self.client.close()
                self.client = None
            
            self.connection_status = ConnectionStatus.DISCONNECTED
            logger.info(f"Modbus设备 {self.device_id} 已断开连接")
            return True
            
        except Exception as e:
            logger.error(f"Modbus设备 {self.device_id} 断开连接异常: {e}")
            return False
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """读取Modbus设备数据"""
        if not self.is_connected():
            return None
        
        try:
            data = {
                "machine_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "is_virtual": False
            }
            
            # 读取寄存器数据
            for param, register_info in self.register_map.items():
                register_type = register_info.get("type", "holding")
                address = register_info.get("address", 0)
                count = register_info.get("count", 1)
                scale = register_info.get("scale", 1.0)
                offset = register_info.get("offset", 0.0)
                
                if register_type == "holding":
                    result = await self.client.read_holding_registers(
                        address, count, unit=self.unit_id
                    )
                elif register_type == "input":
                    result = await self.client.read_input_registers(
                        address, count, unit=self.unit_id
                    )
                elif register_type == "coil":
                    result = await self.client.read_coils(
                        address, count, unit=self.unit_id
                    )
                elif register_type == "discrete":
                    result = await self.client.read_discrete_inputs(
                        address, count, unit=self.unit_id
                    )
                else:
                    continue
                
                if not result.isError():
                    if register_type in ["holding", "input"]:
                        raw_value = result.registers[0] if count == 1 else result.registers
                    else:
                        raw_value = result.bits[0] if count == 1 else result.bits
                    
                    # 应用缩放和偏移
                    if isinstance(raw_value, (int, float)):
                        data[param] = raw_value * scale + offset
                    else:
                        data[param] = raw_value
                else:
                    logger.warning(f"读取寄存器 {address} 失败: {result}")
            
            self.last_data_time = datetime.now()
            self.error_count = 0
            return data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"读取Modbus设备 {self.device_id} 数据异常: {e}")
            
            if self.error_count >= self.max_errors:
                self.connection_status = ConnectionStatus.ERROR
            
            return None
    
    async def write_command(self, command: Dict[str, Any]) -> bool:
        """向Modbus设备发送命令"""
        if not self.is_connected():
            return False
        
        try:
            command_type = command.get("type")
            address = command.get("address")
            value = command.get("value")
            
            if command_type == "write_register":
                result = await self.client.write_register(
                    address, value, unit=self.unit_id
                )
            elif command_type == "write_registers":
                result = await self.client.write_registers(
                    address, value, unit=self.unit_id
                )
            elif command_type == "write_coil":
                result = await self.client.write_coil(
                    address, value, unit=self.unit_id
                )
            elif command_type == "write_coils":
                result = await self.client.write_coils(
                    address, value, unit=self.unit_id
                )
            else:
                logger.error(f"不支持的命令类型: {command_type}")
                return False
            
            if not result.isError():
                logger.info(f"向Modbus设备 {self.device_id} 发送命令成功")
                return True
            else:
                logger.error(f"向Modbus设备 {self.device_id} 发送命令失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"向Modbus设备 {self.device_id} 发送命令异常: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """获取Modbus设备信息"""
        return {
            "device_id": self.device_id,
            "protocol": "modbus_tcp",
            "host": self.host,
            "port": self.port,
            "unit_id": self.unit_id,
            "register_map": self.register_map,
            "connection_status": self.connection_status.value
        }

class OPCUADevice(DeviceInterface):
    """OPC UA设备接口"""
    
    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        super().__init__(device_id, device_config)
        self.client = None
        self.endpoint_url = device_config.get("endpoint_url", "opc.tcp://localhost:4840")
        self.security_policy = device_config.get("security_policy", "None")
        self.username = device_config.get("username")
        self.password = device_config.get("password")
        self.node_map = device_config.get("node_map", {})
    
    async def connect(self) -> bool:
        """连接OPC UA设备"""
        try:
            from asyncua import Client
            
            self.connection_status = ConnectionStatus.CONNECTING
            
            self.client = Client(url=self.endpoint_url)
            
            # 设置安全策略
            if self.security_policy != "None":
                self.client.set_security_string(self.security_policy)
            
            # 设置用户认证
            if self.username and self.password:
                self.client.set_user(self.username)
                self.client.set_password(self.password)
            
            await self.client.connect()
            
            self.connection_status = ConnectionStatus.CONNECTED
            self.error_count = 0
            logger.info(f"OPC UA设备 {self.device_id} 连接成功")
            return True
            
        except Exception as e:
            self.connection_status = ConnectionStatus.ERROR
            self.error_count += 1
            logger.error(f"OPC UA设备 {self.device_id} 连接异常: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开OPC UA设备连接"""
        try:
            if self.client:
                await self.client.disconnect()
                self.client = None
            
            self.connection_status = ConnectionStatus.DISCONNECTED
            logger.info(f"OPC UA设备 {self.device_id} 已断开连接")
            return True
            
        except Exception as e:
            logger.error(f"OPC UA设备 {self.device_id} 断开连接异常: {e}")
            return False
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """读取OPC UA设备数据"""
        if not self.is_connected():
            return None
        
        try:
            data = {
                "machine_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "is_virtual": False
            }
            
            # 读取节点数据
            for param, node_info in self.node_map.items():
                node_id = node_info.get("node_id")
                scale = node_info.get("scale", 1.0)
                offset = node_info.get("offset", 0.0)
                
                if node_id:
                    node = self.client.get_node(node_id)
                    raw_value = await node.read_value()
                    
                    # 应用缩放和偏移
                    if isinstance(raw_value, (int, float)):
                        data[param] = raw_value * scale + offset
                    else:
                        data[param] = raw_value
            
            self.last_data_time = datetime.now()
            self.error_count = 0
            return data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"读取OPC UA设备 {self.device_id} 数据异常: {e}")
            
            if self.error_count >= self.max_errors:
                self.connection_status = ConnectionStatus.ERROR
            
            return None
    
    async def write_command(self, command: Dict[str, Any]) -> bool:
        """向OPC UA设备发送命令"""
        if not self.is_connected():
            return False
        
        try:
            node_id = command.get("node_id")
            value = command.get("value")
            
            if node_id and value is not None:
                node = self.client.get_node(node_id)
                await node.write_value(value)
                
                logger.info(f"向OPC UA设备 {self.device_id} 发送命令成功")
                return True
            else:
                logger.error("命令参数不完整")
                return False
                
        except Exception as e:
            logger.error(f"向OPC UA设备 {self.device_id} 发送命令异常: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """获取OPC UA设备信息"""
        return {
            "device_id": self.device_id,
            "protocol": "opcua",
            "endpoint_url": self.endpoint_url,
            "security_policy": self.security_policy,
            "node_map": self.node_map,
            "connection_status": self.connection_status.value
        }

class VirtualDevice(DeviceInterface):
    """虚拟设备接口"""
    
    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        super().__init__(device_id, device_config)
        self.twin_manager = None
    
    async def connect(self) -> bool:
        """连接虚拟设备"""
        try:
            # 虚拟设备总是连接成功
            self.connection_status = ConnectionStatus.CONNECTED
            self.error_count = 0
            logger.info(f"虚拟设备 {self.device_id} 连接成功")
            return True
            
        except Exception as e:
            self.connection_status = ConnectionStatus.ERROR
            self.error_count += 1
            logger.error(f"虚拟设备 {self.device_id} 连接异常: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开虚拟设备连接"""
        try:
            self.connection_status = ConnectionStatus.DISCONNECTED
            logger.info(f"虚拟设备 {self.device_id} 已断开连接")
            return True
            
        except Exception as e:
            logger.error(f"虚拟设备 {self.device_id} 断开连接异常: {e}")
            return False
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """读取虚拟设备数据"""
        if not self.is_connected():
            return None
        
        try:
            # 从数字孪生获取数据
            if self.twin_manager:
                twin_data = await self.twin_manager.get_twin_state(self.device_id)
                if twin_data and "current_data" in twin_data:
                    self.last_data_time = datetime.now()
                    return twin_data["current_data"]
            
            # 如果没有数字孪生，生成模拟数据
            import random
            data = {
                "machine_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "temperature": random.uniform(25, 75),
                "vibration": random.uniform(0, 8),
                "current": random.uniform(5, 45),
                "speed": random.uniform(800, 2500),
                "pressure": random.uniform(2, 8),
                "tool_wear": random.uniform(0, 80),
                "power_consumption": random.uniform(10, 80),
                "is_virtual": True
            }
            
            self.last_data_time = datetime.now()
            return data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"读取虚拟设备 {self.device_id} 数据异常: {e}")
            return None
    
    async def write_command(self, command: Dict[str, Any]) -> bool:
        """向虚拟设备发送命令"""
        if not self.is_connected():
            return False
        
        try:
            # 虚拟设备命令处理
            command_type = command.get("type")
            
            if command_type == "start":
                logger.info(f"虚拟设备 {self.device_id} 启动")
            elif command_type == "stop":
                logger.info(f"虚拟设备 {self.device_id} 停止")
            elif command_type == "set_speed":
                speed = command.get("value", 1000)
                logger.info(f"虚拟设备 {self.device_id} 设置转速: {speed}")
            else:
                logger.warning(f"虚拟设备 {self.device_id} 不支持的命令: {command_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"向虚拟设备 {self.device_id} 发送命令异常: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """获取虚拟设备信息"""
        return {
            "device_id": self.device_id,
            "protocol": "virtual",
            "device_config": self.device_config,
            "connection_status": self.connection_status.value
        }
    
    def set_twin_manager(self, twin_manager):
        """设置数字孪生管理器"""
        self.twin_manager = twin_manager

class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInterface] = {}
        self.device_configs: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.data_collection_task = None
        self.twin_manager = None
    
    def set_twin_manager(self, twin_manager):
        """设置数字孪生管理器"""
        self.twin_manager = twin_manager
    
    async def initialize(self):
        """初始化设备管理器"""
        try:
            # 加载设备配置
            await self._load_device_configs()
            
            # 创建设备实例
            await self._create_devices()
            
            self.is_running = True
            logger.info("设备管理器初始化完成")
            
        except Exception as e:
            logger.error(f"设备管理器初始化失败: {e}")
            raise
    
    async def _load_device_configs(self):
        """加载设备配置"""
        # 默认设备配置
        self.device_configs = {
            "CNC001": {
                "type": "virtual",
                "name": "数控车床-001",
                "machine_type": "CNC_LATHE"
            },
            "MILL001": {
                "type": "virtual",
                "name": "铣床-001",
                "machine_type": "MILLING_MACHINE"
            },
            "DRILL001": {
                "type": "virtual",
                "name": "钻床-001",
                "machine_type": "DRILLING_MACHINE"
            }
        }
        
        # 可以从配置文件或数据库加载更多设备配置
        logger.info(f"加载了 {len(self.device_configs)} 个设备配置")
    
    async def _create_devices(self):
        """创建设备实例"""
        for device_id, config in self.device_configs.items():
            device_type = config.get("type", "virtual")
            
            if device_type == "modbus":
                device = ModbusDevice(device_id, config)
            elif device_type == "opcua":
                device = OPCUADevice(device_id, config)
            elif device_type == "virtual":
                device = VirtualDevice(device_id, config)
                if self.twin_manager:
                    device.set_twin_manager(self.twin_manager)
            else:
                logger.warning(f"不支持的设备类型: {device_type}")
                continue
            
            self.devices[device_id] = device
            logger.info(f"创建设备实例: {device_id} ({device_type})")
    
    async def add_device(self, device_id: str, device_config: Dict[str, Any]) -> bool:
        """添加设备"""
        try:
            if device_id in self.devices:
                logger.warning(f"设备 {device_id} 已存在")
                return False
            
            device_type = device_config.get("type", "virtual")
            
            if device_type == "modbus":
                device = ModbusDevice(device_id, device_config)
            elif device_type == "opcua":
                device = OPCUADevice(device_id, device_config)
            elif device_type == "virtual":
                device = VirtualDevice(device_id, device_config)
                if self.twin_manager:
                    device.set_twin_manager(self.twin_manager)
            else:
                logger.error(f"不支持的设备类型: {device_type}")
                return False
            
            self.devices[device_id] = device
            self.device_configs[device_id] = device_config
            
            logger.info(f"添加设备: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加设备失败: {e}")
            return False
    
    async def remove_device(self, device_id: str) -> bool:
        """移除设备"""
        try:
            if device_id not in self.devices:
                logger.warning(f"设备 {device_id} 不存在")
                return False
            
            device = self.devices[device_id]
            await device.disconnect()
            
            del self.devices[device_id]
            del self.device_configs[device_id]
            
            logger.info(f"移除设备: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"移除设备失败: {e}")
            return False
    
    async def connect_device(self, device_id: str) -> bool:
        """连接设备"""
        if device_id not in self.devices:
            logger.error(f"设备 {device_id} 不存在")
            return False
        
        device = self.devices[device_id]
        return await device.connect()
    
    async def disconnect_device(self, device_id: str) -> bool:
        """断开设备连接"""
        if device_id not in self.devices:
            logger.error(f"设备 {device_id} 不存在")
            return False
        
        device = self.devices[device_id]
        return await device.disconnect()
    
    async def connect_all_devices(self):
        """连接所有设备"""
        tasks = []
        for device_id, device in self.devices.items():
            tasks.append(device.connect())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        logger.info(f"连接设备完成: {success_count}/{len(self.devices)} 成功")
    
    async def disconnect_all_devices(self):
        """断开所有设备连接"""
        tasks = []
        for device_id, device in self.devices.items():
            tasks.append(device.disconnect())
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("所有设备已断开连接")
    
    async def read_device_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """读取设备数据"""
        if device_id not in self.devices:
            logger.error(f"设备 {device_id} 不存在")
            return None
        
        device = self.devices[device_id]
        return await device.read_data()
    
    async def send_device_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """向设备发送命令"""
        if device_id not in self.devices:
            logger.error(f"设备 {device_id} 不存在")
            return False
        
        device = self.devices[device_id]
        return await device.write_command(command)
    
    async def switch_device_mode(self, device_id: str, target_type: str) -> bool:
        """切换设备模式（真实/虚拟）"""
        try:
            if device_id not in self.devices:
                logger.error(f"设备 {device_id} 不存在")
                return False
            
            current_device = self.devices[device_id]
            current_config = self.device_configs[device_id].copy()
            
            # 断开当前设备
            await current_device.disconnect()
            
            # 更新配置
            current_config["type"] = target_type
            
            # 创建新设备实例
            if target_type == "modbus":
                new_device = ModbusDevice(device_id, current_config)
            elif target_type == "opcua":
                new_device = OPCUADevice(device_id, current_config)
            elif target_type == "virtual":
                new_device = VirtualDevice(device_id, current_config)
                if self.twin_manager:
                    new_device.set_twin_manager(self.twin_manager)
            else:
                logger.error(f"不支持的设备类型: {target_type}")
                return False
            
            # 替换设备实例
            self.devices[device_id] = new_device
            self.device_configs[device_id] = current_config
            
            # 连接新设备
            await new_device.connect()
            
            logger.info(f"设备 {device_id} 已切换到 {target_type} 模式")
            return True
            
        except Exception as e:
            logger.error(f"切换设备模式失败: {e}")
            return False
    
    async def start_data_collection(self, interval: float = 1.0):
        """启动数据采集"""
        if self.data_collection_task:
            logger.warning("数据采集任务已在运行")
            return
        
        self.data_collection_task = asyncio.create_task(
            self._data_collection_loop(interval)
        )
        logger.info(f"启动数据采集，采集间隔: {interval}秒")
    
    async def stop_data_collection(self):
        """停止数据采集"""
        if self.data_collection_task:
            self.data_collection_task.cancel()
            try:
                await self.data_collection_task
            except asyncio.CancelledError:
                pass
            self.data_collection_task = None
            logger.info("数据采集已停止")
    
    async def _data_collection_loop(self, interval: float):
        """数据采集循环"""
        while self.is_running:
            try:
                # 并行读取所有设备数据
                tasks = []
                for device_id, device in self.devices.items():
                    if device.is_connected():
                        tasks.append(device.read_data())
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 处理采集结果
                    for i, result in enumerate(results):
                        if isinstance(result, dict) and result:
                            # 这里可以将数据发送到MQTT或其他处理模块
                            logger.debug(f"采集到设备数据: {result.get('machine_id')}")
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"数据采集循环异常: {e}")
                await asyncio.sleep(interval)
    
    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """获取设备状态"""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        return device.get_status()
    
    def get_all_devices_status(self) -> Dict[str, Any]:
        """获取所有设备状态"""
        status = {
            "total_devices": len(self.devices),
            "connected_devices": sum(1 for device in self.devices.values() if device.is_connected()),
            "devices": {}
        }
        
        for device_id, device in self.devices.items():
            status["devices"][device_id] = device.get_status()
        
        return status
    
    async def shutdown(self):
        """关闭设备管理器"""
        try:
            self.is_running = False
            
            # 停止数据采集
            await self.stop_data_collection()
            
            # 断开所有设备
            await self.disconnect_all_devices()
            
            # 清理设备实例
            self.devices.clear()
            self.device_configs.clear()
            
            logger.info("设备管理器已关闭")
            
        except Exception as e:
