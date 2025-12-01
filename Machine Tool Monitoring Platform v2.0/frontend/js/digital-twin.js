// 移除import语句，直接使用window上的API对象
// import { machinesAPI, machineDataAPI } from './api.js';

// Three.js 相关全局变量
let scene, camera, renderer;
let selectedMachine = null;
let machineDataInterval = null;

/**
 * 初始化数字孪生模块
 */
async function initDigitalTwin() {
    try {
        // 初始化Three.js场景
        initThreeJs();
        
        // 加载设备列表
        await loadMachinesForTwinSelect();
        
        // 绑定事件监听器
        bindEventListeners();
    } catch (error) {
        console.error('初始化数字孪生模块失败:', error);
        showErrorMessage('数字孪生模块初始化失败');
    }
}

/**
 * 初始化Three.js场景
 */
function initThreeJs() {
    // 获取容器元素
    const container = document.getElementById('three-container');
    
    // 创建场景
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f9fa);
    
    // 创建相机
    camera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(10, 10, 10);
    camera.lookAt(0, 0, 0);
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    
    // 移除轨道控制器代码
    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    // 添加方向光
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);
    
    // 添加网格辅助线
    const gridHelper = new THREE.GridHelper(20, 20, 0xcccccc, 0xcccccc);
    scene.add(gridHelper);
    
    // 开始动画循环
    animate();
    
    // 添加窗口大小变化监听
    window.addEventListener('resize', onWindowResize);
}

/**
 * 动画循环
 */
function animate() {
    requestAnimationFrame(animate);
    
    // 移除控制器更新
    // if (controls) {
    //     controls.update();
    // }
    
    // 渲染场景
    if (renderer && scene && camera) {
        renderer.render(scene, camera);
    }
}

/**
 * 窗口大小变化处理
 */
function onWindowResize() {
    const container = document.getElementById('three-container');
    
    if (camera && renderer && container) {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
}

/**
 * 加载设备列表到选择器
 */
async function loadMachinesForTwinSelect() {
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
                    type: '数控车床'
                },
                {
                    id: 3,
                    name: '铣床1',
                    type: '铣床'
                },
                {
                    id: 4,
                    name: '机器人1',
                    type: '工业机器人'
                },
                {
                    id: 5,
                    name: '加工中心2',
                    type: '加工中心'
                },
                {
                    id: 6,
                    name: '激光切割机',
                    type: '激光切割'
                }
            ];
        }
        
        const selectElement = document.getElementById('twin-machine-select');
        
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
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 设备选择器变化
    document.getElementById('twin-machine-select').addEventListener('change', async function() {
        const machineId = parseInt(this.value);
        if (machineId) {
            await loadMachineModel(machineId);
        } else {
            // 清空场景
            clearMachineModel();
            clearMachineDetails();
        }
    });
}

/**
 * 加载设备模型
 */
async function loadMachineModel(machineId) {
    try {
        // 停止之前的数据更新
        if (machineDataInterval) {
            clearInterval(machineDataInterval);
        }
        
        // 加载设备信息
        let machine;
        try {
            machine = await machinesAPI.getMachine(machineId);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟设备数据:', apiError);
            // 提供模拟设备信息
            machine = {
                id: machineId,
                name: `模拟设备${machineId}`,
                type: ['加工中心', '数控车床', '铣床', '工业机器人'][machineId % 4],
                status: '运行中',
                location: '车间A',
                ip: '192.168.1.100'
            };
        }
        
        selectedMachine = machine;
        
        // 清空场景
        clearMachineModel();
        
        // 加载设备详情
        updateMachineDetails(machine);
        
        // 根据设备类型创建不同的3D模型
        createMachineModel(machine.type);
        
        // 开始更新设备数据
        updateMachineData();
        
        // 设置定时更新
        machineDataInterval = setInterval(updateMachineData, 5000); // 每5秒更新一次
    } catch (error) {
        console.error('加载设备模型失败:', error);
        showErrorMessage('加载设备模型失败');
    }
}

/**
 * 创建设备3D模型
 */
function createMachineModel(machineType) {
    // 创建一个基础机器模型
    // 根据不同的设备类型创建不同的几何形状
    let geometry;
    
    switch (machineType.toLowerCase()) {
        case '加工中心':
            geometry = createMachiningCenterModel();
            break;
        case '数控车床':
            geometry = createLatheModel();
            break;
        case '铣床':
            geometry = createMillingMachineModel();
            break;
        case '工业机器人':
            geometry = createRobotModel();
            break;
        default:
            geometry = createDefaultMachineModel();
    }
    
    // 将模型添加到场景
    if (geometry) {
        geometry.forEach(mesh => {
            scene.add(mesh);
        });
    }
}

