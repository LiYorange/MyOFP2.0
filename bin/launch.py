# -------------------------------------------------------------------------------
# Name:         launch
# Description:
# Author:       A07567
# Date:         2020/12/16
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QApplication

import merge_window
import unpack_window


class LaunchWindow(QWidget):
    def __init__(self):
        super(LaunchWindow, self).__init__()
        # 初始化界面
        self.window = QUiLoader().load('../res/ui/launch.ui')
        self.unpack = unpack_window.Unpack_Window()
        self.merge = merge_window.Merge_Window()

        # 绑定事件
        self.window.unpack_button.clicked.connect(self.load_unpack)
        self.window.merge_button.clicked.connect(self.load_merge)

    def plot(self):
        pass

    # 载入解压界面
    def load_unpack(self):
        self.unpack.window.show()

    # 载入合并界面
    def load_merge(self):
        self.merge.window.show()


if __name__ == '__main__':
    app = QApplication([])
    draw_window = LaunchWindow()
    draw_window.window.show()
    app.exec_()
