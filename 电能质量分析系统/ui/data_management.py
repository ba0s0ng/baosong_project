#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
"""

import logging
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QPushButton, QComboBox, QDateEdit,
                            QFileDialog, QProgressBar, QMessageBox)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont

from utils.fake_data import FakeDataGenerator

class DataManagementWidget(QWidget):
    """数据管理部件"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.fake_data = FakeDataGenerator()
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("数据管理")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 数据查询区域
        layout.addWidget(self.create_query_panel())
        
        # 数据表格
        layout.addWidget(self.create_data_table())
        
        # 操作按钮区域
        layout.addWidget(self.create_operation_panel())
        
        layout.addStretch()
        
    def create_query_panel(self):
        """创建查询面板"""
        group_box = QGroupBox("数据查询")
        layout = QGridLayout(group_box)
        
        # 监测点选择
        layout.addWidget(QLabel("监测点:"), 0, 0)
        self.point_combo = QComboBox()
        self.point_combo.addItems(["所有监测点", "监测点1", "监测点2", "监测点3"])
        layout.addWidget(self.point_combo, 0, 1)
        
        # 开始日期
        layout.addWidget(QLabel("开始日期:"), 0, 2)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        layout.addWidget(self.start_date, 0, 3)
        
        # 结束日期
        layout.addWidget(QLabel("结束日期:"), 1, 0)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        layout.addWidget(self.end_date, 1, 1)
        
        # 数据类型
        layout.addWidget(QLabel("数据类型:"), 1, 2)
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["所有数据", "实时数据", "告警数据", "统计数据"])
        layout.addWidget(self.data_type_combo, 1, 3)
        
        # 查询按钮
        self.query_btn = QPushButton("查询")
        self.query_btn.clicked.connect(self.query_data)
        layout.addWidget(self.query_btn, 2, 0, 1, 2)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_query)
        layout.addWidget(self.reset_btn, 2, 2, 1, 2)
        
        return group_box
        
    def create_data_table(self):
        """创建数据表格"""
        group_box = QGroupBox("数据列表")
        layout = QVBoxLayout(group_box)
        
        # 数据表格
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(8)
        self.data_table.setHorizontalHeaderLabels([
            "时间", "监测点", "电压(V)", "电流(A)", "频率(Hz)", "功率因数", "状态", "操作"
        ])
        
        # 设置表格属性
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 添加示例数据
        self.load_sample_data()
        
        layout.addWidget(self.data_table)
        
        return group_box
        
    def create_operation_panel(self):
        """创建操作面板"""
        group_box = QGroupBox("数据操作")
        layout = QHBoxLayout(group_box)
        
        # 导出按钮
        self.export_btn = QPushButton("导出数据")
        self.export_btn.clicked.connect(self.export_data)
        layout.addWidget(self.export_btn)
        
        # 导入按钮
        self.import_btn = QPushButton("导入数据")
        self.import_btn.clicked.connect(self.import_data)
        layout.addWidget(self.import_btn)
        
        # 备份按钮
        self.backup_btn = QPushButton("数据备份")
        self.backup_btn.clicked.connect(self.backup_data)
        layout.addWidget(self.backup_btn)
        
        # 删除按钮
        self.delete_btn = QPushButton("删除数据")
        self.delete_btn.clicked.connect(self.delete_data)
        layout.addWidget(self.delete_btn)
        
        layout.addStretch()
        
        return group_box
        
    def load_sample_data(self):
        """加载示例数据"""
        # 清空表格
        self.data_table.setRowCount(0)
        
        # 添加示例数据
        sample_data = [
            ["2024-01-15 10:30:00", "监测点1", "220.5", "102.3", "50.01", "0.95", "正常", "查看"],
            ["2024-01-15 10:29:00", "监测点2", "219.8", "98.7", "49.98", "0.93", "正常", "查看"],
            ["2024-01-15 10:28:00", "监测点1", "221.2", "105.6", "50.03", "0.96", "正常", "查看"],
            ["2024-01-15 10:27:00", "监测点3", "218.5", "95.4", "49.95", "0.91", "警告", "查看"],
            ["2024-01-15 10:26:00", "监测点2", "222.1", "101.2", "50.05", "0.94", "正常", "查看"],
            ["2024-01-15 10:25:00", "监测点1", "219.3", "99.8", "49.97", "0.92", "正常", "查看"],
            ["2024-01-15 10:24:00", "监测点3", "217.9", "94.1", "49.93", "0.90", "异常", "查看"],
            ["2024-01-15 10:23:00", "监测点2", "220.7", "103.5", "50.02", "0.95", "正常", "查看"]
        ]
        
        self.data_table.setRowCount(len(sample_data))
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                
                # 设置状态颜色
                if col == 6:  # 状态列
                    if value == "正常":
                        item.setForeground(Qt.green)
                    elif value == "警告":
                        item.setForeground(Qt.yellow)
                    elif value == "异常":
                        item.setForeground(Qt.red)
                
                self.data_table.setItem(row, col, item)
        
        # 添加操作按钮
        for row in range(len(sample_data)):
            view_btn = QPushButton("查看详情")
            view_btn.clicked.connect(lambda checked, r=row: self.view_data_details(r))
            self.data_table.setCellWidget(row, 7, view_btn)
        
    def query_data(self):
        """查询数据"""
        try:
            monitor_point = self.point_combo.currentText()
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            data_type = self.data_type_combo.currentText()
            
            self.logger.info(f"查询数据: {monitor_point}, {start_date} 到 {end_date}, {data_type}")
            
            # 显示查询结果
            QMessageBox.information(self, "查询结果", 
                                  f"查询条件:\n监测点: {monitor_point}\n"
                                  f"时间范围: {start_date} 到 {end_date}\n"
                                  f"数据类型: {data_type}\n\n"
                                  f"找到 8 条记录")
            
        except Exception as e:
            self.logger.error(f"查询数据失败: {e}")
            QMessageBox.critical(self, "错误", f"查询数据失败: {str(e)}")
            
    def reset_query(self):
        """重置查询条件"""
        self.point_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.end_date.setDate(QDate.currentDate())
        self.data_type_combo.setCurrentIndex(0)
        
    def export_data(self):
        """导出数据"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出数据", "", "CSV文件 (*.csv);;Excel文件 (*.xlsx);;所有文件 (*)"
            )
            
            if file_path:
                self.logger.info(f"导出数据到: {file_path}")
                
                # 模拟导出过程
                progress_dialog = QMessageBox(self)
                progress_dialog.setText("正在导出数据...")
                progress_dialog.show()
                
                # 这里可以添加实际的导出逻辑
                QMessageBox.information(self, "导出成功", f"数据已成功导出到: {file_path}")
                
        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            QMessageBox.critical(self, "错误", f"导出数据失败: {str(e)}")
            
    def import_data(self):
        """导入数据"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入数据", "", "CSV文件 (*.csv);;Excel文件 (*.xlsx);;所有文件 (*)"
            )
            
            if file_path:
                self.logger.info(f"从文件导入数据: {file_path}")
                
                # 模拟导入过程
                QMessageBox.information(self, "导入成功", 
                                      f"数据已成功从文件导入: {os.path.basename(file_path)}")
                
        except Exception as e:
            self.logger.error(f"导入数据失败: {e}")
            QMessageBox.critical(self, "错误", f"导入数据失败: {str(e)}")
            
    def backup_data(self):
        """备份数据"""
        try:
            backup_dir = QFileDialog.getExistingDirectory(self, "选择备份目录")
            
            if backup_dir:
                self.logger.info(f"备份数据到: {backup_dir}")
                
                # 模拟备份过程
                QMessageBox.information(self, "备份成功", 
                                      f"数据已成功备份到: {backup_dir}")
                
        except Exception as e:
            self.logger.error(f"备份数据失败: {e}")
            QMessageBox.critical(self, "错误", f"备份数据失败: {str(e)}")
            
    def delete_data(self):
        """删除数据"""
        try:
            reply = QMessageBox.question(
                self, "确认删除",
                "确定要删除选中的数据吗？此操作不可恢复。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.logger.info("删除选中的数据")
                QMessageBox.information(self, "删除成功", "数据删除成功")
                
        except Exception as e:
            self.logger.error(f"删除数据失败: {e}")
            QMessageBox.critical(self, "错误", f"删除数据失败: {str(e)}")
            
    def view_data_details(self, row):
        """查看数据详情"""
        try:
            time = self.data_table.item(row, 0).text()
            point = self.data_table.item(row, 1).text()
            voltage = self.data_table.item(row, 2).text()
            current = self.data_table.item(row, 3).text()
            frequency = self.data_table.item(row, 4).text()
            power_factor = self.data_table.item(row, 5).text()
            status = self.data_table.item(row, 6).text()
            
            detail_text = f"""
            <h3>数据详情</h3>
            <p><b>时间:</b> {time}</p>
            <p><b>监测点:</b> {point}</p>
            <p><b>电压:</b> {voltage} V</p>
            <p><b>电流:</b> {current} A</p>
            <p><b>频率:</b> {frequency} Hz</p>
            <p><b>功率因数:</b> {power_factor}</p>
            <p><b>状态:</b> {status}</p>
            """
            
            QMessageBox.information(self, "数据详情", detail_text)
            
        except Exception as e:
            self.logger.error(f"查看数据详情失败: {e}")
            QMessageBox.critical(self, "错误", f"查看数据详情失败: {str(e)}")