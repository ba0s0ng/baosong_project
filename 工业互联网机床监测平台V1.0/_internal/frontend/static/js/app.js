/**
 * 工业互联网机床状态监测平台 - 主应用模块
 */

class IndustrialIoTApp {
    constructor() {
        this.currentTab = 'dashboard';
        this.machines = new Map();
        this.alarms = [];
        this.systemStatus = {};
        
        // API基础URL
        this.apiBaseUrl = '/api';
        
        // 初始化应用
        this.init();
    }
    
    /**
     * 初始化应用
     */
    init() {
        console.log('初始化工业互联网机床监测平台...');
        
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupApp();
            });
        } else {
            this.setupApp();
        }
    }
    
    /**
     * 设置应用
     */
    setupApp() {
        // 设置导航
        this.setupNavigation();
        
        // 设置事件监听器
        this.setupEventListeners();
        
        // 设置WebSocket事件处理
        this.setupWebSocketHandlers();
        
        // 初始化数据
        this.loadInitialData();
        
        // 设置定时任务
        this.setupTimers();
        
        console.log('应用初始化完成');
    }
    
    /**
     * 设置导航
     */
    setupNavigation() {
        const navLinks = document.querySelectorAll('[data-tab]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = link.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }
    
    /**
     * 切换标签页
     */
    switchTab(tabName) {
        // 隐藏所有标签页内容
        const tabContents = document.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // 显示选中的标签页
        const targetContent = document.getElementById(`${tabName}-content`);
        if (targetContent) {
            targetContent.classList.add('active');
        }
        
        // 更新导航状态
        const navLinks = document.querySelectorAll('[data-tab]');
        navLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        this.currentTab = tabName;
        
        // 根据标签页执行特定操作
        this.onTabSwitch(tabName);
    }
    
    /**
     * 标签页切换时的处理
     */
    onTabSwitch(tabName) {
        switch (tabName) {
            case 'dashboard':
                this.refreshDashboard();
                break;
            case 'machines':
                this.refreshMachines();
                break;
            case 'digital-twin':
                this.refreshDigitalTwin();
                break;
            case 'alarms':
                this.refreshAlarms();
                break;
            case 'analytics':
                this.refreshAnalytics();
                break;
        }
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 数字孪生控制面板事件
        this.setupDigitalTwinControls();
        
        // 全局按钮事件
        this.setupGlobalButtons();
    }
    
    /**
     * 设置数字孪生控制面板
     */
    setupDigitalTwinControls() {
        // 机床选择
        const machineSelect = document.getElementById('twin-machine-select');
        if (machineSelect) {
            machineSelect.addEventListener('change', (e) => {
                const machineId = e.target.value;
                if (machineId && window.threeSceneManager) {
                    window.threeSceneManager.selectMachine(machineId);
                }
            });
        }
        
        // 转速滑块
        const speedSlider = document.getElementById('twin-speed-slider');
        const speedValue = document.getElementById('twin-speed-value');
        if (speedSlider && speedValue) {
            speedSlider.addEventListener('input', (e) => {
                speedValue.textContent = e.target.value;
            });
        }
        
        // 负载滑块
        const loadSlider = document.getElementById('twin-load-slider');
        const loadValue = document.getElementById('twin-load-value');
        if (loadSlider && loadValue) {
            loadSlider.addEventListener('input', (e) => {
                loadValue.textContent = e.target.value;
            });
        }
    }
    
    /**
     * 设置全局按钮
     */
    setupGlobalButtons() {
        // 为所有按钮添加点击效果
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn')) {
                e.target.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    e.target.style.transform = 'scale(1)';
                }, 100);
            }
        });
    }
    
    /**
     * 设置WebSocket事件处理
     */
    setupWebSocketHandlers() {
        if (window.wsManager) {
            // 机床数据更新
            window.wsManager.on('machine_data', (message) => {
                this.handleMachineDataUpdate(message);
            });
            
            // 报警事件
            window.wsManager.on('alarm', (message) => {
                this.handleAlarmEvent(message);
            });
            
            // 状态变化
            window.wsManager.on('status_change', (message) => {
                this.handleStatusChange(message);
            });
            
            // 连接状态变化
            window.wsManager.on('connected', () => {
                this.onWebSocketConnected();
            });
            
            window.wsManager.on('disconnected', () => {
                this.onWebSocketDisconnected();
            });
        }
    }
    
    /**
     * WebSocket连接成功
     */
    onWebSocketConnected() {
        console.log('WebSocket连接成功');
        // 订阅所有机床数据
        this.machines.forEach((machine, machineId) => {
            window.wsManager.subscribe(machineId);
        });
    }
    
    /**
     * WebSocket连接断开
     */
    onWebSocketDisconnected() {
        console.log('WebSocket连接断开');
        this.showNotification('连接已断开，正在尝试重连...', 'warning');
    }
    
    /**
     * 处理机床数据更新
     */
    handleMachineDataUpdate(message) {
        const machineId = message.machine_id;
        const data = message.data;
        
        // 更新机床数据
        this.updateMachineData(machineId, data);
        
        // 更新图表
        if (window.chartManager) {
            window.chartManager.updateRealtimeChart(machineId, data);
        }
        
        // 更新3D场景
        if (window.threeSceneManager) {
            window.threeSceneManager.updateMachineStatus(machineId, 'RUNNING', data);
        }
    }
    
    /**
     * 处理报警事件
     */
    handleAlarmEvent(message) {
        const alarm = message.alarm;
        this.showAlarmNotification(alarm);
        this.addAlarmToList(alarm);
        this.updateAlarmCount();
    }
    
    /**
     * 处理状态变化
     */
    handleStatusChange(message) {
        const machineId = message.machine_id;
        const newStatus = message.new_status;
        
        this.updateMachineStatus(machineId, newStatus);
    }
    
    /**
     * 加载初始数据
     */
    async loadInitialData() {
        try {
            // 加载系统健康状态
            await this.loadSystemHealth();
            
            // 加载机床列表
            await this.loadMachines();
            
            // 加载报警数据
            await this.loadAlarms();
            
            // 更新仪表盘
            this.updateDashboard();
            
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.showNotification('加载数据失败，请刷新页面重试', 'error');
        }
    }
    
    /**
     * 加载系统健康状态
     */
    async loadSystemHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            this.systemStatus = data.components || {};
            this.updateSystemStatus();
            
        } catch (error) {
            console.error('加载系统状态失败:', error);
        }
    }
    
    /**
     * 加载机床列表
     */
    async loadMachines() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/machines`);
            const data = await response.json();
            
            if (data.machines) {
                data.machines.forEach(machine => {
                    this.machines.set(machine.machine_id, machine);
                });
                
                this.updateMachinesList();
                this.updateMachineSelect();
            }
            
        } catch (error) {
            console.error('加载机床列表失败:', error);
        }
    }
    
    /**
     * 加载报警数据
     */
    async loadAlarms() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/alarms`);
            const data = await response.json();
            
            if (data.alarms) {
                this.alarms = data.alarms;
                this.updateAlarmsList();
                this.updateAlarmCount();
            }
            
        } catch (error) {
            console.error('加载报警数据失败:', error);
        }
    }
    
    /**
     * 更新机床数据
     */
    updateMachineData(machineId, data) {
        const machine = this.machines.get(machineId);
        if (machine) {
            machine.data = { ...machine.data, ...data };
            machine.last_update = new Date().toISOString();
            
            // 更新显示
            this.updateMachineStatusDisplay(machineId);
        }
    }
    
    /**
     * 更新机床状态
     */
    updateMachineStatus(machineId, status) {
        const machine = this.machines.get(machineId);
        if (machine) {
            machine.status = status;
            this.updateMachineStatusDisplay(machineId);
        }
    }
    
    /**
     * 更新仪表盘
     */
    updateDashboard() {
        this.updateStatCards();
        this.updateMachineStatusList();
        this.updateRecentAlarms();
    }
    
    /**
     * 更新统计卡片
     */
    updateStatCards() {
        const onlineMachines = Array.from(this.machines.values()).filter(m => m.status !== 'OFFLINE').length;
        const runningMachines = Array.from(this.machines.values()).filter(m => m.status === 'RUNNING').length;
        const activeAlarms = this.alarms.filter(a => !a.is_acknowledged).length;
        const avgEfficiency = this.calculateAverageEfficiency();
        
        this.updateElement('online-machines', onlineMachines);
        this.updateElement('running-machines', runningMachines);
        this.updateElement('active-alarms', activeAlarms);
        this.updateElement('avg-efficiency', `${avgEfficiency}%`);
    }
    
    /**
     * 计算平均效率
     */
    calculateAverageEfficiency() {
        const runningMachines = Array.from(this.machines.values()).filter(m => m.status === 'RUNNING');
        if (runningMachines.length === 0) return 0;
        
        const totalEfficiency = runningMachines.reduce((sum, machine) => {
            return sum + (machine.efficiency || 85); // 默认效率85%
        }, 0);
        
        return Math.round(totalEfficiency / runningMachines.length);
    }
    
    /**
     * 更新机床状态列表
     */
    updateMachineStatusList() {
        const container = document.getElementById('machine-status-list');
        if (!container) return;
        
        const html = Array.from(this.machines.values()).map(machine => {
            const data = machine.data || {};
            const statusClass = this.getStatusClass(machine.status);
            
            return `
                <div class="machine-status-item" onclick="app.selectMachine('${machine.machine_id}')">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="machine-id">${machine.machine_id}</div>
                            <div class="machine-type">${machine.type || 'Unknown'}</div>
                        </div>
                        <div class="status-indicator ${statusClass}"></div>
                    </div>
                    <div class="status-row">
                        <span class="metric">
                            <span class="metric-label">温度:</span>
                            <span class="metric-value">${(data.temperature || 0).toFixed(1)}°C</span>
                        </span>
                        <span class="metric">
                            <span class="metric-label">振动:</span>
                            <span class="metric-value">${(data.vibration || 0).toFixed(2)}mm/s</span>
                        </span>
                        <span class="metric">
                            <span class="metric-label">转速:</span>
                            <span class="metric-value">${(data.speed || 0).toFixed(0)}rpm</span>
                        </span>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html || '<div class="empty-state"><p>暂无机床数据</p></div>';
    }
    
    /**
     * 更新最新报警
     */
    updateRecentAlarms() {
        const container = document.getElementById('recent-alarms');
        if (!container) return;
        
        const recentAlarms = this.alarms.slice(0, 5);
        const html = recentAlarms.map(alarm => {
            const levelClass = alarm.level.toLowerCase();
            const timeStr = new Date(alarm.timestamp).toLocaleString();
            
            return `
                <div class="alarm-item level-${levelClass}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="alarm-machine">${alarm.machine_id}</div>
                        <div class="alarm-level ${levelClass}">${alarm.level}</div>
                    </div>
                    <div class="alarm-message">${alarm.message}</div>
                    <div class="alarm-time">${timeStr}</div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html || '<div class="empty-state"><p>暂无报警信息</p></div>';
    }
    
    /**
     * 更新系统状态
     */
    updateSystemStatus() {
        const statusMap = {
            mqtt: 'mqtt-status',
            database: 'db-status',
            rule_engine: 'rule-engine-status',
            digital_twin: 'digital-twin-status'
        };
        
        Object.entries(statusMap).forEach(([key, elementId]) => {
            const element = document.getElementById(elementId);
            if (element) {
                const status = this.systemStatus[key];
                element.textContent = status ? '正常' : '异常';
                element.className = `badge ${status ? 'bg-success' : 'bg-danger'}`;
            }
        });
    }
    
    /**
     * 获取状态样式类
     */
    getStatusClass(status) {
        const statusMap = {
            'RUNNING': 'status-running',
            'IDLE': 'status-idle',
            'ERROR': 'status-error',
            'OFFLINE': 'status-offline',
            'MAINTENANCE': 'status-maintenance'
        };
        return statusMap[status] || 'status-offline';
    }
    
    /**
     * 显示报警通知
     */
    showAlarmNotification(alarm) {
        // 更新模态框内容
        const alarmDetails = document.getElementById('alarm-details');
        if (alarmDetails) {
            alarmDetails.innerHTML = `
                <div class="alert alert-${this.getAlarmBootstrapClass(alarm.level)}">
                    <h6><strong>${alarm.machine_id}</strong> - ${alarm.level}</h6>
                    <p>${alarm.message}</p>
                    <small>时间: ${new Date(alarm.timestamp).toLocaleString()}</small>
                    <br>
                    <small>参数: ${alarm.parameter} = ${alarm.value} (阈值: ${alarm.threshold})</small>
                </div>
            `;
        }
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('alarmModal'));
        modal.show();
        
        // 存储当前报警ID用于确认
        this.currentAlarmId = alarm.alarm_id;
    }
    
    /**
     * 获取Bootstrap报警样式类
     */
    getAlarmBootstrapClass(level) {
        const classMap = {
            'CRITICAL': 'danger',
            'ERROR': 'warning',
            'WARNING': 'warning',
            'INFO': 'info'
        };
        return classMap[level] || 'secondary';
    }
    
    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    /**
     * 更新元素内容
     */
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
            element.classList.add('data-updated');
            setTimeout(() => {
                element.classList.remove('data-updated');
            }, 500);
        }
    }
    
    /**
     * 设置定时任务
     */
    setupTimers() {
        // 每30秒刷新系统状态
        setInterval(() => {
            this.loadSystemHealth();
        }, 30000);
        
        // 每分钟更新仪表盘
        setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.updateDashboard();
            }
        }, 60000);
    }
    
    /**
     * 刷新方法
     */
    refreshDashboard() {
        this.updateDashboard();
    }
    
    refreshMachines() {
        this.loadMachines();
    }
    
    refreshDigitalTwin() {
        this.updateMachineSelect();
    }
    
    refreshAlarms() {
        this.loadAlarms();
    }
    
    refreshAnalytics() {
        // 刷新分析图表
        if (window.chartManager) {
            window.chartManager.resizeAllCharts();
        }
    }
    
    /**
     * 更新机床选择下拉框
     */
    updateMachineSelect() {
        const select = document.getElementById('twin-machine-select');
        if (!select) return;
        
        const options = Array.from(this.machines.values()).map(machine => {
            return `<option value="${machine.machine_id}">${machine.machine_id} (${machine.type})</option>`;
        }).join('');
        
        select.innerHTML = '<option value="">请选择机床</option>' + options;
    }
    
    /**
     * 选择机床
     */
    selectMachine(machineId) {
        if (window.threeSceneManager) {
            window.threeSceneManager.selectMachine(machineId);
        }
        
        // 切换到数字孪生页面
        this.switchTab('digital-twin');
    }
}

// 全局函数定义
window.refreshMachines = function() {
    if (window.app) {
        window.app.refreshMachines();
    }
};

window.refreshAlarms = function() {
    if (window.app) {
        window.app.refreshAlarms();
    }
};

window.acknowledgeAllAlarms = function() {
    if (window.app) {
        window.app.acknowledgeAllAlarms();
    }
};

window.acknowledgeAlarm = function() {
    if (window.app && window.app.currentAlarmId) {
        window.app.acknowledgeAlarm(window.app.currentAlarmId);
    }
};

window.updateTwinState = function() {
    if (window.app) {
        window.app.updateTwinState();
    }
};

window.simulateFault = function(faultType) {
    if (window.app) {
        window.app.simulateFault(faultType);
    }
};

// 创建全局应用实例
window.app = new IndustrialIoTApp();

// 导出应用类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IndustrialIoTApp;
}
