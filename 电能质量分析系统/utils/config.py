#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件管理模块
"""

import os
import json
import logging
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json'
        )
        self.data = self._load_default_config()
        self._load_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "app": {
                "name": "电能质量分析系统",
                "version": "1.0.0",
                "company": "电力科技",
                "language": "zh_CN"
            },
            "ui": {
                "theme": "default",
                "font_size": 10,
                "window_width": 1200,
                "window_height": 800,
                "auto_save_interval": 300  # 5分钟
            },
            "data": {
                "sampling_rate": 1000,  # 采样率(Hz)
                "buffer_size": 10000,   # 缓冲区大小
                "history_days": 30,      # 历史数据保存天数
                "fake_data_enabled": True  # 启用假数据
            },
            "analysis": {
                "harmonic_orders": 50,   # 谐波分析阶数
                "voltage_threshold": 0.1,  # 电压偏差阈值
                "frequency_threshold": 0.05,  # 频率偏差阈值
                "flicker_threshold": 1.0,    # 闪变阈值
            },
            "alarm": {
                "voltage_upper": 1.1,    # 电压上限(标幺值)
                "voltage_lower": 0.9,    # 电压下限
                "frequency_upper": 50.2, # 频率上限(Hz)
                "frequency_lower": 49.8,  # 频率下限
                "harmonic_thd_limit": 0.08  # 谐波畸变率限值
            }
        }
    
    def _load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
        except Exception as e:
            logging.warning(f"加载配置文件失败: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """合并配置"""
        def merge_dict(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.data, new_config)
    
    def save(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        current = self.data
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def __getitem__(self, key: str):
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        self.set(key, value)