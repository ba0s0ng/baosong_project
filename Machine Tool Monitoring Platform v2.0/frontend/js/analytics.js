/**
 * 工业互联网机床监测平台 - 数据分析模块
 * 负责机床运行数据的统计分析、图表生成和趋势预测
 */

// 移除import语句，直接使用window上的API对象
// import { analyticsAPI, machinesAPI } from './api.js';
let trendChart = null;
let correlationChart = null;
let efficiencyChart = null;
let predictionChart = null;
let statsChart = null;

/**
 * 初始化数据分析模块
 */
async function initAnalytics() {
    try {
        // 加载设备列表
        await loadMachinesForSelect();
        
        // 设置默认时间范围
        setDefaultDateRange();
        
        // 绑定事件监听器
        bindEventListeners();
        
        // 加载初始图表
        loadInitialCharts();
    } catch (error) {
        console.error('初始化数据分析模块失败:', error);
        showErrorMessage('数据分析模块初始化失败');
    }
}

/**
 * 加载设备列表到选择器
 */
async function loadMachinesForSelect() {
    try {
        let machines;
        try {
            // 尝试从API获取数据
            machines = await machinesAPI.getAllMachines();
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            // 提供模拟设备数据
            machines = [
                {
                    id: 1,
                    name: '加工中心1',
                    type: '加工中心'
                },
                {
                    id: 2,
                    name: '车床1',
                    type: '车床'
                },
                {
                    id: 3,
                    name: '铣床1',
                    type: '铣床'
                },
                {
                    id: 4,
                    name: '车床2',
                    type: '车床'
                },
                {
                    id: 5,
                    name: '机器人1',
                    type: '工业机器人'
                },
                {
                    id: 6,
                    name: '铣床2',
                    type: '铣床'
                },
                {
                    id: 7,
                    name: '加工中心2',
                    type: '加工中心'
                },
                {
                    id: 8,
                    name: '机器人2',
                    type: '工业机器人'
                },
                {
                    id: 9,
                    name: '检测设备1',
                    type: '三坐标测量机'
                },
                {
                    id: 10,
                    name: '激光切割机',
                    type: '激光切割'
                }
            ];
        }
        
        const selectElement = document.getElementById('analytics-machine-select');
        
        // 清空现有选项
        selectElement.innerHTML = '<option value="">请选择设备</option>';
        
        // 添加设备选项
        machines.forEach(machine => {
            const option = document.createElement('option');
            option.value = machine.id;
            option.textContent = machine.name;
            selectElement.appendChild(option);
        });
    } catch (error) {
        console.error('加载设备列表失败:', error);
    }
}

/**
 * 设置默认时间范围
 */
function setDefaultDateRange() {
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    // 格式化日期
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };
    
    document.getElementById('analytics-start-date').value = formatDate(lastWeek);
    document.getElementById('analytics-end-date').value = formatDate(today);
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 刷新图表按钮
    document.getElementById('refresh-charts-btn').addEventListener('click', loadAllCharts);
    
    // 导出报表按钮
    document.getElementById('export-report-btn').addEventListener('click', exportReport);
    
    // 切换图表类型
    document.getElementById('trend-chart-type').addEventListener('change', updateTrendChart);
    document.getElementById('correlation-parameter-1').addEventListener('change', updateCorrelationChart);
    document.getElementById('correlation-parameter-2').addEventListener('change', updateCorrelationChart);
}

/**
 * 加载初始图表
 */
async function loadInitialCharts() {
    try {
        // 加载设备效率分析图表
        await updateEfficiencyChart();
        
        // 加载设备状态统计图表
        await updateStatsChart();
    } catch (error) {
        console.error('加载初始图表失败:', error);
    }
}

/**
 * 加载所有图表
 */
async function loadAllCharts() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value;
        if (!machineId) {
            showErrorMessage('请先选择设备');
            return;
        }
        
        // 显示加载状态
        showLoadingState(true);
        
        // 更新所有图表
        await Promise.all([
            updateTrendChart(),
            updateCorrelationChart(),
            updateEfficiencyChart(),
            updatePredictionChart(),
            updateStatsChart()
        ]);
        
        // 更新设备健康评分
        await updateHealthScore();
        
        // 更新预测性维护建议
        await updateMaintenanceSuggestions();
        
        showLoadingState(false);
    } catch (error) {
        console.error('加载图表失败:', error);
        showErrorMessage('加载图表失败');
        showLoadingState(false);
    }
}

