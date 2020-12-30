# -------------------------------------------------------------------------------
# Name:         gearbox
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, Signal
import my_log
import time
import gloable_var as gl
log = my_log.Log(__name__).getlog()


class GearBox(QThread):
    def __init__(self, pm):
        super(GearBox, self).__init__()
        self.postman = pm

    def run(self):
        log.info("齿轮箱开始处理：{}".format(gl.now_file))

        print(time.time())
        self.fun1()
        self.func2()

    def fun1(self):
        time.sleep(1)
        log.info("齿轮箱正在处理")
        self.postman.send_to_MM.emit(
            {"from": "gearbox", "to": "model_manager",
             "message": {"function": 1,
                         "result": True}}
        )

    def func2(self):
        log.info("齿轮箱处理完成")
        self.postman.send_to_MM.emit(
            {"from": "gearbox", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )
