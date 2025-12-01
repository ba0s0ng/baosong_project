/**
 * 工业互联网机床监测平台 - 设备管理模块
 * 负责机床设备的信息展示、状态监控和参数配置
 */

// 移除import语句，直接使用window上的API对象
// import { machinesAPI } from './api.js';
/**
 * 初始化设备管理页面
 */
async function initMachines() {
    try {
        // 加载设备列表
        await loadMachinesList();
        
        // 绑定事件监听器
        bindEventListeners();
        
        // 设置定时刷新
        setInterval(() => {
            loadMachinesList();
        }, 60000); // 每分钟刷新一次
    } catch (error) {
        console.error('初始化设备管理失败:', error);
        showErrorMessage('设备数据加载失败');
    }
}

/**
 * 加载设备列表
 */
async function loadMachinesList() {
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
                    type: '加工中心',
                    model: 'DMG MORI CMX 1100 V',
                    location: 'A区',
                    status: 'online',
                    ip_address: '192.168.1.101',
                    last_update: new Date(Date.now() - 1000 * 60 * 5).toISOString()
                },
                {
                    id: 2,
                    name: '车床1',
                    type: '车床',
                    model: 'HAAS SL-20',
                    location: 'B区',
                    status: 'online',
                    ip_address: '192.168.1.102',
                    last_update: new Date(Date.now() - 1000 * 60 * 3).toISOString()
                },
                {
                    id: 3,
                    name: '铣床1',
                    type: '铣床',
                    model: 'FANUC Robodrill',
                    location: 'A区',
                    status: 'offline',
                    ip_address: '192.168.1.103',
                    last_update: new Date(Date.now() - 1000 * 60 * 60).toISOString()
                },
                {
                    id: 4,
                    name: '车床2',
                    type: '车床',
                    model: 'MAZAK QTS-200MSY',
                    location: 'B区',
                    status: 'online',
                    ip_address: '192.168.1.104',
                    last_update: new Date(Date.now() - 1000 * 60 * 2).toISOString()
                },
                {
                    id: 5,
                    name: '机器人1',
                    type: '工业机器人',
                    model: 'ABB IRB 6700',
                    location: 'C区',
                    status: 'online',
                    ip_address: '192.168.1.105',
                    last_update: new Date(Date.now() - 1000 * 60 * 1).toISOString()
                },
                {
                    id: 6,
                    name: '铣床2',
                    type: '铣床',
                    model: 'OKUMA MX-500V',
                    location: 'C区',
                    status: 'offline',
                    ip_address: '192.168.1.106',
                    last_update: new Date(Date.now() - 1000 * 60 * 30).toISOString()
                },
                {
                    id: 7,
                    name: '加工中心2',
                    type: '加工中心',
                    model: 'MAZAK VTC-800/30 SR',
                    location: 'A区',
                    status: 'online',
                    ip_address: '192.168.1.107',
                    last_update: new Date(Date.now() - 1000 * 60 * 4).toISOString()
                },
                {
                    id: 8,
                    name: '机器人2',
                    type: '工业机器人',
                    model: 'KUKA KR QUANTEC',
                    location: 'B区',
                    status: 'online',
                    ip_address: '192.168.1.108',
                    last_update: new Date(Date.now() - 1000 * 60 * 2).toISOString()
                },
                {
                    id: 9,
                    name: '检测设备1',
                    type: '三坐标测量机',
                    model: 'HEXAGON Global',
                    location: '质量部',
                    status: 'online',
                    ip_address: '192.168.1.109',
                    last_update: new Date(Date.now() - 1000 * 60 * 6).toISOString()
                },
                {
                    id: 10,
                    name: '激光切割机',
                    type: '激光切割',
                    model: 'TRUMPF TruLaser 3030',
                    location: 'D区',
                    status: 'offline',
                    ip_address: '192.168.1.110',
                    last_update: new Date(Date.now() - 1000 * 60 * 90).toISOString()
                }
            ];
        }
        
        const tableBody = document.getElementById('machines-table');
        
        if (machines.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center">暂无设备</td></tr>';
            return;
        }
        
        let html = '';
        machines.forEach(machine => {
            const statusClass = machine.status === 'online' ? 'status-online' : 'status-offline';
            const statusText = machine.status === 'online' ? '在线' : '离线';
            
            html += `
                <tr data-id="${machine.id}">
                    <td>${machine.name}</td>
                    <td>${machine.type}</td>
                    <td>${machine.model || '-'}</td>
                    <td>${machine.location || '-'}</td>
                    <td>
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </td>
                    <td>
                        <button class="btn btn-info btn-sm view-machine" data-id="${machine.id}">
                            <i class="fa fa-eye mr-1"></i> 查看
                        </button>
                        <button class="btn btn-warning btn-sm edit-machine" data-id="${machine.id}">
                            <i class="fa fa-pencil mr-1"></i> 编辑
                        </button>
                        <button class="btn btn-danger btn-sm delete-machine" data-id="${machine.id}">
                            <i class="fa fa-trash mr-1"></i> 删除
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
        
        // 绑定行内按钮事件
        bindTableButtonEvents();
    } catch (error) {
        console.error('加载设备列表失败:', error);
        document.getElementById('machines-table').innerHTML = 
            '<tr><td colspan="6" class="text-center text-danger">加载设备信息失败</td></tr>';
    }
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 保存设备按钮
    document.getElementById('saveMachineBtn').addEventListener('click', saveMachine);
    
    // 为添加维护记录模态框中的设备选择器加载设备
    const addMaintenanceModal = document.getElementById('addMaintenanceModal');
    if (addMaintenanceModal) {
        addMaintenanceModal.addEventListener('show.bs.modal', loadMachinesForMaintenanceSelect);
    }
}

/**
 * 绑定表格内按钮事件
 */
function bindTableButtonEvents() {
    // 查看设备
    document.querySelectorAll('.view-machine').forEach(button => {
        button.addEventListener('click', function() {
            const machineId = parseInt(this.getAttribute('data-id'));
            viewMachineDetails(machineId);
        });
    });
    
    // 编辑设备
    document.querySelectorAll('.edit-machine').forEach(button => {
        button.addEventListener('click', function() {
            const machineId = parseInt(this.getAttribute('data-id'));
            editMachine(machineId);
        });
    });
    
    // 删除设备
    document.querySelectorAll('.delete-machine').forEach(button => {
        button.addEventListener('click', function() {
            const machineId = parseInt(this.getAttribute('data-id'));
            deleteMachine(machineId);
        });
    });
}

/**
 * 保存设备信息
 */
async function saveMachine() {
    try {
        // 获取表单数据
        const machineName = document.getElementById('machine-name').value.trim();
        const machineType = document.getElementById('machine-type').value.trim();
        const machineModel = document.getElementById('machine-model').value.trim();
        const machineLocation = document.getElementById('machine-location').value.trim();
        const machineStatus = document.getElementById('machine-status').value;
        
        // 验证表单
        if (!machineName || !machineType) {
            showAlert('设备名称和类型为必填项', 'error');
            return;
        }
        
        // 准备设备数据
        const machineData = {
            name: machineName,
            type: machineType,
            model: machineModel,
            location: machineLocation,
            status: machineStatus
        };
        
        // 获取是否是编辑模式
        const editMode = document.getElementById('addMachineModal').getAttribute('data-edit-mode') === 'true';
        const machineId = parseInt(document.getElementById('addMachineModal').getAttribute('data-machine-id'));
        
        if (editMode) {
            // 更新设备
            await machinesAPI.updateMachine(machineId, machineData);
            showAlert('设备更新成功', 'success');
        } else {
            // 创建新设备
            await machinesAPI.createMachine(machineData);
            showAlert('设备添加成功', 'success');
        }
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('addMachineModal'));
        modal.hide();
        
        // 重置表单
        document.getElementById('addMachineForm').reset();
        
        // 刷新设备列表
        await loadMachinesList();
    } catch (error) {
        console.error('保存设备失败:', error);
        showAlert('保存设备失败: ' + error.message, 'error');
    }
}

/**
 * 查看设备详情
 */
async function viewMachineDetails(machineId) {
    try {
        const machine = await machinesAPI.getMachine(machineId);
        
        // 创建详情模态框内容
        const modalContent = `
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">设备详情</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="detail-card">
                        <div class="detail-label">设备名称</div>
                        <div class="detail-value">${machine.name}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">设备类型</div>
                        <div class="detail-value">${machine.type}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">设备型号</div>
                        <div class="detail-value">${machine.model || '-'}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">设备位置</div>
                        <div class="detail-value">${machine.location || '-'}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">设备状态</div>
                        <div class="detail-value">
                            <span class="status-badge ${machine.status === 'online' ? 'status-online' : 'status-offline'}">
                                ${machine.status === 'online' ? '在线' : '离线'}
                            </span>
                        </div>
                    </div>
                    ${machine.temperature !== undefined ? `
                    <div class="detail-card">
                        <div class="detail-label">当前温度</div>
                        <div class="detail-value">${machine.temperature} °C</div>
                    </div>
                    ` : ''}
                    ${machine.vibration !== undefined ? `
                    <div class="detail-card">
                        <div class="detail-label">当前振动</div>
                        <div class="detail-value">${machine.vibration} mm/s</div>
                    </div>
                    ` : ''}
                    ${machine.current !== undefined ? `
                    <div class="detail-card">
                        <div class="detail-label">当前电流</div>
                        <div class="detail-value">${machine.current} A</div>
                    </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                </div>
            </div>
        `;
        
        // 创建模态框元素
        const modalElement = document.createElement('div');
        modalElement.className = 'modal fade';
        modalElement.tabIndex = -1;
        modalElement.innerHTML = modalContent;
        
        // 添加到body
        document.body.appendChild(modalElement);
        
        // 显示模态框
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        // 模态框关闭后移除元素
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        });
    } catch (error) {
        console.error('查看设备详情失败:', error);
        showAlert('查看设备详情失败', 'error');
    }
}

