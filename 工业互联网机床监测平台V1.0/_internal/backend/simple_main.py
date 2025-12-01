"""
工业互联网机床状态监测平台 - 简化版本主应用
用于快速启动和测试基础功能
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import random
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
import os
from pathlib import Path

# 创建FastAPI应用
app = FastAPI(
    title="工业互联网机床状态监测平台",
    version="2.0.0",
    description="基于工业互联网标准的机床状态监测平台 - 基础版本"
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
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# 历史数据存储
historical_data = {}
alarms_data = []

# 生成2024年1月1日至今的历史数据
def generate_historical_data():
    """生成从2024年1月1日至今的历史数据"""
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()
    
    # 每小时生成一条数据
    current_date = start_date
    while current_date <= end_date:
        timestamp = current_date.isoformat()
        
        for machine_id in machines_data.keys():
            machine = machines_data[machine_id]
            
            # 生成历史数据点
            historical_point = {
                "machine_id": machine_id,
                "timestamp": timestamp,
                "temperature": random.uniform(25, 75),
                "vibration": random.uniform(0.5, 8.0),
                "current": random.uniform(2, 25),
                "speed": random.uniform(0, 2500),
                "pressure": random.uniform(1, 10),
                "efficiency": random.uniform(70, 95),
                "status": random.choice(["running", "idle", "maintenance", "offline"]),
                "is_historical": True
            }
            
            # 存储历史数据
            key = f"{machine_id}_{int(current_date.timestamp())}"
            historical_data[key] = historical_point
        
        current_date += timedelta(hours=1)
    
    print(f"生成历史数据完成，共 {len(historical_data)} 条记录")

# 生成随机报警信息
def generate_random_alarms():
    """生成随机报警信息"""
    alarm_types = ["temperature", "vibration", "current", "speed", "pressure", "tool_wear"]
    alarm_levels = ["WARNING", "CRITICAL", "INFO"]
    
    # 为每台机床生成一些历史报警
    for machine_id in machines_data.keys():
        machine = machines_data[machine_id]
        
        # 随机生成5-15个报警
        num_alarms = random.randint(5, 15)
        
        for i in range(num_alarms):
            alarm_time = datetime.now() - timedelta(
                days=random.randint(0, 300),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            alarm_type = random.choice(alarm_types)
            alarm_level = random.choice(alarm_levels)
            
            # 根据类型生成相应的报警消息
            messages = {
                "temperature": f"机床 {machine_id} 温度异常: {random.uniform(70, 90):.1f}°C",
                "vibration": f"机床 {machine_id} 振动过大: {random.uniform(5, 10):.1f}mm/s",
                "current": f"机床 {machine_id} 电流异常: {random.uniform(25, 40):.1f}A",
                "speed": f"机床 {machine_id} 转速异常: {random.randint(2500, 3500)}rpm",
                "pressure": f"机床 {machine_id} 压力异常: {random.uniform(10, 15):.1f}bar",
                "tool_wear": f"机床 {machine_id} 刀具磨损严重: {random.uniform(85, 100):.1f}%"
            }
            
            alarm = {
                "id": f"ALARM_{machine_id}_{int(alarm_time.timestamp())}_{i}",
                "machine_id": machine_id,
                "type": alarm_type,
                "level": alarm_level,
                "message": messages[alarm_type],
                "timestamp": alarm_time.isoformat(),
                "acknowledged": random.choice([True, False]),
                "is_historical": True
            }
            
            alarms_data.append(alarm)
    
    # 按时间排序
    alarms_data.sort(key=lambda x: x["timestamp"], reverse=True)
    print(f"生成报警数据完成，共 {len(alarms_data)} 条记录")

# 模拟数据存储 - 10款国内外主流机床品牌
machines_data = {
    # 德国DMG MORI数控车床
    "DMG001": {
        "id": "DMG001",
        "name": "DMG MORI CTX beta 800",
        "brand": "DMG MORI",
        "country": "德国",
        "type": "CNC_LATHE",
        "model": "CTX beta 800",
        "status": "running",
        "temperature": 45.2,
        "vibration": 2.1,
        "current": 15.8,
        "speed": 1200,
        "pressure": 6.5,
        "tool_wear": 25.0,
        "power_consumption": 12.5,
        "is_virtual": True,
        "location": "车间A-01",
        "installation_date": "2023-06-15",
        "last_maintenance": "2024-09-01",
        "next_maintenance": "2024-12-01",
        "last_update": datetime.now().isoformat()
    },
    # 日本MAZAK加工中心
    "MAZAK001": {
        "id": "MAZAK001",
        "name": "MAZAK VARIAXIS i-700",
        "brand": "MAZAK",
        "country": "日本",
        "type": "MACHINING_CENTER",
        "model": "VARIAXIS i-700",
        "status": "running",
        "temperature": 38.7,
        "vibration": 1.8,
        "current": 12.3,
        "speed": 800,
        "pressure": 5.2,
        "tool_wear": 15.0,
        "power_consumption": 18.9,
        "is_virtual": True,
        "location": "车间A-02",
        "installation_date": "2023-08-20",
        "last_maintenance": "2024-08-15",
        "next_maintenance": "2024-11-15",
        "last_update": datetime.now().isoformat()
    },
    # 瑞士STUDER磨床
    "STUDER001": {
        "id": "STUDER001",
        "name": "STUDER S33",
        "brand": "STUDER",
        "country": "瑞士",
        "type": "GRINDING_MACHINE",
        "model": "S33",
        "status": "idle",
        "temperature": 25.0,
        "vibration": 0.5,
        "current": 2.1,
        "speed": 0,
        "pressure": 2.0,
        "tool_wear": 8.0,
        "power_consumption": 3.2,
        "is_virtual": True,
        "location": "车间B-01",
        "installation_date": "2023-05-10",
        "last_maintenance": "2024-07-20",
        "next_maintenance": "2024-10-20",
        "last_update": datetime.now().isoformat()
    },
    # 中国沈阳机床数控车床
    "SMTCL001": {
        "id": "SMTCL001",
        "name": "沈阳机床CAK6150",
        "brand": "沈阳机床",
        "country": "中国",
        "type": "CNC_LATHE",
        "model": "CAK6150",
        "status": "running",
        "temperature": 42.5,
        "vibration": 2.3,
        "current": 14.2,
        "speed": 1100,
        "pressure": 6.0,
        "tool_wear": 32.0,
        "power_consumption": 11.8,
        "is_virtual": True,
        "location": "车间A-03",
        "installation_date": "2023-07-05",
        "last_maintenance": "2024-08-10",
        "next_maintenance": "2024-11-10",
        "last_update": datetime.now().isoformat()
    },
    # 美国HAAS加工中心
    "HAAS001": {
        "id": "HAAS001",
        "name": "HAAS VF-4SS",
        "brand": "HAAS",
        "country": "美国",
        "type": "MACHINING_CENTER",
        "model": "VF-4SS",
        "status": "running",
        "temperature": 41.3,
        "vibration": 1.9,
        "current": 13.7,
        "speed": 900,
        "pressure": 5.8,
        "tool_wear": 22.0,
        "power_consumption": 16.5,
        "is_virtual": True,
        "location": "车间A-04",
        "installation_date": "2023-09-12",
        "last_maintenance": "2024-09-05",
        "next_maintenance": "2024-12-05",
        "last_update": datetime.now().isoformat()
    },
    # 德国TRUMPF激光切割机
    "TRUMPF001": {
        "id": "TRUMPF001",
        "name": "TRUMPF TruLaser 3030",
        "brand": "TRUMPF",
        "country": "德国",
        "type": "LASER_CUTTING",
        "model": "TruLaser 3030",
        "status": "running",
        "temperature": 35.8,
        "vibration": 0.8,
        "current": 25.4,
        "speed": 1500,
        "pressure": 8.2,
        "tool_wear": 5.0,
        "power_consumption": 28.3,
        "is_virtual": True,
        "location": "车间C-01",
        "installation_date": "2023-04-18",
        "last_maintenance": "2024-08-25",
        "next_maintenance": "2024-11-25",
        "last_update": datetime.now().isoformat()
    },
    # 中国大连机床加工中心
    "DALIAN001": {
        "id": "DALIAN001",
        "name": "大连机床VDL-1000A",
        "brand": "大连机床",
        "country": "中国",
        "type": "MACHINING_CENTER",
        "model": "VDL-1000A",
        "status": "maintenance",
        "temperature": 28.5,
        "vibration": 0.3,
        "current": 1.8,
        "speed": 0,
        "pressure": 1.5,
        "tool_wear": 45.0,
        "power_consumption": 2.1,
        "is_virtual": True,
        "location": "车间A-05",
        "installation_date": "2023-03-22",
        "last_maintenance": "2024-10-01",
        "next_maintenance": "2024-10-15",
        "last_update": datetime.now().isoformat()
    },
    # 日本OKUMA数控车床
    "OKUMA001": {
        "id": "OKUMA001",
        "name": "OKUMA GENOS L3000-M",
        "brand": "OKUMA",
        "country": "日本",
        "type": "CNC_LATHE",
        "model": "GENOS L3000-M",
        "status": "running",
        "temperature": 44.1,
        "vibration": 2.0,
        "current": 16.2,
        "speed": 1300,
        "pressure": 6.8,
        "tool_wear": 28.5,
        "power_consumption": 13.7,
        "is_virtual": True,
        "location": "车间A-06",
        "installation_date": "2023-06-30",
        "last_maintenance": "2024-09-10",
        "next_maintenance": "2024-12-10",
        "last_update": datetime.now().isoformat()
    },
    # 意大利FIDIA加工中心
    "FIDIA001": {
        "id": "FIDIA001",
        "name": "FIDIA K193",
        "brand": "FIDIA",
        "country": "意大利",
        "type": "MACHINING_CENTER",
        "model": "K193",
        "status": "idle",
        "temperature": 32.2,
        "vibration": 0.7,
        "current": 3.5,
        "speed": 0,
        "pressure": 3.0,
        "tool_wear": 12.0,
        "power_consumption": 4.8,
        "is_virtual": True,
        "location": "车间B-02",
        "installation_date": "2023-05-25",
        "last_maintenance": "2024-07-30",
        "next_maintenance": "2024-10-30",
        "last_update": datetime.now().isoformat()
    },
    # 中国华中数控加工中心
    "HZNC001": {
        "id": "HZNC001",
        "name": "华中数控HMC500",
        "brand": "华中数控",
        "country": "中国",
        "type": "MACHINING_CENTER",
        "model": "HMC500",
        "status": "running",
        "temperature": 39.6,
        "vibration": 1.7,
        "current": 11.9,
        "speed": 750,
        "pressure": 5.5,
        "tool_wear": 18.5,
        "power_consumption": 15.2,
        "is_virtual": True,
        "location": "车间A-07",
        "installation_date": "2023-08-08",
        "last_maintenance": "2024-08-20",
        "next_maintenance": "2024-11-20",
        "last_update": datetime.now().isoformat()
    }
}

# 历史数据存储
historical_data = {}
alarms_data = []

# WebSocket连接管理
active_connections: List[WebSocket] = []

# ==================== 页面路由 ====================

@app.get("/")
async def root():
    """根路径 - 重定向到仪表盘页面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard():
    """仪表盘页面"""
    frontend_file = frontend_path / "dashboard.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return HTMLResponse(content="<h1>仪表盘页面</h1><p>正在开发中...</p>")

