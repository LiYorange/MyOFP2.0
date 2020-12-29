# -------------------------------------------------------------------------------
# Name:         thread_manager
# Description:
# Author:       A07567
# Date:         2020/12/25
# Description:  线程管理，负责开关线程
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, QObject, Signal, QMutex
from PySide2.QtWidgets import QApplication
import sys
import time
import os
import my_log

qm1 = QMutex()
log = my_log.Log(__name__).getlog()


class ThreadManage(QThread):

    def __init__(self, pm):
        super(ThreadManage, self).__init__()
        self.postman = pm
        self.postman.send_to_TM.connect(self.receive_message)

    def receive_message(self, message):
        """
        收到消息，根据消息类型决定开启或退出线程
        """
        msg = message.get("message")
        log.info("from:{},to:{},do_what:{}".format(message.get("from"), message.get("to"),
                                                   [msg.get("thread_name"), msg.get("do_what")]))
        try:
            if msg.get("do_what") == "start":
                """提出开启线程申请"""
                self.judge_start(msg.get("thread_name"))
            elif msg.get("do_what") == "quit":
                """提出退出线程申请"""
                self.judge_quit(msg.get("thread_name"))
            else:
                pass
        except KeyError as e:
            log.error(e)

    def send_message(self, message):
        # message["from"] = "thread_manager"
        # message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def judge_start(self, thread_names: QThread):
        for thread_name in thread_names:
            while not thread_name.isRunning():
                thread_name.start()
            self.send_message({"from": "thread_manager", "to": "model_manager",
                               "message": {"thread_name": thread_name,
                                           "state": "started"}
                               })

    def judge_quit(self, thread_name: QThread):
        while thread_name.isRunning():
            thread_name.quit()
            # thread_name.wait()
            # 强制退出线程
            thread_name.terminate()
        self.send_message({"from": "thread_manager", "to": "model_manager",
                           "message": {"thread_name": thread_name,
                                       "state": "quitted"}
                           })
        del thread_name

    def run(self):
        pass


class GearBox(QThread):
    def __init__(self, pm):
        super(GearBox, self).__init__()
        self.postman = pm

    def run(self):
        log.info("齿轮箱开始")
        self.fun1()
        self.func2()

    def fun1(self):
        log.info("齿轮箱正在处理")

    def func2(self):
        log.info("齿轮箱处理完成")
        self.postman.send_to_MM.emit(
            {"from": "gearbox", "to": "model_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )


class Generator(QThread):
    def __init__(self, pm):
        super(Generator, self).__init__()
        self.postman = pm

    def run(self):
        log.info("发电机开始")
        self.fun1()
        self.func2()

    def fun1(self):
        log.info("发电机正在处理")

    def func2(self):
        log.info("发电机处理完成")
        self.postman.send_to_MM.emit(
            {"from": "generator", "to": "model_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )


class ModelManager(QThread):

    def __init__(self, files: list, model_list: list, pm):
        """
        :param files: 需要处理的文件堆
        :param model_list:需要管理的模块
        :param pm: 雇佣的postman
        """
        super(ModelManager, self).__init__()
        self.files = files
        self.model_list = model_list
        self.postman = pm
        self.postman.send_to_MM.connect(self.receive_message)
        # 当前需要处理的文件
        self.file = None

    def send_message(self, message):
        """用于与TM通讯，雇佣postman"""
        message["from"] = "model_manager"
        message["to"] = "thread_manager"
        # 发送消息
        self.postman.send_to_TM.emit(message)

    def analyse_receive_message(self):
        """处理收到的消息"""

    def receive_message(self, message: dict):
        """分发收到的消息"""
        come_from = message.get("from")
        if come_from != "thread_manager" and come_from is not None:
            log.info("from:{},to:{},thread_name:{},do_what:{}".format(
                message.get("from"), message.get("to"),
                message.get("message").get("thread_name"),
                message.get("message").get("do_what")))
            self.send_message(message)
        else:
            log.info("from:{},to:{},[thread_name{},state:{}]".format(
                message.get("from"), message.get("to"),
                message.get("message").get("thread_name"),
                message.get("message").get("state")))

    def run(self):
        self.analyse_files()

    def analyse_files(self):
        """拿到一个文件判断大小"""
        self.file = self.files.pop()
        file_size = float(os.path.getsize(self.file)) / float(1024 * 1024)
        if file_size < 300:
            self.deal_small_file(self.file)
        else:
            self.deal_big_file(self.file)

    def deal_small_file(self, file):
        """"""
        self.send_message(
            {"from": "model_manager", "to": "thread_manager",
             "message": {"thread_name": self.model_list,
                         "do_what": "start"}
             }
        )

    def deal_big_file(self):
        """"""
        pass


class PostMan(QObject):
    """用于TM与MM M与MM之间通讯"""
    send_to_TM = Signal(dict)
    send_to_MM = Signal(dict)

    def __init__(self):
        super(PostMan, self).__init__()


if __name__ == '__main__':
    app = QApplication([])
    # 创建postman用于投递消息
    postman = PostMan()
    # 创建线程管理者，并雇佣postman
    thread_manager = ThreadManage(postman)
    thread_manager.start()
    gearbox = GearBox(postman)
    generator = Generator(postman)
    # 创建模块管理者，并雇佣postman
    manage = ModelManager(["../db/60005036_20200930南鹏岛.csv", "../db/60004036_20200930（外罗）.csv"], [gearbox, generator],
                          postman)

    manage.start()
    app.exec_()
