# -------------------------------------------------------------------------------
# Name:         core
# Description:
# Author:       A07567
# Date:         2020/12/18
# Description:  所有的功能实现核心
# -------------------------------------------------------------------------------
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QThread, Signal
import os
import sys
from core import cores
from core import my_log
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class Merge_Window(QThread):
    signal_log = Signal(str)

    def __init__(self):
        """
            1. UI
            2. 初始化数据
                2.1 合并区
            3. 绑定事件
        """
        # 1 初始化UI
        super(Merge_Window, self).__init__()
        self.window = QUiLoader().load('../res/ui/merge.ui')
        self.window.setFixedSize(self.window.width(), self.window.height())
        # 2 初始化变量
        # # 2.1 >>> 合并区
        self.merge_files = None
        # 3 绑定事件
        # 选择合并文件
        self.window.select_files_pushButton.clicked.connect(self.select_merge_files)
        self.signal_log.connect(self.write_log)

    # 选择合并文件
    def select_merge_files(self):
        """
        根据文件前5位数字判断项目，根据不同的项目选择不同的数据标签点进行合并
        60004：外罗
        60005:南鹏岛
        60006：沙扒
        :return:
        """
        # 设置合并按钮不可见，防止二次操作时选择不同项目数据合并时此按钮为可见状态
        self.window.merge_pushButton.setEnabled(False)
        # 获得上一层目录
        path = os.path.abspath(os.path.dirname(os.getcwd())) + "\\data"
        # 主程序调用，不需要获取上层目录
        # path = os.getcwd() + "\\data"
        Dialog = QFileDialog()
        file_names, filetype = Dialog.getOpenFileNames(self.window,
                                                       "选取文件",
                                                       # 获得当前路径
                                                       path,  # 起始路径
                                                       "csv(*.csv)")  # 设置文件扩展名过滤,用双分号间隔
        if file_names == []:
            QMessageBox.warning(self.window, "警告", "请选择文件！")
        else:
            flag = []
            for file in file_names:
                """
                创建一个list 存放切分的文件名前5位数，判断是否为同一个项目
                """
                try:
                    # 判断文件命名是否规范
                    flag.append(str(os.path.basename(file)).split(".")[-2].split("_")[0][:5])
                except Exception as e:
                    QMessageBox.warning(self.window, "警告", "文件名称包含非法字符！")
                    print(e)
                    return
            # 判断是否为同一个项目，如果不同则提示，如果同则显示合并按钮
            one = len(set(flag))
            # print(flag)
            if one != 1:
                QMessageBox.warning(self.window, "警告", "请选择同一项目的数据!")
                return
            else:
                self.window.merge_pushButton.setEnabled(True)
                # # 取第0项
                # self.compare_value = flag[0]
                # 将file_names 赋值给csv_files
                self.merge_files = file_names

                self.window.log_plainTextEdit.clear()
                self.window.file_lineEdit.setText(str(file_names))
                self.window.merge_pushButton.setEnabled(True)
                self.window.merge_pushButton.clicked.connect(self.start)

    def merge_file(self):
        self.signal_log.emit("正在合并...")
        merge_result = cores.merge(self.merge_files)
        self.signal_log.emit("完成合并...")
        return merge_result

    def write_log(self, text):
        self.window.log_plainTextEdit.appendHtml(text)

    def run(self):
        self.merge_file()


if __name__ == '__main__':
    app = QApplication([])
    win = Merge_Window()
    win.window.show()
    app.exec_()
