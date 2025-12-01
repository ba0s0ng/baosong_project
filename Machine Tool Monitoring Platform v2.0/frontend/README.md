# 工业互联网机床监测平台 - 前端项目

## 项目概述

本目录包含工业互联网机床监测平台的前端代码，采用纯静态网页设计，负责用户界面展示和与后端API的交互。

## 技术栈

- **核心技术**：HTML5, CSS3, JavaScript (ES6+)
- **UI框架**：Bootstrap 5
- **图标库**：Font Awesome
- **图表展示**：Chart.js
- **通信方式**：AJAX/fetch API

## 目录结构

```
frontend/
├── css/              # CSS样式文件
│   ├── bootstrap.min.css    # Bootstrap核心样式
│   ├── style.css            # 自定义样式
│   └── responsive.css       # 响应式设计样式
├── js/               # JavaScript脚本
│   ├── app.js               # 主应用脚本
│   ├── api.js               # API请求封装
│   ├── analytics.js         # 数据分析模块
│   ├── alarms.js            # 报警管理模块
│   ├── machines.js          # 设备管理模块
│   ├── bootstrap.bundle.min.js  # Bootstrap核心脚本
│   └── chart.js             # 图表库
├── img/              # 图片资源
│   ├── logo.png             # 系统logo
│   ├── icons/               # 功能图标
│   └── backgrounds/         # 背景图片
├── index.html        # 主页面
└── README.md         # 前端项目说明
```

## 第三方资源

### 样式资源
- **Bootstrap 5**：用于构建响应式、移动优先的界面设计
- **Font Awesome**：提供丰富的图标资源

### JavaScript库
- **Chart.js**：用于数据可视化和图表生成
- **Axios**（可选）：用于简化HTTP请求
- **jQuery**（可选）：提供DOM操作和事件处理功能

## 部署说明

### 开发环境
1. 确保后端服务正在运行（端口8000）
2. 启动前端HTTP服务器
   ```bash
   python -m http.server 8080
   ```
3. 在浏览器中访问 http://localhost:8080

### 生产环境
1. 确保后端服务部署到生产服务器
2. 将前端文件部署到Web服务器（如Nginx、Apache等）
3. 修改前端配置文件中的API地址指向生产后端服务

## 配置说明

前端项目的主要配置位于 `js/api.js` 文件中，包括：
- API基础URL
- 请求超时设置
- 错误处理配置

## 浏览器兼容性

- Chrome 90+（推荐）
- Firefox 88+
- Microsoft Edge 90+
- Safari 14+

## 开发注意事项

1. 修改前端API调用时，请确保与后端API接口定义保持一致
2. 添加新功能时，建议遵循现有的代码组织结构和命名规范
3. 所有JavaScript代码应确保在严格模式下运行
4. 样式调整应优先考虑响应式设计原则，确保在不同设备上都有良好的显示效果