@app.get("/machines")
async def machines_page():
    """机床管理页面"""
    frontend_file = frontend_path / "machines.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return HTMLResponse(content="<h1>机床管理页面</h1><p>正在开发中...</p>")

@app.get("/digital-twin")
async def digital_twin_page():
    """数字孪生页面"""
    frontend_file = frontend_path / "digital_twin.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return HTMLResponse(content="<h1>数字孪生页面</h1><p>正在开发中...</p>")

@app.get("/alarms")
async def alarms_page():
    """报警管理页面"""
    frontend_file = frontend_path / "alarms.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return HTMLResponse(content="<h1>报警管理页面</h1><p>正在开发中...</p>")

@app.get("/analytics")
async def analytics_page():
    """数据分析页面"""
    frontend_file = frontend_path / "analytics.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return HTMLResponse(content="<h1>数据分析页面</h1><p>正在开发中...</p>")

@app.get("/database")
async def database_page():
    """数据库管理页面"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>数据库管理 - 工业互联网机床状态监测平台</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1, h2 { color: #2c3e50; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .btn { background: #3498db; color: white; padding: 8px 15px; border: none; border-radius: 3px; cursor: pointer; margin: 5px; }
                .btn:hover { background: #2980b9; }
                .btn-danger { background: #e74c3c; }
                .btn-danger:hover { background: #c0392b; }
                .btn-success { background: #27ae60; }
                .btn-success:hover { background: #229954; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #f8f9fa; }
                .status-running { color: #27ae60; font-weight: bold; }
                .status-idle { color: #f39c12; font-weight: bold; }
                .nav-back { margin-bottom: 20px; }
                .nav-back a { color: #3498db; text-decoration: none; }
                .nav-back a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav-back">
                    <a href="/">← 返回主页</a>
                </div>
                <h1>💾 数据库管理</h1>
                
                <div class="section">
                    <h2>🔧 机床数据管理</h2>
                    <button class="btn" onclick="loadMachineData()">刷新机床数据</button>
                    <button class="btn btn-success" onclick="exportData('machines')">导出机床数据</button>
                    <button class="btn btn-danger" onclick="clearData('machines')">清空机床数据</button>
                    <div id="machineData"></div>
                </div>
                
                <div class="section">
                    <h2>🎯 数字孪生数据管理</h2>
                    <button class="btn" onclick="loadTwinData()">刷新孪生数据</button>
                    <button class="btn btn-success" onclick="exportData('twins')">导出孪生数据</button>
                    <button class="btn btn-danger" onclick="clearData('twins')">清空孪生数据</button>
                    <div id="twinData"></div>
                </div>
                
                <div class="section">
                    <h2>📊 历史数据管理</h2>
                    <button class="btn" onclick="loadHistoricalData()">刷新历史数据</button>
                    <button class="btn btn-success" onclick="exportData('historical')">导出历史数据</button>
                    <button class="btn btn-danger" onclick="clearData('historical')">清空历史数据</button>
                    <div id="historicalData"></div>
                </div>
                
                <div class="section">
                    <h2>⚠️ 报警数据管理</h2>
                    <button class="btn" onclick="loadAlarmData()">刷新报警数据</button>
                    <button class="btn btn-success" onclick="exportData('alarms')">导出报警数据</button>
                    <button class="btn btn-danger" onclick="clearData('alarms')">清空报警数据</button>
                    <div id="alarmData"></div>
                </div>
                
                <div class="section">
                    <h2>🔄 数据同步</h2>
                    <button class="btn btn-success" onclick="syncData()">同步真实数据到孪生</button>
                    <button class="btn btn-success" onclick="syncTwinToReal()">同步孪生数据到真实</button>
                    <p><small>注意：数据同步将覆盖目标数据源的现有数据</small></p>
                </div>
            </div>
            
            <script>
                async function loadMachineData() {
                    try {
                        const response = await fetch('/api/machines');
                        const data = await response.json();
                        const html = `
                            <h3>机床数据 (${data.machines.length} 条记录)</h3>
                            <table>
                                <tr><th>ID</th><th>名称</th><th>类型</th><th>状态</th><th>温度</th><th>振动</th><th>转速</th><th>最后更新</th></tr>
                                ${data.machines.map(m => `
                                    <tr>
                                        <td>${m.id}</td>
                                        <td>${m.name}</td>
                                        <td>${m.type}</td>
                                        <td class="status-${m.status}">${m.status}</td>
                                        <td>${m.temperature.toFixed(1)}°C</td>
                                        <td>${m.vibration.toFixed(2)}mm/s</td>
                                        <td>${m.speed}rpm</td>
                                        <td>${new Date(m.last_update).toLocaleString()}</td>
                                    </tr>
                                `).join('')}
                            </table>
                        `;
                        document.getElementById('machineData').innerHTML = html;
                    } catch (error) {
                        document.getElementById('machineData').innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
                    }
                }
                
                async function loadTwinData() {
                    try {
                        const machines = ['DMG001', 'MAZAK001', 'STUDER001', 'SMTCL001', 'HAAS001', 'TRUMPF001', 'DALIAN001', 'OKUMA001', 'FIDIA001', 'HZNC001'];
                        let html = '<h3>数字孪生数据</h3><table><tr><th>机床ID</th><th>品牌</th><th>健康评分</th><th>剩余寿命</th><th>运行状态</th><th>预测温度</th></tr>';
                        
                        for (const machineId of machines) {
                            try {
                                const response = await fetch(`/api/digital-twin/${machineId}`);
                                const data = await response.json();
                                html += `
                                    <tr>
                                        <td>${data.machine_id}</td>
                                        <td>${data.current_data.brand || 'N/A'}</td>
                                        <td>${data.health_score}%</td>
                                        <td>${data.remaining_life ? data.remaining_life + 'h' : 'N/A'}</td>
                                        <td>${data.physics_state.is_running ? '运行中' : '停止'}</td>
                                        <td>${data.predicted_values.temperature_1h.toFixed(1)}°C</td>
                                    </tr>
                                `;
                            } catch (err) {
                                html += `
                                    <tr>
                                        <td>${machineId}</td>
                                        <td colspan="5" style="color: red;">数据加载失败</td>
                                    </tr>
                                `;
                            }
                        }
                        html += '</table>';
                        document.getElementById('twinData').innerHTML = html;
                    } catch (error) {
                        document.getElementById('twinData').innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
                    }
                }
                
                async function loadHistoricalData() {
                    try {
                        const response = await fetch('/api/database/historical');
                        const data = await response.json();
                        const html = `
                            <h3>历史数据 (${data.total_records} 条记录)</h3>
                            <p>数据时间范围: ${data.time_range.start} 至 ${data.time_range.end}</p>
                            <p>存储大小: ${data.storage_size}</p>
                        `;
                        document.getElementById('historicalData').innerHTML = html;
                    } catch (error) {
                        document.getElementById('historicalData').innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
                    }
                }
                
                async function loadAlarmData() {
                    try {
                        const response = await fetch('/api/alarms');
                        const data = await response.json();
                        const html = `
                            <h3>报警数据 (${data.alarms.length} 条记录)</h3>
                            <table>
                                <tr><th>机床ID</th><th>类型</th><th>级别</th><th>消息</th><th>时间</th></tr>
                                ${data.alarms.slice(0, 10).map(a => `
                                    <tr>
                                        <td>${a.machine_id}</td>
                                        <td>${a.type}</td>
                                        <td style="color: ${a.level === 'CRITICAL' ? 'red' : 'orange'}">${a.level}</td>
                                        <td>${a.message}</td>
                                        <td>${new Date(a.timestamp).toLocaleString()}</td>
                                    </tr>
                                `).join('')}
                            </table>
                            ${data.alarms.length > 10 ? '<p>显示最近10条记录...</p>' : ''}
                        `;
                        document.getElementById('alarmData').innerHTML = html;
                    } catch (error) {
                        document.getElementById('alarmData').innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
                    }
                }
                
                async function exportData(type) {
                    try {
                        const response = await fetch(`/api/database/export/${type}`);
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${type}_data_${new Date().toISOString().split('T')[0]}.json`;
                        a.click();
                        window.URL.revokeObjectURL(url);
                        alert('数据导出成功！');
                    } catch (error) {
                        alert('导出失败: ' + error.message);
                    }
                }
                
                async function clearData(type) {
                    if (!confirm(`确定要清空${type}数据吗？此操作不可恢复！`)) return;
                    
                    try {
                        const response = await fetch(`/api/database/clear/${type}`, { method: 'DELETE' });
                        const result = await response.json();
                        alert(result.message);
                        // 重新加载数据
                        if (type === 'machines') loadMachineData();
                        else if (type === 'twins') loadTwinData();
                        else if (type === 'historical') loadHistoricalData();
                        else if (type === 'alarms') loadAlarmData();
                    } catch (error) {
                        alert('清空失败: ' + error.message);
                    }
                }
                
                async function syncData() {
                    try {
                        const response = await fetch('/api/database/sync/real-to-twin', { method: 'POST' });
                        const result = await response.json();
                        alert(result.message);
                        loadTwinData();
                    } catch (error) {
                        alert('同步失败: ' + error.message);
                    }
                }
                
                async function syncTwinToReal() {
                    try {
                        const response = await fetch('/api/database/sync/twin-to-real', { method: 'POST' });
                        const result = await response.json();
                        alert(result.message);
                        loadMachineData();
                    } catch (error) {
                        alert('同步失败: ' + error.message);
                    }
                }
                
                // 页面加载时自动加载数据
                window.onload = function() {
                    loadMachineData();
                    loadTwinData();
                    loadHistoricalData();
                    loadAlarmData();
                };
            </script>
        </body>
    </html>
    """)

