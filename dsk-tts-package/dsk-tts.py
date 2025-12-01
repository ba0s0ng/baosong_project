"""
智能语音问答系统 - 本地AI聊天客户端

功能概述：
1. 基于PyQt5的图形用户界面，提供美观的聊天体验
2. 集成Ollama本地API，支持与DeepSeek等本地模型交互
3. 支持文本对话功能，带有用户和AI的消息气泡显示
4. 可选文本转语音(TTS)功能，支持语音播报AI回复
5. 自适应界面布局，消息气泡根据内容自动调整大小
6. 错误处理和状态提示机制

主要特点：
- 完全本地运行，保护隐私
- 响应式设计，适应不同窗口大小
- 跨平台支持(Windows/macOS/Linux)
- 可配置的模型选择和API设置
- 详细的错误反馈和日志

依赖库：
- PyQt5: 图形界面
- requests: HTTP请求
- pyttsx3: 文本转语音(可选)

使用方法：
1. 确保Ollama服务已启动并运行在localhost:11434
2. 安装必要依赖: pip install PyQt5 requests pyttsx3
3. 运行本脚本启动聊天客户端

作者: DeepSeek
版本: 1.0
"""

import sys
import json
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QScrollArea, 
                            QLabel, QFrame, QSizePolicy, QCheckBox, QSlider)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer, QRect
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtGui import QFont, QIcon, QFontMetrics

# 延迟导入以避免依赖问题
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("错误: requests库未安装，请运行: pip install requests")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("警告: pyttsx3未安装，语音播报功能将被禁用")

try:
    import speech_recognition as sr
    SPEECH_RECOG_AVAILABLE = True
except ImportError:
    SPEECH_RECOG_AVAILABLE = False
    print("警告: speech_recognition库未安装，语音输入功能将被禁用")

# Ollama配置
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ollama API地址
MODEL_NAME = "deepseek-r1:14b"  # 默认使用的模型

class OllamaWorker(QThread):
    """
    Ollama API工作线程类
    负责在后台与Ollama API通信，避免阻塞主线程
    
    信号:
    - response_received: 接收到API响应时发射，携带响应文本
    - error_occurred: 发生错误时发射，携带错误信息
    """
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt):
        """
        初始化工作线程
        
        参数:
        - prompt: 发送给AI的提示文本
        """
        super().__init__()
        self.prompt = prompt

    def run(self):
        """线程主执行方法"""
        if not REQUESTS_AVAILABLE:
            self.error_occurred.emit("错误: requests库不可用，请安装requests")
            return
            
        try:
            # 准备API请求数据
            data = {
                "model": MODEL_NAME,  # 使用的模型名称
                "prompt": self.prompt,  # 用户输入的提示
                "stream": False  # 不使用流式响应
            }
            
            # 发送POST请求到Ollama API
            response = requests.post(
                OLLAMA_API_URL,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30  # 30秒超时
            )
            response.raise_for_status()  # 检查HTTP错误
            
            # 从响应中提取AI回复并发射信号
            self.response_received.emit(response.json().get("response", ""))
        except Exception as e:
            # 发生错误时发射错误信号
            self.error_occurred.emit(f"API错误: {str(e)}")

