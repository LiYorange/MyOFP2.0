# -------------------------------------------------------------------------------
# Name:         model_manager
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:  
# -------------------------------------------------------------------------------

import os
import sys
import re
from PyQt5.QtCore import QThread, pyqtSignal
from core import my_log
from core import gloable_var as gl
from core.get_df import GetDf
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class ModelManager(QThread):
    # thread_state: dict[str, int]
    assign_task_signal = pyqtSignal(bool)
    small_file_signal = pyqtSignal(tuple)
    big_file_signal = pyqtSignal(tuple)

    def __init__(self, files: list, model_list: list, pm):
        """
        :param files: 需要处理的文件堆
        :param model_list:需要管理的模块
        :param pm: 雇佣的postman
        """
        super(ModelManager, self).__init__()
        self.files_length = len(files)
        self.files = files[:]
        self.files.reverse()
        self.model_list = model_list
        self.postman = pm
        self.postman.send_to_MM.connect(self.receive_message)
        # 当前需要处理的文件
        self.file = None
        # 绑定信号
        self.assign_task_signal.connect(self.assign_task)
        self.small_file_signal.connect(self.deal_small_file)
        self.big_file_signal.connect(self.deal_big_file)
        # 线程状态  -1 未知状态，0 退出 1 活动
        self.DF = None
        self.thread_state = {"GearBox": -1, "Generator": -1, "Pitch": -1, "Converter": -1, "Hydraulic": -1,
                             "Sensor": -1}

    def send_message(self, message: dict):
        """"""
        """用于与TM RW通讯，雇佣postman"""
        # 发送消息
        to = message.get("to")
        if to == "model_manager":
            try:
                message["message"]["file"] = self.files_length - len(self.files) - 1
                message["message"]["file_name"] = self.file

                self.postman.send_to_RW.emit(message)
            except KeyError as e:
                log.warning(e)
        elif to == "thread_manager":
            self.postman.send_to_TM.emit(message)

    def receive_message(self, message: dict):

        self.analyse_receive_message(message)

    def analyse_receive_message(self, message: dict):

        """
        收到的消息 1. 来自TM
                   1.1 started
                   1.2 quitted
                    1.2.1 小文件退出线程
                    1.2.2 大文件退出线程
               2. 来自M
                   2.1 function result
                   2.2 quit
        """
        try:
            come_from = message.get("from")
            """如果是来自TM的，判断是否为大文件"""
            if come_from == "thread_manager":
                msg: dict = message["message"]
                if msg.get("state") == "started":
                    gl.started_thread_number = msg.get("thread_number")
                    gl.started_thread_name = re.findall(r"'(.+?)'", str(msg.get("thread_name").__class__))
                    # log.error((gl.started_thread_name,gl.now_file))
                if msg.get("state") == "quitted":
                    quit_thread_name = re.findall(r"'(.+?)'", str(msg.get("thread_name").__class__))
                    if gl.started_thread_name == quit_thread_name:
                        if gl.started_thread_number is not None:
                            number = gl.started_thread_number + 1
                            if number < 6:
                                self.big_file_signal.emit(([self.model_list[number]], self.file))
                    self.statistic_thread_number(message)
            else:
                self.send_message(message)
        except Exception as e:
            log.error(e)

    def run(self):
        self.assign_task_signal.emit(True)

    def assign_task(self, task: bool):
        if task:
            queue = len(self.files)
            if queue >= 1:
                self.analyse_files()

    def analyse_files(self):
        """拿到一个文件判断大小"""
        self.file = self.files.pop()
        gl.now_file = self.file
        file_size = float(os.path.getsize(self.file)) / float(1024 * 1024)
        if file_size < 300:
            self.DF = GetDf(self.file)
            self.DF.start()

            def over_DF(flag):
                if flag:
                    self.small_file_signal.emit((self.model_list, self.file))

            self.DF.over_signal.connect(over_DF)
        else:
            self.big_file_signal.emit(([self.model_list[0]], self.file))

    def deal_small_file(self, tup: tuple):
        # self.get_data(tup[1], tickets=None)
        """小文件一次开启所有线程"""
        log.warning("处理小文件:{}".format(tup[1]))
        self.send_message(
            {"from": "model_manager", "to": "thread_manager",
             "message": {"thread_name": tup[0],
                         "do_what": "start",
                         "file": tup[1]}
             })

    def deal_big_file(self, tup: tuple):
        """"""
        log.warning("处理大文件:{}".format(tup[1]))
        self.send_message(
            {"from": "model_manager", "to": "thread_manager",
             "message": {"thread_name": tup[0],
                         "do_what": "start",
                         "thread_number": self.model_list.index(tup[0][0]),
                         "file": tup[1]}
             })

    def statistic_thread_number(self, message: dict):
        """分析目前线程的状态，如果所有的线程都结束了那就请求分配任务处理下一个文件"""
        try:
            thread = re.findall(r"'(.+?)'", str(message.get("message").get("thread_name").__class__))
            thread[0] = thread[0].split(".")[-1]
            self.thread_state[thread[0]] = 0
        except Exception as e:
            log.error(e)
        finally:
            """全为0 false 有不为0 true"""
            result = any(self.thread_state.values())
            if result:
                pass
            else:
                """线程结束，处理下一个文件"""
                # 重新修改 thread_state
                for k in self.thread_state:
                    self.thread_state[k] = -1
                log.warning("over_signal")
                import time
                time.sleep(1)
                # ***************************
                self.DF.quit()
                gl.df = None
                # ***************************
                self.assign_task_signal.emit(True)


