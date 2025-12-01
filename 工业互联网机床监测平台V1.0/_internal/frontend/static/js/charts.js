/**
 * 工业互联网机床状态监测平台 - 图表管理模块
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.realtimeChart = null;
        this.temperatureTrendChart = null;
        this.vibrationSpectrumChart = null;
        this.energyConsumptionChart = null;
        this.efficiencyStatsChart = null;
        
        // 数据缓存
        this.realtimeData = new Map();
        this.maxDataPoints = 50;
        
        this.initializeCharts();
    }
    
    /**
     * 初始化所有图表
     */
    initializeCharts() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupCharts();
            });
        } else {
            this.setupCharts();
        }
    }
    
    /**
     * 设置图表
     */
    setupCharts() {
        this.initRealtimeChart();
        this.initTemperatureTrendChart();
        this.initVibrationSpectrumChart();
        this.initEnergyConsumptionChart();
        this.initEfficiencyStatsChart();
    }
    
    /**
     * 初始化实时数据图表
     */
    initRealtimeChart() {
        const container = document.getElementById('realtime-chart');
        if (!container) return;
        
        this.realtimeChart = echarts.init(container);
        
        const option = {
            title: {
                text: '实时监测数据',
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#6a7985'
                    }
                },
                formatter: function(params) {
                    let result = `时间: ${params[0].axisValue}<br/>`;
                    params.forEach(param => {
                        result += `${param.seriesName}: ${param.value} ${param.data.unit || ''}<br/>`;
                    });
                    return result;
                }
            },
            legend: {
                data: ['温度', '振动', '电流', '转速', '压力'],
                top: 30
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: [],
                axisLabel: {
                    formatter: function(value) {
                        return new Date(value).toLocaleTimeString();
                    }
                }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '温度(°C)',
                    position: 'left',
                    axisLabel: {
                        formatter: '{value}°C'
                    }
                },
                {
                    type: 'value',
                    name: '振动(mm/s)',
                    position: 'right',
                    axisLabel: {
                        formatter: '{value}mm/s'
                    }
                }
            ],
            series: [
                {
                    name: '温度',
                    type: 'line',
                    yAxisIndex: 0,
                    data: [],
                    smooth: true,
                    lineStyle: {
                        color: '#ff6b6b'
                    },
                    itemStyle: {
                        color: '#ff6b6b'
                    }
                },
                {
                    name: '振动',
                    type: 'line',
                    yAxisIndex: 1,
                    data: [],
                    smooth: true,
                    lineStyle: {
                        color: '#4ecdc4'
                    },
                    itemStyle: {
                        color: '#4ecdc4'
                    }
                },
                {
                    name: '电流',
                    type: 'line',
                    yAxisIndex: 0,
                    data: [],
                    smooth: true,
                    lineStyle: {
                        color: '#45b7d1'
                    },
                    itemStyle: {
                        color: '#45b7d1'
                    }
                },
                {
                    name: '转速',
                    type: 'line',
                    yAxisIndex: 1,
                    data: [],
                    smooth: true,
                    lineStyle: {
                        color: '#f9ca24'
                    },
                    itemStyle: {
                        color: '#f9ca24'
                    }
                },
                {
                    name: '压力',
                    type: 'line',
                    yAxisIndex: 0,
                    data: [],
                    smooth: true,
                    lineStyle: {
                        color: '#6c5ce7'
                    },
                    itemStyle: {
                        color: '#6c5ce7'
                    }
                }
            ]
        };
        
        this.realtimeChart.setOption(option);
        this.charts.set('realtime', this.realtimeChart);
        
        // 响应式调整
        window.addEventListener('resize', () => {
            this.realtimeChart.resize();
        });
    }
    
    /**
     * 初始化温度趋势图表
     */
    initTemperatureTrendChart() {
        const container = document.getElementById('temperature-trend-chart');
        if (!container) return;
        
        this.temperatureTrendChart = echarts.init(container);
        
        const option = {
            title: {
                text: '温度趋势分析',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['CNC001', 'MILL001', 'DRILL001'],
                top: 30
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: this.generateTimeLabels(24) // 24小时
            },
            yAxis: {
                type: 'value',
                name: '温度(°C)',
                axisLabel: {
                    formatter: '{value}°C'
                }
            },
            series: [
                {
                    name: 'CNC001',
                    type: 'line',
                    data: this.generateRandomData(24, 25, 80),
                    smooth: true
                },
                {
                    name: 'MILL001',
                    type: 'line',
                    data: this.generateRandomData(24, 25, 80),
                    smooth: true
                },
                {
                    name: 'DRILL001',
                    type: 'line',
                    data: this.generateRandomData(24, 25, 80),
                    smooth: true
                }
            ]
        };
        
        this.temperatureTrendChart.setOption(option);
        this.charts.set('temperature-trend', this.temperatureTrendChart);
    }
    
    /**
     * 初始化振动频谱图表
     */
    initVibrationSpectrumChart() {
        const container = document.getElementById('vibration-spectrum-chart');
        if (!container) return;
        
        this.vibrationSpectrumChart = echarts.init(container);
        
        const frequencies = [];
        const amplitudes = [];
        
        // 生成频谱数据
        for (let i = 0; i <= 100; i++) {
            frequencies.push(i * 10); // 0-1000Hz
            amplitudes.push(Math.random() * 10 * Math.exp(-i * 0.05));
        }
        
        const option = {
            title: {
                text: '振动频谱分析',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    return `频率: ${params[0].name}Hz<br/>幅值: ${params[0].value.toFixed(2)}mm/s`;
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: frequencies,
                name: '频率(Hz)',
                axisLabel: {
                    interval: 10,
                    formatter: '{value}Hz'
                }
            },
            yAxis: {
                type: 'value',
                name: '幅值(mm/s)',
                axisLabel: {
                    formatter: '{value}mm/s'
                }
            },
            series: [{
                name: '振动幅值',
                type: 'line',
                data: amplitudes,
                lineStyle: {
                    color: '#4ecdc4'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0, color: 'rgba(78, 205, 196, 0.8)'
                        }, {
                            offset: 1, color: 'rgba(78, 205, 196, 0.1)'
                        }]
                    }
                }
            }]
        };
        
        this.vibrationSpectrumChart.setOption(option);
        this.charts.set('vibration-spectrum', this.vibrationSpectrumChart);
    }
    
    /**
     * 初始化能耗分析图表
     */
    initEnergyConsumptionChart() {
        const container = document.getElementById('energy-consumption-chart');
        if (!container) return;
        
        this.energyConsumptionChart = echarts.init(container);
        
        const option = {
            title: {
                text: '能耗分析',
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c}kW ({d}%)'
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                top: 'middle',
                data: ['CNC001', 'MILL001', 'DRILL001', '其他设备']
            },
            series: [
                {
                    name: '能耗分布',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    center: ['60%', '50%'],
                    avoidLabelOverlap: false,
                    label: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: '18',
                            fontWeight: 'bold'
                        }
                    },
                    labelLine: {
                        show: false
                    },
                    data: [
                        {value: 35.2, name: 'CNC001'},
                        {value: 28.7, name: 'MILL001'},
                        {value: 22.1, name: 'DRILL001'},
                        {value: 14.0, name: '其他设备'}
                    ]
                }
            ]
        };
        
        this.energyConsumptionChart.setOption(option);
        this.charts.set('energy-consumption', this.energyConsumptionChart);
    }
    
    /**
     * 初始化效率统计图表
     */
    initEfficiencyStatsChart() {
        const container = document.getElementById('efficiency-stats-chart');
        if (!container) return;
        
        this.efficiencyStatsChart = echarts.init(container);
        
        const option = {
            title: {
                text: '设备效率统计',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            legend: {
                data: ['运行效率', '能效比', '质量合格率'],
                top: 30
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: ['CNC001', 'MILL001', 'DRILL001']
            },
            yAxis: {
                type: 'value',
                name: '百分比(%)',
                max: 100,
                axisLabel: {
                    formatter: '{value}%'
                }
            },
            series: [
                {
                    name: '运行效率',
                    type: 'bar',
                    data: [85.2, 78.9, 92.1],
                    itemStyle: {
                        color: '#5dade2'
                    }
                },
                {
                    name: '能效比',
                    type: 'bar',
                    data: [76.8, 82.3, 88.7],
                    itemStyle: {
                        color: '#58d68d'
                    }
                },
                {
                    name: '质量合格率',
                    type: 'bar',
                    data: [96.5, 94.2, 98.1],
                    itemStyle: {
                        color: '#f7dc6f'
                    }
                }
            ]
        };
        
        this.efficiencyStatsChart.setOption(option);
        this.charts.set('efficiency-stats', this.efficiencyStatsChart);
    }
    
    /**
     * 更新实时数据图表
     */
    updateRealtimeChart(machineId, data) {
        if (!this.realtimeChart) return;
        
        const timestamp = new Date(data.timestamp);
        const timeStr = timestamp.toISOString();
        
        // 获取当前图表配置
        const option = this.realtimeChart.getOption();
        
        // 更新时间轴
        if (option.xAxis[0].data.length >= this.maxDataPoints) {
            option.xAxis[0].data.shift();
        }
        option.xAxis[0].data.push(timeStr);
        
        // 更新各个系列数据
        const seriesData = [
            data.temperature || 0,
            data.vibration || 0,
            data.current || 0,
            data.speed || 0,
            data.pressure || 0
        ];
        
        option.series.forEach((series, index) => {
            if (series.data.length >= this.maxDataPoints) {
                series.data.shift();
            }
            series.data.push(seriesData[index]);
        });
        
        // 更新图表
        this.realtimeChart.setOption(option);
    }
    
    /**
     * 更新温度趋势图表
     */
    updateTemperatureTrendChart(machineId, temperature) {
        if (!this.temperatureTrendChart) return;
        
        const option = this.temperatureTrendChart.getOption();
        const series = option.series.find(s => s.name === machineId);
        
        if (series) {
            // 移除最旧的数据点
            if (series.data.length >= 24) {
                series.data.shift();
            }
            // 添加新数据点
            series.data.push(temperature);
            
            this.temperatureTrendChart.setOption(option);
        }
    }
    
    /**
     * 生成时间标签
     */
    generateTimeLabels(hours) {
        const labels = [];
        const now = new Date();
        
        for (let i = hours - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.getHours() + ':00');
        }
        
        return labels;
    }
    
    /**
     * 生成随机数据
     */
    generateRandomData(count, min, max) {
        const data = [];
        for (let i = 0; i < count; i++) {
            data.push((Math.random() * (max - min) + min).toFixed(1));
        }
        return data;
    }
    
    /**
     * 调整所有图表大小
     */
    resizeAllCharts() {
        this.charts.forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
    
    /**
     * 销毁所有图表
     */
    destroyAllCharts() {
        this.charts.forEach(chart => {
            if (chart && typeof chart.dispose === 'function') {
                chart.dispose();
            }
        });
        this.charts.clear();
    }
    
    /**
     * 获取图表实例
     */
    getChart(name) {
        return this.charts.get(name);
    }
    
    /**
     * 设置图表主题
     */
    setTheme(theme) {
        this.charts.forEach((chart, name) => {
            if (chart && typeof chart.dispose === 'function') {
                chart.dispose();
            }
            
            // 重新初始化图表
            const container = document.getElementById(name + '-chart');
            if (container) {
                const newChart = echarts.init(container, theme);
                this.charts.set(name, newChart);
            }
        });
        
        // 重新设置图表
        this.setupCharts();
    }
    
    /**
     * 导出图表为图片
     */
    exportChart(chartName, filename) {
        const chart = this.charts.get(chartName);
        if (chart) {
            const url = chart.getDataURL({
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#fff'
            });
            
            // 创建下载链接
            const link = document.createElement('a');
            link.href = url;
            link.download = filename || `${chartName}-${new Date().getTime()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
    
    /**
     * 更新图表数据
     */
    updateChartData(chartName, data) {
        const chart = this.charts.get(chartName);
        if (chart) {
            const option = chart.getOption();
            
            // 根据图表类型更新数据
            switch (chartName) {
                case 'realtime':
                    this.updateRealtimeChartData(option, data);
                    break;
                case 'temperature-trend':
                    this.updateTemperatureTrendData(option, data);
                    break;
                case 'vibration-spectrum':
                    this.updateVibrationSpectrumData(option, data);
                    break;
                case 'energy-consumption':
                    this.updateEnergyConsumptionData(option, data);
                    break;
                case 'efficiency-stats':
                    this.updateEfficiencyStatsData(option, data);
                    break;
            }
            
            chart.setOption(option);
        }
    }
    
    /**
     * 更新实时图表数据
     */
    updateRealtimeChartData(option, data) {
        // 实现实时数据更新逻辑
        console.log('更新实时图表数据:', data);
    }
    
    /**
     * 更新温度趋势数据
     */
    updateTemperatureTrendData(option, data) {
        // 实现温度趋势数据更新逻辑
        console.log('更新温度趋势数据:', data);
    }
    
    /**
     * 更新振动频谱数据
     */
    updateVibrationSpectrumData(option, data) {
        // 实现振动频谱数据更新逻辑
        console.log('更新振动频谱数据:', data);
    }
    
    /**
     * 更新能耗数据
     */
    updateEnergyConsumptionData(option, data) {
        // 实现能耗数据更新逻辑
        console.log('更新能耗数据:', data);
    }
    
    /**
     * 更新效率统计数据
     */
    updateEfficiencyStatsData(option, data) {
        // 实现效率统计数据更新逻辑
        console.log('更新效率统计数据:', data);
    }
}

// 创建全局图表管理器实例
window.chartManager = new ChartManager();

// 窗口大小改变时调整图表
window.addEventListener('resize', () => {
    if (window.chartManager) {
        window.chartManager.resizeAllCharts();
    }
});

// 页面卸载前销毁图表
window.addEventListener('beforeunload', () => {
    if (window.chartManager) {
        window.chartManager.destroyAllCharts();
    }
});
