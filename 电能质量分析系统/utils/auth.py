#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证和权限管理模块
"""

import logging
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class User:
    """用户类"""
    
    def __init__(self, username: str, password_hash: str, role: str, 
                 full_name: str = "", email: str = "", is_active: bool = True):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.email = email
        self.is_active = is_active
        self.created_at = datetime.now()
        self.last_login = None
        self.login_count = 0
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'full_name': self.full_name,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """从字典创建用户"""
        user = cls(
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            is_active=data.get('is_active', True)
        )
        
        if data.get('created_at'):
            user.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
        user.login_count = data.get('login_count', 0)
        
        return user

class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.permissions = {
            'admin': [
                'system.config',
                'user.manage',
                'data.view',
                'data.export',
                'report.generate',
                'report.export',
                'dashboard.view',
                'monitor.view',
                'analysis.view'
            ],
            'operator': [
                'data.view',
                'data.export',
                'report.generate',
                'report.export',
                'dashboard.view',
                'monitor.view',
                'analysis.view'
            ],
            'viewer': [
                'data.view',
                'dashboard.view',
                'monitor.view',
                'analysis.view'
            ]
        }
        
    def has_permission(self, role: str, permission: str) -> bool:
        """检查用户角色是否有指定权限"""
        return permission in self.permissions.get(role, [])
        
    def get_role_permissions(self, role: str) -> List[str]:
        """获取角色所有权限"""
        return self.permissions.get(role, [])

class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self, data_file: str = 'data/users.json'):
        self.logger = logging.getLogger(__name__)
        self.data_file = data_file
        self.users: Dict[str, User] = {}
        self.permission_manager = PermissionManager()
        self.current_user: Optional[User] = None
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        self.load_users()
        self.initialize_default_users()
        
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def load_users(self):
        """加载用户数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for user_data in data.get('users', []):
                    user = User.from_dict(user_data)
                    self.users[user.username] = user
                    
                self.logger.info(f"加载了 {len(self.users)} 个用户")
            else:
                self.logger.info("用户数据文件不存在，将创建默认用户")
                
        except Exception as e:
            self.logger.error(f"加载用户数据失败: {e}")
            
    def save_users(self):
        """保存用户数据"""
        try:
            data = {
                'users': [user.to_dict() for user in self.users.values()]
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info("用户数据保存成功")
            
        except Exception as e:
            self.logger.error(f"保存用户数据失败: {e}")
            
    def initialize_default_users(self):
        """初始化默认用户"""
        if not self.users:
            # 创建默认管理员用户
            default_users = [
                ('admin', 'admin123', 'admin', '系统管理员', 'admin@power.com'),
                ('operator', 'operator123', 'operator', '操作员', 'operator@power.com'),
                ('viewer', 'viewer123', 'viewer', '查看者', 'viewer@power.com')
            ]
            
            for username, password, role, full_name, email in default_users:
                if username not in self.users:
                    password_hash = self.hash_password(password)
                    user = User(username, password_hash, role, full_name, email)
                    self.users[username] = user
                    
            self.save_users()
            self.logger.info("默认用户创建完成")
            
    def authenticate(self, username: str, password: str) -> bool:
        """用户认证"""
        if username not in self.users:
            self.logger.warning(f"用户不存在: {username}")
            return False
            
        user = self.users[username]
        
        if not user.is_active:
            self.logger.warning(f"用户已被禁用: {username}")
            return False
            
        password_hash = self.hash_password(password)
        
        if user.password_hash == password_hash:
            # 更新登录信息
            user.last_login = datetime.now()
            user.login_count += 1
            self.current_user = user
            self.save_users()
            
            self.logger.info(f"用户登录成功: {username}")
            return True
        else:
            self.logger.warning(f"密码错误: {username}")
            return False
            
    def logout(self):
        """用户登出"""
        if self.current_user:
            self.logger.info(f"用户登出: {self.current_user.username}")
            self.current_user = None
            
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str = "", email: str = "") -> bool:
        """创建新用户"""
        if username in self.users:
            self.logger.warning(f"用户已存在: {username}")
            return False
            
        if role not in ['admin', 'operator', 'viewer']:
            self.logger.warning(f"无效的角色: {role}")
            return False
            
        password_hash = self.hash_password(password)
        user = User(username, password_hash, role, full_name, email)
        self.users[username] = user
        
        self.save_users()
        self.logger.info(f"用户创建成功: {username}")
        return True
        
    def update_user(self, username: str, **kwargs) -> bool:
        """更新用户信息"""
        if username not in self.users:
            self.logger.warning(f"用户不存在: {username}")
            return False
            
        user = self.users[username]
        
        if 'password' in kwargs:
            user.password_hash = self.hash_password(kwargs['password'])
            
        if 'role' in kwargs:
            if kwargs['role'] in ['admin', 'operator', 'viewer']:
                user.role = kwargs['role']
            else:
                self.logger.warning(f"无效的角色: {kwargs['role']}")
                return False
                
        if 'full_name' in kwargs:
            user.full_name = kwargs['full_name']
            
        if 'email' in kwargs:
            user.email = kwargs['email']
            
        if 'is_active' in kwargs:
            user.is_active = kwargs['is_active']
            
        self.save_users()
        self.logger.info(f"用户信息更新成功: {username}")
        return True
        
    def delete_user(self, username: str) -> bool:
        """删除用户"""
        if username not in self.users:
            self.logger.warning(f"用户不存在: {username}")
            return False
            
        if username == 'admin':
            self.logger.warning("不能删除管理员账户")
            return False
            
        del self.users[username]
        self.save_users()
        self.logger.info(f"用户删除成功: {username}")
        return True
        
    def get_user(self, username: str) -> Optional[User]:
        """获取用户信息"""
        return self.users.get(username)
        
    def list_users(self) -> List[User]:
        """获取用户列表"""
        return list(self.users.values())
        
    def has_permission(self, permission: str) -> bool:
        """检查当前用户是否有指定权限"""
        if not self.current_user:
            return False
            
        return self.permission_manager.has_permission(
            self.current_user.role, permission
        )
        
    def get_current_user_permissions(self) -> List[str]:
        """获取当前用户所有权限"""
        if not self.current_user:
            return []
            
        return self.permission_manager.get_role_permissions(self.current_user.role)

# 全局认证管理器实例
auth_manager = AuthenticationManager()