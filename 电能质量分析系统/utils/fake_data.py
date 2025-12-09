#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
假数据生成器模块
用于生成电能质量分析系统的演示数据
"""

import random
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class FakeDataGenerator:
    """假数据生成器类"""
    
    def __init__(self):
        self.base_voltage = 220.0  # 基准电压
        self.base_current = 100.0  # 基准电流
        self.base_frequency = 50.0  # 基准频率
        self.last_update_time = time.time()
        
        # 初始化随机种子
        random.seed(time.time())
        np.random.seed(int(time.time()))
        
    def generate_realtime_data(self) -> Dict[str, float]:
        """生成实时监测数据"""
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        
        # 模拟电压波动
        voltage_variation = np.sin(current_time * 0.5) * 5 + np.random.normal(0, 1)
        voltage = self.base_voltage + voltage_variation
        
        # 模拟电流波动
        current_variation = np.sin(current_time * 0.3) * 10 + np.random.normal(0, 2)
        current = self.base_current + current_variation
        
        # 模拟频率波动
        frequency_variation = np.sin(current_time * 0.1) * 0.1 + np.random.normal(0, 0.02)
        frequency = self.base_frequency + frequency_variation
        
        # 模拟功率因数
        power_factor = 0.95 + np.sin(current_time * 0.2) * 0.05 + np.random.normal(0, 0.01)
        power_factor = max(0.8, min(1.0, power_factor))  # 限制在合理范围内
        
        # 模拟有功功率和无功功率
        active_power = voltage * current * power_factor / 1000  # kW
        reactive_power = voltage * current * np.sqrt(1 - power_factor**2) / 1000  # kvar
        
        self.last_update_time = current_time
        
        return {
            'voltage': round(voltage, 1),
            'current': round(current, 1),
            'frequency': round(frequency, 2),
            'power_factor': round(power_factor, 3),
            'active_power': round(active_power, 2),
            'reactive_power': round(reactive_power, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_three_phase_data(self) -> Dict[str, Dict[str, float]]:
        """生成三相数据"""
        current_time = time.time()
        
        # 生成三相电压（带相位差）
        phase_shift = 2 * np.pi / 3  # 120度相位差
        
        voltages = {}
        currents = {}
        active_powers = {}
        reactive_powers = {}
        power_factors = {}
        
        for i, phase in enumerate(['A', 'B', 'C']):
            # 电压数据
            base_voltage = self.base_voltage
            voltage_variation = np.sin(current_time * 0.5 + i * phase_shift) * 3
            voltage_noise = np.random.normal(0, 0.5)
            voltages[phase] = round(base_voltage + voltage_variation + voltage_noise, 1)
            
            # 电流数据
            base_current = self.base_current
            current_variation = np.sin(current_time * 0.3 + i * phase_shift) * 5
            current_noise = np.random.normal(0, 1)
            currents[phase] = round(base_current + current_variation + current_noise, 1)
            
            # 功率因数（每相略有不同）
            pf_variation = np.sin(current_time * 0.2 + i * phase_shift * 0.5) * 0.03
            power_factor = 0.95 + pf_variation + np.random.normal(0, 0.005)
            power_factors[phase] = round(max(0.85, min(0.99, power_factor)), 3)
            
            # 有功功率和无功功率
            active_power = (voltages[phase] * currents[phase] * power_factors[phase]) / 1000
            reactive_power = (voltages[phase] * currents[phase] * 
                            np.sqrt(1 - power_factors[phase]**2)) / 1000
            
            active_powers[phase] = round(active_power, 2)
            reactive_powers[phase] = round(reactive_power, 2)
        
        return {
            'voltages': voltages,
            'currents': currents,
            'active_powers': active_powers,
            'reactive_powers': reactive_powers,
            'power_factors': power_factors,
            'frequency': round(self.base_frequency + np.random.normal(0, 0.01), 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_harmonic_data(self) -> Dict[str, List[float]]:
        """生成谐波分析数据"""
        # 谐波次数：2, 3, 5, 7, 11, 13次
        harmonic_orders = [2, 3, 5, 7, 11, 13]
        
        # 生成三相谐波数据
        harmonic_data = {}
        
        for phase in ['A', 'B', 'C']:
            phase_harmonics = []
            
            for order in harmonic_orders:
                # 谐波含量随次数增加而减小
                base_content = 3.0 / (order ** 0.7)
                
                # 添加随机波动
                variation = np.random.normal(0, 0.1)
                harmonic_content = max(0.1, base_content + variation)
                
                phase_harmonics.append(round(harmonic_content, 2))
            
            harmonic_data[f'{phase}_phase'] = phase_harmonics
        
        # 计算总谐波畸变率(THD)
        thd_values = {}
        for phase in ['A', 'B', 'C']:
            harmonics_sum = sum([h**2 for h in harmonic_data[f'{phase}_phase']])
            thd = np.sqrt(harmonics_sum) * 100 / self.base_voltage
            thd_values[phase] = round(thd, 2)
        
        harmonic_data['thd'] = thd_values
        harmonic_data['orders'] = harmonic_orders
        
        return harmonic_data
    
    def generate_voltage_deviation_data(self, hours: int = 24) -> Dict[str, Any]:
        """生成电压偏差数据"""
        # 生成指定小时数的电压偏差数据
        data_points = []
        current_time = datetime.now()
        
        for i in range(hours):
            timestamp = current_time - timedelta(hours=i)
            
            # 电压偏差（百分比）
            base_deviation = np.sin(i * 0.5) * 2  # 基础波动
            random_deviation = np.random.normal(0, 0.5)  # 随机波动
            deviation = base_deviation + random_deviation
            
            # 电压值
            voltage = self.base_voltage * (1 + deviation / 100)
            
            data_points.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'deviation_percent': round(deviation, 2),
                'voltage': round(voltage, 1),
                'is_normal': abs(deviation) <= 7  # 国标允许±7%
            })
        
        # 统计信息
        deviations = [point['deviation_percent'] for point in data_points]
        normal_count = sum(1 for point in data_points if point['is_normal'])
        
        stats = {
            'max_deviation': round(max(deviations), 2),
            'min_deviation': round(min(deviations), 2),
            'avg_deviation': round(np.mean(deviations), 2),
            'normal_rate': round(normal_count / len(data_points) * 100, 1)
        }
        
        return {
            'data_points': data_points[::-1],  # 反转顺序，最新的在前
            'statistics': stats
        }
    
    def generate_frequency_deviation_data(self, hours: int = 24) -> Dict[str, Any]:
        """生成频率偏差数据"""
        data_points = []
        current_time = datetime.now()
        
        for i in range(hours):
            timestamp = current_time - timedelta(hours=i)
            
            # 频率偏差（Hz）
            base_deviation = np.sin(i * 0.3) * 0.08  # 基础波动
            random_deviation = np.random.normal(0, 0.02)  # 随机波动
            deviation = base_deviation + random_deviation
            
            # 频率值
            frequency = self.base_frequency + deviation
            
            data_points.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'deviation_hz': round(deviation, 3),
                'frequency': round(frequency, 3),
                'is_normal': abs(deviation) <= 0.2  # 国标允许±0.2Hz
            })
        
        # 统计信息
        deviations = [point['deviation_hz'] for point in data_points]
        normal_count = sum(1 for point in data_points if point['is_normal'])
        
        stats = {
            'max_deviation': round(max(deviations), 3),
            'min_deviation': round(min(deviations), 3),
            'avg_deviation': round(np.mean(deviations), 3),
            'normal_rate': round(normal_count / len(data_points) * 100, 1)
        }
        
        return {
            'data_points': data_points[::-1],
            'statistics': stats
        }
    
    def generate_unbalance_data(self) -> Dict[str, float]:
        """生成三相不平衡数据"""
        # 电压不平衡度
        voltage_imbalance = 1.2 + np.random.normal(0, 0.3)
        voltage_imbalance = max(0.5, min(5.0, voltage_imbalance))
        
        # 电流不平衡度
        current_imbalance = 3.5 + np.random.normal(0, 0.5)
        current_imbalance = max(1.0, min(8.0, current_imbalance))
        
        return {
            'voltage_unbalance_percent': round(voltage_imbalance, 2),
            'current_unbalance_percent': round(current_imbalance, 2),
            'max_unbalance_percent': round(max(voltage_imbalance, current_imbalance), 2),
            'occurrence_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': random.randint(5, 30)
        }
    
    def generate_flicker_data(self) -> Dict[str, float]:
        """生成电压闪变数据"""
        # 短时闪变值Pst
        pst = 0.85 + np.random.normal(0, 0.1)
        pst = max(0.5, min(1.5, pst))
        
        # 长时闪变值Plt
        plt = 0.72 + np.random.normal(0, 0.08)
        plt = max(0.4, min(1.2, plt))
        
        # 闪变等级评估
        if pst < 0.8:
            flicker_level = "无影响"
        elif pst < 1.0:
            flicker_level = "轻微"
        elif pst < 1.3:
            flicker_level = "明显"
        else:
            flicker_level = "严重"
        
        return {
            'pst': round(pst, 2),
            'plt': round(plt, 2),
            'max_pst': round(pst + np.random.normal(0, 0.2), 2),
            'flicker_level': flicker_level,
            'occurrence_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_historical_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """生成历史数据"""
        historical_data = []
        current_time = datetime.now()
        
        for day in range(days):
            date = current_time - timedelta(days=day)
            
            # 每日统计数据
            daily_data = {
                'date': date.strftime('%Y-%m-%d'),
                'avg_voltage': round(self.base_voltage + np.random.normal(0, 2), 1),
                'avg_current': round(self.base_current + np.random.normal(0, 5), 1),
                'avg_frequency': round(self.base_frequency + np.random.normal(0, 0.01), 3),
                'max_voltage_deviation': round(abs(np.random.normal(3, 1)), 2),
                'max_frequency_deviation': round(abs(np.random.normal(0.1, 0.03)), 3),
                'thd': round(np.random.normal(3, 0.5), 2),
                'alarm_count': random.randint(0, 5)
            }
            
            historical_data.append(daily_data)
        
        return historical_data

# 使用示例
if __name__ == "__main__":
    generator = FakeDataGenerator()
    
    # 测试实时数据生成
    realtime_data = generator.generate_realtime_data()
    print("实时数据:", realtime_data)
    
    # 测试三相数据生成
    three_phase_data = generator.generate_three_phase_data()
    print("三相数据:", three_phase_data)
    
    # 测试谐波数据生成
    harmonic_data = generator.generate_harmonic_data()
    print("谐波数据:", harmonic_data)