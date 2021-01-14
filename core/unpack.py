# -------------------------------------------------------------------------------
# Name:         unpack
# Description:
# Author:       A07567
# Date:         2020/12/22
# Description:  
# -------------------------------------------------------------------------------

import os
import sys
import shutil
from core import my_log
from PyQt5.QtCore import QThread, pyqtSignal
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class UnPack(QThread):
    signal_result = pyqtSignal(str)

    def __init__(self, files=None):
        super(UnPack, self).__init__()
        if files is not None:
            self.files = files
        else:
            return

    def unpack(self) -> str:

        """
        :param files:需要解压的文件
        生成一个data文件夹，用于存放解压数据，每次打开程序先清空该文件夹
        :return:如果解压成功返回真，否则返回假
        """
        # 获得上一层目录
        data = os.path.abspath(os.path.dirname(os.getcwd())) + "\\data"
        # 主程序调用，不需要得到上层目录
        # data = os.getcwd() + "\\data"
        try:
            # 不存在则创建，存在则清空
            if not os.path.exists(data):
                os.makedirs(data)
            else:
                shutil.rmtree(data)
                os.mkdir(data)
        except Exception as e:
            log.error(e)
        try:
            result = []
            for file in self.files:
                cmd = str(
                    os.path.abspath(os.path.dirname(os.getcwd())) + '/lib/bandzip/bz.exe x -o:{} {}'.format(data, file))
                result.append(os.system(cmd))
                """解压成功返回的是0"""
            if ~bool(all(result)):
                self.signal_result.emit("解压成功")
            else:
                self.signal_result.emit("解压失败，请重试或更换解压软件！")
        except Exception as e:
            log.error(e)

    def run(self):
        self.unpack()
