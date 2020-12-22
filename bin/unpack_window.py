# -------------------------------------------------------------------------------
# Name:         core
# Description:
# Author:       A07567
# Date:         2020/12/18
# Description:  所有的功能实现核心
# -------------------------------------------------------------------------------
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QThread
import os
from core import core

class Unpack_Window(QThread):

    def __init__(self):
        """
            1. UI
            2. 初始化数据
                2.1 解压区
            3. 绑定事件
        """
        # 1 初始化UI
        super(Unpack_Window, self).__init__()
        self.window = QUiLoader().load('../res/ui/bandzip.ui')
        self.window.setFixedSize(self.window.width(), self.window.height())
        # 2 初始化变量
        # # 2.1 >>> 解压区
        self.unpack_files = None
        # 3 绑定事件
        # 选择解压文件
        self.window.file_path_pushButton.clicked.connect(self.select_unpack_file)

    # 选择解压文件
    def select_unpack_file(self):
        self.window.unpack_pushButton.setEnabled(False)
        Dialog = QFileDialog()
        file_names, filetype = Dialog.getOpenFileNames(self.window,
                                                       "选取文件",
                                                       # 获得当前路径
                                                       os.getcwd(),  # 起始路径
                                                       "zip文件 (*.zip);;"
                                                       "gz文件 (*.gz);;"
                                                       "rar文件 (*.rar);;"
                                                       "7z文件(*.7z);;"
                                                       "tar文件 (*.gz);;"
                                                       "所有文件 (*)")  # 设置文件扩展名过滤,用双分号间隔
        if not file_names:
            QMessageBox.warning(self.window, "警告", "请选择文件！")
        else:
            self.window.plainTextEdit.clear()
            self.unpack_files = file_names
            self.window.file_path_lineEdit.setText(str(file_names))
            self.window.unpack_pushButton.setEnabled(True)
            self.window.unpack_pushButton.clicked.connect(self.unpack_file)

    def unpack_file(self):
        unpack_result = core.unpack(self.unpack_files)
        return unpack_result


if __name__ == '__main__':
    app = QApplication([])
    win = Unpack_Window()
    win.window.show()
    app.exec_()