# ==================== API路由 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "components": {
            "api": True,
            "websocket": True,
            "digital_twin": True,
            "rules_engine": True,
            "database": True
        }
    }

@app.get("/api/machines")
async def get_machines():
    """获取所有机床列表"""
    return {"machines": list(machines_data.values())}

@app.get("/api/machines/{machine_id}")
async def get_machine(machine_id: str):
    """获取指定机床信息"""
    if machine_id not in machines_data:
        raise HTTPException(status_code=404, detail="机床未找到")
    
    # 更新模拟数据
    machine = machines_data[machine_id].copy()
    if machine["status"] == "running":
        machine["temperature"] += random.uniform(-2, 2)
        machine["vibration"] += random.uniform(-0.5, 0.5)
        machine["current"] += random.uniform(-1, 1)
        machine["speed"] += random.uniform(-50, 50)
        machine["pressure"] += random.uniform(-0.5, 0.5)
        machine["tool_wear"] += random.uniform(0, 0.1)
        machine["power_consumption"] += random.uniform(-1, 1)
        
        # 确保数值在合理范围内
        machine["temperature"] = max(20, min(80, machine["temperature"]))
        machine["vibration"] = max(0, min(10, machine["vibration"]))
        machine["current"] = max(0, min(50, machine["current"]))
        machine["speed"] = max(0, min(3000, machine["speed"]))
        machine["pressure"] = max(0, min(10, machine["pressure"]))
        machine["tool_wear"] = max(0, min(100, machine["tool_wear"]))
        machine["power_consumption"] = max(0, min(100, machine["power_consumption"]))
    
    machine["last_update"] = datetime.now().isoformat()
    machines_data[machine_id] = machine
    
    return machine

