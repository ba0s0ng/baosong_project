import sys
import traceback
import time
import signal
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

# 处理信号
def signal_handler(sig, frame):
    print(f"接收到信号 {sig}，正在退出...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    print(f"程序开始启动... (时间: {time.strftime('%H:%M:%S')})")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {sys.path[0]}")
    try:
        print("创建QApplication实例...")
        app = QApplication(sys.argv)
        print(f"QApplication创建成功 (时间: {time.strftime('%H:%M:%S')})")
        
        print("创建MainWindow实例...")
        window = MainWindow()
        print(f"MainWindow创建成功 (时间: {time.strftime('%H:%M:%S')})")
        
        print("显示窗口...")
        window.show()
        print(f"窗口显示成功 (时间: {time.strftime('%H:%M:%S')})")
        
        print("开始事件循环...")
        exit_code = app.exec_()
        print(f"应用程序退出，退出码: {exit_code} (时间: {time.strftime('%H:%M:%S')})")
        sys.exit(exit_code)
    except Exception as e:
        print(f"程序运行出错: {e} (时间: {time.strftime('%H:%M:%S')})")
        traceback.print_exc()
        sys.exit(1)
    except SystemExit as se:
        print(f"系统退出: {se} (时间: {time.strftime('%H:%M:%S')})")
        sys.exit(se.code)
    except:
        print(f"未知错误 (时间: {time.strftime('%H:%M:%S')})")
        traceback.print_exc()
        sys.exit(1)