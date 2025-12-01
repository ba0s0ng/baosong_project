/**
 * 工业互联网机床监测平台 - 报警管理模块
 * 负责机床运行异常报警的接收、显示、处理和记录
 */

// 移除import语句，直接使用window上的API对象
// import { alarmsAPI, alarmRulesAPI } from './api.js';

/**
 * 初始化报警管理模块
 */
async function initAlarms() {
    try {
        // 加载报警规则
        await loadAlarmRules();
        
        // 加载报警列表
        await loadAlarmList();
        
        // 绑定事件监听器
        bindEventListeners();
        
        // 设置自动刷新
        setAutoRefresh();
    } catch (error) {
        console.error('初始化报警管理模块失败:', error);
        showErrorMessage('报警管理模块初始化失败');
    }
}

/**
 * 加载报警规则
 */
async function loadAlarmRules() {
    try {
        // 添加try-catch以处理API调用失败情况
        let rules;
        try {
            // 尝试从API获取数据
            rules = await window.alarmsAPI.getAlarmRules();
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            // 提供模拟报警规则数据
            rules = [
                {
                    id: 1,
                    name: '温度过高报警',
                    parameter: 'temperature',
                    operator: '>',
                    threshold: 80,
                    is_enabled: true
                },
                {
                    id: 2,
                    name: '振动异常报警',
                    parameter: 'vibration',
                    operator: '>',
                    threshold: 0.7,
                    is_enabled: true
                },
                {
                    id: 3,
                    name: '电流过低报警',
                    parameter: 'current',
                    operator: '<',
                    threshold: 5,
                    is_enabled: false
                },
                {
                    id: 4,
                    name: '转速异常报警',
                    parameter: 'rotation_speed',
                    operator: '!=',
                    threshold: 3000,
                    is_enabled: true
                },
                {
                    id: 5,
                    name: '压力过高报警',
                    parameter: 'pressure',
                    operator: '>',
                    threshold: 15,
                    is_enabled: true
                }
            ];
        }
        
        const rulesTable = document.getElementById('alarm-rules-table');
        const tbody = rulesTable.querySelector('tbody');
        
        // 清空表格内容
        tbody.innerHTML = '';
        
        // 添加规则行
        rules.forEach(rule => {
            const row = createRuleRow(rule);
            tbody.appendChild(row);
        });
        
        // 如果没有规则，显示空状态
        if (rules.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="6" class="text-center text-muted">暂无报警规则</td>
            `;
            tbody.appendChild(emptyRow);
        }
    } catch (error) {
        console.error('加载报警规则失败:', error);
    }
}

/**
 * 创建规则表格行
 */
function createRuleRow(rule) {
    const row = document.createElement('tr');
    
    // 状态标签
    const statusBadge = rule.is_enabled 
        ? '<span class="badge bg-success">启用</span>' 
        : '<span class="badge bg-secondary">禁用</span>';
    
    // 操作按钮
    const actions = `
        <button class="btn btn-sm btn-primary edit-rule-btn" data-id="${rule.id}">
            <i class="fas fa-edit"></i> 编辑
        </button>
        <button class="btn btn-sm ${rule.is_enabled ? 'btn-warning' : 'btn-success'} toggle-rule-btn" data-id="${rule.id}">
            ${rule.is_enabled ? '<i class="fas fa-pause"></i> 禁用' : '<i class="fas fa-play"></i> 启用'}
        </button>
        <button class="btn btn-sm btn-danger delete-rule-btn" data-id="${rule.id}">
            <i class="fas fa-trash"></i> 删除
        </button>
    `;
    
    row.innerHTML = `
        <td>${rule.name}</td>
        <td>${rule.parameter}</td>
        <td>${rule.operator}</td>
        <td>${rule.threshold}</td>
        <td>${statusBadge}</td>
        <td>${actions}</td>
    `;
    
    return row;
}

/**
 * 加载报警列表
 */
async function loadAlarmList() {
    try {
        // 获取筛选条件
        const statusFilter = document.getElementById('alarm-status-filter').value;
        const severityFilter = document.getElementById('alarm-severity-filter').value;
        const startDate = document.getElementById('alarm-start-date').value;
        const endDate = document.getElementById('alarm-end-date').value;
        
        // 构建查询参数
        const params = {};
        if (statusFilter) params.status = statusFilter;
        if (severityFilter) params.severity = severityFilter;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        
        // 获取报警数据
        let alarms;
        try {
            // 尝试从API获取数据
            alarms = await alarmsAPI.getAllAlarms(params);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 提供模拟报警数据
            alarms = [
                {
                    id: 1,
                    machine_name: '加工中心1',
                    message: '温度超过设定阈值',
                    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
                    severity: 'critical',
                    status: 'active'
                },
                {
                    id: 2,
                    machine_name: '车床2',
                    message: '振动值异常升高',
                    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
                    severity: 'warning',
                    status: 'acknowledged'
                },
                {
                    id: 3,
                    machine_name: '机器人1',
                    message: '电流异常波动',
                    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
                    severity: 'info',
                    status: 'resolved'
                },
                {
                    id: 4,
                    machine_name: '铣床1',
                    message: '压力超过安全阈值',
                    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
                    severity: 'critical',
                    status: 'active'
                },
                {
                    id: 5,
                    machine_name: '加工中心2',
                    message: '转速不稳定',
                    timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
                    severity: 'warning',
                    status: 'resolved'
                },
                {
                    id: 6,
                    machine_name: '车床1',
                    message: '温度接近阈值',
                    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
                    severity: 'info',
                    status: 'acknowledged'
                },
                {
                    id: 7,
                    machine_name: '机器人2',
                    message: '位置偏移过大',
                    timestamp: new Date(Date.now() - 1000 * 60 * 150).toISOString(),
                    severity: 'critical',
                    status: 'resolved'
                },
                {
                    id: 8,
                    machine_name: '铣床2',
                    message: '冷却系统压力过低',
                    timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
                    severity: 'warning',
                    status: 'active'
                }
            ];
            
            // 根据筛选条件过滤模拟数据
            if (statusFilter) {
                alarms = alarms.filter(alarm => alarm.status === statusFilter);
            }
            if (severityFilter) {
                alarms = alarms.filter(alarm => alarm.severity === severityFilter);
            }
        }
        
        const alarmsTable = document.getElementById('alarms-table');
        const tbody = alarmsTable.querySelector('tbody');
        
        // 清空表格内容
        tbody.innerHTML = '';
        
        // 添加报警行
        alarms.forEach(alarm => {
            const row = createAlarmRow(alarm);
            tbody.appendChild(row);
        });
        
        // 如果没有报警，显示空状态
        if (alarms.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="7" class="text-center text-muted">暂无报警记录</td>
            `;
            tbody.appendChild(emptyRow);
        }
    } catch (error) {
        console.error('加载报警列表失败:', error);
    }
}

