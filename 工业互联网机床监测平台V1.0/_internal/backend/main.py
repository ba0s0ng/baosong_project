"""
工业互联网机床状态监测平台 - FastAPI主应用
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
import uvicorn

from config import settings
from backend.models import MachineData, MachineStatus, AlarmEvent
from backend.mqtt_client import MQTTClient
from backend.database import DatabaseManager
from backend.websocket_manager import WebSocketManager
from rules_engine.rule_engine import RuleEngine
from digital_twin.twin_manager import DigitalTwinManager

# WebSocket连接管理器
websocket_manager = WebSocketManager()

# 全局组件实例
mqtt_client = None
db_manager = None
rule_engine = None
twin_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global mqtt_client, db_manager, rule_engine, twin_manager
    
    # 启动时初始化组件
    print("🚀 启动工业互联网机床状态监测平台...")
    
    # 初始化数据库管理器
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    # 初始化MQTT客户端
    mqtt_client = MQTTClient()
    await mqtt_client.connect()
    
    # 初始化规则引擎
    rule_engine = RuleEngine()
    rule_engine.load_rules()
    
    # 初始化数字孪生管理器
    twin_manager = DigitalTwinManager()
    await twin_manager.initialize()
    
    # 启动后台任务
    asyncio.create_task(data_processing_task())
    asyncio.create_task(twin_update_task())
    
    print("✅ 平台启动完成")
    
    yield
    
    # 关闭时清理资源
    print("🔄 正在关闭平台...")
    if mqtt_client:
        await mqtt_client.disconnect()
    if db_manager:
        await db_manager.close()
    if twin_manager:
        await twin_manager.shutdown()
    print("✅ 平台已关闭")

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于工业互联网标准的机床状态监测平台",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "components": {
            "mqtt": mqtt_client.is_connected() if mqtt_client else False,
            "database": db_manager.is_connected() if db_manager else False,
            "rule_engine": rule_engine.is_active() if rule_engine else False,
            "digital_twin": twin_manager.is_running() if twin_manager else False
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/machines")
async def get_machines():
    """获取所有机床列表"""
    try:
        machines = await db_manager.get_all_machines()
        return {"machines": machines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/machines/{machine_id}/status")
async def get_machine_status(machine_id: str):
    """获取指定机床状态"""
    try:
        status = await db_manager.get_machine_status(machine_id)
        if not status:
            raise HTTPException(status_code=404, detail="机床未找到")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/machines/{machine_id}/data")
async def get_machine_data(machine_id: str, limit: int = 100):
    """获取机床历史数据"""
    try:
        data = await db_manager.get_machine_data(machine_id, limit)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alarms")
async def get_alarms(limit: int = 50):
    """获取报警信息"""
    try:
        alarms = await db_manager.get_alarms(limit)
        return {"alarms": alarms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/machines/{machine_id}/control")
async def control_machine(machine_id: str, command: Dict[str, Any]):
    """机床控制命令"""
    try:
        # 发送控制命令到MQTT
        topic = f"industrial/machine/{machine_id}/control"
        await mqtt_client.publish(topic, json.dumps(command))
        
        # 记录控制日志
        await db_manager.log_control_command(machine_id, command)
        
        return {"status": "success", "message": "控制命令已发送"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/digital-twin/{machine_id}")
async def get_digital_twin(machine_id: str):
    """获取数字孪生模型状态"""
    try:
        twin_data = await twin_manager.get_twin_state(machine_id)
        if not twin_data:
            raise HTTPException(status_code=404, detail="数字孪生模型未找到")
        return twin_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            data = await websocket.receive_text()
            # 处理客户端消息
            message = json.loads(data)
            await handle_websocket_message(websocket, message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """处理WebSocket消息"""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # 订阅特定机床数据
        machine_id = message.get("machine_id")
        await websocket_manager.subscribe(websocket, machine_id)
    elif message_type == "unsubscribe":
        # 取消订阅
        machine_id = message.get("machine_id")
        await websocket_manager.unsubscribe(websocket, machine_id)

async def data_processing_task():
    """数据处理后台任务"""
    while True:
        try:
            # 处理MQTT接收到的数据
            if mqtt_client and mqtt_client.has_pending_data():
                data = await mqtt_client.get_pending_data()
                
                # 存储到数据库
                await db_manager.store_machine_data(data)
                
                # 规则引擎处理
                alarm = await rule_engine.process_data(data)
                if alarm:
                    # 发送报警
                    await websocket_manager.broadcast_alarm(alarm)
                    await db_manager.store_alarm(alarm)
                
                # 更新数字孪生
                await twin_manager.update_from_real_data(data)
                
                # 广播实时数据
                await websocket_manager.broadcast_data(data)
            
            await asyncio.sleep(0.1)  # 100ms处理间隔
        except Exception as e:
            print(f"数据处理任务错误: {e}")
            await asyncio.sleep(1)

async def twin_update_task():
    """数字孪生更新任务"""
    while True:
        try:
            if twin_manager:
                # 更新物理仿真
                await twin_manager.update_physics()
                
                # 生成虚拟数据（当没有真实设备时）
                virtual_data = await twin_manager.generate_virtual_data()
                if virtual_data:
                    # 处理虚拟数据
                    await db_manager.store_machine_data(virtual_data)
                    await websocket_manager.broadcast_data(virtual_data)
            
            await asyncio.sleep(settings.DIGITAL_TWIN_UPDATE_INTERVAL)
        except Exception as e:
            print(f"数字孪生更新任务错误: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG
    )
