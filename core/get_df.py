# -------------------------------------------------------------------------------
# Name:         get_df
# Description:
# Author:       A07567
# Date:         2021/1/11
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread
from core import cores
import gloable_var as gl
import pandas as pd


class GetDf(QThread):
    def __init__(self, file):
        super(GetDf, self).__init__()
        self.df = None
        self.file = file

    def run(self):
        gl.df = None
        gl.df = cores.read_csv(self.file)
        # gl.df.insert(0, "time", pd.to_datetime(self.df[self.tickets[0]]))

    def exit(self, retcode: int = ...):
        print("tuichu")
