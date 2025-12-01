/**
 * 工业互联网机床状态监测平台 - Three.js 3D场景模块
 */

class ThreeSceneManager {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.container = null;
        
        // 机床模型
        this.machines = new Map();
        this.selectedMachine = null;
        
        // 动画
        this.animationId = null;
        this.clock = new THREE.Clock();
        
        // 灯光
        this.lights = [];
        
        // 材质
        this.materials = new Map();
        
        this.initializeScene();
    }
    
    /**
     * 初始化3D场景
     */
    initializeScene() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupScene();
            });
        } else {
            this.setupScene();
        }
    }
    
    /**
     * 设置3D场景
     */
    setupScene() {
        this.container = document.getElementById('three-js-container');
        if (!this.container) {
            console.warn('Three.js容器未找到');
            return;
        }
        
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        
        // 创建相机
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(10, 10, 10);
        this.camera.lookAt(0, 0, 0);
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // 添加轨道控制器
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
        }
        
        // 设置灯光
        this.setupLights();
        
        // 创建地面
        this.createGround();
        
        // 创建机床模型
        this.createMachineModels();
        
        // 开始渲染循环
        this.startRenderLoop();
        
        // 添加事件监听器
        this.addEventListeners();
        
        console.log('Three.js场景初始化完成');
    }
    
    /**
     * 设置灯光
     */
    setupLights() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        this.lights.push(ambientLight);
        
        // 方向光
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        this.scene.add(directionalLight);
        this.lights.push(directionalLight);
        
        // 点光源
        const pointLight = new THREE.PointLight(0xffffff, 0.5, 30);
        pointLight.position.set(-10, 10, -10);
        this.scene.add(pointLight);
        this.lights.push(pointLight);
    }
    
    /**
     * 创建地面
     */
    createGround() {
        const groundGeometry = new THREE.PlaneGeometry(50, 50);
        const groundMaterial = new THREE.MeshLambertMaterial({ 
            color: 0xcccccc,
            transparent: true,
            opacity: 0.8
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
        
        // 添加网格
        const gridHelper = new THREE.GridHelper(50, 50, 0x888888, 0xaaaaaa);
        this.scene.add(gridHelper);
    }
    
    /**
     * 创建机床模型
     */
    createMachineModels() {
        // 创建默认机床模型
        const machines = [
            { id: 'CNC001', type: 'CNC_LATHE', position: [-8, 0, -8], color: 0x4a90e2 },
            { id: 'MILL001', type: 'MILLING_MACHINE', position: [0, 0, -8], color: 0x7ed321 },
            { id: 'DRILL001', type: 'DRILLING_MACHINE', position: [8, 0, -8], color: 0xf5a623 }
        ];
        
        machines.forEach(machineConfig => {
            this.createMachineModel(machineConfig);
        });
    }
    
    /**
     * 创建单个机床模型
     */
    createMachineModel(config) {
        const group = new THREE.Group();
        group.userData = {
            id: config.id,
            type: config.type,
            status: 'OFFLINE',
            data: {}
        };
        
        // 机床基座
        const baseGeometry = new THREE.BoxGeometry(3, 0.5, 2);
        const baseMaterial = new THREE.MeshPhongMaterial({ color: 0x666666 });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.25;
        base.castShadow = true;
        base.receiveShadow = true;
        group.add(base);
        
        // 机床主体
        const bodyGeometry = new THREE.BoxGeometry(2, 2, 1.5);
        const bodyMaterial = new THREE.MeshPhongMaterial({ color: config.color });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 1.5;
        body.castShadow = true;
        body.receiveShadow = true;
        group.add(body);
        
        // 主轴（根据机床类型创建不同形状）
        let spindleGeometry;
        switch (config.type) {
            case 'CNC_LATHE':
                spindleGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1.5);
                break;
            case 'MILLING_MACHINE':
                spindleGeometry = new THREE.CylinderGeometry(0.15, 0.15, 1);
                break;
            case 'DRILLING_MACHINE':
                spindleGeometry = new THREE.CylinderGeometry(0.08, 0.08, 1.2);
                break;
            default:
                spindleGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1);
        }
        
        const spindleMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
        const spindle = new THREE.Mesh(spindleGeometry, spindleMaterial);
        spindle.position.set(0, 2.5, 0);
        spindle.castShadow = true;
        spindle.name = 'spindle';
        group.add(spindle);
        
        // 状态指示器
        const indicatorGeometry = new THREE.SphereGeometry(0.2);
        const indicatorMaterial = new THREE.MeshBasicMaterial({ 
            color: 0x666666,
            transparent: true,
            opacity: 0.8
        });
        const indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial);
        indicator.position.set(1.2, 2, 0);
        indicator.name = 'statusIndicator';
        group.add(indicator);
        
        // 机床标签
        this.createMachineLabel(group, config.id);
        
        // 设置位置
        group.position.set(...config.position);
        
        // 添加到场景
        this.scene.add(group);
        this.machines.set(config.id, group);
        
        // 添加点击事件
        this.addMachineClickHandler(group);
    }
    
    /**
     * 创建机床标签
     */
    createMachineLabel(group, machineId) {
        // 创建文本纹理
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        
        context.fillStyle = 'rgba(255, 255, 255, 0.9)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        context.fillStyle = '#333333';
        context.font = 'bold 24px Arial';
        context.textAlign = 'center';
        context.fillText(machineId, canvas.width / 2, canvas.height / 2 + 8);
        
        const texture = new THREE.CanvasTexture(canvas);
        const labelMaterial = new THREE.MeshBasicMaterial({ 
            map: texture,
            transparent: true
        });
        
        const labelGeometry = new THREE.PlaneGeometry(2, 0.5);
        const label = new THREE.Mesh(labelGeometry, labelMaterial);
        label.position.set(0, 3.5, 0);
        label.name = 'label';
        
        group.add(label);
    }
    
    /**
     * 添加机床点击事件处理器
     */
    addMachineClickHandler(machineGroup) {
        // 这里可以添加鼠标点击检测逻辑
        // 由于Three.js的事件处理比较复杂，这里简化处理
        machineGroup.userData.onClick = () => {
            this.selectMachine(machineGroup.userData.id);
        };
    }
    
    /**
     * 选择机床
     */
    selectMachine(machineId) {
        // 取消之前的选择
        if (this.selectedMachine) {
            this.highlightMachine(this.selectedMachine, false);
        }
        
        // 选择新机床
        const machine = this.machines.get(machineId);
        if (machine) {
            this.selectedMachine = machineId;
            this.highlightMachine(machineId, true);
            
            // 更新数字孪生控制面板
            this.updateTwinControlPanel(machineId);
            
            console.log('选择机床:', machineId);
        }
    }
    
    /**
     * 高亮显示机床
     */
    highlightMachine(machineId, highlight) {
        const machine = this.machines.get(machineId);
        if (!machine) return;
        
        machine.children.forEach(child => {
            if (child.material && child.name !== 'label' && child.name !== 'statusIndicator') {
                if (highlight) {
                    child.material.emissive.setHex(0x333333);
                } else {
                    child.material.emissive.setHex(0x000000);
                }
            }
        });
    }
    
    /**
     * 更新机床状态
     */
    updateMachineStatus(machineId, status, data = {}) {
        const machine = this.machines.get(machineId);
        if (!machine) return;
        
        machine.userData.status = status;
        machine.userData.data = { ...machine.userData.data, ...data };
        
        // 更新状态指示器颜色
        const indicator = machine.getObjectByName('statusIndicator');
        if (indicator) {
            let color;
            switch (status) {
                case 'RUNNING':
                    color = 0x00ff00; // 绿色
                    break;
                case 'IDLE':
                    color = 0xffff00; // 黄色
                    break;
                case 'ERROR':
                    color = 0xff0000; // 红色
                    break;
                case 'MAINTENANCE':
                    color = 0x00ffff; // 青色
                    break;
                default:
                    color = 0x666666; // 灰色
            }
            indicator.material.color.setHex(color);
        }
        
        // 更新主轴旋转
        const spindle = machine.getObjectByName('spindle');
        if (spindle && status === 'RUNNING' && data.speed) {
            spindle.userData.rotationSpeed = (data.speed || 0) * 0.001; // 转换为合适的旋转速度
        } else if (spindle) {
            spindle.userData.rotationSpeed = 0;
        }
        
        console.log(`更新机床状态: ${machineId} -> ${status}`);
    }
    
    /**
     * 更新数字孪生控制面板
     */
    updateTwinControlPanel(machineId) {
        const machine = this.machines.get(machineId);
        if (!machine) return;
        
        // 更新机床选择下拉框
        const machineSelect = document.getElementById('twin-machine-select');
        if (machineSelect) {
            machineSelect.value = machineId;
        }
        
        // 更新控制面板状态
        const runningSwitch = document.getElementById('twin-running-switch');
        const speedSlider = document.getElementById('twin-speed-slider');
        const loadSlider = document.getElementById('twin-load-slider');
        const speedValue = document.getElementById('twin-speed-value');
        const loadValue = document.getElementById('twin-load-value');
        
        if (runningSwitch) {
            runningSwitch.checked = machine.userData.status === 'RUNNING';
        }
        
        if (speedSlider && speedValue) {
            const speed = machine.userData.data.speed || 0;
            speedSlider.value = speed;
            speedValue.textContent = Math.round(speed);
        }
        
        if (loadSlider && loadValue) {
            const load = machine.userData.data.load_factor || 0;
            loadSlider.value = load * 100;
            loadValue.textContent = Math.round(load * 100);
        }
        
        // 更新详细信息
        this.updateTwinDetails(machineId);
    }
    
    /**
     * 更新数字孪生详细信息
     */
    updateTwinDetails(machineId) {
        const machine = this.machines.get(machineId);
        if (!machine) return;
        
        const detailsContainer = document.getElementById('twin-details');
        if (!detailsContainer) return;
        
        const data = machine.userData.data;
        const status = machine.userData.status;
        
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>基本信息</h6>
                    <p><strong>机床ID:</strong> ${machineId}</p>
                    <p><strong>类型:</strong> ${machine.userData.type}</p>
                    <p><strong>状态:</strong> <span class="status-badge ${status.toLowerCase()}">${status}</span></p>
                </div>
                <div class="col-md-6">
                    <h6>实时数据</h6>
                    <p><strong>温度:</strong> ${(data.temperature || 0).toFixed(1)}°C</p>
                    <p><strong>振动:</strong> ${(data.vibration || 0).toFixed(2)}mm/s</p>
                    <p><strong>转速:</strong> ${(data.speed || 0).toFixed(0)}rpm</p>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6>物理状态</h6>
                    <div class="row">
                        <div class="col-4">
                            <small class="text-muted">位置 X</small>
                            <div>${machine.position.x.toFixed(1)}</div>
                        </div>
                        <div class="col-4">
                            <small class="text-muted">位置 Y</small>
                            <div>${machine.position.y.toFixed(1)}</div>
                        </div>
                        <div class="col-4">
                            <small class="text-muted">位置 Z</small>
                            <div>${machine.position.z.toFixed(1)}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        detailsContainer.innerHTML = html;
    }
    
    /**
     * 开始渲染循环
     */
    startRenderLoop() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            
            const delta = this.clock.getDelta();
            
            // 更新控制器
            if (this.controls) {
                this.controls.update();
            }
            
            // 更新机床动画
            this.updateMachineAnimations(delta);
            
            // 渲染场景
            this.renderer.render(this.scene, this.camera);
        };
        
        animate();
    }
    
    /**
     * 更新机床动画
     */
    updateMachineAnimations(delta) {
        this.machines.forEach(machine => {
            const spindle = machine.getObjectByName('spindle');
            if (spindle && spindle.userData.rotationSpeed) {
                spindle.rotation.y += spindle.userData.rotationSpeed * delta * 60;
            }
            
            // 标签始终面向相机
            const label = machine.getObjectByName('label');
            if (label) {
                label.lookAt(this.camera.position);
            }
        });
    }
    
    /**
     * 添加事件监听器
     */
    addEventListeners() {
        // 窗口大小改变
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
        
        // 鼠标点击
        this.renderer.domElement.addEventListener('click', (event) => {
            this.onMouseClick(event);
        });
    }
    
    /**
     * 窗口大小改变处理
     */
    onWindowResize() {
        if (!this.container || !this.camera || !this.renderer) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    /**
     * 鼠标点击处理
     */
    onMouseClick(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        const mouse = new THREE.Vector2();
        
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(mouse, this.camera);
        
        // 检测与机床的交互
        const machineObjects = [];
        this.machines.forEach(machine => {
            machineObjects.push(...machine.children);
        });
        
        const intersects = raycaster.intersectObjects(machineObjects);
        
        if (intersects.length > 0) {
            const clickedObject = intersects[0].object;
            const machineGroup = clickedObject.parent;
            
            if (machineGroup && machineGroup.userData.id) {
                this.selectMachine(machineGroup.userData.id);
            }
        }
    }
    
    /**
     * 销毁场景
     */
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.container && this.renderer) {
            this.container.removeChild(this.renderer.domElement);
        }
        
        // 清理资源
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.machines.clear();
        
        console.log('Three.js场景已销毁');
    }
    
    /**
     * 获取机床列表
     */
    getMachineList() {
        const machines = [];
        this.machines.forEach((machine, id) => {
            machines.push({
                id: id,
                type: machine.userData.type,
                status: machine.userData.status,
                data: machine.userData.data
            });
        });
        return machines;
    }
    
    /**
     * 设置相机位置
     */
    setCameraPosition(x, y, z) {
        if (this.camera) {
            this.camera.position.set(x, y, z);
        }
    }
    
    /**
     * 重置相机视角
     */
    resetCamera() {
        if (this.camera && this.controls) {
            this.camera.position.set(10, 10, 10);
            this.camera.lookAt(0, 0, 0);
            this.controls.reset();
        }
    }
}

// 创建全局Three.js场景管理器实例
window.threeSceneManager = new ThreeSceneManager();

// 页面卸载前销毁场景
window.addEventListener('beforeunload', () => {
    if (window.threeSceneManager) {
        window.threeSceneManager.destroy();
    }
});
