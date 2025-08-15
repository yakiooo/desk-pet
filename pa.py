import sys
import os
import keyboard
from PyQt5.QtWidgets import QApplication, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QMovie, QCursor


# ==================== 资源路径处理 ====================
def get_resource_path(relative_path):
    """ 自动适配开发环境和打包后的资源路径 """
    try:
        # 打包后的临时文件夹路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境路径
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    if not os.path.exists(path):
        print(f"资源文件缺失: {path}")
        input("按回车键退出...")
        sys.exit(1)
    return path


# ==================== 键盘监听线程 ====================
class KeyboardThread(QThread):
    key_pressed = pyqtSignal(str)  # 信号：left/right

    def run(self):
        keyboard.hook(self.on_key_event)

    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            key = event.name.lower()
            if key in {'q', 'w', 'e', 'r', 't', 'a', 's', 'd', 'f', 'g', 'z', 'x', 'c', 'v', 'b'}:
                self.key_pressed.emit('left')
            else:
                self.key_pressed.emit('right')
        return True


# ==================== 桌面宠物主类 ====================
class DesktopPet(QLabel):
    def __init__(self):
        super().__init__()

        # 初始化资源路径
        self.resources = {
            'default': get_resource_path("default.gif"),
            'click': get_resource_path("click.gif"),
            'left': get_resource_path("left_typing.gif"),
            'right': get_resource_path("right_typing.gif")
        }

        # 加载动画
        self.movies = {
            'default': QMovie(self.resources['default']),
            'click': QMovie(self.resources['click']),
            'left': QMovie(self.resources['left']),
            'right': QMovie(self.resources['right'])
        }

        # 初始状态
        self.setMovie(self.movies['default'])
        self.movies['default'].start()

        # 窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.adjustSize()
        self.move_center()

        # 鼠标控制
        self.drag_pos = QPoint()
        self.is_dragging = False

        # 动画计时器
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reset_animation)

        # 启动键盘监听
        self.kb_thread = KeyboardThread()
        self.kb_thread.key_pressed.connect(self.play_typing_animation)
        self.kb_thread.start()

    def move_center(self):
        """ 居中显示 """
        screen = QDesktopWidget().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def play_typing_animation(self, hand_type):
        """ 播放打字动画 """
        self.setMovie(self.movies[hand_type])
        self.movies[hand_type].start()
        self.timer.start(100)  # 100ms后恢复

    def reset_animation(self):
        """ 恢复默认状态 """
        if not self.is_dragging:
            self.setMovie(self.movies['default'])
            self.movies['default'].start()

    # ========== 鼠标事件 ==========
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.pos()
            self.setMovie(self.movies['click'])
            self.movies['click'].start()
            self.is_dragging = True

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.reset_animation()

    def closeEvent(self, event):
        self.kb_thread.terminate()
        event.accept()


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    # 确保程序单例运行
    try:
        app = QApplication(sys.argv)
        pet = DesktopPet()
        pet.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序错误: {str(e)}")
        input("按回车键退出...")