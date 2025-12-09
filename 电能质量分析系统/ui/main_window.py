#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
"""

import os
import logging
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QStatusBar, QMenuBar, QMenu, QAction,
                            QToolBar, QLabel, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont

from ui.dashboard import DashboardWidget
from ui.real_time_monitor import RealTimeMonitorWidget
from ui.quality_analysis import QualityAnalysisWidget
from ui.data_management import DataManagementWidget
from ui.report_generator import ReportGeneratorWidget
from ui.system_config import SystemConfigWidget
from utils.config import Config

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
        
    def setup_ui(self):
        """设置用户界面"""
        # 设置窗口属性
        self.setWindowTitle(f"{self.config['app.name']} v{self.config['app.version']}")
        self.setMinimumSize(1000, 700)
        
        # 设置菜单栏
        self.setup_menu_bar()
        
        # 设置工具栏
        self.setup_tool_bar()
        
        # 设置状态栏
        self.setup_status_bar()
        
        # 设置中心部件
        self.setup_central_widget()
        
    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        new_action = QAction('新建(&N)', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        
        open_action = QAction('打开(&O)', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('保存(&S)', self)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        dashboard_action = QAction('仪表盘', self)
        dashboard_action.setShortcut('Ctrl+1')
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(dashboard_action)
        
        monitor_action = QAction('实时监测', self)
        monitor_action.setShortcut('Ctrl+2')
        monitor_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(monitor_action)
        
        analysis_action = QAction('质量分析', self)
        analysis_action.setShortcut('Ctrl+3')
        analysis_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(analysis_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        config_action = QAction('系统配置', self)
        config_action.setShortcut('Ctrl+,')
        config_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))
        tools_menu.addAction(config_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_tool_bar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # 添加工具栏按钮
        dashboard_btn = QAction('仪表盘', self)
        dashboard_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(dashboard_btn)
        
        monitor_btn = QAction('实时监测', self)
        monitor_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(monitor_btn)
        
        analysis_btn = QAction('质量分析', self)
        analysis_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(analysis_btn)
        
        toolbar.addSeparator()
        
        report_btn = QAction('报表生成', self)
        report_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        toolbar.addAction(report_btn)
        
    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 状态信息
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        
        # 系统时间
        self.time_label = QLabel()
        status_bar.addPermanentWidget(self.time_label)
        
        # 连接状态
        self.connection_label = QLabel("离线")
        status_bar.addPermanentWidget(self.connection_label)
        
    def setup_central_widget(self):
        """设置中心部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页部件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        
        # 添加各个功能页面
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_widget, "仪表盘")
        
        self.monitor_widget = RealTimeMonitorWidget()
        self.tab_widget.addTab(self.monitor_widget, "实时监测")
        
        self.analysis_widget = QualityAnalysisWidget()
        self.tab_widget.addTab(self.analysis_widget, "质量分析")
        
        self.data_widget = DataManagementWidget()
        self.tab_widget.addTab(self.data_widget, "数据管理")
        
        self.report_widget = ReportGeneratorWidget()
        self.tab_widget.addTab(self.report_widget, "报表生成")
        
        self.config_widget = SystemConfigWidget()
        self.tab_widget.addTab(self.config_widget, "系统配置")
        
        layout.addWidget(self.tab_widget)
        
    def setup_connections(self):
        """设置信号连接"""
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def setup_timers(self):
        """设置定时器"""
        # 更新时间定时器
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # 每秒更新一次
        
        self.update_time()
        
    def update_time(self):
        """更新时间显示"""
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(current_time)
        
    def on_tab_changed(self, index):
        """标签页切换事件"""
        tab_names = ["仪表盘", "实时监测", "质量分析", "数据管理", "报表生成", "系统配置"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"当前页面: {tab_names[index]}")
            
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""
        <h2>{self.config['app.name']}</h2>
        <p>版本: {self.config['app.version']}</p>
        <p>开发公司: {self.config['app.company']}</p>
        <p>电能质量分析系统是一款专业的电力系统监测与分析软件，
        旨在实时监测、分析和评估电力系统的电能质量状况。</p>
        <p>功能包括：实时数据监测、电能质量分析、数据存储管理、
        报表生成等。</p>
        """
        
        QMessageBox.about(self, "关于", about_text)
        
    def closeEvent(self, event):
        """关闭事件处理"""
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出电能质量分析系统吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 保存配置
            self.config.save()
            
            # 停止所有定时器
            self.time_timer.stop()
            
            event.accept()
            self.logger.info("应用程序正常退出")
        else:
            event.ignore()