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