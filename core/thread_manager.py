# -------------------------------------------------------------------------------
# Name:         thread_manager
# Description:
# Author:       A07567
# Date:         2020/12/25
# Description:  线程管理，负责开关线程
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, QObject, Signal
import sys
import my_log

log = my_log.Log(__name__).getlog()


class ThreadManage(QObject):
    message_signal = Signal()

    def __init__(self):
        super(ThreadManage, self).__init__()

    def receive_message(self, **message):
        """
        收到消息，根据消息类型决定开启或退出线程
        """
        try:
            msg = message['message']
            if msg.get("do_what") == "start":
                self.judge_start(msg.get("thread_name"), 1)
                """提出开启线程申请"""
            elif msg.get("do_what") == "quit":
                """提出退出线程申请"""
            else:
                pass
        except KeyError as e:
            log.error(e)

    def judge_start(self, thread_name: QThread, live: bool):
        if thread_name.isRunning():
            pass
        else:
            thread_name.start()


class GearBox(QThread):
    def __init__(self):
        super(GearBox, self).__init__()
        pass

    def run(self):
        for i in range(10):
            print(i)


class Manager:
    def __init__(self):
        pass

    def run(self, **kwargs):
        self.thread_manager = ThreadManage()
        self.thread_manager.receive_message(**kwargs)
        import time
        time.sleep(5)


if __name__ == '__main__':
    gearbox = GearBox()
    manage = Manager()
    manage.run(message={"thread_name": gearbox, "do_what": "start"})
