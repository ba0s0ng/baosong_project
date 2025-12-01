import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "machine_monitor.db")

# 初始化数据库
def init_db():
    """初始化数据库，创建所需的表"""
    # 确保数据目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as db:
        # 创建设备表
        db.execute('''
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            model TEXT,
            location TEXT,
            status TEXT DEFAULT 'offline',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建设备数据表（调整为与main.py匹配的结构）
        db.execute('''
        CREATE TABLE IF NOT EXISTS machine_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER,
            temperature REAL,
            vibration REAL,
            noise REAL,
            power_consumption REAL,
            operating_hours REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (machine_id) REFERENCES machines (id)
        )
        ''')
        
        # 创建报警表（调整为与main.py匹配的结构）
        db.execute('''
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER,
            rule_id INTEGER,
            value REAL,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_handled BOOLEAN DEFAULT FALSE,
            handled_by TEXT,
            handled_at TIMESTAMP,
            FOREIGN KEY (machine_id) REFERENCES machines (id),
            FOREIGN KEY (rule_id) REFERENCES alarm_rules (id)
        )
        ''')
        
        # 创建报警规则表（调整为与main.py匹配的结构）
        db.execute('''
        CREATE TABLE IF NOT EXISTS alarm_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parameter TEXT NOT NULL,
            threshold REAL NOT NULL,
            comparison TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
        ''')
        
        # 创建维护记录表
        db.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id INTEGER,
            maintenance_type TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            performed_by TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (machine_id) REFERENCES machines (id)
        )
        ''')
        
        # 插入默认数据
        # 1. 插入示例设备
        cursor = db.execute("SELECT COUNT(*) FROM machines")
        count = cursor.fetchone()
        if count[0] == 0:
            db.execute(
                "INSERT INTO machines (name, type, model, location, status) VALUES (?, ?, ?, ?, ?)",
                ("CNC加工中心001", "CNC铣床", "VMC-850", "生产车间A区", "online")
            )
            db.execute(
                "INSERT INTO machines (name, type, model, location, status) VALUES (?, ?, ?, ?, ?)",
                ("数控车床001", "车床", "CK6150", "生产车间B区", "online")
            )
            db.execute(
                "INSERT INTO machines (name, type, model, location, status) VALUES (?, ?, ?, ?, ?)",
                ("激光切割机001", "激光切割", "LCF-3015", "生产车间C区", "offline")
            )
        
        # 2. 插入默认报警规则
        cursor = db.execute("SELECT COUNT(*) FROM alarm_rules")
        count = cursor.fetchone()
        if count[0] == 0:
            db.execute(
                "INSERT INTO alarm_rules (name, parameter, threshold, comparison, is_active) VALUES (?, ?, ?, ?, ?)",
                ("温度过高", "temperature", 80.0, ">", True)
            )
            db.execute(
                "INSERT INTO alarm_rules (name, parameter, threshold, comparison, is_active) VALUES (?, ?, ?, ?, ?)",
                ("振动异常", "vibration", 5.0, ">", True)
            )
            db.execute(
                "INSERT INTO alarm_rules (name, parameter, threshold, comparison, is_active) VALUES (?, ?, ?, ?, ?)",
                ("噪音过大", "noise", 90.0, ">", True)
            )
        
        # 提交事务
        db.commit()

# 通用数据库查询函数
def execute_query(query, params=None):
    """执行SQL查询"""
    with sqlite3.connect(DB_PATH) as db:
        if params:
            cursor = db.execute(query, params)
        else:
            cursor = db.execute(query)
        db.commit()
        return cursor

def fetch_all(query, params=None):
    """获取所有查询结果"""
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row  # 使用Row工厂以便返回字典形式的结果
        if params:
            cursor = db.execute(query, params)
        else:
            cursor = db.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=None):
    """获取单个查询结果"""
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row  # 使用Row工厂以便返回字典形式的结果
        if params:
            cursor = db.execute(query, params)
        else:
            cursor = db.execute(query)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None