@app.post("/api/machines/{machine_id}/control")
async def control_machine(machine_id: str, command: Dict[str, Any]):
    """机床控制命令"""
    if machine_id not in machines_data:
        raise HTTPException(status_code=404, detail="机床未找到")
    
    machine = machines_data[machine_id]
    command_type = command.get("type")
    
    if command_type == "start":
        machine["status"] = "running"
        if machine["speed"] == 0:
            machine["speed"] = 1000  # 默认启动转速
        machine["current"] = 15.0
    elif command_type == "stop":
        machine["status"] = "idle"
        machine["speed"] = 0
        machine["current"] = 2.0
    elif command_type == "set_status":
        new_status = command.get("status")
        if new_status in ["running", "idle", "offline", "error", "maintenance"]:
            machine["status"] = new_status
            if new_status == "running":
                if machine["speed"] == 0:
                    machine["speed"] = 1000
                machine["current"] = 15.0
            elif new_status in ["idle", "offline", "error", "maintenance"]:
                machine["speed"] = 0
                machine["current"] = 2.0 if new_status != "offline" else 0.0
    elif command_type == "set_speed":
        if machine["status"] == "running":
            machine["speed"] = max(0, min(3000, command.get("value", 1000)))
    elif command_type == "emergency_stop":
        machine["status"] = "error"
        machine["speed"] = 0
        machine["current"] = 0.0
        machine["temperature"] = max(20, machine["temperature"] - 10)
    
    machine["last_update"] = datetime.now().isoformat()
    
    # 通过WebSocket广播状态变更到所有连接的客户端
    await broadcast_machine_update(machine_id, machine)
    
    return {"status": "success", "message": f"命令 {command_type} 已执行", "machine": machine}