/**
 * 显示加载状态
 */
function showLoadingState(isLoading) {
    const loadingElement = document.getElementById('charts-loading');
    const chartsContainer = document.getElementById('charts-container');
    
    if (isLoading) {
        loadingElement.style.display = 'block';
        chartsContainer.style.opacity = '0.5';
    } else {
        loadingElement.style.display = 'none';
        chartsContainer.style.opacity = '1';
    }
}

/**
 * 更新趋势分析图表
 */
async function updateTrendChart() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value || '1'; // 默认选择第一个设备
        const chartType = document.getElementById('trend-chart-type').value;
        const startDate = document.getElementById('analytics-start-date').value;
        const endDate = document.getElementById('analytics-end-date').value;
        
        if (!machineId) return;
        
        // 获取趋势数据
        let data;
        try {
            // 尝试从API获取数据
            data = await analyticsAPI.getTrendData(machineId, chartType, startDate, endDate);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            const dates = [];
            const values = [];
            const now = new Date();
            const days = startDate && endDate ? 
                Math.floor((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)) : 7;
            
            // 生成日期和对应的值
            for (let i = days; i >= 0; i--) {
                const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
                dates.push(date.toLocaleDateString('zh-CN'));
                
                // 根据不同的图表类型生成不同范围的随机值
                let base, range;
                switch (chartType) {
                    case 'temperature':
                        base = 70;
                        range = 30;
                        break;
                    case 'vibration':
                        base = 0.4;
                        range = 0.6;
                        break;
                    case 'current':
                        base = 12;
                        range = 8;
                        break;
                    case 'rotation_speed':
                        base = 3000;
                        range = 500;
                        break;
                    case 'pressure':
                        base = 10;
                        range = 6;
                        break;
                    default:
                        base = 50;
                        range = 40;
                }
                values.push(Math.round((base + (Math.random() - 0.5) * range) * 10) / 10);
            }
            
            data = {
                dates: dates,
                values: values
            };
        }
        
        // 销毁旧图表
        if (trendChart) {
            trendChart.dispose();
        }
        
        // 创建新图表
        const chartDom = document.getElementById('trend-chart');
        trendChart = echarts.init(chartDom);
        
        // 设置图表选项
        const option = getTrendChartOption(data, chartType);
        trendChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            if (trendChart) {
                trendChart.resize();
            }
        });
    } catch (error) {
        console.error('更新趋势图表失败:', error);
    }
}

/**
 * 获取趋势图表选项
 */
function getTrendChartOption(data, parameter) {
    // 参数配置
    const paramConfig = {
        temperature: { name: '温度', unit: '°C', color: '#ff7875', yAxisName: '温度 (°C)' },
        vibration: { name: '振动', unit: 'mm/s', color: '#ffa940', yAxisName: '振动 (mm/s)' },
        current: { name: '电流', unit: 'A', color: '#36cfc9', yAxisName: '电流 (A)' },
        rotation_speed: { name: '转速', unit: 'RPM', color: '#40a9ff', yAxisName: '转速 (RPM)' },
        pressure: { name: '压力', unit: 'MPa', color: '#73d13d', yAxisName: '压力 (MPa)' },
        power: { name: '功率', unit: 'kW', color: '#9254de', yAxisName: '功率 (kW)' }
    };
    
    const config = paramConfig[parameter] || { name: '参数', unit: '', color: '#1890ff', yAxisName: '参数值' };
    
    // 格式化数据
    const timestamps = data.map(item => new Date(item.timestamp).toLocaleString('zh-CN'));
    const values = data.map(item => item.value);
    
    return {
        title: {
            text: `${config.name}趋势分析`,
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                const param = params[0];
                return `${param.name}<br/>时间: ${param.axisValue}<br/>值: ${param.value} ${config.unit}`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timestamps,
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: config.yAxisName
        },
        series: [{
            name: config.name,
            type: 'line',
            data: values,
            smooth: true,
            lineStyle: {
                color: config.color,
                width: 2
            },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                    offset: 0,
                    color: config.color + '80'
                }, {
                    offset: 1,
                    color: config.color + '10'
                }])
            },
            markPoint: {
                data: [
                    { type: 'max', name: '最大值' },
                    { type: 'min', name: '最小值' }
                ]
            },
            markLine: {
                data: [
                    { type: 'average', name: '平均值' }
                ]
            }
        }]
    };
}

/**
 * 更新关联性分析图表
 */
