#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电能质量分析模块
"""

import logging
import random
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QTabWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QPushButton,
                            QComboBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils.fake_data import FakeDataGenerator

class QualityAnalysisWidget(QWidget):
    """电能质量分析部件"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.fake_data = FakeDataGenerator()
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("电能质量分析")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 谐波分析标签页
        self.harmonic_tab = self.create_harmonic_analysis_tab()
        self.tab_widget.addTab(self.harmonic_tab, "谐波分析")
        
        # 电压偏差分析标签页
        self.voltage_tab = self.create_voltage_analysis_tab()
        self.tab_widget.addTab(self.voltage_tab, "电压偏差")
        
        # 频率偏差分析标签页
        self.frequency_tab = self.create_frequency_analysis_tab()
        self.tab_widget.addTab(self.frequency_tab, "频率偏差")
        
        # 三相不平衡分析标签页
        self.unbalance_tab = self.create_unbalance_analysis_tab()
        self.tab_widget.addTab(self.unbalance_tab, "三相不平衡")
        
        # 闪变分析标签页
        self.flicker_tab = self.create_flicker_analysis_tab()
        self.tab_widget.addTab(self.flicker_tab, "电压闪变")
        
        layout.addWidget(self.tab_widget)
        
    def create_harmonic_analysis_tab(self):
        """创建谐波分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制区域
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("监测点:"))
        point_combo = QComboBox()
        point_combo.addItems(["监测点1", "监测点2", "监测点3"])
        control_layout.addWidget(point_combo)
        
        analyze_btn = QPushButton("开始分析")
        analyze_btn.clicked.connect(self.perform_harmonic_analysis)
        control_layout.addWidget(analyze_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 谐波数据表格
        harmonic_table = QTableWidget()
        harmonic_table.setColumnCount(5)
        harmonic_table.setHorizontalHeaderLabels([
            "谐波次数", "A相含量(%)", "B相含量(%)", "C相含量(%)", "限值(%)"
        ])
        
        # 设置谐波数据
        harmonic_orders = ["2次", "3次", "5次", "7次", "11次", "13次", "THD"]
        harmonic_table.setRowCount(len(harmonic_orders))
        
        for i, order in enumerate(harmonic_orders):
            harmonic_table.setItem(i, 0, QTableWidgetItem(order))
            for j in range(1, 4):
                harmonic_table.setItem(i, j, QTableWidgetItem("--"))
            # 设置限值
            if order == "THD":
                harmonic_table.setItem(i, 4, QTableWidgetItem("8.0"))
            else:
                harmonic_table.setItem(i, 4, QTableWidgetItem("4.0"))
        
        harmonic_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(harmonic_table)
        
        # 谐波频谱图
        harmonic_chart = self.create_harmonic_chart()
        layout.addWidget(harmonic_chart)
        
        return widget
        
    def create_harmonic_chart(self):
        """创建谐波频谱图（使用matplotlib）"""
        # 创建matplotlib图形
        fig = Figure(figsize=(8, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 谐波数据
        harmonic_orders = ["2次", "3次", "5次", "7次", "11次", "13次"]
        x_pos = range(len(harmonic_orders))
        
        # 三相谐波含量数据
        harmonic_a = [2.1, 1.8, 1.2, 0.8, 0.5, 0.3]
        harmonic_b = [1.9, 1.6, 1.1, 0.7, 0.4, 0.2]
        harmonic_c = [2.0, 1.7, 1.0, 0.6, 0.3, 0.1]
        
        # 设置柱状图宽度
        bar_width = 0.25
        
        # 绘制三相谐波柱状图
        ax.bar([x - bar_width for x in x_pos], harmonic_a, bar_width, 
               label='A相', color='red', alpha=0.7)
        ax.bar(x_pos, harmonic_b, bar_width, 
               label='B相', color='green', alpha=0.7)
        ax.bar([x + bar_width for x in x_pos], harmonic_c, bar_width, 
               label='C相', color='blue', alpha=0.7)
        
        ax.set_title("谐波频谱分析", fontsize=14, fontweight='bold')
        ax.set_xlabel("谐波次数", fontsize=12)
        ax.set_ylabel("谐波含量(%)", fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(harmonic_orders)
        ax.set_ylim(0, 5)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 设置画布大小
        canvas.setMinimumSize(600, 400)
        
        return canvas
        
    def create_voltage_analysis_tab(self):
        """创建电压偏差分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 电压偏差统计
        stats_group = QGroupBox("电压偏差统计")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("监测时段:"), 0, 0)
        stats_layout.addWidget(QLabel("最近24小时"), 0, 1)
        
        stats_layout.addWidget(QLabel("最大偏差:"), 1, 0)
        stats_layout.addWidget(QLabel("+3.2%"), 1, 1)
        
        stats_layout.addWidget(QLabel("最小偏差:"), 2, 0)
        stats_layout.addWidget(QLabel("-2.1%"), 2, 1)
        
        stats_layout.addWidget(QLabel("平均偏差:"), 3, 0)
        stats_layout.addWidget(QLabel("+0.5%"), 3, 1)
        
        stats_layout.addWidget(QLabel("合格率:"), 4, 0)
        stats_layout.addWidget(QLabel("98.7%"), 4, 1)
        
        layout.addWidget(stats_group)
        
        # 电压偏差趋势图
        trend_label = QLabel("电压偏差趋势")
        trend_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(trend_label)
        
        # 这里可以添加电压偏差趋势图表
        
        return widget
        
    def create_frequency_analysis_tab(self):
        """创建频率偏差分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 频率偏差统计
        stats_group = QGroupBox("频率偏差统计")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("监测时段:"), 0, 0)
        stats_layout.addWidget(QLabel("最近24小时"), 0, 1)
        
        stats_layout.addWidget(QLabel("最大偏差:"), 1, 0)
        stats_layout.addWidget(QLabel("+0.15Hz"), 1, 1)
        
        stats_layout.addWidget(QLabel("最小偏差:"), 2, 0)
        stats_layout.addWidget(QLabel("-0.12Hz"), 2, 1)
        
        stats_layout.addWidget(QLabel("平均偏差:"), 3, 0)
        stats_layout.addWidget(QLabel("+0.03Hz"), 3, 1)
        
        stats_layout.addWidget(QLabel("合格率:"), 4, 0)
        stats_layout.addWidget(QLabel("99.2%"), 4, 1)
        
        layout.addWidget(stats_group)
        
        return widget
        
    def create_unbalance_analysis_tab(self):
        """创建三相不平衡分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 三相不平衡度统计
        stats_group = QGroupBox("三相不平衡度统计")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("电压不平衡度:"), 0, 0)
        stats_layout.addWidget(QLabel("1.2%"), 0, 1)
        
        stats_layout.addWidget(QLabel("电流不平衡度:"), 1, 0)
        stats_layout.addWidget(QLabel("3.5%"), 1, 1)
        
        stats_layout.addWidget(QLabel("最大不平衡度:"), 2, 0)
        stats_layout.addWidget(QLabel("4.8%"), 2, 1)
        
        stats_layout.addWidget(QLabel("发生时间:"), 3, 0)
        stats_layout.addWidget(QLabel("14:30:25"), 3, 1)
        
        stats_layout.addWidget(QLabel("持续时间:"), 4, 0)
        stats_layout.addWidget(QLabel("15分钟"), 4, 1)
        
        layout.addWidget(stats_group)
        
        return widget
        
    def create_flicker_analysis_tab(self):
        """创建闪变分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 闪变统计
        stats_group = QGroupBox("电压闪变统计")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("短时闪变Pst:"), 0, 0)
        stats_layout.addWidget(QLabel("0.85"), 0, 1)
        
        stats_layout.addWidget(QLabel("长时闪变Plt:"), 1, 0)
        stats_layout.addWidget(QLabel("0.72"), 1, 1)
        
        stats_layout.addWidget(QLabel("最大Pst:"), 2, 0)
        stats_layout.addWidget(QLabel("1.25"), 2, 1)
        
        stats_layout.addWidget(QLabel("发生时间:"), 3, 0)
        stats_layout.addWidget(QLabel("09:15:10"), 3, 1)
        
        stats_layout.addWidget(QLabel("闪变等级:"), 4, 0)
        stats_layout.addWidget(QLabel("轻微"), 4, 1)
        
        layout.addWidget(stats_group)
        
        return widget
        
    def perform_harmonic_analysis(self):
        """执行谐波分析"""
        try:
            # 生成谐波分析假数据
            harmonic_data = self.fake_data.generate_harmonic_data()
            
            # 这里可以添加谐波分析结果更新逻辑
            self.logger.info("谐波分析完成")
            
        except Exception as e:
            self.logger.error(f"谐波分析失败: {e}")