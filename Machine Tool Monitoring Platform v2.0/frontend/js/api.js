/**
 * 工业互联网机床监测平台 - 前端API交互模块
 * 负责与后端API进行数据交互，提供统一的数据请求接口
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * 通用HTTP请求方法
 * @param {string} endpoint - API端点
 * @param {string} method - HTTP方法
 * @param {Object} data - 请求数据
 * @param {Object} options - 附加选项
 * @returns {Promise} - 返回Promise对象
 */
async function apiRequest(endpoint, method = 'GET', data = null, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    const config = {
        method,
        headers,
        ...options
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `请求失败: ${response.status}`);
        }

        // 处理204 No Content响应
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error(`API请求错误 (${url}):`, error);
        // 如果是网络错误，可能是后端未运行，返回模拟数据
        if (error.message.includes('Failed to fetch')) {
            return getMockData(endpoint, method, data);
        }
        throw error;
    }
}

/**
 * 仪表盘相关API
 */
const dashboardAPI = {
    // 获取仪表盘概览数据
    getOverview() {
        return apiRequest('/dashboard/overview');
    },
    
    // 获取最近报警
    getRecentAlarms(limit = 10) {
        return apiRequest(`/dashboard/recent-alarms?limit=${limit}`);
    }
};

/**
 * 设备管理相关API
 */
const machinesAPI = {
    // 获取所有设备
    getAllMachines() {
        return apiRequest('/machines');
    },
    
    // 获取单个设备信息
    getMachine(id) {
        return apiRequest(`/machines/${id}`);
    },
    
    // 创建新设备
    createMachine(machineData) {
        return apiRequest('/machines', 'POST', machineData);
    },
    
    // 更新设备信息
    updateMachine(id, machineData) {
        return apiRequest(`/machines/${id}`, 'PUT', machineData);
    },
    
    // 删除设备
    deleteMachine(id) {
        return apiRequest(`/machines/${id}`, 'DELETE');
    },
    
    // 获取设备最新数据
    getMachineLatestData(id) {
        return apiRequest(`/machines/${id}/latest-data`);
    }
};

/**
 * 设备数据相关API
 */
const machineDataAPI = {
    // 获取设备历史数据
    getMachineHistory(id, params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        return apiRequest(`/machine-data/${id}?${queryParams}`);
    },
    
    // 获取设备趋势数据
    getMachineTrends(id, parameters = [], hours = 24) {
        return apiRequest(`/machine-data/${id}/trends`, 'POST', {
            parameters,
            hours
        });
    }
};

/**
 * 报警相关API
 */
const alarmsAPI = {
    // 获取所有报警
    getAllAlarms(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        return apiRequest(`/alarms?${queryParams}`);
    },
    
    // 获取报警详情
    getAlarm(id) {
        return apiRequest(`/alarms/${id}`);
    },
    
    // 处理报警
    handleAlarm(id, data) {
        return apiRequest(`/alarms/${id}/handle`, 'PUT', data);
    },
    
    // 获取报警规则
    getAlarmRules() {
        return apiRequest('/alarm-rules');
    }
};

/**
 * 维护记录相关API
 */
const maintenanceAPI = {
    // 获取所有维护记录
    getAllMaintenance() {
        return apiRequest('/maintenance');
    },
    
    // 创建维护记录
    createMaintenance(maintenanceData) {
        return apiRequest('/maintenance', 'POST', maintenanceData);
    },
    
    // 更新维护记录
    updateMaintenance(id, maintenanceData) {
        return apiRequest(`/maintenance/${id}`, 'PUT', maintenanceData);
    },
    
    // 删除维护记录
    deleteMaintenance(id) {
        return apiRequest(`/maintenance/${id}`, 'DELETE');
    }
};

/**
 * 数据分析相关API
 */
const analyticsAPI = {
    // 获取设备统计信息
    getMachineStatistics(id) {
        return apiRequest(`/analytics/machine-statistics/${id}`);
    },
    
    // 获取参数统计信息
    getParameterStatistics(id, parameter, hours = 24) {
        return apiRequest(`/analytics/parameter-statistics/${id}`, 'POST', {
            parameter,
            hours
        });
    }
};