class ChatBubble(QFrame):
    """
    聊天消息气泡控件
    
    属性:
    - is_user: 是否为用户消息(决定气泡样式和位置)
    - text: 显示的文本内容
    """
    def __init__(self, text, is_user=False):
        """
        初始化消息气泡
        
        参数:
        - text: 显示的文本内容
        - is_user: 是否为用户发送的消息(默认为False，即AI消息)
        """
        super().__init__()
        self.is_user = is_user
        self.text = text
        
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.setMinimumWidth(100)  # 最小宽度
        self.setMaximumWidth(600)  # 最大宽度
        
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)  # 内边距
        layout.setSpacing(0)  # 无间距
        
        # 确保ChatBubble控件正确显示圆角
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 设置背景自动填充
        self.setAutoFillBackground(True)
        
        self.setLayout(layout)
        self.setLayout(layout)
        
        # 创建文本标签
        self.label = QLabel(text)
        self.label.setWordWrap(True)  # 启用自动换行
        self.label.setTextFormat(Qt.RichText)  # 支持富文本
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许文本选择
        
        # 更新样式并添加标签
        self.update_style()
        layout.addWidget(self.label)
        self.adjust_size()
        
        # 延迟调整大小以确保正确计算
        QTimer.singleShot(100, self.adjust_size)
    
    def update_style(self):
        """根据消息类型更新气泡样式"""
        # 用户消息和AI消息使用不同颜色
        bubble_color = "#e3f2fd" if self.is_user else "#f5f5f5"
        text_color = "#000000"
        shadow_color = "#bbdefb" if self.is_user else "#e0e0e0"
        
        align = Qt.AlignRight if self.is_user else Qt.AlignLeft  # 用户消息右对齐，AI消息左对齐
        
        # 设置样式表，确保圆角效果
        self.setStyleSheet(f"""
            ChatBubble {{
                background-color: {bubble_color};
                border-radius: 25px;
                padding: 12px 15px;
                margin: 8px;
                border: 1px solid {shadow_color};
            }}
            QLabel {{
                color: {text_color};
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                line-height: 1.5;
                min-height: 20px;
            }}
        """)
        # 设置布局和标签的对齐方式
        self.layout().setAlignment(align)
        self.label.setAlignment(align)
        
        # 强制更新样式
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        self.label.update()
    
    def adjust_size(self):
        """根据文本内容调整气泡大小"""
        font_metrics = QFontMetrics(self.label.font())
        
        # 计算文本宽度
        text_width = font_metrics.width(self.text) + 30  # 增加一些边距
        
        # 限制最大宽度为父控件宽度的80%或600像素
        max_width = min(600, self.parent().width() * 0.8) if self.parent() else 600
        text_width = min(max_width, max(100, text_width))
        
        # 根据消息类型设置不同的对齐方式
        text_alignment = Qt.AlignRight if self.is_user else Qt.AlignLeft
        
        # 计算文本高度
        text_rect = font_metrics.boundingRect(
            QRect(0, 0, text_width - 30, 1000),  # 可用宽度和最大高度
            Qt.TextWordWrap | text_alignment,  # 自动换行，根据消息类型对齐
            self.text
        )
        text_height = text_rect.height() + 30  # 增加一些边距
        
        # 设置固定大小并更新
        self.setFixedSize(int(text_width), int(text_height))
        self.updateGeometry()
        if self.parent():
            self.parent().updateGeometry()

