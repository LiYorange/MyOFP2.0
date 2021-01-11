# -------------------------------------------------------------------------------
# Name:         draw
# Description:
# Author:       A07567
# Date:         2020/12/17
# Description:  
# -------------------------------------------------------------------------------
import gc
import os
import sys
import time
import traceback
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as AA
from mpl_toolkits.axes_grid1 import host_subplot
import pandas as pd

from core import cores
from core import my_log

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class Draw:
    def __init__(self, data=None, line=False, scatter=False, bar=False, grad=False,
                 x_L=1, y_L=1, r_s=1):
        self.data = data
        self.y_number = 1
        self.li = None
        self.x, self.x_label, self.ys, self.y_labels = None, None, None, None
        self.line_flag, self.scatter_flag, self.bar_flag, self.grid_flag = line, scatter, bar, grad
        self.x_L, self.y_L, self.r_s = x_L, y_L, r_s

        self.tickets = None
        self.en = None
        self.df = pd.DataFrame()
        self.host = None

    def read_df(self):
        # # # 拿到file和tickets
        file = self.data["file_name"]
        self.tickets = [i for i in self.data["y_tickets"]]
        self.tickets.append(self.data["x_ticket"])

        # # # 拿到英文标签，与中文标签对应
        project_name = str(os.path.basename(file)).split(".")[-2].split("_")[0][:5]
        self.en = cores.get_en_tickets("../db/tickets.my", project_name, self.tickets)
        for index, li in zip(range(len(self.en)), self.en):
            if li is not None:
                self.en[index] = li[1]
            else:
                self.en[index] = False

        self.df = cores.read_csv(file=file, tickets=self.tickets)

        if "时间" in self.tickets:
            index = self.tickets.index("时间")
            self.df[self.en[index]] = self.df[self.en[index]].apply(
                lambda x: time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S')))
            self.df["time"] = self.df[self.en[index]].map(lambda x: pd.Timestamp(x, unit="s"))
            self.df.set_index("time", inplace=True)
            self.df = self.df.resample("%ds" % self.r_s).mean()
        else:
            self.df["time"] = pd.date_range('1/1/2021 0:00:00', freq='S', periods=self.df.shape[0])
            self.df.set_index("time", inplace=True)
            self.df = self.df.resample("%ds" % self.r_s).mean()
            self.df.set_index(self.en[-1], inplace=True)
        self.y_number = len(self.tickets[:-1])

    def get_x(self):
        """从df中拿到x"""
        if "时间" == self.tickets[-1]:
            index = self.tickets.index("时间")
            self.df[self.en[index]] = self.df[self.en[index]].map(lambda x: pd.Timestamp(x, unit="s"))
            self.df[self.en[index]] = self.df[self.en[index]].apply(lambda x: x.replace(microsecond=0))
            self.df.set_index(self.en[index], inplace=True)

    def get_y(self):
        """从df中拿到y,y的值也许是多个"""
        if "时间" in self.tickets[:-1]:
            index = self.tickets.index("时间")
            self.df[self.en[index]] = self.df[self.en[index]].map(lambda x: pd.Timestamp(x, unit="s"))
            self.df[self.en[index]] = self.df[self.en[index]].apply(lambda x: x.replace(microsecond=0))
            self.df.set_index(self.en[-1], inplace=True)

    def drawing(self):

        """根据x,y绘图"""
        plt.close()
        if self.line_flag:
            self.plot()
        if self.scatter_flag:
            self.scatter()
        if self.bar_flag:
            self.bar()
        if self.grid_flag:
            plt.grid()
        plt.margins(self.x_L, self.y_L)
        plt.legend()
        plt.show()
        del self.data
        del self.df
        gc.collect()

    def plot(self):
        """绘制折线图"""
        # _ = self.df.plot(kind="line", ax=self.ax)
        for col in self.df.columns:
            plt.plot(self.df.index, self.df[col], label=str(col))

    def scatter(self):
        """绘制散点图"""

        for col in self.df.columns:
            plt.scatter(self.df.index, self.df[col], label=str(col))

    def bar(self):
        """绘制条形图"""
        pass
        _ = self.df.plot(kind="bar")
        # for col in self.df.columns:
        #     plt.bar(x=[x.strftime('%H:%M:%S') for x in self.df.index], height=self.df[col], width=0.1)

    def run(self):
        self.read_df()
        self.get_x()
        self.get_y()
        self.drawing()


if __name__ == '__main__':
    d = Draw()
    d.read_df()
    d.get_x()
    d.get_y()
    d.line_flag = True
    d.scatter_flag = True
    d.bar_flag = True
    d.drawing()