async function updateCorrelationChart() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value || '1'; // 默认选择第一个设备
        const param1 = document.getElementById('correlation-parameter-1')?.value || 'temperature';
        const param2 = document.getElementById('correlation-parameter-2')?.value || 'vibration';
        const startDate = document.getElementById('analytics-start-date').value;
        const endDate = document.getElementById('analytics-end-date').value;
        
        // 获取关联性数据
        let data;
        try {
            // 尝试从API获取数据
            data = await analyticsAPI.getCorrelationData(machineId, param1, param2, startDate, endDate);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            data = generateCorrelationMockData(param1, param2, 50);
        }
        
        // 销毁旧图表
        if (correlationChart) {
            correlationChart.dispose();
        }
        
        // 创建新图表
        const chartDom = document.getElementById('correlation-chart');
        correlationChart = echarts.init(chartDom);
        
        // 设置图表选项
        const option = getCorrelationChartOption(data, param1, param2);
        correlationChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            if (correlationChart) {
                correlationChart.resize();
            }
        });
    } catch (error) {
        console.error('更新关联性图表失败:', error);
    }
}

/**
 * 生成关联性分析的模拟数据
 */
function generateCorrelationMockData(param1, param2, count) {
    const data = [];
    
    // 参数配置
    const paramConfig = {
        temperature: { base: 70, range: 30 },
        vibration: { base: 0.5, range: 0.5 },
        current: { base: 15, range: 10 },
        rotation_speed: { base: 3000, range: 1000 },
        pressure: { base: 12, range: 8 },
        power: { base: 20, range: 15 }
    };
    
    const config1 = paramConfig[param1] || { base: 50, range: 40 };
    const config2 = paramConfig[param2] || { base: 50, range: 40 };
    
    // 生成一定相关性的数据
    for (let i = 0; i < count; i++) {
        const value1 = Math.round((config1.base + (Math.random() - 0.5) * config1.range) * 10) / 10;
        // 添加一些相关性，使数据看起来更真实
        const correlationFactor = 0.6; // 相关性因子
        const value2 = Math.round((config2.base + 
            correlationFactor * (value1 - config1.base) * (config2.range / config1.range) + 
            (1 - correlationFactor) * (Math.random() - 0.5) * config2.range) * 10) / 10;
        
        data.push({ value1, value2 });
    }
    
    return data;
}

/**
 * 获取关联性图表选项
 */
function getCorrelationChartOption(data, param1, param2) {
    // 参数配置
    const paramConfig = {
        temperature: { name: '温度', unit: '°C', color: '#ff7875' },
        vibration: { name: '振动', unit: 'mm/s', color: '#ffa940' },
        current: { name: '电流', unit: 'A', color: '#36cfc9' },
        rotation_speed: { name: '转速', unit: 'RPM', color: '#40a9ff' },
        pressure: { name: '压力', unit: 'MPa', color: '#73d13d' },
        power: { name: '功率', unit: 'kW', color: '#9254de' }
    };
    
    const config1 = paramConfig[param1] || { name: '参数1', unit: '', color: '#1890ff' };
    const config2 = paramConfig[param2] || { name: '参数2', unit: '', color: '#52c41a' };
    
    // 格式化数据
    const seriesData = data.map(item => [item.value1, item.value2]);
    
    return {
        title: {
            text: `${config1.name}与${config2.name}关联性分析`,
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `${config1.name}: ${params.value[0]} ${config1.unit}<br/>${config2.name}: ${params.value[1]} ${config2.unit}`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            name: `${config1.name} (${config1.unit})`,
            scale: true
        },
        yAxis: {
            type: 'value',
            name: `${config2.name} (${config2.unit})`,
            scale: true
        },
        series: [{
            name: '关联性',
            type: 'scatter',
            data: seriesData,
            symbolSize: 8,
            itemStyle: {
                color: '#1890ff',
                opacity: 0.6
            },
            emphasis: {
                itemStyle: {
                    color: '#f5222d',
                    opacity: 1
                }
            }
        }]
    };
}

/**
 * 更新效率分析图表
 */