class ChatWindow(QMainWindow):
    """
    主聊天窗口类
    
    功能:
    - 提供完整的聊天界面
    - 处理用户输入
    - 显示聊天历史
    - 管理TTS功能
    """
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setWindowTitle(f"智能语音问答系统 ({MODEL_NAME})")  # 窗口标题
        self.setGeometry(100, 100, 850, 650)  # 稍大一些的初始尺寸
        # 设置全局样式
        self.setStyleSheet(""".QWidget { background-color: #f5f7fa; }""")
        # 添加窗口阴影
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        # 设置中文字体支持
        font = QFont()
        font.setFamily("Microsoft YaHei")
        self.setFont(font)
        
        # 初始化TTS引擎
        self.tts_engine = None
        self.init_tts()
        
        # 初始化UI
        self.init_ui()
        self.add_welcome_message()
    
    def on_volume_changed(self, value):
        """处理音量变化事件"""
        if self.tts_engine:
            try:
                volume = value / 100.0  # 转换为0.0-1.0范围
                self.tts_engine.setProperty('volume', volume)
                print(f"音量已调整为: {volume}")
            except Exception as e:
                print(f"调整音量失败: {str(e)}")

    def init_tts(self):
        """初始化文本转语音(TTS)引擎"""
        if not TTS_AVAILABLE:
            print("TTS功能不可用")
            return
            
        self.tts_engine = None
        try:
            # 不指定驱动程序，让pyttsx3自动选择
            self.tts_engine = pyttsx3.init()
            
            # 检查引擎是否成功创建
            if self.tts_engine is None:
                print("TTS引擎创建失败")
                return
            
            # 设置语音属性
            try:
                self.tts_engine.setProperty('rate', 150)  # 语速
                # 初始音量将在on_volume_changed中设置
            except Exception as e:
                print(f"设置TTS属性失败: {str(e)}")
            
            # 尝试设置女性声音（更通用的方式）
            try:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'female' in voice.id.lower() or 'woman' in voice.id.lower():
                        try:
                            self.tts_engine.setProperty('voice', voice.id)
                            print("已设置女性声音")
                            break
                        except:
                            continue
            except Exception as e:
                print(f"设置TTS声音失败: {str(e)}")
            
            print("TTS初始化成功")
            
        except Exception as e:
            print(f"TTS初始化失败: {str(e)}")
            self.tts_engine = None
    
    def init_ui(self):
        """初始化用户界面"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 无外边距
        self.main_layout.setSpacing(0)  # 无间距
        self.central_widget.setLayout(self.main_layout)
        
        # 添加固定欢迎消息
        self.add_fixed_welcome_message()
        
        # 初始化聊天区域
        self.init_chat_area()
        
        # 初始化输入区域
        self.init_input_area()
    
    def init_chat_area(self):
        """初始化聊天消息显示区域"""
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)  # 可调整大小
        
        # 设置滚动区域样式
        self.chat_scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #f5f7fa; }
            QScrollBar:vertical { width: 8px; background: #f1f1f1; margin: 5px 0 5px 0; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #c1c1c1; min-height: 30px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #a8a8a8; }
        """)
        
        # 创建聊天内容容器
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #ffffff; border-radius: 10px; margin: 10px;")
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)  # 内容顶部对齐
        self.chat_layout.setSpacing(12)  # 消息间距
        self.chat_layout.setContentsMargins(20, 20, 20, 20)  # 内边距
        self.chat_container.setLayout(self.chat_layout)
        
        # 设置滚动区域的内容
        self.chat_scroll.setWidget(self.chat_container)
        
        # 将聊天区域添加到主布局(占7份空间)
        self.main_layout.addWidget(self.chat_scroll, stretch=7)
    
    def init_input_area(self):
        """初始化用户输入区域"""
        self.input_area = QWidget()
        self.input_area.setMinimumHeight(150)  # 最小高度
        
        # 输入区域布局
        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(15, 10, 15, 15)  # 内边距
        self.input_area.setLayout(self.input_layout)
        
        # 输入文本框
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 25px;
                padding: 15px 20px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background-color: #ffffff;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
            }
            QTextEdit:focus {
                border-color: #4a90e2;
                outline: none;
            }
        """)
        self.input_text.setPlaceholderText("输入您的问题...")  # 占位文本
        self.input_text.setMinimumHeight(50)
        self.input_text.setMaximumHeight(120)
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(90, 50)  # 固定大小
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                border: none;
                border-radius: 25px;
                color: white;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                padding: 5px;

            }
            QPushButton:hover { 
                background-color: #3a7bc8;
                }
                QPushButton:pressed { 
                    background-color: #2a6bb8;
                }
        """)
        self.send_button.clicked.connect(self.send_message)  # 点击事件
        
        # 只在TTS可用时添加复选框
        if TTS_AVAILABLE:
            # 语音播报复选框
            self.tts_checkbox = QCheckBox("语音播报")
            self.tts_checkbox.setChecked(True)  # 默认启用
            self.tts_checkbox.setStyleSheet("""
                QCheckBox {
                    color: #555555;
                    font-size: 14px;
                    font-family: 'Microsoft YaHei';
                    spacing: 8px;
                    padding: 5px 15px 5px 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #d0d0d0;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border-color: #4a90e2;
                    background-color: #4a90e2;
                }
                QCheckBox::indicator:checked::text {
                    color: #333333;
                }
            """)
            self.input_layout.addWidget(self.tts_checkbox)
        
        # 只在语音识别可用时添加语音输入按钮
        if SPEECH_RECOG_AVAILABLE:
            self.voice_input_button = QPushButton("语音输入")
            self.voice_input_button.setFixedSize(90, 50)  # 固定大小
            self.voice_input_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    border: none;
                    border-radius: 25px;
                    color: white;
                    font-size: 14px;
                    font-family: 'Microsoft YaHei';
                    padding: 5px;
    
                }
                QPushButton:hover { 
                    background-color: #388e3c;
                }
                QPushButton:pressed { 
                    background-color: #2e7d32;
                }
            """)
            self.voice_input_button.clicked.connect(self.voice_input)
            self.input_layout.addWidget(self.voice_input_button, stretch=1)
        
        # 创建一个水平布局来放置音量控件
        volume_layout = QHBoxLayout()
        
        # 音量标签
        volume_label = QLabel("音量:")
        volume_label.setStyleSheet("font-size: 14px; font-family: 'Microsoft YaHei'; color: #555555;")
        volume_layout.addWidget(volume_label)

        # 音量滑块
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(90)  # 默认音量90%
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: white;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #3a7bc8);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        # 创建一个容器widget来放置音量布局
        volume_widget = QWidget()
        volume_widget.setLayout(volume_layout)
        
        # 将音量widget添加到输入布局
        self.input_layout.addWidget(volume_widget)
        
        # 将控件添加到输入布局
        self.input_layout.addWidget(self.input_text, stretch=5)  # 文本框占5份空间
        self.input_layout.addWidget(self.send_button, stretch=1)  # 按钮占1份空间
        
        # 将输入区域添加到主布局(占3份空间)
        self.main_layout.addWidget(self.input_area, stretch=3)
    
    def add_fixed_welcome_message(self):
        """添加固定的欢迎消息(在聊天区域上方)"""
        welcome_text = f"""
        <div style='text-align: center; margin: 20px;'>
            <h2 style='color: #4a90e2; font-family: "Microsoft YaHei"; font-weight: 600;'>欢迎使用 智能语音问答系统</h2>
            <p style='color: #666; font-family: "Microsoft YaHei"; margin-top: 10px;'>我正在使用本地Ollama服务的 {MODEL_NAME} 模型</p>
            <p style='color: #666; font-family: "Microsoft YaHei"; margin-top: 5px;'>请在下方的输入框中提问，或使用语音输入。</p>
        </div>
        """
        self.fixed_welcome = QLabel(welcome_text)
        self.fixed_welcome.setAlignment(Qt.AlignCenter)  # 居中
        self.fixed_welcome.setWordWrap(True)  # 自动换行
        self.fixed_welcome.setTextFormat(Qt.RichText)  # 富文本
        self.fixed_welcome.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                padding: 20px 0;

            }
        """)
        self.fixed_welcome.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.fixed_welcome)
    
    def resizeEvent(self, event):
        """
        窗口大小改变事件处理
        确保所有消息气泡都能正确调整大小
        """
        super().resizeEvent(event)
        # 遍历所有消息气泡并调整大小
        for i in range(self.chat_layout.count()):
            item = self.chat_layout.itemAt(i)
            if item and hasattr(item.widget(), 'adjust_size'):
                item.widget().adjust_size()
    
    def add_welcome_message(self):
        """在聊天区域添加欢迎消息"""
        welcome_container = QWidget()
        welcome_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # 容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        welcome_container.setLayout(container_layout)
        
        # 欢迎文本
        welcome_text = """
        <div style='text-align: center; margin: 20px;'>
            <p style='color: #666;'>开始对话吧!</p>
        </div>
        """
        welcome_label = QLabel(welcome_text)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setWordWrap(True)
        welcome_label.setTextFormat(Qt.RichText)
        welcome_label.setStyleSheet("background-color: transparent;")
        
        # 添加欢迎标签到容器
        container_layout.addStretch()
        container_layout.addWidget(welcome_label)
        container_layout.addStretch()
        
        # 将欢迎容器添加到聊天区域
        self.chat_layout.addWidget(welcome_container)
        self.chat_layout.addStretch()
    
    def send_message(self):
        """处理发送消息逻辑"""
        if not REQUESTS_AVAILABLE:
            # 显示错误消息
            error_bubble = ChatBubble("错误: requests库不可用，请安装requests", is_user=False)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_bubble)
            self.scroll_to_bottom()
            return
            
        # 获取用户输入并去除首尾空格
        message = self.input_text.toPlainText().strip()
        if not message:  # 空消息不处理
            return
        
        # 创建用户消息气泡并添加到聊天区域
        user_bubble = ChatBubble(message, is_user=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_bubble)
        # 设置用户消息右对齐
        self.chat_layout.setAlignment(user_bubble, Qt.AlignRight)
        self.input_text.clear()  # 清空输入框
        self.scroll_to_bottom()  # 滚动到底部
        
        # 创建工作线程与Ollama API交互
        self.ollama_worker = OllamaWorker(message)
        self.ollama_worker.response_received.connect(self.handle_ollama_response)
        self.ollama_worker.error_occurred.connect(self.handle_ollama_error)
        self.ollama_worker.start()  # 启动线程
        
        # 显示"思考中..."提示
        self.thinking_label = QLabel("思考中...")
        self.thinking_label.setAlignment(Qt.AlignLeft)
        self.thinking_label.setStyleSheet("color: #888; font-style: italic; background-color: transparent;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.thinking_label)
        self.scroll_to_bottom()
    
    def handle_ollama_response(self, response):
        """处理Ollama API的响应"""
        self.thinking_label.deleteLater()  # 移除"思考中..."提示
        
        # 清理响应中的特殊标记
        cleaned_response = response.replace("<think>", "").replace("</think>", "")
        
        # 创建AI消息气泡并添加到聊天区域
        ai_bubble = ChatBubble(cleaned_response, is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_bubble)
        # 设置AI消息左对齐
        self.chat_layout.setAlignment(ai_bubble, Qt.AlignLeft)
        self.scroll_to_bottom()
        
        # 检查是否需要语音播报
        if (TTS_AVAILABLE and hasattr(self, 'tts_checkbox') 
           and self.tts_checkbox.isChecked() and self.tts_engine):
            self.speak(cleaned_response)
    
    def speak(self, text):
        """使用TTS引擎播报文本"""
        try:
            self.tts_engine.stop()  # 停止当前播报
            self.tts_engine.say(text)  # 播报新文本
            self.tts_engine.runAndWait()  # 等待播报完成
        except Exception as e:
            print(f"语音播报错误: {str(e)}")
            # 显示语音错误消息
            error_bubble = ChatBubble(f"语音播报错误: {str(e)}", is_user=False)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_bubble)
            self.scroll_to_bottom()
    
    def handle_ollama_error(self, error_message):
        """处理Ollama API错误"""
        self.thinking_label.deleteLater()  # 移除"思考中..."提示
        
        # 创建错误消息气泡
        error_bubble = ChatBubble(error_message, is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_bubble)
        self.scroll_to_bottom()
        
        # 添加轻微的抖动动画以引起注意
        self.animate_error_bubble(error_bubble)
        
        # 如果需要，播报错误消息
        if (TTS_AVAILABLE and hasattr(self, 'tts_checkbox') 
           and self.tts_checkbox.isChecked() and self.tts_engine):
            self.speak("发生错误：" + error_message)
    
    def voice_input(self):
        """处理语音输入功能"""
        if not SPEECH_RECOG_AVAILABLE:
            # 显示错误消息
            error_bubble = ChatBubble("错误: speech_recognition库不可用，请安装该库", is_user=False)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_bubble)
            self.scroll_to_bottom()
            return
        
        # 显示"正在收听..."提示
        self.listening_label = QLabel("正在收听...")
        self.listening_label.setAlignment(Qt.AlignLeft)
        self.listening_label.setStyleSheet("color: #888; font-style: italic; background-color: transparent;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.listening_label)
        self.scroll_to_bottom()
        
        # 创建一个引用，确保在定时器回调中使用时不会被垃圾回收
        self.listening_label_ptr = self.listening_label
        
        def safe_delete_label():
            """安全删除标签的辅助函数"""
            if hasattr(self, 'listening_label_ptr') and self.listening_label_ptr is not None:
                # 使用QApplication.processEvents确保UI更新
                QApplication.processEvents()
                self.listening_label_ptr.deleteLater()
                self.listening_label_ptr = None
                # 清除对原始标签的引用
                if hasattr(self, 'listening_label'):
                    self.listening_label = None
        
        try:
            # 创建语音识别器
            recognizer = sr.Recognizer()
            
            # 调整麦克风灵敏度
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            
            # 使用麦克风录制音频
            with sr.Microphone() as source:
                # 显示"请说话..."提示
                if hasattr(self, 'listening_label') and self.listening_label is not None:
                    self.listening_label.setText("请说话...")
                    self.scroll_to_bottom()
                else:
                    return
                
                # 监听语音输入
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
                # 显示"正在识别..."提示
                if hasattr(self, 'listening_label') and self.listening_label is not None:
                    self.listening_label.setText("正在识别...")
                    self.scroll_to_bottom()
                else:
                    return
                
                try:
                    # 使用百度语音识别API（中文识别效果较好）
                    # 注意：这里使用的是公共API，实际使用中可能需要配置自己的API密钥
                    text = recognizer.recognize_baidu(audio, language='zh-CN')
                    
                    # 将识别的文本填入输入框
                    self.input_text.setPlainText(text)
                    
                    # 显示"语音识别完成"提示
                    if hasattr(self, 'listening_label') and self.listening_label is not None:
                        self.listening_label.setText("语音识别完成")
                        self.scroll_to_bottom()
                        
                        # 3秒后移除提示
                        QTimer.singleShot(3000, safe_delete_label)
                    
                except sr.UnknownValueError:
                    if hasattr(self, 'listening_label') and self.listening_label is not None:
                        self.listening_label.setText("无法识别语音，请重试")
                        QTimer.singleShot(3000, safe_delete_label)
                        self.scroll_to_bottom()
                except sr.RequestError as e:
                    if hasattr(self, 'listening_label') and self.listening_label is not None:
                        self.listening_label.setText(f"语音识别服务错误: {e}")
                        QTimer.singleShot(3000, safe_delete_label)
                        self.scroll_to_bottom()
                except Exception as e:
                    if hasattr(self, 'listening_label') and self.listening_label is not None:
                        self.listening_label.setText(f"语音识别错误: {str(e)}")
                        QTimer.singleShot(3000, safe_delete_label)
                        self.scroll_to_bottom()
        except Exception as e:
            if hasattr(self, 'listening_label') and self.listening_label is not None:
                self.listening_label.setText(f"麦克风错误: {str(e)}")
                QTimer.singleShot(3000, safe_delete_label)
                self.scroll_to_bottom()
    
    def animate_error_bubble(self, bubble):
        """为错误气泡添加抖动动画"""
        animation = QPropertyAnimation(bubble, b"pos")
        animation.setDuration(500)
        animation.setLoopCount(1)
        
        start_pos = bubble.pos()
        
        # 定义抖动路径
        key_frames = [
            (0, start_pos),
            (0.1, QPoint(start_pos.x() + 5, start_pos.y())),
            (0.2, QPoint(start_pos.x() - 5, start_pos.y())),
            (0.3, QPoint(start_pos.x() + 5, start_pos.y())),
            (0.4, QPoint(start_pos.x() - 5, start_pos.y())),
            (0.5, QPoint(start_pos.x() + 3, start_pos.y())),
            (0.6, QPoint(start_pos.x() - 3, start_pos.y())),
            (0.7, QPoint(start_pos.x() + 3, start_pos.y())),
            (0.8, QPoint(start_pos.x() - 3, start_pos.y())),
            (1.0, start_pos)
        ]
        
        # 添加关键帧
        for time, pos in key_frames:
            animation.setKeyValueAt(time, pos)
        
        animation.start()
    
    def scroll_to_bottom(self):
        """滚动聊天区域到底部"""
        # 添加平滑滚动效果
        scroll_bar = self.chat_scroll.verticalScrollBar()
        animation = QPropertyAnimation(scroll_bar, b"value")
        animation.setDuration(300)
        animation.setStartValue(scroll_bar.value())
        animation.setEndValue(scroll_bar.maximum())
        animation.start()
        # 确保滚动到底部
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

if __name__ == "__main__":
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 设置字体 - Windows使用微软雅黑，macOS使用苹方
    font = QFont()
    font.setFamily("Microsoft YaHei" if sys.platform == "win32" else "PingFang SC")
    app.setFont(font)
    
    # 创建并显示主窗口
    window = ChatWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())