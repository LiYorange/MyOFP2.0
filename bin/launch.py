# -------------------------------------------------------------------------------
# Name:         launch
# Description:
# Author:       A07567
# Date:         2020/12/16
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox, QInputDialog, QLineEdit
import os
import sys
import gc
import merge_window
import unpack_window
import run_window
import subprocess
from core import cores
from core.post_man import PostMan
from core.thread_manager import ThreadManage
from core.model_manager import ModelManager
from core.gearbox import GearBox
from core.generator import Generator
from core.pitch import Pitch
from core.converter import Converter
from core.hydraulic import Hydraulic
from core.sensor import Sensor

import traceback
from core import my_log

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


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
        self.postman = None
        self.thread_manager = None
        self.model_manager = None
        self.gearbox = None
        self.generator = None
        self.converter = None
        self.pitch = None
        self.hydraulic = None
        self.sensor = None
        # 绑定事件
        self.window.unpack_button.clicked.connect(self.load_unpack)
        self.window.merge_button.clicked.connect(self.load_merge)
        self.window.import_files_button.clicked.connect(self.load_data)
        self.window.run_button.clicked.connect(self.load_run_window)
        self.window.add_item_button.clicked.connect(self.add_item)
        self.window.revise_item_button.clicked.connect(self.revise_item)
        self.window.about_button.clicked.connect(self.about)
        self.window.help_button.clicked.connect(self.help)

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
        path = os.path.abspath(os.path.dirname(os.getcwd())) + "\\data"
        file_names, filetype = QFileDialog.getOpenFileNames(self.window,
                                                            "选取文件",
                                                            # 获得当前路径
                                                            path,  # 起始路径
                                                            "CSV文件 (*.csv);;所有文件 (*)")  # 设置文件扩展名过滤,用双分号间隔
        if not file_names:
            pass
        else:
            self.files = file_names

    def load_run_window(self):
        """先启动TM，再启动MM在启动window"""
        self.DEL(self.postman, self.thread_manager, self.gearbox, self.generator, self.converter,
                 self.pitch, self.hydraulic, self.sensor, self.model_manager)
        self.postman = PostMan()
        # 创建线程管理者，并雇佣postman
        self.thread_manager = ThreadManage(self.postman)
        self.thread_manager.start()
        self.gearbox = GearBox(self.postman)
        self.generator = Generator(self.postman)
        self.pitch = Pitch(self.postman)
        self.converter = Converter(self.postman)
        self.hydraulic = Hydraulic(self.postman)
        self.sensor = Sensor(self.postman)
        # 创建模块管理者，并雇佣postman
        self.model_manager = ModelManager(self.files, [self.gearbox, self.generator, self.pitch, self.converter, self.hydraulic, self.sensor],
                                          self.postman)
        # self.model_manager = ModelManager(self.files, [self.gearbox], self.postman)
        self.model_manager.start()
        self.run_window = run_window.RunWindow(self.files, PM=self.postman)
        self.run_window.start()

    def DEL(self, *args):
        for i in args:
            try:
                del i
            except Exception as e:
                log.info(e)
            finally:
                gc.collect()

    def add_item(self):
        text, okPressed = QInputDialog.getText(self, "添加项目", "输入密码:", QLineEdit.Password, "")
        if okPressed and text == '12345':
            try:
                subprocess.call(['notepad.exe', '../db/tickets.my'])
            except IOError as e:
                QMessageBox.warning(self, '警告', '文件丢失', QMessageBox.Yes)
        elif okPressed and text != '12345':
            QMessageBox.warning(self, '警告', '密码错误！', QMessageBox.Yes)
        else:
            pass

    def revise_item(self):
        text, okPressed = QInputDialog.getText(self, "修改项目", "输入密码:", QLineEdit.Password, "")
        if okPressed and text == '12345':
            try:
                subprocess.call(['notepad.exe', '../db/tickets.my'])
            except IOError as e:
                QMessageBox.warning(self, '警告', '文件丢失', QMessageBox.Yes)
        elif okPressed and text != '12345':
            QMessageBox.warning(self, '警告', '密码错误！', QMessageBox.Yes)
        else:
            pass

    def about(self):
        msg = "线下故障预警模型软件V2.0版本\n海上工程技术部\n如有问题请联系:\nchencheng06@mywind.com.cn\n或malinlin@mywind.com.cn"
        QMessageBox.about(self.window, "关于", msg)

    def help(self):
        cmd = os.path.abspath(os.path.dirname(os.getcwd())) + "\\res\说明文档.docx"
        os.system(cmd)


if __name__ == '__main__':
    app = QApplication([])
    launch_window = LaunchWindow()
    launch_window.window.show()
    app.exec_()