/**
 * 创建默认设备模型
 */
function createDefaultMachineModel() {
    const meshes = [];
    
    // 机器主体
    const bodyGeometry = new THREE.BoxGeometry(4, 2, 6);
    const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.set(0, 1, 0);
    meshes.push(body);
    
    // 控制面板
    const panelGeometry = new THREE.BoxGeometry(0.2, 1.5, 3);
    const panelMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.9, roughness: 0.1 });
    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
    panel.position.set(2.1, 1, 0);
    meshes.push(panel);
    
    // 控制面板屏幕
    const screenGeometry = new THREE.BoxGeometry(0.1, 1, 2);
    const screenMaterial = new THREE.MeshStandardMaterial({ color: 0x2ecc71 });
    const screen = new THREE.Mesh(screenGeometry, screenMaterial);
    screen.position.set(2.15, 1, 0);
    meshes.push(screen);
    
    // 工作区域
    const workGeometry = new THREE.BoxGeometry(3, 0.5, 4);
    const workMaterial = new THREE.MeshStandardMaterial({ color: 0x95a5a6 });
    const work = new THREE.Mesh(workGeometry, workMaterial);
    work.position.set(0, 2.25, 0);
    meshes.push(work);
    
    return meshes;
}

/**
 * 创建加工中心模型
 */
function createMachiningCenterModel() {
    const meshes = [];
    
    // 底座
    const baseGeometry = new THREE.BoxGeometry(6, 1, 8);
    const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x34495e, metalness: 0.8, roughness: 0.2 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.set(0, 0.5, 0);
    meshes.push(base);
    
    // 立柱
    const columnGeometry = new THREE.BoxGeometry(2, 4, 6);
    const columnMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.8, roughness: 0.2 });
    const column = new THREE.Mesh(columnGeometry, columnMaterial);
    column.position.set(1, 3, 0);
    meshes.push(column);
    
    // 主轴箱
    const headGeometry = new THREE.BoxGeometry(1, 1.5, 2);
    const headMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.set(1, 4.25, 0);
    meshes.push(head);
    
    // 工作台
    const tableGeometry = new THREE.BoxGeometry(5, 0.5, 6);
    const tableMaterial = new THREE.MeshStandardMaterial({ color: 0x7f8c8d });
    const table = new THREE.Mesh(tableGeometry, tableMaterial);
    table.position.set(-1, 1, 0);
    meshes.push(table);
    
    // 控制面板
    const panelGeometry = new THREE.BoxGeometry(0.1, 1.5, 3);
    const panelMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.9, roughness: 0.1 });
    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
    panel.position.set(-3.05, 1.75, 0);
    meshes.push(panel);
    
    // 控制面板屏幕
    const screenGeometry = new THREE.BoxGeometry(0.01, 1, 2);
    const screenMaterial = new THREE.MeshStandardMaterial({ color: 0x2ecc71 });
    const screen = new THREE.Mesh(screenGeometry, screenMaterial);
    screen.position.set(-3.1, 1.75, 0);
    meshes.push(screen);
    
    return meshes;
}

/**
 * 创建车床模型
 */
function createLatheModel() {
    const meshes = [];
    
    // 床身
    const bedGeometry = new THREE.BoxGeometry(1, 2, 8);
    const bedMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.8, roughness: 0.2 });
    const bed = new THREE.Mesh(bedGeometry, bedMaterial);
    bed.position.set(0, 1, 0);
    meshes.push(bed);
    
    // 主轴箱
    const headstockGeometry = new THREE.BoxGeometry(2, 2, 2);
    const headstockMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const headstock = new THREE.Mesh(headstockGeometry, headstockMaterial);
    headstock.position.set(0, 2, -3);
    meshes.push(headstock);
    
    // 尾座
    const tailstockGeometry = new THREE.BoxGeometry(1.5, 1.5, 2);
    const tailstockMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const tailstock = new THREE.Mesh(tailstockGeometry, tailstockMaterial);
    tailstock.position.set(0, 1.75, 3);
    meshes.push(tailstock);
    
    // 刀架
    const carriageGeometry = new THREE.BoxGeometry(1.5, 0.5, 1);
    const carriageMaterial = new THREE.MeshStandardMaterial({ color: 0xe74c3c });
    const carriage = new THREE.Mesh(carriageGeometry, carriageMaterial);
    carriage.position.set(0, 2, 0);
    meshes.push(carriage);
    
    // 控制面板
    const panelGeometry = new THREE.BoxGeometry(0.1, 1, 1.5);
    const panelMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.9, roughness: 0.1 });
    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
    panel.position.set(-1.55, 2, -3);
    meshes.push(panel);
    
    // 控制面板屏幕
    const screenGeometry = new THREE.BoxGeometry(0.01, 0.8, 1.2);
    const screenMaterial = new THREE.MeshStandardMaterial({ color: 0x2ecc71 });
    const screen = new THREE.Mesh(screenGeometry, screenMaterial);
    screen.position.set(-1.6, 2, -3);
    meshes.push(screen);
    
    return meshes;
}

