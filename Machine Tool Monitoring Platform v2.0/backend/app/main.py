from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import random
import time
from datetime import datetime

from .routes import router
from .db import init_db, execute_query, fetch_all

# 创建FastAPI应用实例
app = FastAPI(
    title="工业互联网机床监测平台API",
    description="提供工业互联网机床监测平台的后端服务API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

# 简单的模拟数据生成函数
def generate_mock_data():
    while True:
        try:
            # 获取所有设备
            machines = fetch_all("SELECT id, name FROM machines")
            
            for machine in machines:
                # 生成模拟数据
                temperature = round(random.uniform(30.0, 80.0), 2)
                vibration = round(random.uniform(0.1, 5.0), 2)
                noise = round(random.uniform(40, 100), 2)
                power_consumption = round(random.uniform(1000, 5000), 2)
                operating_hours = round(random.uniform(0, 24), 1)
                
                # 插入数据
                execute_query(
                    "INSERT INTO machine_data (machine_id, temperature, vibration, noise, power_consumption, operating_hours, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (machine['id'], temperature, vibration, noise, power_consumption, operating_hours, datetime.now().isoformat())
                )
                
                # 检查报警规则
                rules = fetch_all("SELECT id, parameter, threshold, comparison FROM alarm_rules WHERE is_active = 1")
                for rule in rules:
                    param_value = locals()[rule['parameter']]
                    threshold = float(rule['threshold'])
                    trigger_alarm = False
                    
                    if rule['comparison'] == '>' and param_value > threshold:
                        trigger_alarm = True
                    elif rule['comparison'] == '<' and param_value < threshold:
                        trigger_alarm = True
                    elif rule['comparison'] == '>=' and param_value >= threshold:
                        trigger_alarm = True
                    elif rule['comparison'] == '<=' and param_value <= threshold:
                        trigger_alarm = True
                    
                    if trigger_alarm:
                        execute_query(
                            "INSERT INTO alarms (machine_id, rule_id, value, message, timestamp) VALUES (?, ?, ?, ?, ?)",
                            (machine['id'], rule['id'], param_value, f"{rule['parameter']} {rule['comparison']} {threshold}", datetime.now().isoformat())
                        )
        except Exception as e:
            print(f"生成模拟数据时出错: {e}")
        
        # 每5秒生成一次数据
        time.sleep(5)

# 启动事件
@app.on_event("startup")
def startup_event():
    # 初始化数据库
    init_db()
    # 启动模拟数据生成线程
    data_thread = threading.Thread(target=generate_mock_data, daemon=True)
    data_thread.start()

@app.get("/")
def root():
    return {"message": "工业互联网机床监测平台API服务运行中"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)