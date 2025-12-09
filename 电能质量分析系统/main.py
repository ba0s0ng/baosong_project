#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电能质量分析系统 - 主程序入口
基于PyQt5开发的电能质量监测与分析系统
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont

# 导入自定义模块
from ui.main_window import MainWindow
from utils.config import Config
from utils.logger import setup_logging
from ui.login_dialog import LoginDialog

class PowerQualityApp:
    """电能质量分析系统主应用类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = Config()
        
        # 设置应用程序信息
        self.app.setApplicationName("电能质量分析系统")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("电力科技")
        
        # 设置应用字体
        font = QFont("Microsoft YaHei", 10)
        self.app.setFont(font)
        
        # 设置日志
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 创建主窗口（但不立即显示）
        self.main_window = MainWindow()
        
        # 创建登录对话框
        self.login_dialog = LoginDialog()
        
    def run(self):
        """运行应用程序"""
        try:
            self.logger.info("启动电能质量分析系统")
            
            def on_login_success():
                """登录成功回调"""
                self.login_dialog.accept()
                self.main_window.showMaximized()
                self.logger.info("用户登录成功，显示主窗口")
                
            # 连接登录成功信号
            self.login_dialog.login_success.connect(on_login_success)
            
            # 显示登录对话框
            if self.login_dialog.exec_() == QDialog.Accepted:
                # 登录成功，应用继续运行
                self.logger.info("应用程序启动成功")
                return self.app.exec_()
            else:
                # 用户取消登录
                self.logger.info("用户取消登录，应用程序退出")
                return 0
            
        except Exception as e:
            self.logger.error(f"应用程序启动失败: {e}")
            QMessageBox.critical(None, "启动错误", f"应用程序启动失败:\n{str(e)}")
            return 1

def main():
    """主函数"""
    # 检查必要的依赖
    try:
        import PyQt5
        import numpy
        import matplotlib
    except ImportError as e:
        print(f"缺少必要的依赖包: {e}")
        print("请安装以下包: PyQt5, numpy, matplotlib")
        return 1
    
    # 创建并运行应用程序
    app = PowerQualityApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())