# -------------------------------------------------------------------------------
# Name:         launch
# Description:
# Author:       A07567
# Date:         2020/12/16
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QApplication, QFileDialog
import os
import merge_window
import unpack_window
import run_window


class LaunchWindow(QWidget):
    def __init__(self):
        super(LaunchWindow, self).__init__()
        # 初始化界面
        self.window = QUiLoader().load('../res/ui/launch.ui')
        self.unpack = None
        self.merge = None
        self.run_window = None
        # 初始化数据
        self.files = []  # 需要处理的文件
        # 绑定事件
        self.window.unpack_button.clicked.connect(self.load_unpack)
        self.window.merge_button.clicked.connect(self.load_merge)
        self.window.import_files_button.clicked.connect(self.load_data)
        self.window.run_button.clicked.connect(self.load_run_window)

    def plot(self):
        pass

    # 载入解压界面
    def load_unpack(self):
        self.unpack = unpack_window.Unpack_Window()
        self.unpack.window.show()

    # 载入合并界面
    def load_merge(self):
        self.merge = merge_window.Merge_Window()
        self.merge.window.show()

    def load_data(self):
        file_names, filetype = QFileDialog.getOpenFileNames(self.window,
                                                            "选取文件",
                                                            # 获得当前路径
                                                            os.getcwd(),  # 起始路径
                                                            "CSV文件 (*.csv);;所有文件 (*)")  # 设置文件扩展名过滤,用双分号间隔
        if not file_names:
            pass
        else:
            self.files = file_names

    def load_run_window(self):
        """先启动TM，再启动MM在启动window"""
        pass
        self.run_window = run_window.RunWindow(["南鹏岛", "外罗", "沙扒", "金湾"])
        self.run_window.window.show()


if __name__ == '__main__':
    app = QApplication([])
    draw_window = LaunchWindow()
    draw_window.window.show()
    app.exec_()