async function updateEfficiencyChart() {
    try {
        // 获取设备ID（如果未选择则使用默认值）
        const machineId = document.getElementById('analytics-machine-select').value || '1';
        const startDate = document.getElementById('analytics-start-date').value;
        const endDate = document.getElementById('analytics-end-date').value;
        
        // 获取效率数据
        let data;
        try {
            // 尝试从API获取数据
            data = await analyticsAPI.getEfficiencyData(machineId, startDate, endDate);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            const dates = [];
            const availability = [];
            const performance = [];
            const quality = [];
            const oee = [];
            
            const now = new Date();
            const days = startDate && endDate ? 
                Math.floor((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)) : 7;
            
            // 生成日期和对应的值
            for (let i = days; i >= 0; i--) {
                const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
                dates.push(date.toLocaleDateString('zh-CN'));
                
                // 生成合理范围内的效率数据
                const avail = Math.round((85 + Math.random() * 15) * 10) / 10; // 85-100%
                const perf = Math.round((75 + Math.random() * 20) * 10) / 10;   // 75-95%
                const qual = Math.round((90 + Math.random() * 10) * 10) / 10;   // 90-100%
                const oeeVal = Math.round((avail * perf * qual / 10000) * 10) / 10;
                
                availability.push(avail);
                performance.push(perf);
                quality.push(qual);
                oee.push(oeeVal);
            }
            
            data = {
                dates: dates,
                availability: availability,
                performance: performance,
                quality: quality,
                oee: oee
            };
        }
        
        // 销毁旧图表
        if (efficiencyChart) {
            efficiencyChart.dispose();
        }
        
        // 创建新图表
        const chartDom = document.getElementById('efficiency-chart');
        efficiencyChart = echarts.init(chartDom);
        
        // 设置图表选项
        const option = {
            title: {
                text: '设备效率分析 (OEE)',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['可用性', '性能率', '质量率', 'OEE'],
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
                data: data.dates
            },
            yAxis: {
                type: 'value',
                max: 100,
                axisLabel: {
                    formatter: '{value}%'
                }
            },
            series: [
                {
                    name: '可用性',
                    type: 'line',
                    data: data.availability,
                    smooth: true
                },
                {
                    name: '性能率',
                    type: 'line',
                    data: data.performance,
                    smooth: true
                },
                {
                    name: '质量率',
                    type: 'line',
                    data: data.quality,
                    smooth: true
                },
                {
                    name: 'OEE',
                    type: 'line',
                    data: data.oee,
                    smooth: true,
                    lineStyle: {
                        width: 3
                    }
                }
            ]
        };
        
        efficiencyChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            if (efficiencyChart) {
                efficiencyChart.resize();
            }
        });
    } catch (error) {
        console.error('更新效率图表失败:', error);
    }
}

/**
 * 获取效率图表选项
 */
function getEfficiencyChartOption(data) {
    // 格式化数据
    const categories = data.map(item => item.category || item.date);
    const runtimes = data.map(item => item.runtime || item.value);
    const efficiencies = data.map(item => item.efficiency || 0);
    
    return {
        title: {
            text: '设备运行效率分析',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['运行时间(小时)', '运行效率(%)'],
            top: 30
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: 80,
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: categories
        },
        yAxis: [
            {
                type: 'value',
                name: '运行时间(小时)',
                position: 'left'
            },
            {
                type: 'value',
                name: '运行效率(%)',
                position: 'right',
                max: 100
            }
        ],
        series: [
            {
                name: '运行时间(小时)',
                type: 'bar',
                data: runtimes,
                itemStyle: {
                    color: '#52c41a'
                }
            },
            {
                name: '运行效率(%)',
                type: 'line',
                yAxisIndex: 1,
                data: efficiencies,
                smooth: true,
                lineStyle: {
                    color: '#1890ff',
                    width: 3
                },
                itemStyle: {
                    color: '#1890ff'
                }
            }
        ]
    };
}

/**
 * 更新预测分析图表
 */
async function updatePredictionChart() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value || '1';
        const startDate = document.getElementById('analytics-start-date').value;
        const endDate = document.getElementById('analytics-end-date').value;
        
        // 获取预测数据
        let data;
        try {
            // 尝试从API获取数据
            data = await analyticsAPI.getPredictionData(machineId, startDate, endDate);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            data = generatePredictionMockData();
        }
        
        // 销毁旧图表
        if (predictionChart) {
            predictionChart.dispose();
        }
        
        // 创建新图表
        const chartDom = document.getElementById('prediction-chart');
        predictionChart = echarts.init(chartDom);
        
        // 设置图表选项
        const option = getPredictionChartOption(data);
        predictionChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            if (predictionChart) {
                predictionChart.resize();
            }
        });
    } catch (error) {
        console.error('更新预测图表失败:', error);
    }
}

/**
 * 生成预测分析的模拟数据
 */