/**
 * 创建铣床模型
 */
function createMillingMachineModel() {
    const meshes = [];
    
    // 底座
    const baseGeometry = new THREE.BoxGeometry(6, 1, 6);
    const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x34495e, metalness: 0.8, roughness: 0.2 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.set(0, 0.5, 0);
    meshes.push(base);
    
    // 工作台
    const tableGeometry = new THREE.BoxGeometry(5, 0.5, 5);
    const tableMaterial = new THREE.MeshStandardMaterial({ color: 0x7f8c8d });
    const table = new THREE.Mesh(tableGeometry, tableMaterial);
    table.position.set(0, 1.25, 0);
    meshes.push(table);
    
    // 立柱
    const columnGeometry = new THREE.BoxGeometry(1, 5, 4);
    const columnMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.8, roughness: 0.2 });
    const column = new THREE.Mesh(columnGeometry, columnMaterial);
    column.position.set(2, 3.5, 0);
    meshes.push(column);
    
    // 主轴箱
    const headGeometry = new THREE.BoxGeometry(2, 1, 2);
    const headMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.set(1, 5.5, 0);
    meshes.push(head);
    
    // 控制面板
    const panelGeometry = new THREE.BoxGeometry(0.1, 1.5, 2);
    const panelMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.9, roughness: 0.1 });
    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
    panel.position.set(-3.05, 1.75, 0);
    meshes.push(panel);
    
    // 控制面板屏幕
    const screenGeometry = new THREE.BoxGeometry(0.01, 1, 1.5);
    const screenMaterial = new THREE.MeshStandardMaterial({ color: 0x2ecc71 });
    const screen = new THREE.Mesh(screenGeometry, screenMaterial);
    screen.position.set(-3.1, 1.75, 0);
    meshes.push(screen);
    
    return meshes;
}

/**
 * 创建机器人模型
 */
function createRobotModel() {
    const meshes = [];
    
    // 底座
    const baseGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.5, 32);
    const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.8, roughness: 0.2 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.set(0, 0.25, 0);
    meshes.push(base);
    
    // 腰部
    const waistGeometry = new THREE.CylinderGeometry(1, 1, 1, 32);
    const waistMaterial = new THREE.MeshStandardMaterial({ color: 0xe74c3c });
    const waist = new THREE.Mesh(waistGeometry, waistMaterial);
    waist.position.set(0, 1.25, 0);
    meshes.push(waist);
    
    // 大臂
    const upperArmGeometry = new THREE.BoxGeometry(0.5, 3, 0.5);
    const upperArmMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const upperArm = new THREE.Mesh(upperArmGeometry, upperArmMaterial);
    upperArm.position.set(0, 3.75, 1.25);
    upperArm.rotation.x = Math.PI / 4;
    meshes.push(upperArm);
    
    // 小臂
    const lowerArmGeometry = new THREE.BoxGeometry(0.5, 2, 0.5);
    const lowerArmMaterial = new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.7, roughness: 0.3 });
    const lowerArm = new THREE.Mesh(lowerArmGeometry, lowerArmMaterial);
    lowerArm.position.set(0, 4.25, 3.25);
    lowerArm.rotation.x = -Math.PI / 4;
    meshes.push(lowerArm);
    
    // 手腕
    const wristGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.5, 32);
    const wristMaterial = new THREE.MeshStandardMaterial({ color: 0xe74c3c });
    const wrist = new THREE.Mesh(wristGeometry, wristMaterial);
    wrist.position.set(0, 3.75, 4.75);
    meshes.push(wrist);
    
    return meshes;
}

/**
 * 清空设备模型
 */
