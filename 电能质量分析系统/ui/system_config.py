#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统配置模块
"""

import logging
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QComboBox, QLineEdit, QPushButton,
                            QSpinBox, QDoubleSpinBox, QCheckBox, QTabWidget,
                            QMessageBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator

from utils.config import Config

class SystemConfigWidget(QWidget):
    """系统配置部件"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("系统配置")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 基本设置标签页
        self.tab_widget.addTab(self.create_basic_settings_tab(), "基本设置")
        
        # 数据采集标签页
        self.tab_widget.addTab(self.create_data_acquisition_tab(), "数据采集")
        
        # 分析参数标签页
        self.tab_widget.addTab(self.create_analysis_params_tab(), "分析参数")
        
        # 告警设置标签页
        self.tab_widget.addTab(self.create_alarm_settings_tab(), "告警设置")
        
        # 用户管理标签页
        self.tab_widget.addTab(self.create_user_management_tab(), "用户管理")
        
        layout.addWidget(self.tab_widget)
        
        # 操作按钮
        layout.addWidget(self.create_operation_panel())
        
        layout.addStretch()
        
    def create_basic_settings_tab(self):
        """创建基本设置标签页"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # 应用设置
        layout.addWidget(QLabel("应用名称:"), 0, 0)
        self.app_name = QLineEdit()
        layout.addWidget(self.app_name, 0, 1)
        
        layout.addWidget(QLabel("版本号:"), 1, 0)
        self.app_version = QLineEdit()
        layout.addWidget(self.app_version, 1, 1)
        
        layout.addWidget(QLabel("公司名称:"), 2, 0)
        self.company_name = QLineEdit()
        layout.addWidget(self.company_name, 2, 1)
        
        # 界面设置
        layout.addWidget(QLabel("界面语言:"), 3, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        layout.addWidget(self.language_combo, 3, 1)
        
        layout.addWidget(QLabel("主题风格:"), 4, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认主题", "深色主题", "蓝色主题"])
        layout.addWidget(self.theme_combo, 4, 1)
        
        layout.addWidget(QLabel("字体大小:"), 5, 0)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 20)
        self.font_size.setValue(10)
        layout.addWidget(self.font_size, 5, 1)
        
        # 系统设置
        layout.addWidget(QLabel("数据保存路径:"), 6, 0)
        data_path_layout = QHBoxLayout()
        self.data_path = QLineEdit()
        data_path_layout.addWidget(self.data_path)
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_data_path)
        data_path_layout.addWidget(self.browse_btn)
        layout.addLayout(data_path_layout, 6, 1)
        
        layout.addWidget(QLabel("日志级别:"), 7, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        layout.addWidget(self.log_level_combo, 7, 1)
        
        layout.addWidget(QLabel("自动保存间隔(分钟):"), 8, 0)
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(5)
        layout.addWidget(self.auto_save_interval, 8, 1)
        
        layout.setRowStretch(9, 1)
        
        return widget
        
    def create_data_acquisition_tab(self):
        """创建数据采集标签页"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # 采集参数
        layout.addWidget(QLabel("采样频率(Hz):"), 0, 0)
        self.sampling_frequency = QSpinBox()
        self.sampling_frequency.setRange(100, 10000)
        self.sampling_frequency.setValue(1000)
        layout.addWidget(self.sampling_frequency, 0, 1)
        
        layout.addWidget(QLabel("采样点数:"), 1, 0)
        self.sampling_points = QSpinBox()
        self.sampling_points.setRange(128, 8192)
        self.sampling_points.setValue(1024)
        layout.addWidget(self.sampling_points, 1, 1)
        
        layout.addWidget(QLabel("数据更新间隔(秒):"), 2, 0)
        self.data_update_interval = QSpinBox()
        self.data_update_interval.setRange(1, 60)
        self.data_update_interval.setValue(5)
        layout.addWidget(self.data_update_interval, 2, 1)
        
        layout.addWidget(QLabel("数据保存格式:"), 3, 0)
        self.data_format_combo = QComboBox()
        self.data_format_combo.addItems(["CSV", "JSON", "二进制", "数据库"])
        layout.addWidget(self.data_format_combo, 3, 1)
        
        # 监测点配置
        layout.addWidget(QLabel("监测点数量:"), 4, 0)
        self.monitor_points_count = QSpinBox()
        self.monitor_points_count.setRange(1, 10)
        self.monitor_points_count.setValue(3)
        layout.addWidget(self.monitor_points_count, 4, 1)
        
        layout.addWidget(QLabel("监测点名称:"), 5, 0)
        self.monitor_points_names = QLineEdit()
        self.monitor_points_names.setPlaceholderText("监测点1,监测点2,监测点3")
        layout.addWidget(self.monitor_points_names, 5, 1)
        
        layout.setRowStretch(6, 1)
        
        return widget
        
    def create_analysis_params_tab(self):
        """创建分析参数标签页"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # 电压分析参数
        layout.addWidget(QLabel("电压额定值(V):"), 0, 0)
        self.voltage_nominal = QDoubleSpinBox()
        self.voltage_nominal.setRange(100, 500)
        self.voltage_nominal.setValue(220)
        self.voltage_nominal.setDecimals(1)
        layout.addWidget(self.voltage_nominal, 0, 1)
        
        layout.addWidget(QLabel("电压偏差阈值(%):"), 1, 0)
        self.voltage_deviation_threshold = QDoubleSpinBox()
        self.voltage_deviation_threshold.setRange(1, 20)
        self.voltage_deviation_threshold.setValue(7)
        self.voltage_deviation_threshold.setDecimals(1)
        layout.addWidget(self.voltage_deviation_threshold, 1, 1)
        
        # 频率分析参数
        layout.addWidget(QLabel("频率额定值(Hz):"), 2, 0)
        self.frequency_nominal = QDoubleSpinBox()
        self.frequency_nominal.setRange(45, 65)
        self.frequency_nominal.setValue(50)
        self.frequency_nominal.setDecimals(2)
        layout.addWidget(self.frequency_nominal, 2, 1)
        
        layout.addWidget(QLabel("频率偏差阈值(Hz):"), 3, 0)
        self.frequency_deviation_threshold = QDoubleSpinBox()
        self.frequency_deviation_threshold.setRange(0.1, 2)
        self.frequency_deviation_threshold.setValue(0.5)
        self.frequency_deviation_threshold.setDecimals(2)
        layout.addWidget(self.frequency_deviation_threshold, 3, 1)
        
        # 谐波分析参数
        layout.addWidget(QLabel("谐波分析次数:"), 4, 0)
        self.harmonic_orders = QSpinBox()
        self.harmonic_orders.setRange(2, 50)
        self.harmonic_orders.setValue(25)
        layout.addWidget(self.harmonic_orders, 4, 1)
        
        layout.addWidget(QLabel("THD阈值(%):"), 5, 0)
        self.thd_threshold = QDoubleSpinBox()
        self.thd_threshold.setRange(1, 20)
        self.thd_threshold.setValue(5)
        self.thd_threshold.setDecimals(1)
        layout.addWidget(self.thd_threshold, 5, 1)
        
        # 三相不平衡参数
        layout.addWidget(QLabel("三相不平衡阈值(%):"), 6, 0)
        self.unbalance_threshold = QDoubleSpinBox()
        self.unbalance_threshold.setRange(1, 10)
        self.unbalance_threshold.setValue(2)
        self.unbalance_threshold.setDecimals(1)
        layout.addWidget(self.unbalance_threshold, 6, 1)
        
        layout.setRowStretch(7, 1)
        
        return widget
        
    def create_alarm_settings_tab(self):
        """创建告警设置标签页"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # 告警级别设置
        layout.addWidget(QLabel("告警级别:"), 0, 0)
        self.alarm_level_combo = QComboBox()
        self.alarm_level_combo.addItems(["低", "中", "高", "紧急"])
        layout.addWidget(self.alarm_level_combo, 0, 1)
        
        layout.addWidget(QLabel("告警声音:"), 1, 0)
        self.alarm_sound_combo = QComboBox()
        self.alarm_sound_combo.addItems(["默认声音", "蜂鸣声", "语音提示", "静音"])
        layout.addWidget(self.alarm_sound_combo, 1, 1)
        
        layout.addWidget(QLabel("告警持续时间(秒):"), 2, 0)
        self.alarm_duration = QSpinBox()
        self.alarm_duration.setRange(5, 300)
        self.alarm_duration.setValue(30)
        layout.addWidget(self.alarm_duration, 2, 1)
        
        # 告警类型设置
        layout.addWidget(QLabel("电压告警:"), 3, 0)
        self.voltage_alarm_enabled = QCheckBox("启用")
        self.voltage_alarm_enabled.setChecked(True)
        layout.addWidget(self.voltage_alarm_enabled, 3, 1)
        
        layout.addWidget(QLabel("频率告警:"), 4, 0)
        self.frequency_alarm_enabled = QCheckBox("启用")
        self.frequency_alarm_enabled.setChecked(True)
        layout.addWidget(self.frequency_alarm_enabled, 4, 1)
        
        layout.addWidget(QLabel("谐波告警:"), 5, 0)
        self.harmonic_alarm_enabled = QCheckBox("启用")
        self.harmonic_alarm_enabled.setChecked(True)
        layout.addWidget(self.harmonic_alarm_enabled, 5, 1)
        
        layout.addWidget(QLabel("不平衡告警:"), 6, 0)
        self.unbalance_alarm_enabled = QCheckBox("启用")
        self.unbalance_alarm_enabled.setChecked(True)
        layout.addWidget(self.unbalance_alarm_enabled, 6, 1)
        
        layout.setRowStretch(7, 1)
        
        return widget
        
    def create_user_management_tab(self):
        """创建用户管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 用户表格
        user_group = QGroupBox("用户列表")
        user_layout = QVBoxLayout(user_group)
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["用户名", "角色", "状态", "最后登录"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 添加示例用户数据
        self.populate_user_table()
        
        user_layout.addWidget(self.user_table)
        
        # 用户操作按钮
        user_btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("添加用户")
        self.edit_user_btn = QPushButton("编辑用户")
        self.delete_user_btn = QPushButton("删除用户")
        self.reset_password_btn = QPushButton("重置密码")
        
        user_btn_layout.addWidget(self.add_user_btn)
        user_btn_layout.addWidget(self.edit_user_btn)
        user_btn_layout.addWidget(self.delete_user_btn)
        user_btn_layout.addWidget(self.reset_password_btn)
        user_btn_layout.addStretch()
        
        user_layout.addLayout(user_btn_layout)
        layout.addWidget(user_group)
        
        # 权限设置
        perm_group = QGroupBox("权限设置")
        perm_layout = QGridLayout(perm_group)
        
        perm_layout.addWidget(QLabel("管理员权限:"), 0, 0)
        self.admin_perms = QTextEdit()
        self.admin_perms.setMaximumHeight(80)
        self.admin_perms.setText("系统配置、用户管理、数据导出、报表生成")
        perm_layout.addWidget(self.admin_perms, 0, 1)
        
        perm_layout.addWidget(QLabel("操作员权限:"), 1, 0)
        self.operator_perms = QTextEdit()
        self.operator_perms.setMaximumHeight(80)
        self.operator_perms.setText("实时监测、数据分析、报表查看")
        perm_layout.addWidget(self.operator_perms, 1, 1)
        
        perm_layout.addWidget(QLabel("查看者权限:"), 2, 0)
        self.viewer_perms = QTextEdit()
        self.viewer_perms.setMaximumHeight(80)
        self.viewer_perms.setText("数据查看、报表查看")
        perm_layout.addWidget(self.viewer_perms, 2, 1)
        
        layout.addWidget(perm_group)
        
        return widget
        
    def create_operation_panel(self):
        """创建操作面板"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 保存按钮
        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self.save_config)
        layout.addWidget(self.save_btn)
        
        # 应用按钮
        self.apply_btn = QPushButton("应用配置")
        self.apply_btn.clicked.connect(self.apply_config)
        layout.addWidget(self.apply_btn)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置配置")
        self.reset_btn.clicked.connect(self.reset_config)
        layout.addWidget(self.reset_btn)
        
        # 恢复默认按钮
        self.default_btn = QPushButton("恢复默认")
        self.default_btn.clicked.connect(self.restore_defaults)
        layout.addWidget(self.default_btn)
        
        layout.addStretch()
        
        return widget
        
    def populate_user_table(self):
        """填充用户表格数据"""
        users = [
            ["admin", "管理员", "在线", "2024-01-15 10:30"],
            ["operator1", "操作员", "离线", "2024-01-14 16:45"],
            ["viewer1", "查看者", "在线", "2024-01-15 09:15"]
        ]
        
        self.user_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            for col, value in enumerate(user):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.user_table.setItem(row, col, item)
        
    def browse_data_path(self):
        """浏览数据保存路径"""
        from PyQt5.QtWidgets import QFileDialog
        
        path = QFileDialog.getExistingDirectory(self, "选择数据保存路径")
        if path:
            self.data_path.setText(path)
            
    def load_config(self):
        """加载配置"""
        try:
            # 基本设置
            self.app_name.setText(self.config.get('app.name', '电能质量分析系统'))
            self.app_version.setText(self.config.get('app.version', '1.0.0'))
            self.company_name.setText(self.config.get('app.company', '电力科技公司'))
            
            # 界面设置
            self.language_combo.setCurrentText(self.config.get('ui.language', '简体中文'))
            self.theme_combo.setCurrentText(self.config.get('ui.theme', '默认主题'))
            self.font_size.setValue(self.config.get('ui.font_size', 10))
            
            # 系统设置
            self.data_path.setText(self.config.get('system.data_path', './data'))
            self.log_level_combo.setCurrentText(self.config.get('system.log_level', 'INFO'))
            self.auto_save_interval.setValue(self.config.get('system.auto_save_interval', 5))
            
            # 数据采集
            self.sampling_frequency.setValue(self.config.get('acquisition.sampling_frequency', 1000))
            self.sampling_points.setValue(self.config.get('acquisition.sampling_points', 1024))
            self.data_update_interval.setValue(self.config.get('acquisition.update_interval', 5))
            self.data_format_combo.setCurrentText(self.config.get('acquisition.data_format', 'CSV'))
            self.monitor_points_count.setValue(self.config.get('acquisition.monitor_points', 3))
            self.monitor_points_names.setText(self.config.get('acquisition.point_names', '监测点1,监测点2,监测点3'))
            
            # 分析参数
            self.voltage_nominal.setValue(self.config.get('analysis.voltage_nominal', 220))
            self.voltage_deviation_threshold.setValue(self.config.get('analysis.voltage_deviation_threshold', 7))
            self.frequency_nominal.setValue(self.config.get('analysis.frequency_nominal', 50))
            self.frequency_deviation_threshold.setValue(self.config.get('analysis.frequency_deviation_threshold', 0.5))
            self.harmonic_orders.setValue(self.config.get('analysis.harmonic_orders', 25))
            self.thd_threshold.setValue(self.config.get('analysis.thd_threshold', 5))
            self.unbalance_threshold.setValue(self.config.get('analysis.unbalance_threshold', 2))
            
            # 告警设置
            self.alarm_level_combo.setCurrentText(self.config.get('alarm.level', '中'))
            self.alarm_sound_combo.setCurrentText(self.config.get('alarm.sound', '默认声音'))
            self.alarm_duration.setValue(self.config.get('alarm.duration', 30))
            
            self.logger.info("配置加载成功")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            
    def save_config(self):
        """保存配置"""
        try:
            # 基本设置
            self.config.set('app.name', self.app_name.text())
            self.config.set('app.version', self.app_version.text())
            self.config.set('app.company', self.company_name.text())
            
            # 界面设置
            self.config.set('ui.language', self.language_combo.currentText())
            self.config.set('ui.theme', self.theme_combo.currentText())
            self.config.set('ui.font_size', self.font_size.value())
            
            # 系统设置
            self.config.set('system.data_path', self.data_path.text())
            self.config.set('system.log_level', self.log_level_combo.currentText())
            self.config.set('system.auto_save_interval', self.auto_save_interval.value())
            
            # 数据采集
            self.config.set('acquisition.sampling_frequency', self.sampling_frequency.value())
            self.config.set('acquisition.sampling_points', self.sampling_points.value())
            self.config.set('acquisition.update_interval', self.data_update_interval.value())
            self.config.set('acquisition.data_format', self.data_format_combo.currentText())
            self.config.set('acquisition.monitor_points', self.monitor_points_count.value())
            self.config.set('acquisition.point_names', self.monitor_points_names.text())
            
            # 分析参数
            self.config.set('analysis.voltage_nominal', self.voltage_nominal.value())
            self.config.set('analysis.voltage_deviation_threshold', self.voltage_deviation_threshold.value())
            self.config.set('analysis.frequency_nominal', self.frequency_nominal.value())
            self.config.set('analysis.frequency_deviation_threshold', self.frequency_deviation_threshold.value())
            self.config.set('analysis.harmonic_orders', self.harmonic_orders.value())
            self.config.set('analysis.thd_threshold', self.thd_threshold.value())
            self.config.set('analysis.unbalance_threshold', self.unbalance_threshold.value())
            
            # 告警设置
            self.config.set('alarm.level', self.alarm_level_combo.currentText())
            self.config.set('alarm.sound', self.alarm_sound_combo.currentText())
            self.config.set('alarm.duration', self.alarm_duration.value())
            
            # 保存到文件
            self.config.save()
            
            QMessageBox.information(self, "保存成功", "系统配置已成功保存")
            self.logger.info("配置保存成功")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            QMessageBox.critical(self, "保存失败", f"保存配置失败: {str(e)}")
            
    def apply_config(self):
        """应用配置"""
        try:
            self.save_config()
            QMessageBox.information(self, "应用成功", "系统配置已应用，部分设置需要重启生效")
            
        except Exception as e:
            self.logger.error(f"应用配置失败: {e}")
            QMessageBox.critical(self, "应用失败", f"应用配置失败: {str(e)}")
            
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(self, "确认重置", 
                                   "确定要重置当前配置吗？所有修改将丢失。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.load_config()
            QMessageBox.information(self, "重置成功", "配置已重置为当前保存状态")
            
    def restore_defaults(self):
        """恢复默认配置"""
        reply = QMessageBox.question(self, "确认恢复默认", 
                                   "确定要恢复默认配置吗？所有自定义设置将丢失。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.config.restore_defaults()
            self.load_config()
            QMessageBox.information(self, "恢复成功", "配置已恢复为默认设置")

# 添加必要的导入
from PyQt5.QtWidgets import QFileDialog