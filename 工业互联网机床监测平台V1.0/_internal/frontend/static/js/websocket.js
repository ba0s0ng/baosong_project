/**
 * 工业互联网机床状态监测平台 - WebSocket通信模块
 */

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 5000; // 5秒
        this.messageHandlers = new Map();
        this.subscriptions = new Set();
        
        // 绑定事件处理器
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onClose = this.onClose.bind(this);
        this.onError = this.onError.bind(this);
    }
    
    /**
     * 连接WebSocket服务器
     */
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            console.log('正在连接WebSocket服务器:', wsUrl);
            this.updateConnectionStatus('connecting');
            
            this.ws = new WebSocket(wsUrl);
            this.ws.onopen = this.onOpen;
            this.ws.onmessage = this.onMessage;
            this.ws.onclose = this.onClose;
            this.ws.onerror = this.onError;
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.updateConnectionStatus('disconnected');
            this.scheduleReconnect();
        }
    }
    
    /**
     * 断开WebSocket连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.updateConnectionStatus('disconnected');
    }
    
    /**
     * WebSocket连接打开事件
     */
    onOpen(event) {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateConnectionStatus('connected');
        
        // 重新订阅之前的主题
        this.resubscribe();
        
        // 触发连接成功事件
        this.emit('connected', event);
    }
    
    /**
     * WebSocket消息接收事件
     */
    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            console.log('收到WebSocket消息:', message);
            
            // 根据消息类型分发处理
            this.handleMessage(message);
            
        } catch (error) {
            console.error('解析WebSocket消息失败:', error, event.data);
        }
    }
    
    /**
     * WebSocket连接关闭事件
     */
    onClose(event) {
        console.log('WebSocket连接已关闭:', event.code, event.reason);
        this.isConnected = false;
        this.updateConnectionStatus('disconnected');
        
        // 触发断开连接事件
        this.emit('disconnected', event);
        
        // 如果不是主动关闭，尝试重连
        if (event.code !== 1000) {
            this.scheduleReconnect();
        }
    }
    
    /**
     * WebSocket错误事件
     */
    onError(event) {
        console.error('WebSocket连接错误:', event);
        this.emit('error', event);
    }
    
    /**
     * 发送消息
     */
    send(message) {
        if (this.isConnected && this.ws) {
            try {
                const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
                this.ws.send(messageStr);
                console.log('发送WebSocket消息:', message);
                return true;
            } catch (error) {
                console.error('发送WebSocket消息失败:', error);
                return false;
            }
        } else {
            console.warn('WebSocket未连接，无法发送消息:', message);
            return false;
        }
    }
    
    /**
     * 订阅机床数据
     */
    subscribe(machineId) {
        const message = {
            type: 'subscribe',
            machine_id: machineId
        };
        
        if (this.send(message)) {
            this.subscriptions.add(machineId);
            console.log('订阅机床数据:', machineId);
            return true;
        }
        return false;
    }
    
    /**
     * 取消订阅机床数据
     */
    unsubscribe(machineId) {
        const message = {
            type: 'unsubscribe',
            machine_id: machineId
        };
        
        if (this.send(message)) {
            this.subscriptions.delete(machineId);
            console.log('取消订阅机床数据:', machineId);
            return true;
        }
        return false;
    }
    
    /**
     * 重新订阅所有主题
     */
    resubscribe() {
        for (const machineId of this.subscriptions) {
            this.subscribe(machineId);
        }
    }
    
    /**
     * 处理接收到的消息
     */
    handleMessage(message) {
        const messageType = message.type;
        
        switch (messageType) {
            case 'welcome':
                this.handleWelcomeMessage(message);
                break;
            case 'machine_data':
                this.handleMachineDataMessage(message);
                break;
            case 'alarm':
                this.handleAlarmMessage(message);
                break;
            case 'status_change':
                this.handleStatusChangeMessage(message);
                break;
            case 'control_response':
                this.handleControlResponseMessage(message);
                break;
            case 'system_notification':
                this.handleSystemNotificationMessage(message);
                break;
            case 'maintenance_alert':
                this.handleMaintenanceAlertMessage(message);
                break;
            case 'performance_report':
                this.handlePerformanceReportMessage(message);
                break;
            case 'subscription_confirmed':
                this.handleSubscriptionConfirmedMessage(message);
                break;
            case 'unsubscription_confirmed':
                this.handleUnsubscriptionConfirmedMessage(message);
                break;
            case 'ping':
                this.handlePingMessage(message);
                break;
            case 'error':
                this.handleErrorMessage(message);
                break;
            default:
                console.warn('未知的消息类型:', messageType, message);
        }
        
        // 触发通用消息事件
        this.emit('message', message);
        
        // 触发特定类型的消息事件
        this.emit(messageType, message);
    }
    
    /**
     * 处理欢迎消息
     */
    handleWelcomeMessage(message) {
        console.log('收到欢迎消息:', message.message);
        this.emit('welcome', message);
    }
    
    /**
     * 处理机床数据消息
     */
    handleMachineDataMessage(message) {
        const machineId = message.machine_id;
        const data = message.data;
        
        // 更新实时数据显示
        if (window.app && window.app.updateMachineData) {
            window.app.updateMachineData(machineId, data);
        }
        
        this.emit('machine_data', message);
    }
    
    /**
     * 处理报警消息
     */
    handleAlarmMessage(message) {
        const alarm = message.alarm;
        
        // 显示报警通知
        if (window.app && window.app.showAlarmNotification) {
            window.app.showAlarmNotification(alarm);
        }
        
        // 播放报警声音
        this.playAlarmSound(alarm.level);
        
        this.emit('alarm', message);
    }
    
    /**
     * 处理状态变化消息
     */
    handleStatusChangeMessage(message) {
        const machineId = message.machine_id;
        const oldStatus = message.old_status;
        const newStatus = message.new_status;
        
        console.log(`机床 ${machineId} 状态变化: ${oldStatus} -> ${newStatus}`);
        
        // 更新机床状态显示
        if (window.app && window.app.updateMachineStatus) {
            window.app.updateMachineStatus(machineId, newStatus);
        }
        
        this.emit('status_change', message);
    }
    
    /**
     * 处理控制响应消息
     */
    handleControlResponseMessage(message) {
        const machineId = message.machine_id;
        const commandId = message.command_id;
        const response = message.response;
        
        console.log(`机床 ${machineId} 控制响应:`, response);
        
        this.emit('control_response', message);
    }
    
    /**
     * 处理系统通知消息
     */
    handleSystemNotificationMessage(message) {
        const notification = message.notification;
        
        // 显示系统通知
        if (window.app && window.app.showSystemNotification) {
            window.app.showSystemNotification(notification);
        }
        
        this.emit('system_notification', message);
    }
    
    /**
     * 处理维护提醒消息
     */
    handleMaintenanceAlertMessage(message) {
        const machineId = message.machine_id;
        const maintenanceInfo = message.maintenance_info;
        
        console.log(`机床 ${machineId} 维护提醒:`, maintenanceInfo);
        
        this.emit('maintenance_alert', message);
    }
    
    /**
     * 处理性能报告消息
     */
    handlePerformanceReportMessage(message) {
        const machineId = message.machine_id;
        const report = message.report;
        
        console.log(`机床 ${machineId} 性能报告:`, report);
        
        this.emit('performance_report', message);
    }
    
    /**
     * 处理订阅确认消息
     */
    handleSubscriptionConfirmedMessage(message) {
        const machineId = message.machine_id;
        console.log(`订阅确认: ${machineId}`);
        
        this.emit('subscription_confirmed', message);
    }
    
    /**
     * 处理取消订阅确认消息
     */
    handleUnsubscriptionConfirmedMessage(message) {
        const machineId = message.machine_id;
        console.log(`取消订阅确认: ${machineId}`);
        
        this.emit('unsubscription_confirmed', message);
    }
    
    /**
     * 处理心跳消息
     */
    handlePingMessage(message) {
        // 回复心跳
        this.send({
            type: 'pong',
            timestamp: new Date().toISOString()
        });
    }
    
    /**
     * 处理错误消息
     */
    handleErrorMessage(message) {
        console.error('服务器错误:', message.message);
        
        // 显示错误通知
        if (window.app && window.app.showErrorNotification) {
            window.app.showErrorNotification(message.message);
        }
        
        this.emit('server_error', message);
    }
    
    /**
     * 播放报警声音
     */
    playAlarmSound(level) {
        try {
            // 根据报警级别播放不同的声音
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // 根据报警级别设置频率
            let frequency = 440; // 默认频率
            switch (level.toLowerCase()) {
                case 'critical':
                    frequency = 880; // 高频
                    break;
                case 'error':
                    frequency = 660;
                    break;
                case 'warning':
                    frequency = 440;
                    break;
                case 'info':
                    frequency = 330; // 低频
                    break;
            }
            
            oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
            
        } catch (error) {
            console.warn('播放报警声音失败:', error);
        }
    }
    
    /**
     * 安排重连
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`${this.reconnectInterval / 1000}秒后尝试第${this.reconnectAttempts}次重连...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
            
            // 增加重连间隔
            this.reconnectInterval = Math.min(this.reconnectInterval * 1.5, 30000);
        } else {
            console.error('达到最大重连次数，停止重连');
            this.emit('max_reconnect_attempts_reached');
        }
    }
    
    /**
     * 更新连接状态显示
     */
    updateConnectionStatus(status) {
        const statusIcon = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');
        
        if (statusIcon && statusText) {
            statusIcon.className = 'fas fa-wifi';
            
            switch (status) {
                case 'connected':
                    statusIcon.classList.add('connected');
                    statusText.textContent = '已连接';
                    break;
                case 'connecting':
                    statusIcon.classList.add('connecting');
                    statusText.textContent = '连接中...';
                    break;
                case 'disconnected':
                    statusIcon.classList.add('disconnected');
                    statusText.textContent = '已断开';
                    break;
            }
        }
    }
    
    /**
     * 注册消息处理器
     */
    on(eventType, handler) {
        if (!this.messageHandlers.has(eventType)) {
            this.messageHandlers.set(eventType, []);
        }
        this.messageHandlers.get(eventType).push(handler);
    }
    
    /**
     * 移除消息处理器
     */
    off(eventType, handler) {
        if (this.messageHandlers.has(eventType)) {
            const handlers = this.messageHandlers.get(eventType);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    /**
     * 触发事件
     */
    emit(eventType, data) {
        if (this.messageHandlers.has(eventType)) {
            const handlers = this.messageHandlers.get(eventType);
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`事件处理器执行失败 (${eventType}):`, error);
                }
            });
        }
    }
    
    /**
     * 获取连接状态
     */
    getConnectionState() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            subscriptions: Array.from(this.subscriptions)
        };
    }
}

// 创建全局WebSocket管理器实例
window.wsManager = new WebSocketManager();

// 页面加载完成后自动连接
document.addEventListener('DOMContentLoaded', () => {
    window.wsManager.connect();
});

// 页面卸载前断开连接
window.addEventListener('beforeunload', () => {
    window.wsManager.disconnect();
});