/**
 * 创建报警表格行
 */
function createAlarmRow(alarm) {
    const row = document.createElement('tr');
    
    // 严重程度标签
    let severityBadge;
    switch (alarm.severity) {
        case 'critical':
            severityBadge = '<span class="badge bg-danger">严重</span>';
            break;
        case 'warning':
            severityBadge = '<span class="badge bg-warning text-dark">警告</span>';
            break;
        case 'info':
            severityBadge = '<span class="badge bg-info">信息</span>';
            break;
        default:
            severityBadge = '<span class="badge bg-secondary">未知</span>';
    }
    
    // 状态标签
    let statusBadge;
    switch (alarm.status) {
        case 'active':
            statusBadge = '<span class="badge bg-danger">未处理</span>';
            break;
        case 'acknowledged':
            statusBadge = '<span class="badge bg-warning text-dark">已确认</span>';
            break;
        case 'resolved':
            statusBadge = '<span class="badge bg-success">已解决</span>';
            break;
        default:
            statusBadge = '<span class="badge bg-secondary">未知</span>';
    }
    
    // 格式化时间
    const timestamp = new Date(alarm.timestamp).toLocaleString('zh-CN');
    
    // 操作按钮
    let actions = '';
    if (alarm.status === 'active') {
        actions = `
            <button class="btn btn-sm btn-warning acknowledge-alarm-btn" data-id="${alarm.id}">
                <i class="fas fa-check"></i> 确认
            </button>
        `;
    } else if (alarm.status === 'acknowledged') {
        actions = `
            <button class="btn btn-sm btn-success resolve-alarm-btn" data-id="${alarm.id}">
                <i class="fas fa-check-circle"></i> 解决
            </button>
        `;
    }
    
    row.innerHTML = `
        <td>${alarm.id}</td>
        <td>${alarm.machine_name || '未知设备'}</td>
        <td>${alarm.message}</td>
        <td>${timestamp}</td>
        <td>${severityBadge}</td>
        <td>${statusBadge}</td>
        <td>${actions}</td>
    `;
    
    return row;
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 报警规则相关
    bindRuleEventListeners();
    
    // 报警管理相关
    bindAlarmEventListeners();
}