/**
 * Mock数据生成函数 - 当后端API不可用时使用
 */
function getMockData(endpoint, method, data) {
    console.log('使用Mock数据:', endpoint);
    
    // 仪表盘数据
    if (endpoint.includes('/dashboard/overview')) {
        return {
            total_machines: 15,
            online_machines: 12,
            offline_machines: 3,
            active_alarms: 5,
            high_priority_alarms: 2,
            total_alarms: 28,
            maintenance_scheduled: 4,
            maintenance_completed: 16,
            productivity_rate: 87.5,
            efficiency_trend: 'up'
        };
    }
    
    // 最近报警
    if (endpoint.includes('/dashboard/recent-alarms')) {
        return [
            {
                id: 1,
                timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
                machine_name: "CNC加工中心1",
                machine_id: 1,
                type: "temperature",
                level: "high",
                description: "主轴温度超过85°C",
                handled: false,
                location: "车间A-1"
            },
            {
                id: 2,
                timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
                machine_name: "车床2",
                machine_id: 2,
                type: "vibration",
                level: "medium",
                description: "X轴振动超过1.2mm/s",
                handled: false,
                location: "车间B-3"
            },
            {
                id: 3,
                timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
                machine_name: "铣床3",
                machine_id: 3,
                type: "current",
                level: "low",
                description: "主电机电流波动超过±15%",
                handled: true,
                location: "车间C-5",
                handled_by: "工程师张",
                handled_time: new Date(Date.now() - 1000 * 60 * 20).toISOString()
            },
            {
                id: 4,
                timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
                machine_name: "激光切割机7",
                machine_id: 7,
                type: "power",
                level: "high",
                description: "激光功率下降超过20%",
                handled: false,
                location: "车间F-1"
            }
        ];
    }
    
    // 设备列表
    if (endpoint === '/machines' && method === 'GET') {
        return [
            {
                id: 1,
                name: "CNC加工中心1",
                type: "数控加工中心",
                model: "HAAS VF-2",
                location: "车间A-1",
                status: "online",
                serial_number: "HVF2-2020-001",
                installation_date: "2020-03-15",
                manufacturer: "哈斯自动化",
                last_maintenance: "2024-03-10",
                temperature: 78.5,
                vibration: 0.85,
                current: 12.3,
                rotation_speed: 1800
            },
            {
                id: 2,
                name: "数控车床2",
                type: "数控车床",
                model: "MAZAK QTN 200",
                location: "车间B-3",
                status: "online",
                serial_number: "MQTN-2019-015",
                installation_date: "2019-11-22",
                manufacturer: "山崎马扎克",
                last_maintenance: "2024-02-28",
                temperature: 68.3,
                vibration: 0.42,
                current: 9.8,
                rotation_speed: 2000
            },
            {
                id: 3,
                name: "立式铣床3",
                type: "铣床",
                model: "BRIDGEPORT V2XT",
                location: "车间C-5",
                status: "online",
                serial_number: "BPV2-2018-023",
                installation_date: "2018-08-05",
                manufacturer: "哈挺机床",
                last_maintenance: "2024-01-15",
                temperature: 72.1,
                vibration: 0.56,
                current: 8.7,
                rotation_speed: 1500
            },
            {
                id: 4,
                name: "平面磨床4",
                type: "平面磨床",
                model: "OKAMOTO PSG 63",
                location: "车间D-2",
                status: "offline",
                serial_number: "OPSG-2017-018",
                installation_date: "2017-12-10",
                manufacturer: "冈本机床",
                last_maintenance: "2024-02-05",
                fault_reason: "液压系统故障",
                fault_time: "2024-04-01T08:30:00Z"
            },
            {
                id: 5,
                name: "数控冲床5",
                type: "数控冲床",
                model: "AMADA VIPROS 357",
                location: "车间E-4",
                status: "online",
                serial_number: "AVIP-2019-007",
                installation_date: "2019-06-18",
                manufacturer: "天田株式会社",
                last_maintenance: "2024-03-20",
                temperature: 65.8,
                vibration: 0.33,
                current: 15.6,
                pressure: 8.5
            },
            {
                id: 6,
                name: "数控钻床6",
                type: "数控钻床",
                model: "HAAS ST-10",
                location: "车间A-6",
                status: "online",
                serial_number: "HST1-2021-012",
                installation_date: "2021-02-25",
                manufacturer: "哈斯自动化",
                last_maintenance: "2024-03-05",
                temperature: 69.4,
                vibration: 0.28,
                current: 7.2,
                rotation_speed: 2200
            },
            {
                id: 7,
                name: "激光切割机7",
                type: "激光切割",
                model: "TRUMPF TruLaser 3030",
                location: "车间F-1",
                status: "online",
                serial_number: "TTL3-2018-009",
                installation_date: "2018-10-08",
                manufacturer: "通快集团",
                last_maintenance: "2024-02-15",
                temperature: 82.3,
                vibration: 0.45,
                current: 22.5,
                power: 3500
            },
            {
                id: 8,
                name: "注塑机8",
                type: "注塑机",
                model: "HAITIAN MA3800II",
                location: "车间G-3",
                status: "online",
                serial_number: "HMA3-2020-021",
                installation_date: "2020-08-12",
                manufacturer: "海天国际",
                last_maintenance: "2024-03-18",
                temperature: 88.6,
                pressure: 12.5,
                current: 35.8,
                cycle_time: 45
            },
            {
                id: 9,
                name: "液压压力机9",
                type: "液压压力机",
                model: "DONGA-100T",
                location: "车间H-2",
                status: "offline",
                serial_number: "D100-2016-014",
                installation_date: "2016-05-20",
                manufacturer: "东锻机械",
                last_maintenance: "2024-01-25",
                fault_reason: "电气控制系统故障",
                fault_time: "2024-03-30T14:20:00Z"
            },
            {
                id: 10,
                name: "焊接机器人10",
                type: "工业机器人",
                model: "FANUC R-2000iA",
                location: "车间I-5",
                status: "online",
                serial_number: "FRA2-2019-011",
                installation_date: "2019-04-05",
                manufacturer: "发那科",
                last_maintenance: "2024-03-08",
                temperature: 62.1,
                vibration: 0.15,
                current: 18.3,
                accuracy: 0.02
            },
            {
                id: 11,
                name: "数控折弯机11",
                type: "数控折弯机",
                model: "BYSTRONIC Xpert 40",
                location: "车间J-1",
                status: "online",
                serial_number: "BX40-2021-005",
                installation_date: "2021-06-15",
                manufacturer: "百超集团",
                last_maintenance: "2024-03-25",
                temperature: 71.8,
                pressure: 9.2,
                current: 16.8,
                angle_precision: 0.1
            },
            {
                id: 12,
                name: "电火花成型机12",
                type: "电火花加工",
                model: "牧野EDGE3",
                location: "车间K-4",
                status: "online",
                serial_number: "MED3-2018-017",
                installation_date: "2018-09-22",
                manufacturer: "牧野机床",
                last_maintenance: "2024-02-18",
                temperature: 68.5,
                current: 8.3,
                voltage: 50,
                pulse_frequency: 1000
            },
            {
                id: 13,
                name: "线切割机床13",
                type: "线切割",
                model: "慢走丝FW-1",
                location: "车间L-2",
                status: "online",
                serial_number: "FW1-2019-023",
                installation_date: "2019-07-10",
                manufacturer: "沙迪克",
                last_maintenance: "2024-03-12",
                temperature: 67.2,
                current: 3.8,
                voltage: 120,
                wire_speed: 1800
            },
            {
                id: 14,
                name: "自动装配线14",
                type: "自动化线",
                model: "定制装配线-A",
                location: "车间M-5",
                status: "online",
                serial_number: "CALA-2022-001",
                installation_date: "2022-01-20",
                manufacturer: "本地自动化",
                last_maintenance: "2024-03-22",
                temperature: 65.4,
                vibration: 0.32,
                current: 42.7,
                production_rate: 240
            },
            {
                id: 15,
                name: "物料搬运机器人15",
                type: "物流机器人",
                model: "KUKA KR 10 R1100",
                location: "车间N-1",
                status: "offline",
                serial_number: "KKR1-2020-015",
                installation_date: "2020-11-05",
                manufacturer: "库卡机器人",
                last_maintenance: "2024-02-25",
                fault_reason: "电池电量耗尽",
                fault_time: "2024-04-01T10:15:00Z"
            }
        ];
    }
    
    // 设备详情
    if (endpoint.match(/\/machines\/\d+$/) && method === 'GET') {
        const machineId = parseInt(endpoint.split('/').pop());
        const machineNames = ["CNC加工中心1", "数控车床2", "立式铣床3", "平面磨床4", "数控冲床5", 
                             "数控钻床6", "激光切割机7", "注塑机8", "液压压力机9", "焊接机器人10",
                             "数控折弯机11", "电火花成型机12", "线切割机床13", "自动装配线14", "物料搬运机器人15"];
        const machineTypes = ["数控加工中心", "数控车床", "铣床", "平面磨床", "数控冲床", 
                            "数控钻床", "激光切割", "注塑机", "液压压力机", "工业机器人",
                            "数控折弯机", "电火花加工", "线切割", "自动化线", "物流机器人"];
        const models = ["HAAS VF-2", "MAZAK QTN 200", "BRIDGEPORT V2XT", "OKAMOTO PSG 63", "AMADA VIPROS 357",
                       "HAAS ST-10", "TRUMPF TruLaser 3030", "HAITIAN MA3800II", "DONGA-100T", "FANUC R-2000iA",
                       "BYSTRONIC Xpert 40", "牧野EDGE3", "慢走丝FW-1", "定制装配线-A", "KUKA KR 10 R1100"];
        const locations = ["车间A-1", "车间B-3", "车间C-5", "车间D-2", "车间E-4",
                          "车间A-6", "车间F-1", "车间G-3", "车间H-2", "车间I-5",
                          "车间J-1", "车间K-4", "车间L-2", "车间M-5", "车间N-1"];
        const manufacturers = ["哈斯自动化", "山崎马扎克", "哈挺机床", "冈本机床", "天田株式会社",
                              "哈斯自动化", "通快集团", "海天国际", "东锻机械", "发那科",
                              "百超集团", "牧野机床", "沙迪克", "本地自动化", "库卡机器人"];
        
        const idx = (machineId - 1) % machineNames.length;
        
        return {
            id: machineId,
            name: machineNames[idx],
            type: machineTypes[idx],
            model: models[idx],
            location: locations[idx],
            status: machineId % 5 === 0 ? "offline" : "online",
            serial_number: `${models[idx].replace(/\s+/g, '')}-${2020 - (machineId % 5)}-${String(machineId).padStart(3, '0')}`,
            installation_date: `${2022 - (machineId % 6)}-${String((machineId % 12) + 1).padStart(2, '0')}-${String((machineId % 28) + 1).padStart(2, '0')}`,
            manufacturer: manufacturers[idx],
            last_maintenance: `${2024}-${String((machineId % 3) + 1).padStart(2, '0')}-${String((machineId % 28) + 1).padStart(2, '0')}`,
            total_runtime: 12500 + (machineId * 500),
            maintenance_count: 15 + (machineId % 10),
            temperature: Math.round((60 + Math.random() * 20) * 10) / 10,
            vibration: Math.round((0.1 + Math.random() * 0.5) * 100) / 100,
            current: Math.round((10 + Math.random() * 5) * 10) / 10,
            rotation_speed: Math.round(1000 + Math.random() * 1000),
            pressure: Math.round((5 + Math.random() * 5) * 10) / 10,
            power: Math.round((15 + Math.random() * 10) * 10) / 10,
            efficiency_rate: Math.round((85 + Math.random() * 10) * 10) / 10,
            fault_count: machineId % 5,
            current_task: machineId % 3 === 0 ? "维护中" : `生产批次-${machineId}-${Math.floor(Math.random() * 1000)}`,
            next_maintenance_date: `${2024}-${String((machineId % 3) + 4).padStart(2, '0')}-${String((machineId % 28) + 1).padStart(2, '0')}`
        };
    }
    
    // 设备历史数据
    if (endpoint.match(/\/machine-data\/\d+/) && method === 'GET') {
        const hours = endpoint.includes('hours') ? parseInt(endpoint.match(/hours=(\d+)/)[1]) : 24;
        const data = [];
        const now = Date.now();
        
        for (let i = hours * 60; i >= 0; i -= 10) {
            const timestamp = new Date(now - i * 60 * 1000).toISOString();
            data.push({
                timestamp,
                temperature: Math.round((60 + Math.random() * 20) * 10) / 10,
                vibration: Math.round((0.1 + Math.random() * 0.5) * 100) / 100,
                current: Math.round((10 + Math.random() * 5) * 10) / 10,
                rotation_speed: Math.round(1000 + Math.random() * 1000),
                pressure: Math.round((5 + Math.random() * 5) * 10) / 10,
                power: Math.round((15 + Math.random() * 10) * 10) / 10,
                efficiency: Math.round((80 + Math.random() * 15) * 10) / 10,
                production_count: Math.floor(Math.random() * 50)
            });
        }
        
        return data;
    }
    
    // 报警列表
    if (endpoint === '/alarms' && method === 'GET') {
        const alarms = [];
        const alarmTypes = ['temperature', 'vibration', 'current', 'rotation_speed', 'pressure', 'power'];
        const alarmLevels = ['high', 'medium', 'low'];
        const now = Date.now();
        const machineNames = ["CNC加工中心1", "数控车床2", "立式铣床3", "平面磨床4", "数控冲床5", 
                             "数控钻床6", "激光切割机7", "注塑机8", "液压压力机9", "焊接机器人10",
                             "数控折弯机11", "电火花成型机12", "线切割机床13", "自动装配线14", "物料搬运机器人15"];
        
        const descriptions = {
            temperature: {
                high: "温度超过安全阈值",
                medium: "温度接近警告阈值",
                low: "温度异常偏低"
            },
            vibration: {
                high: "振动强度过大",
                medium: "振动异常",
                low: "振动轻微异常"
            },
            current: {
                high: "电流过大",
                medium: "电流波动异常",
                low: "电流偏低"
            },
            rotation_speed: {
                high: "转速过高",
                medium: "转速波动",
                low: "转速偏低"
            },
            pressure: {
                high: "压力过高",
                medium: "压力波动",
                low: "压力不足"
            },
            power: {
                high: "功率消耗异常",
                medium: "功率波动",
                low: "功率过低"
            }
        };
        
        for (let i = 1; i <= 25; i++) {
            const timestamp = new Date(now - i * 60 * 60 * 1000).toISOString();
            const machineId = (i % 15) + 1;
            const type = alarmTypes[i % alarmTypes.length];
            const level = alarmLevels[i % alarmLevels.length];
            const handled = i % 3 === 0;
            
            const alarm = {
                id: i,
                timestamp,
                machine_id: machineId,
                machine_name: machineNames[machineId - 1],
                type,
                level,
                description: `${getParameterName(type)}${descriptions[type][level]}`,
                handled,
                location: `车间${String.fromCharCode(64 + (machineId % 14 + 1))}-${machineId % 5 + 1}`
            };
            
            if (handled) {
                alarm.handled_by = `工程师${['张', '王', '李', '赵', '刘'][i % 5]}`;
                alarm.handled_time = new Date(Date.parse(timestamp) + 30 * 60 * 1000 * (i % 5 + 1)).toISOString();
                alarm.handle_note = `已处理${getParameterName(type)}异常，检查了相关部件并进行了调整`;
            }
            
            alarms.push(alarm);
        }
        
        return alarms;
    }
    
    // 报警规则
    if (endpoint === '/alarm-rules' && method === 'GET') {
        return [
            {
                id: 1,
                name: "温度过高报警",
                parameter: "temperature",
                condition: "gt",
                threshold: 85,
                level: "high",
                description: "当设备温度超过85°C时触发高优先级报警",
                enabled: true
            },
            {
                id: 2,
                name: "温度警告",
                parameter: "temperature",
                condition: "gt",
                threshold: 75,
                level: "medium",
                description: "当设备温度超过75°C时触发中优先级报警",
                enabled: true
            },
            {
                id: 3,
                name: "振动异常报警",
                parameter: "vibration",
                condition: "gt",
                threshold: 1.0,
                level: "high",
                description: "当设备振动超过1.0mm/s时触发高优先级报警",
                enabled: true
            },
            {
                id: 4,
                name: "振动警告",
                parameter: "vibration",
                condition: "gt",
                threshold: 0.7,
                level: "medium",
                description: "当设备振动超过0.7mm/s时触发中优先级报警",
                enabled: true
            },
            {
                id: 5,
                name: "电流异常报警",
                parameter: "current",
                condition: "gt",
                threshold: 30,
                level: "high",
                description: "当设备电流超过30A时触发高优先级报警",
                enabled: true
            },
            {
                id: 6,
                name: "电流波动警告",
                parameter: "current",
                condition: "波动",
                threshold: 20,
                level: "low",
                description: "当设备电流波动超过20%时触发低优先级报警",
                enabled: true
            },
            {
                id: 7,
                name: "转速异常报警",
                parameter: "rotation_speed",
                condition: "gt",
                threshold: 3000,
                level: "high",
                description: "当设备转速超过3000RPM时触发高优先级报警",
                enabled: true
            },
            {
                id: 8,
                name: "压力过高报警",
                parameter: "pressure",
                condition: "gt",
                threshold: 15,
                level: "high",
                description: "当设备压力超过15MPa时触发高优先级报警",
                enabled: true
            }
        ];
    }
    
    // 维护记录
    if (endpoint === '/maintenance' && method === 'GET') {
        const maintenanceRecords = [];
        const maintenanceTypes = ['预防性维护', '故障维修', '校准', '润滑', '零件更换', '系统升级', '清洁保养'];
        const maintenanceStatus = ['pending', 'in_progress', 'completed'];
        const now = Date.now();
        const machineNames = ["CNC加工中心1", "数控车床2", "立式铣床3", "平面磨床4", "数控冲床5", 
                             "数控钻床6", "激光切割机7", "注塑机8", "液压压力机9", "焊接机器人10",
                             "数控折弯机11", "电火花成型机12", "线切割机床13", "自动装配线14", "物料搬运机器人15"];
        const engineers = ['张工', '王工', '李工', '赵工', '刘工', '陈工', '杨工'];
        
        const maintenanceDescriptions = {
            '预防性维护': ['进行全面检查和保养', '更换易损件', '检查液压系统', '检查电气系统', '测试安全装置'],
            '故障维修': ['修复主轴故障', '更换损坏部件', '修复控制系统故障', '修复液压系统泄漏', '修复冷却系统故障'],
            '校准': ['校准主轴精度', '校准定位精度', '校准温度传感器', '校准压力传感器', '校准振动传感器'],
            '润滑': ['更换润滑油', '润滑各运动部件', '检查润滑系统', '清洁润滑管路', '更换润滑滤芯'],
            '零件更换': ['更换主轴轴承', '更换刀具', '更换传感器', '更换电机', '更换控制系统模块'],
            '系统升级': ['升级控制系统软件', '更新PLC程序', '升级监测系统', '更新操作界面', '优化控制参数'],
            '清洁保养': ['清洁设备内部', '清理冷却系统', '清理过滤装置', '清洁电气柜', '清理导轨和丝杠']
        };
        
        for (let i = 1; i <= 20; i++) {
            const timestamp = new Date(now - i * 24 * 60 * 60 * 1000).toISOString();
            const machineId = (i % 15) + 1;
            const maintenanceType = maintenanceTypes[i % maintenanceTypes.length];
            const status = maintenanceStatus[i % maintenanceStatus.length];
            const descriptionArray = maintenanceDescriptions[maintenanceType];
            const description = `${maintenanceType}：${descriptionArray[i % descriptionArray.length]}`;
            
            const record = {
                id: i,
                machine_id: machineId,
                machine_name: machineNames[machineId - 1],
                machine_type: ["数控加工中心", "数控车床", "铣床", "平面磨床", "数控冲床", 
                               "数控钻床", "激光切割", "注塑机", "液压压力机", "工业机器人",
                               "数控折弯机", "电火花加工", "线切割", "自动化线", "物流机器人"][machineId - 1],
                maintenance_type: maintenanceType,
                description: description,
                performed_by: engineers[i % engineers.length],
                start_time: timestamp,
                estimated_duration: `${(i % 5) + 1}小时`,
                priority: ['high', 'medium', 'low'][i % 3],
                cost: Math.round((1000 + Math.random() * 5000) * 100) / 100
            };
            
            if (status === 'completed' || status === 'in_progress') {
                record.end_time = new Date(Date.parse(timestamp) + (i % 10 + 1) * 60 * 60 * 1000).toISOString();
            }
            
            record.status = status;
            
            if (status === 'completed') {
                record.notes = `维护完成，设备运行正常。${Math.random() > 0.5 ? '建议下次维护前检查相关部件。' : ''}`;
                record.satisfaction = Math.floor(Math.random() * 3) + 3; // 3-5分
            }
            
            maintenanceRecords.push(record);
        }
        
        return maintenanceRecords;
    }
    
    // 数据分析统计
    if (endpoint.match(/\/analytics\/machine-statistics\/\d+/) && method === 'GET') {
        const machineId = parseInt(endpoint.match(/\/analytics\/machine-statistics\/(\d+)/)[1]);
        return {
            machine_id: machineId,
            machine_name: `设备${machineId}`,
            total_runtime: Math.floor(10000 + Math.random() * 20000),
            uptime_rate: Math.round((90 + Math.random() * 8) * 10) / 10,
            fault_count: Math.floor(Math.random() * 20),
            maintenance_count: Math.floor(Math.random() * 30) + 10,
            productivity: Math.round((800 + Math.random() * 500) * 10) / 10,
            efficiency_rate: Math.round((85 + Math.random() * 10) * 10) / 10,
            energy_consumption: Math.round((5000 + Math.random() * 10000) * 10) / 10,
            parts_produced: Math.floor(10000 + Math.random() * 40000),
            quality_rate: Math.round((95 + Math.random() * 4) * 10) / 10,
            average_cycle_time: Math.round((30 + Math.random() * 60) * 10) / 10,
            month_comparison: {
                productivity_increase: Math.round((-5 + Math.random() * 20) * 10) / 10,
                efficiency_increase: Math.round((-3 + Math.random() * 10) * 10) / 10,
                fault_decrease: Math.round((-20 + Math.random() * 40) * 10) / 10
            }
        };
    }
    
    // 参数统计信息
    if (endpoint.match(/\/analytics\/parameter-statistics\/\d+/) && method === 'POST') {
        const machineId = parseInt(endpoint.match(/\/analytics\/parameter-statistics\/(\d+)/)[1]);
        const parameter = data?.parameter || 'temperature';
        
        return {
            machine_id: machineId,
            parameter: parameter,
            parameter_name: getParameterName(parameter),
            average_value: Math.round((60 + Math.random() * 20) * 10) / 10,
            max_value: Math.round((80 + Math.random() * 20) * 10) / 10,
            min_value: Math.round((40 + Math.random() * 20) * 10) / 10,
            median_value: Math.round((55 + Math.random() * 30) * 10) / 10,
            standard_deviation: Math.round((2 + Math.random() * 5) * 10) / 10,
            trend: ['stable', 'increasing', 'decreasing'][Math.floor(Math.random() * 3)],
            abnormal_count: Math.floor(Math.random() * 10),
            thresholds: {
                warning: Math.round((70 + Math.random() * 10) * 10) / 10,
                critical: Math.round((85 + Math.random() * 5) * 10) / 10
            }
        };
    }
    
    // 返回空数据或默认响应
    return [];
}

/**
 * 辅助函数 - 获取参数的中文名称
 */
function getParameterName(param) {
    const paramMap = {
        temperature: '温度',
        vibration: '振动',
        current: '电流',
        rotation_speed: '转速',
        pressure: '压力',
        power: '功率'
    };
    return paramMap[param] || param;
}

/**
 * 辅助函数 - 获取报警描述
 */
function getAlarmDescription(type, level) {
    const descriptions = {
        high: '异常高',
        medium: '接近阈值',
        low: '轻微异常'
    };
    return descriptions[level] || '异常';
}

// 挂载API函数到window对象
window.dashboardAPI = dashboardAPI;
window.machinesAPI = machinesAPI;
window.machineDataAPI = machineDataAPI;
window.alarmsAPI = alarmsAPI;
window.maintenanceAPI = maintenanceAPI;
window.analyticsAPI = analyticsAPI;
window.getParameterName = getParameterName;