async def broadcast_machine_update(machine_id: str, machine_data: dict):
    """广播机床状态更新到所有WebSocket连接"""
    if not active_connections:
        return
    
    message = {
        "type": "machine_update",
        "machine_id": machine_id,
        "data": machine_data,
        "timestamp": datetime.now().isoformat()
    }
    
    # 向所有活跃连接发送更新
    disconnected_connections = []
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except Exception as e:
            print(f"发送WebSocket消息失败: {e}")
            disconnected_connections.append(connection)
    
    # 移除断开的连接
    for connection in disconnected_connections:
        if connection in active_connections:
            active_connections.remove(connection)

@app.get("/api/alarms")
async def get_alarms():
    """获取报警信息"""
    # 检查当前机床状态生成报警
    current_alarms = []
    
    for machine_id, machine in machines_data.items():
        if machine["temperature"] > 70:
            current_alarms.append({
                "id": f"TEMP_{machine_id}_{int(time.time())}",
                "machine_id": machine_id,
                "type": "temperature",
                "level": "WARNING" if machine["temperature"] < 80 else "CRITICAL",
                "message": f"机床 {machine_id} 温度过高: {machine['temperature']:.1f}°C",
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            })
        
        if machine["vibration"] > 8:
            current_alarms.append({
                "id": f"VIB_{machine_id}_{int(time.time())}",
                "machine_id": machine_id,
                "type": "vibration",
                "level": "WARNING" if machine["vibration"] < 10 else "CRITICAL",
                "message": f"机床 {machine_id} 振动异常: {machine['vibration']:.1f}mm/s",
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            })
        
        if machine["tool_wear"] > 80:
            current_alarms.append({
                "id": f"WEAR_{machine_id}_{int(time.time())}",
                "machine_id": machine_id,
                "type": "tool_wear",
                "level": "WARNING" if machine["tool_wear"] < 95 else "CRITICAL",
                "message": f"机床 {machine_id} 刀具磨损严重: {machine['tool_wear']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            })
    
    # 合并历史报警和当前报警
    all_alarms = alarms_data + current_alarms
    return {"alarms": all_alarms}

@app.get("/api/machines/{machine_id}/history")
async def get_machine_history(machine_id: str, hours: int = 24):
    """获取指定机床的历史数据"""
    if machine_id not in machines_data:
        raise HTTPException(status_code=404, detail="机床未找到")
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # 筛选历史数据
    machine_history = []
    for key, data in historical_data.items():
        if data.get("machine_id") == machine_id:
            data_time = datetime.fromisoformat(data["timestamp"])
            if start_time <= data_time <= end_time:
                machine_history.append(data)
    
    # 按时间排序
    machine_history.sort(key=lambda x: x["timestamp"])
    
    return {
        "machine_id": machine_id,
        "time_range": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "hours": hours
        },
        "total_records": len(machine_history),
        "data": machine_history
    }

@app.get("/api/digital-twin/{machine_id}")
async def get_digital_twin(machine_id: str):
    """获取数字孪生模型状态"""
    if machine_id not in machines_data:
        raise HTTPException(status_code=404, detail="数字孪生模型未找到")
    
    machine = machines_data[machine_id]
    
    # 计算健康评分
    health_score = 100.0
    if machine["temperature"] > 70:
        health_score -= (machine["temperature"] - 70) * 2
    if machine["vibration"] > 5:
        health_score -= (machine["vibration"] - 5) * 5
    if machine["tool_wear"] > 50:
        health_score -= (machine["tool_wear"] - 50) * 0.5
    
    health_score = max(0, min(100, health_score))
    
    # 估算剩余寿命
    remaining_life = None
    if machine["status"] == "running" and machine["tool_wear"] < 95:
        wear_rate = 0.1  # 每小时磨损率
        remaining_wear = 95 - machine["tool_wear"]
        remaining_life = remaining_wear / wear_rate
    
    return {
        "machine_id": machine_id,
        "timestamp": datetime.now().isoformat(),
        "physics_state": {
            "is_running": machine["status"] == "running",
            "target_speed": machine["speed"],
            "load_factor": 0.7 if machine["status"] == "running" else 0.0
        },
        "current_data": machine,
        "health_score": round(health_score, 2),
        "remaining_life": round(remaining_life, 1) if remaining_life else None,
        "predicted_values": {
            "temperature_1h": machine["temperature"] + random.uniform(-5, 5),
            "tool_wear_1h": machine["tool_wear"] + (0.1 if machine["status"] == "running" else 0),
            "vibration_1h": machine["vibration"] + random.uniform(-0.5, 0.5)
        }
    }

# ==================== 数据库管理API ====================

@app.get("/api/database/historical")
async def get_historical_data():
    """获取历史数据统计"""
    total_records = len(historical_data)
    time_range = {"start": None, "end": None}
    
    if total_records > 0:
        try:
            # 从历史数据中提取时间戳
            timestamps = []
            for key, data in historical_data.items():
                if isinstance(data, dict):
                    if "timestamp" in data:
                        timestamps.append(datetime.fromisoformat(data["timestamp"]))
                    elif "last_update" in data:
                        timestamps.append(datetime.fromisoformat(data["last_update"]))
            
            if timestamps:
                time_range = {
                    "start": min(timestamps).isoformat(),
                    "end": max(timestamps).isoformat()
                }
        except Exception as e:
            print(f"历史数据处理错误: {e}")
            # 如果没有历史数据，使用当前时间作为示例
            now = datetime.now()
            time_range = {
                "start": (now - timedelta(hours=24)).isoformat(),
                "end": now.isoformat()
            }
    
    return {
        "total_records": total_records,
        "time_range": time_range,
        "storage_size": f"{total_records * 0.5:.1f} KB"  # 估算大小
    }

@app.get("/api/database/export/{data_type}")
async def export_data(data_type: str):
    """导出数据"""
    if data_type == "machines":
        data = machines_data
    elif data_type == "twins":
        # 收集所有数字孪生数据
        twin_data = {}
        for machine_id in machines_data.keys():
            twin_info = await get_digital_twin(machine_id)
            twin_data[machine_id] = twin_info
        data = twin_data
    elif data_type == "historical":
        data = historical_data
    elif data_type == "alarms":
        alarms_response = await get_alarms()
        data = {"alarms": alarms_response["alarms"]}
    else:
        raise HTTPException(status_code=400, detail="不支持的数据类型")
    
    export_data = {
        "export_time": datetime.now().isoformat(),
        "data_type": data_type,
        "data": data
    }
    
    return JSONResponse(content=export_data)

@app.delete("/api/database/clear/{data_type}")
async def clear_data(data_type: str):
    """清空数据"""
    global machines_data, historical_data, alarms_data
    
    if data_type == "machines":
        # 重置机床数据到初始状态
        machines_data = {
            "CNC001": {
                "id": "CNC001", "name": "数控车床-001", "type": "CNC_LATHE", "status": "idle",
                "temperature": 25.0, "vibration": 0.5, "current": 2.0, "speed": 0,
                "pressure": 2.0, "tool_wear": 0.0, "power_consumption": 1.0,
                "is_virtual": True, "last_update": datetime.now().isoformat()
            },
            "MILL001": {
                "id": "MILL001", "name": "铣床-001", "type": "MILLING_MACHINE", "status": "idle",
                "temperature": 25.0, "vibration": 0.5, "current": 2.0, "speed": 0,
                "pressure": 2.0, "tool_wear": 0.0, "power_consumption": 1.0,
                "is_virtual": True, "last_update": datetime.now().isoformat()
            },
            "DRILL001": {
                "id": "DRILL001", "name": "钻床-001", "type": "DRILLING_MACHINE", "status": "idle",
                "temperature": 25.0, "vibration": 0.5, "current": 2.0, "speed": 0,
                "pressure": 2.0, "tool_wear": 0.0, "power_consumption": 1.0,
                "is_virtual": True, "last_update": datetime.now().isoformat()
            }
        }
        return {"status": "success", "message": "机床数据已重置"}
    elif data_type == "historical":
        historical_data.clear()
        return {"status": "success", "message": "历史数据已清空"}
    elif data_type == "alarms":
        alarms_data.clear()
        return {"status": "success", "message": "报警数据已清空"}
    elif data_type == "twins":
        # 数字孪生数据通过机床数据重置
        return {"status": "success", "message": "数字孪生数据已重置"}
    else:
        raise HTTPException(status_code=400, detail="不支持的数据类型")

@app.post("/api/database/sync/real-to-twin")
async def sync_real_to_twin():
    """同步真实数据到数字孪生"""
    # 在实际应用中，这里会从真实设备读取数据并更新到数字孪生
    return {"status": "success", "message": "真实数据已同步到数字孪生"}

@app.post("/api/database/sync/twin-to-real")
async def sync_twin_to_real():
    """同步数字孪生数据到真实设备"""
    # 在实际应用中，这里会将数字孪生的配置同步到真实设备
    return {"status": "success", "message": "数字孪生数据已同步到真实设备"}

@app.post("/api/database/sync/realtime")
async def sync_realtime_data(request_data: Dict[str, Any]):
    """同步实时数据到数据库"""
    try:
        data_points = request_data.get("data", [])
        timestamp = request_data.get("timestamp", datetime.now().isoformat())
        
        # 存储实时数据到历史数据库
        for data_point in data_points:
            machine_id = data_point.get("machine_id")
            if machine_id:
                # 生成历史数据键
                key = f"{machine_id}_{int(datetime.now().timestamp())}"
                
                # 存储到历史数据
                historical_data[key] = {
                    **data_point,
                    "is_realtime_sync": True,
                    "sync_timestamp": timestamp
                }
        
        return {
            "status": "success", 
            "message": f"已同步 {len(data_points)} 条实时数据到数据库",
            "synced_count": len(data_points),
            "timestamp": timestamp
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"实时数据同步失败: {str(e)}"
        }

@app.post("/api/machines/{machine_id}/simulate")
async def simulate_machine_data(machine_id: str, simulation_data: Dict[str, Any]):
    """接收数字孪生仿真数据"""
    if machine_id not in machines_data:
        raise HTTPException(status_code=404, detail="机床未找到")
    
    # 更新机床数据
    machine = machines_data[machine_id]
    machine.update({
        "temperature": simulation_data.get("temperature", machine["temperature"]),
        "vibration": simulation_data.get("vibration", machine["vibration"]),
        "speed": simulation_data.get("speed", machine["speed"]),
        "current": simulation_data.get("current", machine["current"]),
        "pressure": simulation_data.get("pressure", machine["pressure"]),
        "efficiency": simulation_data.get("efficiency", machine.get("efficiency", 85)),
        "last_update": simulation_data.get("last_update", datetime.now().isoformat()),
        "is_simulated": True
    })
    
    # 通过WebSocket广播仿真数据更新
    await broadcast_simulation_update(machine_id, machine)
    
    return {"status": "success", "message": "仿真数据已更新", "machine": machine}

async def broadcast_simulation_update(machine_id: str, machine_data: dict):
    """广播仿真数据更新到所有WebSocket连接"""
    if not active_connections:
        return
    
    message = {
        "type": "simulation_update",
        "machine_id": machine_id,
        "data": machine_data,
        "timestamp": datetime.now().isoformat()
    }
    
    # 向所有活跃连接发送更新
    disconnected_connections = []
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except Exception as e:
            print(f"发送WebSocket消息失败: {e}")
            disconnected_connections.append(connection)
    
    # 移除断开的连接
    for connection in disconnected_connections:
        if connection in active_connections:
            active_connections.remove(connection)

# ==================== WebSocket ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # 检查连接是否仍然有效
            if websocket.client_state.name != "CONNECTED":
                break
                
            # 发送实时数据
            data = {
                "type": "machine_data",
                "timestamp": datetime.now().isoformat(),
                "machines": list(machines_data.values())
            }
            
            try:
                await websocket.send_text(json.dumps(data))
            except Exception as e:
                print(f"WebSocket发送数据失败: {e}")
                break
                
            await asyncio.sleep(2)  # 每2秒发送一次数据
            
    except WebSocketDisconnect:
        print("WebSocket客户端断开连接")
    except Exception as e:
        print(f"WebSocket连接错误: {e}")
    finally:
        # 确保从连接列表中移除
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"WebSocket连接已关闭，当前活跃连接数: {len(active_connections)}")