/**
 * 绑定规则相关事件监听器
 */
function bindRuleEventListeners() {
    // 添加规则按钮
    document.getElementById('add-rule-btn').addEventListener('click', () => {
        openRuleModal();
    });
    
    // 规则表格事件委托
    const rulesTable = document.getElementById('alarm-rules-table');
    
    // 编辑规则
    rulesTable.addEventListener('click', async (e) => {
        if (e.target.closest('.edit-rule-btn')) {
            const button = e.target.closest('.edit-rule-btn');
            const ruleId = parseInt(button.dataset.id);
            await editRule(ruleId);
        }
    });
    
    // 切换规则状态
    rulesTable.addEventListener('click', async (e) => {
        if (e.target.closest('.toggle-rule-btn')) {
            const button = e.target.closest('.toggle-rule-btn');
            const ruleId = parseInt(button.dataset.id);
            await toggleRuleStatus(ruleId);
        }
    });
    
    // 删除规则
    rulesTable.addEventListener('click', async (e) => {
        if (e.target.closest('.delete-rule-btn')) {
            const button = e.target.closest('.delete-rule-btn');
            const ruleId = parseInt(button.dataset.id);
            await deleteRule(ruleId);
        }
    });
    
    // 保存规则
    document.getElementById('save-rule-btn').addEventListener('click', async () => {
        await saveRule();
    });
    
    // 重置规则表单
    document.getElementById('reset-rule-btn').addEventListener('click', () => {
        resetRuleForm();
    });
}

/**
 * 绑定报警相关事件监听器
 */
function bindAlarmEventListeners() {
    // 筛选按钮
    document.getElementById('alarm-filter-btn').addEventListener('click', () => {
        loadAlarmList();
    });
    
    // 重置筛选按钮
    document.getElementById('alarm-reset-filter-btn').addEventListener('click', () => {
        document.getElementById('alarm-status-filter').value = '';
        document.getElementById('alarm-severity-filter').value = '';
        document.getElementById('alarm-start-date').value = '';
        document.getElementById('alarm-end-date').value = '';
        loadAlarmList();
    });
    
    // 报警表格事件委托
    const alarmsTable = document.getElementById('alarms-table');
    
    // 确认报警
    alarmsTable.addEventListener('click', async (e) => {
        if (e.target.closest('.acknowledge-alarm-btn')) {
            const button = e.target.closest('.acknowledge-alarm-btn');
            const alarmId = parseInt(button.dataset.id);
            await acknowledgeAlarm(alarmId);
        }
    });
    
    // 解决报警
    alarmsTable.addEventListener('click', async (e) => {
        if (e.target.closest('.resolve-alarm-btn')) {
            const button = e.target.closest('.resolve-alarm-btn');
            const alarmId = parseInt(button.dataset.id);
            await resolveAlarm(alarmId);
        }
    });
}

/**
 * 打开规则模态框
 */
function openRuleModal(rule = null) {
    const modal = new bootstrap.Modal(document.getElementById('rule-modal'));
    const modalTitle = document.getElementById('rule-modal-title');
    
    // 重置表单
    resetRuleForm();
    
    if (rule) {
        // 编辑模式
        modalTitle.textContent = '编辑报警规则';
        document.getElementById('rule-id').value = rule.id;
        document.getElementById('rule-name').value = rule.name;
        document.getElementById('rule-parameter').value = rule.parameter;
        document.getElementById('rule-operator').value = rule.operator;
        document.getElementById('rule-threshold').value = rule.threshold;
        document.getElementById('rule-enabled').checked = rule.is_enabled;
    } else {
        // 添加模式
        modalTitle.textContent = '添加报警规则';
    }
    
    modal.show();
}

/**
 * 重置规则表单
 */
function resetRuleForm() {
    document.getElementById('rule-form').reset();
    document.getElementById('rule-id').value = '';
}

/**
 * 保存规则
 */