/**
 * 编辑设备
 */
async function editMachine(machineId) {
    try {
        const machine = await machinesAPI.getMachine(machineId);
        
        // 填充表单数据
        document.getElementById('machine-name').value = machine.name;
        document.getElementById('machine-type').value = machine.type;
        document.getElementById('machine-model').value = machine.model || '';
        document.getElementById('machine-location').value = machine.location || '';
        document.getElementById('machine-status').value = machine.status;
        
        // 设置为编辑模式
        document.getElementById('addMachineModal').setAttribute('data-edit-mode', 'true');
        document.getElementById('addMachineModal').setAttribute('data-machine-id', machineId);
        document.getElementById('addMachineModalLabel').textContent = '编辑设备';
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('addMachineModal'));
        modal.show();
        
        // 模态框关闭后重置状态
        document.getElementById('addMachineModal').addEventListener('hidden.bs.modal', function resetModal() {
            document.getElementById('addMachineModal').setAttribute('data-edit-mode', 'false');
            document.getElementById('addMachineModal').setAttribute('data-machine-id', '');
            document.getElementById('addMachineModalLabel').textContent = '添加设备';
            document.getElementById('addMachineForm').reset();
            document.getElementById('addMachineModal').removeEventListener('hidden.bs.modal', resetModal);
        });
    } catch (error) {
        console.error('编辑设备失败:', error);
        showAlert('编辑设备失败', 'error');
    }
}

