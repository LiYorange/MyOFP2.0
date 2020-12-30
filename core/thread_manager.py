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
                # self.judge_start(msg.get("thread_name"))
                self.judge_start(message)
            elif msg.get("do_what") == "quit":
                """提出退出线程申请"""
                # self.judge_quit(msg.get("thread_name"))
                self.judge_quit(message)
            else:
                pass
        except KeyError as e:
            log.error(e)

    @staticmethod
    def reedit_message(thread_name: QThread, state, message: dict) -> dict:
        try:
            message = message
            message["from"] = "thread_manager"
            message["to"] = "model_manager"
            message["message"]["thread_name"] = thread_name
            message["message"]["state"] = state
        except Exception as e:
            log.error(e)
        finally:
            return message

    def send_message(self, message):
        # message["from"] = "thread_manager"
        # message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def judge_start(self, message: dict):
        msg: dict = message.get("message")
        thread_names: QThread = msg.get("thread_name")
        for thread_name in thread_names:
            while not thread_name.isRunning():
                thread_name.start()
            result = self.reedit_message(thread_name=thread_name, state="started", message=message)
            self.send_message(result)

    def judge_quit(self, message: dict):
        msg: dict = message.get("message")
        thread_name: QThread = msg.get("thread_name")
        while thread_name.isRunning():
            thread_name.quit()
            # thread_name.wait()
            # 强制退出线程
            thread_name.terminate()
        result = self.reedit_message(thread_name=thread_name, state="quitted", message=message)
        self.send_message(result)
        del thread_name

    def run(self):
        pass

    message = {"from": "model_manager", "to": "thread_manager",
               "message": {"thread_name": "thread_name",
                           "do_what": "start",
                           "thread_number": 1,
                           "file": 1
                           }
               }
