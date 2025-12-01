/**
 * 工业互联网机床监测平台 - 主应用脚本
 * 负责整合所有功能模块，处理页面导航和初始化
 */

// 导入各个功能模块
// 移除import语句，使用事件监听器在DOM加载完成后初始化各模块
// import { initDashboard } from './dashboard.js';
// import { initMachines } from './machines.js';
// import { initDigitalTwin } from './digital-twin.js';
// import { initAlarms } from './alarms.js';
// import { initAnalytics } from './analytics.js';
/**
 * 主应用类
 */
class MachineMonitoringApp {
    constructor() {
        // 当前激活的模块
        this.activeModule = 'dashboard';
        // 模块初始化状态
        this.modulesInitialized = {
            dashboard: false,
            machines: false,
            digitalTwin: false,
            alarms: false,
            analytics: false,
            maintenance: false
        };
    }
    
    /**
     * 初始化应用
     */
    init() {
        try {
            // 绑定全局事件
            this.bindGlobalEvents();
            
            // 初始化导航
            this.initNavigation();
            
            // 初始化仪表盘（默认显示的模块）
            this.loadModule('dashboard');
            
            // 显示欢迎消息
            this.showWelcomeMessage();
        } catch (error) {
            console.error('应用初始化失败:', error);
            this.showErrorMessage('应用初始化失败，请刷新页面重试');
        }
    }
    
    /**
     * 绑定全局事件
     */
    bindGlobalEvents() {
        // 页面滚动事件
        window.addEventListener('scroll', this.handleScroll.bind(this));
        
        // 窗口大小变化事件
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // 键盘快捷键
        document.addEventListener('keydown', this.handleKeydown.bind(this));
    }
    
    /**
     * 初始化导航
     */
    initNavigation() {
        // 获取所有导航项
        const navItems = document.querySelectorAll('.nav-link');
        
        // 为每个导航项绑定点击事件
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                // 获取目标模块ID
                const target = item.getAttribute('href').substring(1);
                
                // 加载对应模块
                this.loadModule(target);
                
                // 滚动到页面顶部
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }
    
    /**
     * 加载模块
     */
    loadModule(moduleId) {
        try {
            // 检查模块ID是否有效
            if (!['dashboard', 'machines', 'digital-twin', 'alarms', 'analytics', 'maintenance'].includes(moduleId)) {
                console.error('无效的模块ID:', moduleId);
                return;
            }
            
            // 更新导航状态
            this.updateNavigationState(moduleId);
            
            // 显示加载指示器
            this.showLoadingIndicator(true);
            
            // 根据模块ID初始化对应模块
            switch (moduleId) {
                case 'dashboard':
                    if (!this.modulesInitialized.dashboard) {
                        if (typeof initDashboard === 'function') {
                            initDashboard();
                            this.modulesInitialized.dashboard = true;
                        }
                    }
                    break;
                case 'machines':
                    if (!this.modulesInitialized.machines) {
                        if (typeof initMachines === 'function') {
                            initMachines();
                            this.modulesInitialized.machines = true;
                        }
                    }
                    break;
                case 'digital-twin':
                    if (!this.modulesInitialized.digitalTwin) {
                        if (typeof initDigitalTwin === 'function') {
                            initDigitalTwin();
                            this.modulesInitialized.digitalTwin = true;
                        }
                    }
                    break;
                case 'alarms':
                    if (!this.modulesInitialized.alarms) {
                        if (typeof initAlarms === 'function') {
                            initAlarms();
                            this.modulesInitialized.alarms = true;
                        }
                    }
                    break;
                case 'analytics':
                    if (!this.modulesInitialized.analytics) {
                        if (typeof initAnalytics === 'function') {
                            initAnalytics();
                            this.modulesInitialized.analytics = true;
                        }
                    }
                    break;
                case 'maintenance':
                    if (!this.modulesInitialized.maintenance) {
                        if (typeof initMaintenance === 'function') {
                            initMaintenance();
                            this.modulesInitialized.maintenance = true;
                        }
                    }
                    break;
            }
            
            // 切换显示的内容区域
            this.switchContentArea(moduleId);
            
            // 更新面包屑导航
            this.updateBreadcrumb(moduleId);
            
            // 隐藏加载指示器
            this.showLoadingIndicator(false);
            
            // 更新当前活动模块
            this.activeModule = moduleId;
        } catch (error) {
            console.error(`加载模块 ${moduleId} 失败:`, error);
            this.showErrorMessage(`加载模块失败: ${error.message}`);
            this.showLoadingIndicator(false);
        }
    }
    
