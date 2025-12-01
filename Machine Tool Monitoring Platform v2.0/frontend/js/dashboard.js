// 仪表盘模块
let parameterTrendChart = null;

/**
 * 初始化仪表盘页面
 */
function initDashboard() {
    // 初始化仪表板概览数据
    updateDashboardOverview();
    
    // 加载设备状态分布图表
    loadMachineStatusChart();
    
    // 加载参数趋势图表
    loadParameterTrendChart();
    
    // 加载最近报警信息
    loadRecentAlarms();
    
    // 设置定时刷新
    setInterval(refreshDashboardData, 30000); // 每30秒刷新一次
}

/**
 * 更新仪表盘概览数据
 */
function updateDashboardOverview(data) {
    try {
        if (!data) {
            // 使用模拟数据
            data = {
                total_machines: 32,
                online_machines: 27,
                offline_machines: 4,
                active_alarms: 12,
                high_priority_alarms: 3,
                total_alarms: 68
            };
        }
        
        // 更新概览数据卡片
        document.getElementById('total-machines').textContent = data.total_machines;
        document.getElementById('online-machines').textContent = data.online_machines;
        document.getElementById('offline-machines').textContent = data.offline_machines;
        document.getElementById('active-alarms').textContent = data.active_alarms;
        document.getElementById('high-priority-alarms').textContent = data.high_priority_alarms;
        document.getElementById('total-alarms').textContent = data.total_alarms;
    } catch (error) {
        console.error('更新仪表盘概览失败:', error);
    }
}

/**
 * 加载设备状态分布图表
 */
function loadMachineStatusChart() {
    try {
        const chartDom = document.getElementById('machine-status-chart');
        let statusChart = echarts.init(chartDom);
        
        // 模拟设备数据
        const machines = [];
        
        // 添加27台在线设备
        for (let i = 1; i <= 27; i++) {
            machines.push({ 
                id: i, 
                name: `设备${i}`, 
                status: 'online', 
                type: ['cnc_milling', 'lathe', 'milling', 'robot'][i % 4] 
            });
        }
        
        // 添加4台离线设备
        for (let i = 28; i <= 31; i++) {
            machines.push({ 
                id: i, 
                name: `设备${i}`, 
                status: 'offline', 
                type: ['cnc_milling', 'lathe', 'milling', 'robot'][i % 4] 
            });
        }
        
        // 添加1台警告状态设备
        machines.push({ 
            id: 32, 
            name: '设备32', 
            status: 'warning', 
            type: 'cnc_milling' 
        });
        
        // 统计各状态设备数量
        const statusCounts = {
            online: 0,
            offline: 0,
            warning: 0
        };
        
        machines.forEach(machine => {
            if (statusCounts.hasOwnProperty(machine.status)) {
                statusCounts[machine.status]++;
            }
        });
        
        // 配置图表选项
        const option = {
            title: {
                text: '设备状态分布',
                left: 'center'
            },
            tooltip: {
                trigger: 'item'
            },
            legend: {
                orient: 'vertical',
                left: 'left',
            },
            series: [
                {
                    name: '设备状态',
                    type: 'pie',
                    radius: '50%',
                    data: [
                        { value: statusCounts.online, name: '在线' },
                        { value: statusCounts.offline, name: '离线' },
                        { value: statusCounts.warning, name: '警告' }
                    ],
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };
        
        option && statusChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            statusChart.resize();
        });
    } catch (error) {
        console.error('加载设备状态图表失败:', error);
    }
}

/**
 * 加载参数趋势图表
 */
function loadParameterTrendChart() {
    try {
        // 直接使用模拟数据生成图表
        loadParameterTrendChartWithMockData();
    } catch (error) {
        console.error('加载参数趋势图表失败:', error);
    }
}

/**
 * 加载模拟的参数趋势图表
 */
