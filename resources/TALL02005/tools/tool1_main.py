from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui, cmds


import importlib

from tools.manager import CustomToolManager

importlib.reload(CustomToolManager)

# 全局变量，用来保存窗口实例
window = None


def get_maya_window():
    """
    获取 Maya 主窗口，通过 OpenMayaUI.MQtUtil.mainWindow() 获取指针，再通过 wrapInstance 转换为 QWidget
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return None


class MainUI(QtWidgets.QDialog):
    """
    示例的 MainUI 类，继承自 QDialog，可根据需要扩展
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义 UI 窗口")
        self.resize(300, 200)
        self.initUI()

    def initUI(self):
        # 添加一个简单的按钮示例
        self.button = QtWidgets.QPushButton("点击我")
        layout = QtWidgets.QVBoxLayout(self)
        self.button.clicked.connect(self.button_function)
        layout.addWidget(self.button)

        CustomToolManager.run_jobs()

    def button_function(self):
        print(CustomToolManager.registration_script_job_list)

    # def print_selected_objects(self, ):
    #     print('print_selected_objects...')

    def closeEvent(self, arg__1):
        CustomToolManager.kill_jobs()
        print(arg__1)
        super().closeEvent(arg__1)


def main_show_ui():
    global window
    print(window)
    # 如果窗口已经存在且处于可见状态，则激活它
    if window is not None and window.isVisible():
        window.raise_()  # 将窗口提升到最前面
        window.activateWindow()  # 激活窗口
        return

    # 否则创建新的窗口实例
    mayaMainWindow = get_maya_window()
    window = MainUI(mayaMainWindow)
    window.setWindowFlags(Qt.Window)  # 设置为独立窗口
    window.show()


if __name__ == '__main__':
    main_show_ui()