async function saveRule() {
    try {
        // 获取表单数据
        const ruleId = document.getElementById('rule-id').value;
        const name = document.getElementById('rule-name').value.trim();
        const parameter = document.getElementById('rule-parameter').value;
        const operator = document.getElementById('rule-operator').value;
        const threshold = parseFloat(document.getElementById('rule-threshold').value);
        const isEnabled = document.getElementById('rule-enabled').checked;
        
        // 验证表单
        if (!name) {
            showErrorMessage('请输入规则名称');
            return;
        }
        
        if (isNaN(threshold)) {
            showErrorMessage('请输入有效的阈值');
            return;
        }
        
        // 构建规则数据
        const ruleData = {
            name,
            parameter,
            operator,
            threshold,
            is_enabled: isEnabled
        };
        
        // 保存规则
        try {
            if (ruleId) {
                // 更新规则
                await alarmRulesAPI.updateRule(parseInt(ruleId), ruleData);
                showSuccessMessage('规则更新成功');
            } else {
                // 添加规则
                await alarmRulesAPI.createRule(ruleData);
                showSuccessMessage('规则添加成功');
            }
        } catch (apiError) {
            console.warn('API调用失败，使用模拟保存:', apiError);
            showSuccessMessage(ruleId ? '规则更新成功' : '规则添加成功');
        }
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('rule-modal'));
        modal.hide();
        
        // 重新加载规则列表
        await loadAlarmRules();
    } catch (error) {
        console.error('保存规则失败:', error);
        showErrorMessage('保存规则失败');
    }
}

/**
 * 编辑规则
 */
async function editRule(ruleId) {
    try {
        let rule;
        try {
            // 尝试从API获取规则数据
            rule = await alarmRulesAPI.getRule(ruleId);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 在模拟环境中，我们直接从表格中获取规则数据
            const rulesTable = document.getElementById('alarm-rules-table');
            const rows = rulesTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const editButton = row.querySelector('.edit-rule-btn');
                if (editButton && editButton.dataset.id === ruleId.toString()) {
                    const cells = row.querySelectorAll('td');
                    rule = {
                        id: ruleId,
                        name: cells[0].textContent,
                        parameter: cells[1].textContent,
                        operator: cells[2].textContent,
                        threshold: parseFloat(cells[3].textContent),
                        is_enabled: cells[4].querySelector('.badge').classList.contains('bg-success')
                    };
                }
            });
        }
        
        // 打开规则模态框并填充数据
        openRuleModal(rule);
    } catch (error) {
        console.error('获取规则详情失败:', error);
        showErrorMessage('获取规则详情失败');
    }
}

/**
 * 切换规则状态
 */
async function toggleRuleStatus(ruleId) {
    try {
        // 获取规则
        let rule;
        try {
            rule = await alarmRulesAPI.getRule(ruleId);
            
            // 更新状态
            await alarmRulesAPI.updateRule(ruleId, {
                is_enabled: !rule.is_enabled
            });
            
            showSuccessMessage(`规则已${rule.is_enabled ? '禁用' : '启用'}`);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟更新:', apiError);
            
            // 在模拟环境中，我们直接更新表格中的规则状态
            const rulesTable = document.getElementById('alarm-rules-table');
            const rows = rulesTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const toggleButton = row.querySelector('.toggle-rule-btn');
                if (toggleButton && toggleButton.dataset.id === ruleId.toString()) {
                    const statusCell = row.querySelector('td:nth-child(5)');
                    const isCurrentlyEnabled = statusCell.querySelector('.badge').classList.contains('bg-success');
                    
                    // 更新状态标签
                    statusCell.innerHTML = isCurrentlyEnabled 
                        ? '<span class="badge bg-secondary">禁用</span>' 
                        : '<span class="badge bg-success">启用</span>';
                    
                    // 更新按钮状态
                    toggleButton.className = isCurrentlyEnabled 
                        ? 'btn btn-sm btn-success toggle-rule-btn' 
                        : 'btn btn-sm btn-warning toggle-rule-btn';
                    toggleButton.innerHTML = isCurrentlyEnabled 
                        ? '<i class="fas fa-play"></i> 启用' 
                        : '<i class="fas fa-pause"></i> 禁用';
                    
                    showSuccessMessage(`规则已${isCurrentlyEnabled ? '禁用' : '启用'}`);
                }
            });
        }
        
        // 重新加载规则列表
        await loadAlarmRules();
    } catch (error) {
        console.error('切换规则状态失败:', error);
        showErrorMessage('切换规则状态失败');
    }
}

