#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表盘模块 - 显示系统关键指标和实时数据
"""

import logging
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QProgressBar, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor

# 使用matplotlib替代PyQtChart
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils.fake_data import FakeDataGenerator

class DashboardWidget(QWidget):
    """仪表盘部件"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.fake_data = FakeDataGenerator()
        
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("电能质量监测仪表盘")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 关键指标区域
        layout.addWidget(self.create_key_metrics())
        
        # 图表区域
        layout.addWidget(self.create_charts_area())
        
        # 告警信息区域
        layout.addWidget(self.create_alerts_area())
        
        layout.addStretch()
        
    def create_key_metrics(self):
        """创建关键指标区域"""
        group_box = QGroupBox("关键指标")
        layout = QGridLayout(group_box)
        
        # 电压指标
        voltage_label = QLabel("电压 (V)")
        self.voltage_value = QLabel("220.0")
        self.voltage_value.setStyleSheet("font-size: 20px; color: blue;")
        self.voltage_status = QLabel("正常")
        self.voltage_status.setStyleSheet("color: green;")
        
        layout.addWidget(voltage_label, 0, 0)
        layout.addWidget(self.voltage_value, 0, 1)
        layout.addWidget(self.voltage_status, 0, 2)
        
        # 电流指标
        current_label = QLabel("电流 (A)")
        self.current_value = QLabel("100.0")
        self.current_value.setStyleSheet("font-size: 20px; color: blue;")
        self.current_status = QLabel("正常")
        self.current_status.setStyleSheet("color: green;")
        
        layout.addWidget(current_label, 1, 0)
        layout.addWidget(self.current_value, 1, 1)
        layout.addWidget(self.current_status, 1, 2)
        
        # 频率指标
        frequency_label = QLabel("频率 (Hz)")
        self.frequency_value = QLabel("50.00")
        self.frequency_value.setStyleSheet("font-size: 20px; color: blue;")
        self.frequency_status = QLabel("正常")
        self.frequency_status.setStyleSheet("color: green;")
        
        layout.addWidget(frequency_label, 2, 0)
        layout.addWidget(self.frequency_value, 2, 1)
        layout.addWidget(self.frequency_status, 2, 2)
        
        # 功率因数
        power_factor_label = QLabel("功率因数")
        self.power_factor_value = QLabel("0.95")
        self.power_factor_value.setStyleSheet("font-size: 20px; color: blue;")
        self.power_factor_status = QLabel("良好")
        self.power_factor_status.setStyleSheet("color: green;")
        
        layout.addWidget(power_factor_label, 3, 0)
        layout.addWidget(self.power_factor_value, 3, 1)
        layout.addWidget(self.power_factor_status, 3, 2)
        
        return group_box
        
    def create_charts_area(self):
        """创建图表区域"""
        group_box = QGroupBox("实时趋势")
        layout = QHBoxLayout(group_box)
        
        # 电压趋势图
        voltage_chart = self.create_simple_chart("电压趋势", "V")
        layout.addWidget(voltage_chart)
        
        # 电流趋势图
        current_chart = self.create_simple_chart("电流趋势", "A")
        layout.addWidget(current_chart)
        
        return group_box
        
    def create_simple_chart(self, title, unit):
        """创建简单图表（使用matplotlib）"""
        import random
        
        # 创建matplotlib图形
        fig = Figure(figsize=(4, 3), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 生成一些初始数据
        x_data = list(range(10))
        if unit == "V":
            y_data = [random.uniform(200, 240) for _ in range(10)]
            y_range = (200, 240)
        else:
            y_data = [random.uniform(80, 120) for _ in range(10)]
            y_range = (80, 120)
        
        # 绘制折线图
        ax.plot(x_data, y_data, 'b-', linewidth=2)
        ax.set_title(title)
        ax.set_xlabel("时间")
        ax.set_ylabel(unit)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(y_range)
        
        # 设置画布大小
        canvas.setMinimumSize(300, 200)
        
        return canvas
        
    def create_alerts_area(self):
        """创建告警信息区域"""
        group_box = QGroupBox("系统状态")
        layout = QVBoxLayout(group_box)
        
        # 系统状态
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        
        status_label = QLabel("系统状态:")
        self.system_status = QLabel("运行正常")
        self.system_status.setStyleSheet("color: green; font-weight: bold;")
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.system_status)
        status_layout.addStretch()
        
        layout.addWidget(status_frame)
        
        # 监测点状态
        monitor_frame = QFrame()
        monitor_layout = QGridLayout(monitor_frame)
        
        monitor_layout.addWidget(QLabel("监测点1:"), 0, 0)
        monitor1_status = QLabel("在线")
        monitor1_status.setStyleSheet("color: green;")
        monitor_layout.addWidget(monitor1_status, 0, 1)
        
        monitor_layout.addWidget(QLabel("监测点2:"), 1, 0)
        monitor2_status = QLabel("在线")
        monitor2_status.setStyleSheet("color: green;")
        monitor_layout.addWidget(monitor2_status, 1, 1)
        
        monitor_layout.addWidget(QLabel("监测点3:"), 2, 0)
        monitor3_status = QLabel("离线")
        monitor3_status.setStyleSheet("color: red;")
        monitor_layout.addWidget(monitor3_status, 2, 1)
        
        layout.addWidget(monitor_frame)
        
        # 数据质量
        quality_frame = QFrame()
        quality_layout = QVBoxLayout(quality_frame)
        
        quality_label = QLabel("数据质量:")
        self.quality_progress = QProgressBar()
        self.quality_progress.setValue(95)
        self.quality_progress.setFormat("%p%")
        
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_progress)
        
        layout.addWidget(quality_frame)
        
        return group_box
        
    def setup_timers(self):
        """设置定时器"""
        # 数据更新定时器
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(2000)  # 每2秒更新一次数据
        
    def update_data(self):
        """更新仪表盘数据"""
        try:
            # 生成假数据
            data = self.fake_data.generate_realtime_data()
            
            # 更新电压数据
            voltage = data.get('voltage', 220.0)
            self.voltage_value.setText(f"{voltage:.1f}")
            
            # 更新电流数据
            current = data.get('current', 100.0)
            self.current_value.setText(f"{current:.1f}")
            
            # 更新频率数据
            frequency = data.get('frequency', 50.0)
            self.frequency_value.setText(f"{frequency:.2f}")
            
            # 更新功率因数
            power_factor = data.get('power_factor', 0.95)
            self.power_factor_value.setText(f"{power_factor:.2f}")
            
            # 更新状态指示
            self.update_status_indicators(data)
            
        except Exception as e:
            self.logger.error(f"更新仪表盘数据失败: {e}")
            
    def update_status_indicators(self, data):
        """更新状态指示器"""
        # 电压状态
        voltage = data.get('voltage', 220.0)
        if 215 <= voltage <= 235:
            self.voltage_status.setText("正常")
            self.voltage_status.setStyleSheet("color: green;")
        elif 210 <= voltage < 215 or 235 < voltage <= 240:
            self.voltage_status.setText("警告")
            self.voltage_status.setStyleSheet("color: orange;")
        else:
            self.voltage_status.setText("异常")
            self.voltage_status.setStyleSheet("color: red;")
            
        # 频率状态
        frequency = data.get('frequency', 50.0)
        if 49.8 <= frequency <= 50.2:
            self.frequency_status.setText("正常")
            self.frequency_status.setStyleSheet("color: green;")
        elif 49.5 <= frequency < 49.8 or 50.2 < frequency <= 50.5:
            self.frequency_status.setText("警告")
            self.frequency_status.setStyleSheet("color: orange;")
        else:
            self.frequency_status.setText("异常")
            self.frequency_status.setStyleSheet("color: red;")
            
        # 随机更新数据质量
        quality = random.randint(90, 99)
        self.quality_progress.setValue(quality)