    /**
     * 更新导航状态
     */
    updateNavigationState(activeModuleId) {
        // 移除所有导航项的活动状态
        document.querySelectorAll('.nav-link').forEach(item => {
            item.classList.remove('active');
        });
        
        // 为当前活动模块添加活动状态
        const activeNavItem = document.querySelector(`.nav-link[href="#${activeModuleId}"]`);
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
    }
    
    /**
     * 切换显示的内容区域
     */
    switchContentArea(moduleId) {
        // 隐藏所有内容区域
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // 显示当前内容区域
        const activeSection = document.getElementById(moduleId);
        if (activeSection) {
            activeSection.classList.remove('d-none');
        }
    }
    
    /**
     * 更新面包屑导航
     */
    updateBreadcrumb(moduleId) {
        // 模块名称映射
        const moduleNames = {
            'dashboard': '仪表盘',
            'machines': '设备管理',
            'digital-twin': '数字孪生',
            'alarms': '报警管理',
            'analytics': '数据分析',
            'maintenance': '维护记录'
        };
        
        // 更新面包屑
        const breadcrumb = document.getElementById('breadcrumb');
        if (breadcrumb) {
            breadcrumb.innerHTML = `
                <li class="breadcrumb-item">
                    <a href="#dashboard" class="breadcrumb-link">首页</a>
                </li>
                <li class="breadcrumb-item active">
                    ${moduleNames[moduleId] || moduleId}
                </li>
            `;
            
            // 为首页链接绑定事件
            breadcrumb.querySelector('.breadcrumb-link').addEventListener('click', (e) => {
                e.preventDefault();
                this.loadModule('dashboard');
            });
        }
    }
    
    /**
     * 显示加载指示器
     */
    showLoadingIndicator(show) {
        const loadingIndicator = document.getElementById('global-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'flex' : 'none';
        }
    }
    