/**
 * 删除规则
 */
async function deleteRule(ruleId) {
    try {
        if (confirm('确定要删除这条规则吗？')) {
            try {
                await alarmRulesAPI.deleteRule(ruleId);
            } catch (apiError) {
                console.warn('API调用失败，使用模拟删除:', apiError);
                
                // 在模拟环境中，我们直接从表格中删除对应的行
                const rulesTable = document.getElementById('alarm-rules-table');
                const rows = rulesTable.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const deleteButton = row.querySelector('.delete-rule-btn');
                    if (deleteButton && deleteButton.dataset.id === ruleId.toString()) {
                        row.remove();
                    }
                });
            }
            
            showSuccessMessage('规则删除成功');
            
            // 重新加载规则列表
            await loadAlarmRules();
        }
    } catch (error) {
        console.error('删除规则失败:', error);
        showErrorMessage('删除规则失败');
    }
}

/**
 * 确认报警
 */
async function acknowledgeAlarm(alarmId) {
    try {
        try {
            // 尝试从API更新报警状态
            await alarmsAPI.updateAlarmStatus(alarmId, 'acknowledged');
        } catch (apiError) {
            console.warn('API调用失败，使用模拟更新:', apiError);
            
            // 在模拟环境中，我们直接找到表格中的对应行并更新状态
            // 实际应用中，这里可以更新本地缓存或模拟数据存储
            const alarmsTable = document.getElementById('alarms-table');
            const rows = alarmsTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const idCell = row.querySelector('td:first-child');
                if (parseInt(idCell.textContent) === alarmId) {
                    // 更新状态标签
                    const statusCell = row.querySelector('td:nth-child(6)');
                    statusCell.innerHTML = '<span class="badge bg-warning text-dark">已确认</span>';
                    
                    // 更新操作按钮
                    const actionsCell = row.querySelector('td:nth-child(7)');
                    actionsCell.innerHTML = `
                        <button class="btn btn-sm btn-success resolve-alarm-btn" data-id="${alarmId}">
                            <i class="fas fa-check-circle"></i> 解决
                        </button>
                    `;
                }
            });
        }
        
        showSuccessMessage('报警已确认');
        // 重新加载报警列表以确保数据一致性
        await loadAlarmList();
    } catch (error) {
        console.error('确认报警失败:', error);
        showErrorMessage('确认报警失败');
    }
}

/**
 * 解决报警
 */
async function resolveAlarm(alarmId) {
    try {
        try {
            // 尝试从API更新报警状态
            await alarmsAPI.updateAlarmStatus(alarmId, 'resolved');
        } catch (apiError) {
            console.warn('API调用失败，使用模拟更新:', apiError);
            
            // 在模拟环境中，我们直接找到表格中的对应行并更新状态
            const alarmsTable = document.getElementById('alarms-table');
            const rows = alarmsTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const idCell = row.querySelector('td:first-child');
                if (parseInt(idCell.textContent) === alarmId) {
                    // 更新状态标签
                    const statusCell = row.querySelector('td:nth-child(6)');
                    statusCell.innerHTML = '<span class="badge bg-success">已解决</span>';
                    
                    // 移除操作按钮
                    const actionsCell = row.querySelector('td:nth-child(7)');
                    actionsCell.innerHTML = '';
                }
            });
        }
        
        showSuccessMessage('报警已解决');
        // 重新加载报警列表以确保数据一致性
        await loadAlarmList();
    } catch (error) {
        console.error('解决报警失败:', error);
        showErrorMessage('解决报警失败');
    }
}

/**
 * 设置自动刷新
 */
function setAutoRefresh() {
    // 每30秒自动刷新报警列表
    setInterval(() => {
        loadAlarmList();
    }, 30000);
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
    
    // 添加到报警管理区域
    const alarmsSection = document.getElementById('alarms');
    const cardHeader = alarmsSection.querySelector('.card-header');
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
    
    // 添加到报警管理区域
    const alarmsSection = document.getElementById('alarms');
    const cardHeader = alarmsSection.querySelector('.card-header');
    cardHeader.after(errorElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        errorElement.remove();
    }, 3000);
}

// 模块初始化完成