/**
 * 删除设备
 */
async function deleteMachine(machineId) {
    if (!confirm('确定要删除该设备吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        await machinesAPI.deleteMachine(machineId);
        showAlert('设备删除成功', 'success');
        
        // 刷新设备列表
        await loadMachinesList();
    } catch (error) {
        console.error('删除设备失败:', error);
        showAlert('删除设备失败: ' + error.message, 'error');
    }
}

/**
 * 为维护记录模态框加载设备列表
 */
async function loadMachinesForMaintenanceSelect() {
    try {
        const machines = await machinesAPI.getAllMachines();
        const selectElement = document.getElementById('maintenance-machine');
        
        // 清空现有选项
        selectElement.innerHTML = '<option value="">选择设备</option>';
        
        // 添加设备选项
        machines.forEach(machine => {
            const option = document.createElement('option');
            option.value = machine.id;
            option.textContent = machine.name;
            selectElement.appendChild(option);
        });
    } catch (error) {
        console.error('加载维护记录设备列表失败:', error);
    }
}

/**
 * 显示提示信息
 */
function showAlert(message, type = 'info') {
    // 创建提示元素
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed top-5 end-5 z-50`;
    alertElement.role = 'alert';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到body
    document.body.appendChild(alertElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        alertElement.remove();
    }, 3000);
}

/**
 * 显示错误消息
 */
function showErrorMessage(message) {
    showAlert(message, 'error');
}

// 模块初始化完成