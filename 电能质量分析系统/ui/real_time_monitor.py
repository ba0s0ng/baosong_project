#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监测模块 - 显示实时电能参数和波形
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QPushButton, QComboBox, QSpinBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor

# 使用matplotlib替代PyQtChart
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils.fake_data import FakeDataGenerator

class RealTimeMonitorWidget(QWidget):
    """实时监测部件"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.fake_data = FakeDataGenerator()
        self.monitoring_points = ["监测点1", "监测点2", "监测点3", "监测点4"]
        self.current_point = self.monitoring_points[0]
        
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题和控制区域
        layout.addWidget(self.create_control_panel())
        
        # 数据展示区域
        layout.addWidget(self.create_data_display())
        
        # 图表区域
        layout.addWidget(self.create_charts_area())
        
        layout.addStretch()
        
    def create_control_panel(self):
        """创建控制面板"""
        group_box = QGroupBox("监测控制")
        layout = QHBoxLayout(group_box)
        
        # 监测点选择
        layout.addWidget(QLabel("监测点:"))
        self.point_combo = QComboBox()
        self.point_combo.addItems(self.monitoring_points)
        self.point_combo.currentTextChanged.connect(self.on_monitor_point_changed)
        layout.addWidget(self.point_combo)
        
        # 刷新间隔
        layout.addWidget(QLabel("刷新间隔(秒):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(2)
        self.interval_spin.valueChanged.connect(self.on_interval_changed)
        layout.addWidget(self.interval_spin)
        
        # 控制按钮
        self.start_btn = QPushButton("开始监测")
        self.start_btn.clicked.connect(self.start_monitoring)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止监测")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        layout.addStretch()
        
        return group_box
        
    def create_data_display(self):
        """创建数据展示区域"""
        group_box = QGroupBox("实时数据")
        layout = QGridLayout(group_box)
        
        # 创建数据表格
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels([
            "参数", "A相", "B相", "C相", "平均值", "状态"
        ])
        
        # 设置表格行
        parameters = ["电压(V)", "电流(A)", "有功功率(kW)", "无功功率(kvar)", "功率因数", "频率(Hz)"]
        self.data_table.setRowCount(len(parameters))
        
        for i, param in enumerate(parameters):
            self.data_table.setItem(i, 0, QTableWidgetItem(param))
            for j in range(1, 5):
                self.data_table.setItem(i, j, QTableWidgetItem("--"))
            self.data_table.setItem(i, 5, QTableWidgetItem("未知"))
        
        # 设置表格属性
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.data_table)
        
        return group_box
        
    def create_charts_area(self):
        """创建图表区域"""
        group_box = QGroupBox("实时波形")
        layout = QHBoxLayout(group_box)
        
        # 电压波形图
        self.voltage_chart = self.create_waveform_chart("电压波形", "V")
        layout.addWidget(self.voltage_chart)
        
        # 电流波形图
        self.current_chart = self.create_waveform_chart("电流波形", "A")
        layout.addWidget(self.current_chart)
        
        return group_box
        
    def create_waveform_chart(self, title, unit):
        """创建波形图表（使用matplotlib）"""
        import math
        
        # 创建matplotlib图形
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 生成三相波形数据
        t = [i * 0.02 for i in range(100)]  # 50Hz波形，每个周期20ms
        
        if unit == "V":
            amplitude = 220 * 1.414
            y_range = (-400, 400)
            y_label = "电压 (V)"
        else:
            amplitude = 100 * 1.414
            y_range = (-200, 200)
            y_label = "电流 (A)"
        
        # 计算三相波形
        y_a = [amplitude * math.sin(2 * math.pi * 50 * time) for time in t]
        y_b = [amplitude * math.sin(2 * math.pi * 50 * time - 2 * math.pi / 3) for time in t]
        y_c = [amplitude * math.sin(2 * math.pi * 50 * time - 4 * math.pi / 3) for time in t]
        
        # 绘制三相波形
        ax.plot(t, y_a, 'r-', linewidth=1.5, label='A相')
        ax.plot(t, y_b, 'g-', linewidth=1.5, label='B相')
        ax.plot(t, y_c, 'b-', linewidth=1.5, label='C相')
        
        ax.set_title(title)
        ax.set_xlabel("时间 (s)")
        ax.set_ylabel(y_label)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.2)
        ax.set_ylim(y_range)
        ax.legend()
        
        # 设置画布大小
        canvas.setMinimumSize(400, 300)
        
        return canvas
        
    def setup_timers(self):
        """设置定时器"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_monitor_data)
        
    def on_monitor_point_changed(self, point_name):
        """监测点改变事件"""
        self.current_point = point_name
        self.logger.info(f"切换到监测点: {point_name}")
        
    def on_interval_changed(self, interval):
        """刷新间隔改变事件"""
        if self.monitor_timer.isActive():
            self.monitor_timer.setInterval(interval * 1000)
        
    def start_monitoring(self):
        """开始监测"""
        interval = self.interval_spin.value() * 1000
        self.monitor_timer.start(interval)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.logger.info(f"开始监测 {self.current_point}，刷新间隔: {interval}ms")
        
    def stop_monitoring(self):
        """停止监测"""
        self.monitor_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.logger.info("停止监测")
        
    def update_monitor_data(self):
        """更新监测数据"""
        try:
            # 生成三相假数据
            data = self.fake_data.generate_three_phase_data()
            
            # 更新表格数据
            self.update_data_table(data)
            
            # 更新波形图
            self.update_waveforms(data)
            
        except Exception as e:
            self.logger.error(f"更新监测数据失败: {e}")
            
    def update_data_table(self, data):
        """更新数据表格"""
        # 电压数据
        voltages = data.get('voltages', {'A': 220, 'B': 220, 'C': 220})
        self.data_table.item(0, 1).setText(f"{voltages['A']:.1f}")
        self.data_table.item(0, 2).setText(f"{voltages['B']:.1f}")
        self.data_table.item(0, 3).setText(f"{voltages['C']:.1f}")
        avg_voltage = (voltages['A'] + voltages['B'] + voltages['C']) / 3
        self.data_table.item(0, 4).setText(f"{avg_voltage:.1f}")
        
        # 电流数据
        currents = data.get('currents', {'A': 100, 'B': 100, 'C': 100})
        self.data_table.item(1, 1).setText(f"{currents['A']:.1f}")
        self.data_table.item(1, 2).setText(f"{currents['B']:.1f}")
        self.data_table.item(1, 3).setText(f"{currents['C']:.1f}")
        avg_current = (currents['A'] + currents['B'] + currents['C']) / 3
        self.data_table.item(1, 4).setText(f"{avg_current:.1f}")
        
        # 功率数据
        active_powers = data.get('active_powers', {'A': 20, 'B': 20, 'C': 20})
        reactive_powers = data.get('reactive_powers', {'A': 5, 'B': 5, 'C': 5})
        power_factors = data.get('power_factors', {'A': 0.95, 'B': 0.95, 'C': 0.95})
        
        # 更新状态指示
        self.update_status_indicators(data)
        
    def update_status_indicators(self, data):
        """更新状态指示器"""
        voltages = data.get('voltages', {'A': 220, 'B': 220, 'C': 220})
        
        # 检查三相不平衡度
        avg_voltage = (voltages['A'] + voltages['B'] + voltages['C']) / 3
        imbalance = max(
            abs(voltages['A'] - avg_voltage) / avg_voltage,
            abs(voltages['B'] - avg_voltage) / avg_voltage,
            abs(voltages['C'] - avg_voltage) / avg_voltage
        )
        
        if imbalance < 0.02:
            status = "正常"
            color = "green"
        elif imbalance < 0.05:
            status = "警告"
            color = "orange"
        else:
            status = "异常"
            color = "red"
        
        for i in range(6):
            self.data_table.item(i, 5).setText(status)
            self.data_table.item(i, 5).setForeground(QColor(color))
            
    def update_waveforms(self, data):
        """更新波形图"""
        # 这里可以添加波形图更新逻辑
        pass

# 添加数学模块导入
import math