# ==================== 后台任务 ====================

@app.on_event("startup")
async def startup_event():
    """启动时的初始化任务"""
    print("正在初始化系统...")
    
    # 生成历史数据
    generate_historical_data()
    
    # 生成报警数据
    generate_random_alarms()
    
    # 启动数据更新任务
    asyncio.create_task(simulate_data_updates())
    
    print("系统初始化完成")

async def simulate_data_updates():
    """模拟数据更新任务"""
    while True:
        try:
            for machine_id, machine in machines_data.items():
                if machine["status"] == "running":
                    # 模拟数据变化
                    machine["temperature"] += random.uniform(-1, 1)
                    machine["vibration"] += random.uniform(-0.2, 0.2)
                    machine["current"] += random.uniform(-0.5, 0.5)
                    machine["speed"] += random.uniform(-20, 20)
                    machine["pressure"] += random.uniform(-0.2, 0.2)
                    machine["tool_wear"] += random.uniform(0, 0.05)
                    machine["power_consumption"] += random.uniform(-0.5, 0.5)
                    
                    # 确保数值在合理范围内
                    machine["temperature"] = max(20, min(80, machine["temperature"]))
                    machine["vibration"] = max(0, min(10, machine["vibration"]))
                    machine["current"] = max(0, min(50, machine["current"]))
                    machine["speed"] = max(0, min(3000, machine["speed"]))
                    machine["pressure"] = max(0, min(10, machine["pressure"]))
                    machine["tool_wear"] = max(0, min(100, machine["tool_wear"]))
                    machine["power_consumption"] = max(0, min(100, machine["power_consumption"]))
                    
                    machine["last_update"] = datetime.now().isoformat()
                    
                    # 存储历史数据
                    historical_key = f"{machine_id}_{int(time.time())}"
                    historical_data[historical_key] = machine.copy()
            
            await asyncio.sleep(5)  # 每5秒更新一次数据
            
        except Exception as e:
            print(f"数据更新任务错误: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