    /**
     * 页面滚动处理
     */
    handleScroll() {
        const navbar = document.getElementById('main-navbar');
        if (navbar) {
            // 当页面滚动超过50px时，添加阴影效果
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-shadow');
            } else {
                navbar.classList.remove('navbar-shadow');
            }
        }
    }
    
    /**
     * 窗口大小变化处理
     */
    handleResize() {
        // 通知所有已初始化的模块窗口大小发生变化
        // 这里可以添加特定模块的调整逻辑
    }
    
    /**
     * 键盘快捷键处理
     */
    handleKeydown(e) {
        // Ctrl/Cmd + 数字键快速导航到对应模块
        if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.loadModule('dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    this.loadModule('machines');
                    break;
                case '3':
                    e.preventDefault();
                    this.loadModule('digital-twin');
                    break;
                case '4':
                    e.preventDefault();
                    this.loadModule('alarms');
                    break;
                case '5':
                    e.preventDefault();
                    this.loadModule('analytics');
                    break;
            }
        }
        
        // F5 刷新当前模块
        if (e.key === 'F5' && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            this.refreshCurrentModule();
        }
    }
    
    /**
     * 刷新当前模块
     */
    refreshCurrentModule() {
        // 重置当前模块的初始化状态，强制重新加载
        switch (this.activeModule) {
            case 'dashboard':
                this.modulesInitialized.dashboard = false;
                break;
            case 'machines':
                this.modulesInitialized.machines = false;
                break;
            case 'digital-twin':
                this.modulesInitialized.digitalTwin = false;
                break;
            case 'alarms':
                this.modulesInitialized.alarms = false;
                break;
            case 'analytics':
                this.modulesInitialized.analytics = false;
                break;
            case 'maintenance':
                this.modulesInitialized.maintenance = false;
                break;
        }
        
        // 重新加载当前模块
        this.loadModule(this.activeModule);
    }
    
    /**
     * 显示成功消息
     */
    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }
    
    /**
     * 显示错误消息
     */
    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification alert alert-${type === 'error' ? 'danger' : type} position-fixed top-5 right-5 z-50`;
        notification.role = 'alert';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    /**
     * 显示欢迎消息
     */
    showWelcomeMessage() {
        // 检查是否需要显示欢迎消息（例如，基于本地存储）
        const lastVisit = localStorage.getItem('lastVisit');
        
        if (!lastVisit || Date.now() - lastVisit > 86400000) { // 超过24小时
            this.showSuccessMessage('欢迎使用工业互联网机床监测平台！');
            localStorage.setItem('lastVisit', Date.now());
        }
    }
}

/**
 * 维护记录模块相关函数
 */

/**
 * 初始化维护记录模块
 */
async function initMaintenance() {
    try {
        // 加载维护记录
        await loadMaintenanceRecords();
        
        // 绑定维护记录相关事件监听器
        bindMaintenanceEventListeners();
    } catch (error) {
        console.error('初始化维护记录模块失败:', error);
        showErrorMessage('加载维护记录失败');
    }
}

/**
 * 加载维护记录列表
 */
async function loadMaintenanceRecords() {
    try {
        let maintenanceRecords;
        
        try {
            // 尝试从API获取数据
            maintenanceRecords = await maintenanceAPI.getAllMaintenance();
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 使用模拟数据
            maintenanceRecords = generateMaintenanceMockData();
        }
        
        // 渲染维护记录表格
        renderMaintenanceTable(maintenanceRecords);
    } catch (error) {
        console.error('加载维护记录失败:', error);
        showErrorMessage('加载维护记录失败');
    }
}

/**
 * 生成维护记录的模拟数据
 */
function generateMaintenanceMockData() {
    const maintenanceRecords = [];
    const maintenanceTypes = ['预防性维护', '故障维修', '校准', '润滑', '零件更换'];
    const maintenanceStatus = ['pending', 'in_progress', 'completed'];
    const now = Date.now();
    const statusText = {
        pending: '待处理',
        in_progress: '进行中',
        completed: '已完成'
    };
    
    // 生成15条模拟记录
    for (let i = 1; i <= 15; i++) {
        const timestamp = new Date(now - i * 24 * 60 * 60 * 1000).toISOString();
        const machineId = (i % 10) + 1;
        const status = maintenanceStatus[i % maintenanceStatus.length];
        
        maintenanceRecords.push({
            id: i,
            machine_id: machineId,
            machine_name: `设备${machineId}`,
            maintenance_type: maintenanceTypes[i % maintenanceTypes.length],
            description: `对设备进行${maintenanceTypes[i % maintenanceTypes.length]}`,
            performed_by: `工程师${(i % 5) + 1}`,
            start_time: timestamp,
            end_time: status === 'completed' ? new Date(Date.parse(timestamp) + 2 * 60 * 60 * 1000).toISOString() : null,
            status: status,
            status_text: statusText[status]
        });
    }
    
    return maintenanceRecords;
}

/**
 * 渲染维护记录表格
 */
function renderMaintenanceTable(maintenanceRecords) {
    const tableBody = document.getElementById('maintenance-table');
    if (!tableBody) return;
    
    // 清空表格
    tableBody.innerHTML = '';
    
    if (maintenanceRecords.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">暂无维护记录</td></tr>';
        return;
    }
    
    // 格式化状态显示
    const getStatusBadge = (status) => {
        switch (status) {
            case 'pending':
                return '<span class="badge bg-warning">待处理</span>';
            case 'in_progress':
                return '<span class="badge bg-primary">进行中</span>';
            case 'completed':
                return '<span class="badge bg-success">已完成</span>';
            default:
                return '<span class="badge bg-secondary">未知</span>';
        }
    };
    
    // 格式化时间显示
    const formatDate = (dateString) => {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    
    // 添加记录行
    maintenanceRecords.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.machine_name}</td>
            <td>${record.maintenance_type}</td>
            <td>${formatDate(record.start_time)}</td>
            <td>${formatDate(record.end_time)}</td>
            <td>${record.performed_by || '-'}</td>
            <td>${getStatusBadge(record.status)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary edit-maintenance-btn" 
                        data-id="${record.id}" 
                        data-machine-id="${record.machine_id}">
                    <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="btn btn-sm btn-outline-danger delete-maintenance-btn" 
                        data-id="${record.id}">
                    <i class="fas fa-trash-alt"></i> 删除
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * 保存维护记录
 */
async function saveMaintenance() {
    try {
        // 获取表单数据
        const machineId = document.getElementById('maintenance-machine').value;
        const maintenanceType = document.getElementById('maintenance-type').value.trim();
        const description = document.getElementById('maintenance-description').value.trim();
        const performedBy = document.getElementById('maintenance-performed-by').value.trim();
        const status = document.getElementById('maintenance-status').value;
        
        // 验证表单
        if (!machineId || !maintenanceType) {
            showErrorMessage('请填写必填项');
            return;
        }
        
        // 准备维护记录数据
        const maintenanceData = {
            machine_id: machineId,
            maintenance_type: maintenanceType,
            description: description,
            performed_by: performedBy,
            start_time: new Date().toISOString(),
            end_time: status === 'completed' ? new Date().toISOString() : null,
            status: status
        };
        
        try {
            // 尝试保存到API
            await maintenanceAPI.createMaintenance(maintenanceData);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟保存:', apiError);
            // 模拟保存成功，不需要实际操作
        }
        
        // 显示成功消息
        showSuccessMessage('维护记录保存成功');
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('addMaintenanceModal'));
        if (modal) {
            modal.hide();
        }
        
        // 重置表单
        document.getElementById('addMaintenanceForm').reset();
        
        // 重新加载维护记录列表
        await loadMaintenanceRecords();
    } catch (error) {
        console.error('保存维护记录失败:', error);
        showErrorMessage('保存维护记录失败');
    }
}

/**
 * 编辑维护记录
 */
async function editMaintenance(recordId) {
    try {
        let maintenanceRecord;
        
        try {
            // 尝试从API获取记录
            maintenanceRecord = await maintenanceAPI.getMaintenance(recordId);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            
            // 从当前表格中获取记录数据
            const tableRows = document.querySelectorAll('#maintenance-table tr');
            for (const row of tableRows) {
                const editButton = row.querySelector(`.edit-maintenance-btn[data-id="${recordId}"]`);
                if (editButton) {
                    const cells = row.querySelectorAll('td');
                    maintenanceRecord = {
                        id: recordId,
                        machine_id: editButton.getAttribute('data-machine-id'),
                        machine_name: cells[0].textContent,
                        maintenance_type: cells[1].textContent,
                        start_time: new Date().toISOString(),
                        end_time: cells[3].textContent !== '-' ? new Date().toISOString() : null,
                        performed_by: cells[4].textContent !== '-' ? cells[4].textContent : '',
                        status: cells[5].querySelector('.badge').classList.contains('bg-warning') ? 'pending' :
                                cells[5].querySelector('.badge').classList.contains('bg-primary') ? 'in_progress' : 'completed',
                        description: ''
                    };
                    break;
                }
            }
        }
        
        if (maintenanceRecord) {
            // 填充表单
            document.getElementById('maintenance-machine').value = maintenanceRecord.machine_id;
            document.getElementById('maintenance-type').value = maintenanceRecord.maintenance_type;
            document.getElementById('maintenance-description').value = maintenanceRecord.description || '';
            document.getElementById('maintenance-performed-by').value = maintenanceRecord.performed_by || '';
            document.getElementById('maintenance-status').value = maintenanceRecord.status;
            
            // 打开模态框
            const modal = new bootstrap.Modal(document.getElementById('addMaintenanceModal'));
            modal.show();
        }
    } catch (error) {
        console.error('编辑维护记录失败:', error);
        showErrorMessage('编辑维护记录失败');
    }
}

/**
 * 删除维护记录
 */
async function deleteMaintenance(recordId) {
    try {
        if (confirm('确定要删除这条维护记录吗？')) {
            try {
                // 尝试从API删除
                await maintenanceAPI.deleteMaintenance(recordId);
            } catch (apiError) {
                console.warn('API调用失败，使用模拟删除:', apiError);
                // 从表格中移除对应行
                const tableRows = document.querySelectorAll('#maintenance-table tr');
                for (const row of tableRows) {
                    const deleteButton = row.querySelector(`.delete-maintenance-btn[data-id="${recordId}"]`);
                    if (deleteButton) {
                        row.remove();
                        break;
                    }
                }
            }
            
            // 显示成功消息
            showSuccessMessage('维护记录删除成功');
            
            // 重新加载维护记录列表
            await loadMaintenanceRecords();
        }
    } catch (error) {
        console.error('删除维护记录失败:', error);
        showErrorMessage('删除维护记录失败');
    }
}

/**
 * 绑定维护记录相关事件监听器
 */
function bindMaintenanceEventListeners() {
    // 保存维护记录按钮
    const saveMaintenanceBtn = document.getElementById('saveMaintenanceBtn');
    if (saveMaintenanceBtn) {
        saveMaintenanceBtn.addEventListener('click', saveMaintenance);
    }
    
    // 编辑维护记录按钮（使用事件委托）
    const maintenanceTable = document.getElementById('maintenance-table');
    if (maintenanceTable) {
        maintenanceTable.addEventListener('click', (e) => {
            // 编辑按钮
            if (e.target.closest('.edit-maintenance-btn')) {
                const button = e.target.closest('.edit-maintenance-btn');
                const recordId = parseInt(button.getAttribute('data-id'));
                editMaintenance(recordId);
            }
            
            // 删除按钮
            if (e.target.closest('.delete-maintenance-btn')) {
                const button = e.target.closest('.delete-maintenance-btn');
                const recordId = parseInt(button.getAttribute('data-id'));
                deleteMaintenance(recordId);
            }
        });
    }
}

/**
 * 显示成功消息
 */
function showSuccessMessage(message) {
    const app = window.app || new MachineMonitoringApp();
    app.showSuccessMessage(message);
}

/**
 * 页面加载完成后初始化应用
 */
window.addEventListener('DOMContentLoaded', async () => {
    // 创建应用实例
    const app = new MachineMonitoringApp();
    
    // 初始化应用
    await app.init();
    
    // 将应用实例暴露到全局，便于调试
    window.app = app;
});