function clearMachineModel() {
    // 移除所有非基础元素
    const toRemove = [];
    scene.traverse(child => {
        // 保留环境光、方向光和网格辅助线
        if (child.type !== 'AmbientLight' && child.type !== 'DirectionalLight' && child.type !== 'GridHelper') {
            toRemove.push(child);
        }
    });
    
    // 移除选中的元素
    toRemove.forEach(child => {
        scene.remove(child);
        // 释放内存
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
            if (Array.isArray(child.material)) {
                child.material.forEach(m => m.dispose());
            } else {
                child.material.dispose();
            }
        }
    });
}

/**
 * 更新设备详情
 */
function updateMachineDetails(machine) {
    const detailsContainer = document.getElementById('machine-details');
    
    const html = `
        <h4>${machine.name}</h4>
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
        <div id="real-time-data">
            <!-- 实时数据将在这里更新 -->
        </div>
    `;
    
    detailsContainer.innerHTML = html;
}

/**
 * 清空设备详情
 */
function clearMachineDetails() {
    const detailsContainer = document.getElementById('machine-details');
    detailsContainer.innerHTML = '<p class="text-center text-muted">请选择设备查看详情</p>';
}

/**
 * 更新设备实时数据
 */
async function updateMachineData() {
    if (!selectedMachine) return;
    
    try {
        let latestData;
        try {
            // 尝试从API获取最新数据
            latestData = await machinesAPI.getMachineLatestData(selectedMachine.id);
        } catch (apiError) {
            console.warn('API调用失败，使用模拟数据:', apiError);
            // 提供模拟实时数据，每个参数在合理范围内随机变化
            latestData = {
                temperature: Math.round((60 + Math.random() * 20) * 10) / 10, // 60-80°C
                vibration: Math.round((0.5 + Math.random() * 2.5) * 10) / 10, // 0.5-3.0 mm/s
                current: Math.round((5 + Math.random() * 15) * 10) / 10, // 5-20 A
                rotation_speed: Math.round(2000 + Math.random() * 3000), // 2000-5000 RPM
                pressure: Math.round((0.5 + Math.random() * 3.5) * 10) / 10, // 0.5-4.0 MPa
                power: Math.round((10 + Math.random() * 40) * 10) / 10 // 10-50 kW
            };
        }
        
        const dataContainer = document.getElementById('real-time-data');
        
        let html = '<h5 class="mt-3 mb-2">实时参数</h5>';
        
        // 更新各项参数
        if (latestData) {
            const parameters = [
                { key: 'temperature', label: '温度', unit: '°C' },
                { key: 'vibration', label: '振动', unit: 'mm/s' },
                { key: 'current', label: '电流', unit: 'A' },
                { key: 'rotation_speed', label: '转速', unit: 'RPM' },
                { key: 'pressure', label: '压力', unit: 'MPa' },
                { key: 'power', label: '功率', unit: 'kW' }
            ];
            
            parameters.forEach(param => {
                if (latestData[param.key] !== undefined) {
                    const value = latestData[param.key];
                    const status = getParameterStatus(param.key, value);
                    
                    html += `
                        <div class="detail-card">
                            <div class="detail-label">${param.label}</div>
                            <div class="detail-value ${status.class}">
                                ${value} ${param.unit}
                            </div>
                        </div>
                    `;
                }
            });
        }
        
        dataContainer.innerHTML = html;
    } catch (error) {
        console.error('更新设备数据失败:', error);
    }
}

/**
 * 获取参数状态
 */
function getParameterStatus(parameter, value) {
    // 这里可以根据实际情况设置不同参数的阈值
    const thresholds = {
        temperature: { normal: 70, warning: 80 },
        vibration: { normal: 0.3, warning: 0.5 },
        current: { normal: 15, warning: 20 },
        rotation_speed: { normal: 1500, warning: 1800 },
        pressure: { normal: 8, warning: 10 },
        power: { normal: 20, warning: 25 }
    };
    
    const threshold = thresholds[parameter];
    if (!threshold) {
        return { class: '', text: '正常' };
    }
    
    if (value > threshold.warning) {
        return { class: 'text-danger', text: '异常' };
    } else if (value > threshold.normal) {
        return { class: 'text-warning', text: '警告' };
    } else {
        return { class: 'text-success', text: '正常' };
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
    
    // 添加到数字孪生区域
    const digitalTwinSection = document.getElementById('digital-twin');
    const cardHeader = digitalTwinSection.querySelector('.card-header');
    cardHeader.after(errorElement);
    
    // 3秒后自动关闭
    setTimeout(() => {
        errorElement.remove();
    }, 3000);
}

// 导出模块
// 模块初始化完成