function generatePredictionMockData() {
    const data = [];
    const now = new Date();
    
    // 生成过去10天的历史数据
    for (let i = 10; i > 0; i--) {
        const timestamp = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
        // 生成带趋势的历史数据，模拟一个缓慢上升的过程
        const value = Math.round((65 + i * 2 + (Math.random() - 0.5) * 10) * 10) / 10;
        
        data.push({
            timestamp: timestamp.toISOString(),
            value: value,
            type: 'historical'
        });
    }
    
    // 生成未来5天的预测数据
    for (let i = 1; i <= 5; i++) {
        const timestamp = new Date(now.getTime() + i * 24 * 60 * 60 * 1000);
        // 基于最后一个历史数据点，继续上升趋势
        const lastHistoricalValue = data[data.length - 1].value;
        const value = Math.round((lastHistoricalValue + i * 3 + (Math.random() - 0.5) * 8) * 10) / 10;
        
        data.push({
            timestamp: timestamp.toISOString(),
            value: value,
            type: 'predicted'
        });
    }
    
    return data;
}

/**
 * 获取预测图表选项
 */
function getPredictionChartOption(data) {
    // 分离历史数据和预测数据
    const historicalData = data.filter(item => item.type === 'historical');
    const predictedData = data.filter(item => item.type === 'predicted');
    
    // 格式化数据
    const allTimestamps = [...historicalData, ...predictedData].map(item => new Date(item.timestamp).toLocaleString('zh-CN'));
    const historicalValues = historicalData.map(item => item.value);
    // 为预测数据创建占位符数组
    const predictedValues = new Array(historicalData.length).fill(null).concat(predictedData.map(item => item.value));
    
    return {
        title: {
            text: '设备参数预测分析',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['历史数据', '预测数据'],
            top: 30
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: 80,
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: allTimestamps,
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: '参数值'
        },
        series: [
            {
                name: '历史数据',
                type: 'line',
                data: historicalValues,
                smooth: true,
                lineStyle: {
                    color: '#1890ff',
                    width: 2
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: '#1890ff80'
                    }, {
                        offset: 1,
                        color: '#1890ff10'
                    }])
                }
            },
            {
                name: '预测数据',
                type: 'line',
                data: predictedValues,
                smooth: true,
                lineStyle: {
                    color: '#ff4d4f',
                    width: 2,
                    type: 'dashed'
                },
                itemStyle: {
                    color: '#ff4d4f'
                }
            }
        ]
    };
}

/**
 * 更新统计图表
 */
async function updateStatsChart() {
    try {
        // 获取统计数据
        let data;
        try {
            // 尝试从API获取数据
            data = await analyticsAPI.getStatsData();
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            data = generateStatsMockData();
        }
        
        // 销毁旧图表
        if (statsChart) {
            statsChart.dispose();
        }
        
        // 创建新图表
        const chartDom = document.getElementById('stats-chart');
        statsChart = echarts.init(chartDom);
        
        // 设置图表选项
        const option = getStatsChartOption(data);
        statsChart.setOption(option);
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', () => {
            if (statsChart) {
                statsChart.resize();
            }
        });
    } catch (error) {
        console.error('更新统计图表失败:', error);
    }
}

/**
 * 生成统计图表的模拟数据
 */
function generateStatsMockData() {
    return [
        { name: '正常运行', value: 75, itemStyle: { color: '#52c41a' } },
        { name: '待机', value: 15, itemStyle: { color: '#1890ff' } },
        { name: '维护中', value: 7, itemStyle: { color: '#faad14' } },
        { name: '故障', value: 3, itemStyle: { color: '#f5222d' } }
    ];
}

/**
 * 获取统计图表选项
 */
