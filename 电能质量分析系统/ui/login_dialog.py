#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录对话框模块
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QLineEdit, QPushButton, QCheckBox,
                            QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from utils.auth import auth_manager

class LoginDialog(QDialog):
    """登录对话框"""
    
    login_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("用户登录")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("电能质量分析系统")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 版本信息
        version_label = QLabel("版本 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        layout.addSpacing(20)
        
        # 登录表单
        login_group = QGroupBox("用户登录")
        login_layout = QGridLayout(login_group)
        
        # 用户名
        login_layout.addWidget(QLabel("用户名:"), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setText("admin")  # 默认用户名
        login_layout.addWidget(self.username_edit, 0, 1)
        
        # 密码
        login_layout.addWidget(QLabel("密码:"), 1, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setText("admin123")  # 默认密码
        login_layout.addWidget(self.password_edit, 1, 1)
        
        # 记住密码
        self.remember_check = QCheckBox("记住密码")
        login_layout.addWidget(self.remember_check, 2, 0, 1, 2)
        
        # 自动登录
        self.auto_login_check = QCheckBox("自动登录")
        login_layout.addWidget(self.auto_login_check, 3, 0, 1, 2)
        
        layout.addWidget(login_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setDefault(True)
        button_layout.addWidget(self.login_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        button_layout.addWidget(self.cancel_btn)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置")
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        # 用户信息
        info_label = QLabel("默认用户: admin/admin123, operator/operator123, viewer/viewer123")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
    def setup_connections(self):
        """设置信号连接"""
        self.login_btn.clicked.connect(self.login)
        self.cancel_btn.clicked.connect(self.reject)
        self.reset_btn.clicked.connect(self.reset_form)
        
        # 回车键登录
        self.username_edit.returnPressed.connect(self.login)
        self.password_edit.returnPressed.connect(self.login)
        
    def login(self):
        """用户登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            self.username_edit.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            self.password_edit.setFocus()
            return
            
        # 尝试认证
        if auth_manager.authenticate(username, password):
            self.logger.info(f"用户登录成功: {username}")
            
            # 保存登录设置（简化实现）
            if self.remember_check.isChecked():
                self.save_login_settings(username, self.auto_login_check.isChecked())
            else:
                self.clear_login_settings()
                
            # 发送登录成功信号
            self.login_success.emit()
            self.accept()
            
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")
            self.password_edit.clear()
            self.password_edit.setFocus()
            
    def reset_form(self):
        """重置表单"""
        self.username_edit.clear()
        self.password_edit.clear()
        self.remember_check.setChecked(False)
        self.auto_login_check.setChecked(False)
        self.username_edit.setFocus()
        
    def save_login_settings(self, username: str, auto_login: bool):
        """保存登录设置"""
        # 简化实现，实际应用中应该加密存储
        try:
            import json
            import os
            
            # 确保data目录存在
            if not os.path.exists('data'):
                os.makedirs('data')
                
            settings = {
                'username': username,
                'auto_login': auto_login,
                'timestamp': '2024-01-15'  # 简化时间戳
            }
            
            with open('data/login_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
            self.logger.info("登录设置已保存")
            
        except Exception as e:
            self.logger.error(f"保存登录设置失败: {e}")
            
    def clear_login_settings(self):
        """清除登录设置"""
        try:
            import os
            if os.path.exists('data/login_settings.json'):
                os.remove('data/login_settings.json')
                self.logger.info("登录设置已清除")
                
        except Exception as e:
            self.logger.error(f"清除登录设置失败: {e}")
            
    def load_login_settings(self):
        """加载登录设置"""
        try:
            import json
            import os
            
            if os.path.exists('data/login_settings.json'):
                with open('data/login_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                self.username_edit.setText(settings.get('username', ''))
                self.auto_login_check.setChecked(settings.get('auto_login', False))
                
                if self.auto_login_check.isChecked():
                    self.remember_check.setChecked(True)
                    # 自动登录逻辑（简化实现）
                    self.logger.info("检测到自动登录设置")
                    
        except Exception as e:
            self.logger.error(f"加载登录设置失败: {e}")
            
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.load_login_settings()
        
        # 如果设置了自动登录，尝试自动登录
        if self.auto_login_check.isChecked() and self.username_edit.text():
            self.logger.info("尝试自动登录")
            # 这里可以添加自动登录逻辑
            # 为了安全，实际应用中应该更谨慎处理自动登录

class UserInfoDialog(QDialog):
    """用户信息对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("用户信息")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout(self)
        
        if auth_manager.current_user:
            user = auth_manager.current_user
            
            # 用户信息
            info_group = QGroupBox("用户信息")
            info_layout = QGridLayout(info_group)
            
            info_layout.addWidget(QLabel("用户名:"), 0, 0)
            info_layout.addWidget(QLabel(user.username), 0, 1)
            
            info_layout.addWidget(QLabel("角色:"), 1, 0)
            info_layout.addWidget(QLabel(user.role), 1, 1)
            
            info_layout.addWidget(QLabel("姓名:"), 2, 0)
            info_layout.addWidget(QLabel(user.full_name), 2, 1)
            
            info_layout.addWidget(QLabel("邮箱:"), 3, 0)
            info_layout.addWidget(QLabel(user.email), 3, 1)
            
            info_layout.addWidget(QLabel("最后登录:"), 4, 0)
            last_login = user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "从未登录"
            info_layout.addWidget(QLabel(last_login), 4, 1)
            
            info_layout.addWidget(QLabel("登录次数:"), 5, 0)
            info_layout.addWidget(QLabel(str(user.login_count)), 5, 1)
            
            layout.addWidget(info_group)
            
        # 按钮
        button_layout = QHBoxLayout()
        
        logout_btn = QPushButton("退出登录")
        logout_btn.clicked.connect(self.logout)
        button_layout.addWidget(logout_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def logout(self):
        """退出登录"""
        auth_manager.logout()
        self.accept()
        
        # 显示登录对话框
        login_dialog = LoginDialog(self.parent())
        login_dialog.exec_()