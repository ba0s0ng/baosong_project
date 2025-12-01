import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QMessageBox, 
                            QFrame, QSplitter, QGroupBox, QFormLayout)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class FireDetectionThread(QThread):
    """火灾检测线程"""
    update_signal = pyqtSignal(QImage, bool)

    def __init__(self, parent=None):
        super(FireDetectionThread, self).__init__(parent)
        self.running = False
        self.camera_id = 0
        self.capture = None
        self.threshold = 0.5  # 火灾检测阈值

    def run(self):
        self.running = True
        self.capture = cv2.VideoCapture(self.camera_id)

        if not self.capture.isOpened():
            QMessageBox.critical(None, "错误", "无法打开摄像头")
            self.running = False
            return

        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                break

            # 检测火灾
            is_fire = self.detect_fire(frame)

            # 转换为Qt图像格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_image = qt_image.scaled(640, 480, Qt.KeepAspectRatio)

            # 发送信号更新UI
            self.update_signal.emit(qt_image, is_fire)

            # 控制帧率
            self.msleep(30)

        if self.capture is not None:
            self.capture.release()

    def stop(self):
        self.running = False
        self.wait()

    def detect_fire(self, frame):
        """
        简单的火灾检测算法
        基于颜色阈值检测火焰
        """
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 定义火焰的颜色范围（红色和黄色）
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])

        # 创建掩码
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask3 = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask = mask1 | mask2 | mask3

        # 去除噪声
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 计算火焰区域比例
        fire_area = cv2.countNonZero(mask)
        total_area = frame.shape[0] * frame.shape[1]
        fire_ratio = fire_area / total_area

        return fire_ratio > self.threshold

class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("火灾识别检测系统")
        self.setGeometry(100, 100, 1024, 768)

        # 初始化火灾检测线程
        self.detection_thread = FireDetectionThread()
        self.detection_thread.update_signal.connect(self.update_frame)

        # 创建UI
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标题
        title_label = QLabel("火灾识别检测系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # 创建图像显示区域
        self.image_label = QLabel("摄像头画面")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        main_layout.addWidget(self.image_label)

        # 创建状态显示
        status_layout = QHBoxLayout()
        main_layout.addLayout(status_layout)

        self.status_label = QLabel("状态: 就绪")
        self.status_label.setStyleSheet("font-size: 16px; color: green;")
        status_layout.addWidget(self.status_label)

        self.fire_label = QLabel("火灾检测: 未检测到")
        self.fire_label.setStyleSheet("font-size: 16px; color: blue;")
        status_layout.addWidget(self.fire_label)
        status_layout.addStretch(1)

        # 创建控制按钮区域
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout()
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        self.start_button = QPushButton("开始检测")
        self.start_button.clicked.connect(self.start_detection)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止检测")
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        self.load_button = QPushButton("加载图像")
        self.load_button.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_button)

        self.camera_button = QPushButton("切换摄像头")
        self.camera_button.clicked.connect(self.switch_camera)
        control_layout.addWidget(self.camera_button)

        # 创建参数设置区域
        param_group = QGroupBox("参数设置")
        param_layout = QFormLayout()
        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)

        # 添加阈值设置（这里简化处理，实际应用中可以添加滑块控件）
        self.threshold_label = QLabel("火灾检测阈值: 0.5")
        param_layout.addRow("检测灵敏度:", self.threshold_label)

    def start_detection(self):
        """开始火灾检测"""
        self.status_label.setText("状态: 检测中")
        self.status_label.setStyleSheet("font-size: 16px; color: orange;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # 启动检测线程
        self.detection_thread.start()

    def stop_detection(self):
        """停止火灾检测"""
        self.status_label.setText("状态: 就绪")
        self.status_label.setStyleSheet("font-size: 16px; color: green;")
        self.fire_label.setText("火灾检测: 未检测到")
        self.fire_label.setStyleSheet("font-size: 16px; color: blue;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # 停止检测线程
        if self.detection_thread.isRunning():
            self.detection_thread.stop()

    def load_image(self):
        """加载图像进行检测"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开图像", "", "图像文件 (*.png *.jpg *.jpeg *.bmp)")

        if file_path:
            # 停止摄像头检测
            if self.detection_thread.isRunning():
                self.stop_detection()

            # 加载图像
            image = cv2.imread(file_path)
            if image is None:
                QMessageBox.warning(self, "警告", "无法加载图像")
                return

            # 检测火灾
            detector = FireDetectionThread()
            is_fire = detector.detect_fire(image)

            # 显示图像
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_image = qt_image.scaled(640, 480, Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(qt_image))

            # 更新状态
            self.status_label.setText("状态: 图像已加载")
            if is_fire:
                self.fire_label.setText("火灾检测: 检测到火灾!")
                self.fire_label.setStyleSheet("font-size: 16px; color: red;")
                QMessageBox.warning(self, "警告", "检测到火灾!")
            else:
                self.fire_label.setText("火灾检测: 未检测到")
                self.fire_label.setStyleSheet("font-size: 16px; color: blue;")

    def switch_camera(self):
        """切换摄像头"""
        # 停止当前检测
        if self.detection_thread.isRunning():
            self.stop_detection()

        # 切换摄像头ID（0表示默认摄像头，1表示外接摄像头等）
        self.detection_thread.camera_id = 1 - self.detection_thread.camera_id

        QMessageBox.information(self, "信息", f"已切换到摄像头 {self.detection_thread.camera_id}")

    def update_frame(self, qt_image, is_fire):
        """更新图像显示和检测状态"""
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

        if is_fire:
            self.fire_label.setText("火灾检测: 检测到火灾!")
            self.fire_label.setStyleSheet("font-size: 16px; color: red;")
        else:
            self.fire_label.setText("火灾检测: 未检测到")
            self.fire_label.setStyleSheet("font-size: 16px; color: blue;")

    def closeEvent(self, event):
        """关闭窗口时停止检测线程"""
        if self.detection_thread.isRunning():
            self.detection_thread.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()