function getStatsChartOption(data) {
    // 提取数据
    const labels = data.map(item => item.name || item.category);
    const values = data.map(item => item.value);
    
    return {
        title: {
            text: '设备状态分布',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [
            {
                name: '设备状态',
                type: 'pie',
                radius: '50%',
                data: data,
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
}

/**
 * 更新设备健康评分
 */
async function updateHealthScore() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value || '1';
        
        // 获取健康评分
        let score;
        try {
            // 尝试从API获取数据
            score = await analyticsAPI.getHealthScore(machineId);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            const scoreValue = Math.round(75 + Math.random() * 20);
            let scoreText;
            
            if (scoreValue >= 90) {
                scoreText = '设备状态极佳';
            } else if (scoreValue >= 80) {
                scoreText = '设备状态良好';
            } else if (scoreValue >= 70) {
                scoreText = '设备状态正常';
            } else {
                scoreText = '需要关注维护';
            }
            
            score = { score: scoreValue, text: scoreText };
        }
        
        // 更新UI
        const scoreElement = document.getElementById('health-score');
        const scoreTextElement = document.getElementById('health-score-text');
        
        scoreElement.textContent = score.score;
        scoreTextElement.textContent = score.text;
        
        // 设置评分颜色
        let scoreColor;
        if (score.score >= 80) {
            scoreColor = '#52c41a'; // 绿色
        } else if (score.score >= 60) {
            scoreColor = '#faad14'; // 黄色
        } else {
            scoreColor = '#f5222d'; // 红色
        }
        
        scoreElement.style.color = scoreColor;
    } catch (error) {
        console.error('更新健康评分失败:', error);
    }
}

/**
 * 更新预测性维护建议
 */
async function updateMaintenanceSuggestions() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value || '1';
        
        // 获取维护建议
        let suggestions;
        try {
            // 尝试从API获取数据
            suggestions = await analyticsAPI.getMaintenanceSuggestions(machineId);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 生成模拟数据
            suggestions = generateMaintenanceSuggestionsMockData();
        }
        
        // 更新UI
        const suggestionsElement = document.getElementById('maintenance-suggestions');
        
        if (suggestions && suggestions.length > 0) {
            let html = '<h5>维护建议</h5><ul class="list-group">';
            
            suggestions.forEach(suggestion => {
                const priorityClass = suggestion.priority === 'high' ? 'list-group-item-danger' : 
                                    suggestion.priority === 'medium' ? 'list-group-item-warning' : 
                                    'list-group-item-success';
                
                html += `
                    <li class="list-group-item ${priorityClass}">
                        <strong>${suggestion.title}</strong>
                        <p class="mb-0">${suggestion.description}</p>
                    </li>
                `;
            });
            
            html += '</ul>';
            suggestionsElement.innerHTML = html;
        } else {
            suggestionsElement.innerHTML = '<p class="text-center text-muted">暂无维护建议</p>';
        }
    } catch (error) {
        console.error('更新维护建议失败:', error);
    }
}

/**
 * 生成维护建议的模拟数据
 */
function generateMaintenanceSuggestionsMockData() {
    return [
        {
            title: '定期轴承检查',
            description: '建议在未来7天内对主轴轴承进行检查和润滑，防止因磨损导致的设备故障。',
            priority: 'high'
        },
        {
            title: '液压系统维护',
            description: '液压油压力略低于正常范围，建议检查液压系统是否存在泄漏。',
            priority: 'medium'
        },
        {
            title: '冷却系统清洗',
            description: '冷却系统效率略有下降，建议在下次计划维护时进行清洗。',
            priority: 'low'
        },
        {
            title: '电气控制系统检查',
            description: '定期检查电气控制系统，确保所有连接正常，防止突发故障。',
            priority: 'medium'
        }
    ];
}

/**
 * 导出报表
 */
async function exportReport() {
    try {
        const machineId = document.getElementById('analytics-machine-select').value;
        const startDate = document.getElementById('analytics-start-date').value;
        const endDate = document.getElementById('analytics-end-date').value;
        
        if (!machineId) {
            showErrorMessage('请先选择设备');
            return;
        }
        
        // 显示导出中的提示
        showSuccessMessage('正在生成报表，请稍候...');
        
        // 实际项目中这里应该调用后端API生成报表
        // 这里简单模拟一个导出操作
        setTimeout(() => {
            showSuccessMessage('报表导出成功');
        }, 1000);
    } catch (error) {
        console.error('导出报表失败:', error);
        showErrorMessage('导出报表失败');
    }
}

/**
 * 显示成功消息
 */
function showSuccessMessage(message) {
    // 创建成功提示元素
    const successElement = document.createElement('div');
    successElement.className = 'alert alert-success alert-dismissible fade show mt-3';
    successElement.role = 'alert';
    successElement.innerHTML = `
        <strong>成功:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到数据分析区域
    const analyticsSection = document.getElementById('analytics');
    const cardHeader = analyticsSection.querySelector('.card-header');
    cardHeader.after(successElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        successElement.remove();
    }, 3000);
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
    
    // 添加到数据分析区域
    const analyticsSection = document.getElementById('analytics');
    const cardHeader = analyticsSection.querySelector('.card-header');
    cardHeader.after(errorElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        errorElement.remove();
    }, 3000);
}

// 导出模块
// 模块初始化完成