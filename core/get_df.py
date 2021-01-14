# -------------------------------------------------------------------------------
# Name:         get_df
# Description:
# Author:       A07567
# Date:         2021/1/11
# Description:  
# -------------------------------------------------------------------------------
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from core import cores
from core import my_log
from core import gloable_var as gl
import pandas as pd
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


class GetDf(QThread):
    over_signal = pyqtSignal(bool)

    def __init__(self, file):
        super(GetDf, self).__init__()
        self.df = None
        self.file = file
        self.over_flag = False
        self.over_signal.connect(self.over)

    def run(self):
        gl.df = None
        gl.df = cores.read_csv(self.file)

        gl.df.insert(0, "time", pd.to_datetime(gl.df["时间"]))
        self.over_signal.emit(True)

    def over(self, flag):
        self.over_flag = flag


# if __name__ == '__main__':
#     app = QApplication([])
#     df = GetDf("../db/60004036_20200930（外罗）.csv")
#     df.start()
#     import time
#
#     while not df.over_flag:
#         print(df.over_flag)
#         time.sleep(1)
#     print(123)
#     app.exec_()