function loadParameterTrendChartWithMockData() {
    try {
        const chartDom = document.getElementById('parameter-trend-chart');
        if (parameterTrendChart) {
            parameterTrendChart.dispose();
        }
        
        parameterTrendChart = echarts.init(chartDom);
        
        // 生成模拟的时间数据（过去24小时）
        const hours = 24;
        const times = [];
        const now = new Date();
        
        for (let i = hours; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            times.push(time.getHours() + ':00');
        }
        
        // 生成模拟的参数数据 - 使用更真实的趋势变化
        function generateMockDataWithTrend(base, min, max, trendFactor = 0.1) {
            const data = [];
            let currentValue = base;
            
            for (let i = 0; i <= hours; i++) {
                // 添加一些周期性变化和随机波动
                const periodicVariation = Math.sin(i * 0.5) * (max - min) * 0.1;
                const randomVariation = (Math.random() - 0.5) * (max - min) * 0.2;
                
                // 添加一个总体趋势
                let trend = 0;
                if (i > hours * 0.3 && i < hours * 0.7) {
                    trend = trendFactor; // 中期上升趋势
                } else if (i > hours * 0.8) {
                    trend = -trendFactor; // 后期下降趋势
                }
                
                currentValue += randomVariation + periodicVariation + trend;
                
                // 确保值在合理范围内
                currentValue = Math.max(min, Math.min(max, currentValue));
                data.push(Math.round(currentValue * 10) / 10);
            }
            
            return data;
        }
        
        // 为不同参数生成有意义的数据范围
        const temperatureData = generateMockDataWithTrend(75, 65, 95, 0.2); // 温度范围65-95°C
        const vibrationData = generateMockDataWithTrend(2.0, 0.5, 5.0, 0.05); // 振动范围0.5-5.0 mm/s
        const currentData = generateMockDataWithTrend(15, 8, 30, 0.3); // 电流范围8-30 A
        
        const option = {
            title: {
                text: '设备参数趋势',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['温度', '振动', '电流'],
                bottom: 0
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            toolbox: {
                feature: {
                    saveAsImage: {}
                }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: times
            },
            yAxis: [
                {
                    type: 'value',
                    name: '温度 (°C)',
                    position: 'left',
                    axisLabel: {
                        formatter: '{value}'
                    }
                },
                {
                    type: 'value',
                    name: '振动 (mm/s)',
                    position: 'right',
                    axisLabel: {
                        formatter: '{value}'
                    }
                },
                {
                    type: 'value',
                    name: '电流 (A)',
                    position: 'right',
                    offset: 80,
                    axisLabel: {
                        formatter: '{value}'
                    }
                }
            ],
            series: [
                {
                    name: '温度',
                    type: 'line',
                    yAxisIndex: 0,
                    data: temperatureData,
                    itemStyle: {
                        color: '#ff4500'
                    },
                    smooth: true,
                    lineStyle: {
                        width: 2
                    }
                },
                {
                    name: '振动',
                    type: 'line',
                    yAxisIndex: 1,
                    data: vibrationData,
                    itemStyle: {
                        color: '#4169e1'
                    },
                    smooth: true,
                    lineStyle: {
                        width: 2
                    }
                },
                {
                    name: '电流',
                    type: 'line',
                    yAxisIndex: 2,
                    data: currentData,
                    itemStyle: {
                        color: '#228b22'
                    },
                    smooth: true,
                    lineStyle: {
                        width: 2
                    }
                }
            ]
        };
        
        parameterTrendChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            if (parameterTrendChart) {
                parameterTrendChart.resize();
            }
        });
    } catch (error) {
        console.error('加载模拟参数趋势图表失败:', error);
    }
}

/**
 * 加载最近报警列表
 */
async function loadRecentAlarms() {
    try {
        // 使用模拟数据
        loadRecentAlarmsWithMockData();
    } catch (error) {
        console.error('加载最近报警失败:', error);
        document.getElementById('recent-alarms-table').innerHTML = 
            '<tr><td colspan="6" class="text-center text-danger">加载报警信息失败</td></tr>';
    }
}

/**
 * 刷新仪表盘数据
 */
async function refreshDashboardData() {
    try {
        // 刷新概览数据
        try {
            updateDashboardOverview(); // 使用默认模拟数据
        } catch (error) {
            console.warn('获取概览数据失败，使用模拟数据:', error);
            updateDashboardOverview(); // 使用默认模拟数据
        }
        
        // 刷新最近报警
        try {
            loadRecentAlarmsWithMockData();
        } catch (error) {
            console.warn('获取最近报警失败，使用模拟数据:', error);
            loadRecentAlarmsWithMockData();
        }
        
        // 刷新参数趋势图表
        try {
            loadParameterTrendChartWithMockData();
        } catch (error) {
            console.warn('获取参数趋势数据失败，使用模拟数据:', error);
            loadParameterTrendChartWithMockData();
        }
    } catch (error) {
        console.error('刷新仪表盘数据失败:', error);
    }
}

/**
 * 显示错误消息
 */
function showErrorMessage(message) {
    // 创建错误提示元素
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger alert-dismissible fade show mt-3';
    errorElement.role = 'alert';
    errorElement.innerHTML = `
        <strong>错误:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到仪表盘区域
    const dashboardSection = document.getElementById('dashboard');
    const cardHeader = dashboardSection.querySelector('.card-header');
    cardHeader.after(errorElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        errorElement.remove();
    }, 3000);
}

/**
 * 获取参数名称
 */
function getParameterName(type) {
    const paramNames = {
        temperature: '温度',
        vibration: '振动',
        current: '电流',
        pressure: '压力',
        rotation_speed: '转速',
        power: '功率',
        humidity: '湿度',
        voltage: '电压'
    };
    return paramNames[type] || type;
}

/**
 * 加载模拟的最近报警数据
 */
function loadRecentAlarmsWithMockData() {
    try {
        const tableBody = document.getElementById('recent-alarms-table');
        
        // 模拟报警数据，确保有12条活跃报警（其中3条高优先级）
        const alarms = [
            // 高优先级报警
            {
                id: 1,
                machine_id: 1,
                machine_name: '设备1',
                type: 'temperature',
                value: 92.5,
                threshold: 85,
                level: 'high',
                description: '温度严重过高',
                timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
                handled: false
            },
            {
                id: 2,
                machine_id: 15,
                machine_name: '设备15',
                type: 'current',
                value: 28.5,
                threshold: 20,
                level: 'high',
                description: '电流异常高，可能存在短路风险',
                timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
                handled: false
            },
            {
                id: 3,
                machine_id: 25,
                machine_name: '设备25',
                type: 'vibration',
                value: 5.8,
                threshold: 4.0,
                level: 'high',
                description: '振动严重超标，需要立即停机检查',
                timestamp: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
                handled: false
            },
            // 中优先级报警
            {
                id: 4,
                machine_id: 4,
                machine_name: '设备4',
                type: 'vibration',
                value: 3.2,
                threshold: 3.0,
                level: 'medium',
                description: '振动接近阈值',
                timestamp: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
                handled: false
            },
            {
                id: 5,
                machine_id: 7,
                machine_name: '设备7',
                type: 'temperature',
                value: 82.0,
                threshold: 80,
                level: 'medium',
                description: '温度略高于阈值',
                timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
                handled: false
            },
            {
                id: 6,
                machine_id: 12,
                machine_name: '设备12',
                type: 'pressure',
                value: 12.8,
                threshold: 12.0,
                level: 'medium',
                description: '压力略高于阈值',
                timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
                handled: false
            },
            {
                id: 7,
                machine_id: 18,
                machine_name: '设备18',
                type: 'rotation_speed',
                value: 4800,
                threshold: 4500,
                level: 'medium',
                description: '转速略高于阈值',
                timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
                handled: false
            },
            // 低优先级报警
            {
                id: 8,
                machine_id: 3,
                machine_name: '设备3',
                type: 'rotation_speed',
                value: 1800,
                threshold: 2000,
                level: 'low',
                description: '转速低于预期',
                timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
                handled: false
            },
            {
                id: 9,
                machine_id: 6,
                machine_name: '设备6',
                type: 'power',
                value: 8.2,
                threshold: 10.0,
                level: 'low',
                description: '功率低于预期',
                timestamp: new Date(Date.now() - 1000 * 60 * 150).toISOString(),
                handled: false
            },
            {
                id: 10,
                machine_id: 20,
                machine_name: '设备20',
                type: 'temperature',
                value: 68.5,
                threshold: 60.0,
                level: 'low',
                description: '温度略高于正常值',
                timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
                handled: false
            },
            {
                id: 11,
                machine_id: 28,
                machine_name: '设备28',
                type: 'humidity',
                value: 72,
                threshold: 70,
                level: 'low',
                description: '环境湿度略高',
                timestamp: new Date(Date.now() - 1000 * 60 * 200).toISOString(),
                handled: false
            },
            {
                id: 12,
                machine_id: 31,
                machine_name: '设备31',
                type: 'voltage',
                value: 238,
                threshold: 240,
                level: 'low',
                description: '电压略低于正常值',
                timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
                handled: false
            }
        ];
        
        let html = '';
        alarms.forEach(alarm => {
            const date = new Date(alarm.timestamp);
            const formattedTime = date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            
            const levelClass = {
                high: 'alarm-level-high',
                medium: 'alarm-level-medium',
                low: 'alarm-level-low'
            }[alarm.level] || '';
            
            const levelText = {
                high: '高',
                medium: '中',
                low: '低'
            }[alarm.level] || '未知';
            
            const statusText = alarm.handled ? 
                '<span class="badge bg-success">已处理</span>' : 
                '<span class="badge bg-danger">未处理</span>';
            
            html += `
                <tr>
                    <td>${formattedTime}</td>
                    <td>${alarm.machine_name}</td>
                    <td>${getParameterName(alarm.type)}</td>
                    <td class="${levelClass}">${levelText}</td>
                    <td>${alarm.description}</td>
                    <td>${statusText}</td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    } catch (error) {
        console.error('加载模拟报警数据失败:', error);
    }
}

// 模块初始化完成