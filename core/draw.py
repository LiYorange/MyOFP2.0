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
import pyqtgraph as pg
import matplotlib.pyplot as plt
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
    def __init__(self, data=None, line=False, scatter=False, bar=False, subplot=False, grad=False,
                 x_LL=0.4, x_UL=1.2, y_LL=0.4, y_UL=1.2):
        self.data = data
        self.x, self.x_label, self.ys, self.y_labels = None, None, None, None
        self.line_flag, self.scatter_flag, self.bar_flag, self.subplot_flag, self.grid_flag = line, scatter, bar, subplot, grad
        self.x_LL, self.x_UL, self.y_LL, self.y_UL = x_LL, x_UL, y_LL, y_UL

    def read_df(self):
        data = {
            "file_name": str,
            "x_ticket": str,
            "y_tickets": list
        }
        file = self.data["file_name"]
        tickets = [i for i in self.data["y_tickets"]]
        tickets.append(self.data["x_ticket"])
        project_name = str(os.path.basename(file)).split(".")[-2].split("_")[0][:5]
        en = cores.get_en_tickets("../db/tickets.my", project_name, tickets)
        for index, li in zip(range(len(en)), en):
            if li is not None:
                en[index] = li[1]
            else:
                en[index] = False
        df = cores.read_csv(file=file, tickets=tickets)
        if tickets[-1] == "时间":
            df[en[-1]] = df[en[-1]].apply(lambda x: time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S')))
            df[en[-1]] = df[en[-1]].map(lambda x: pd.Timestamp(x, unit="s"))
        """拿到file读取为df"""
        self.data = {
            "title": "齿轮箱主轴承温度时间图",
            "x_label": tickets[-1],
            "y_label": str(tickets[0])[-2:],
            "x_data": {"label": [en[-1]],
                       "data": df[en[-1]]
                       },
            "y_data": {"label": tickets[:-1],
                       "data": [df[en[:-1]]]
                       }
        }

    def get_x(self):
        """从df中拿到x"""
        try:
            self.x = self.data["x_data"]["data"]
            self.x_label = self.data["x_data"]["label"]
        except Exception as e:
            log.error(e)

    def get_y(self):
        """从df中拿到y,y的值也许是多个"""
        try:
            self.ys = self.data["y_data"]["data"]
            self.y_labels = self.data["y_data"]["label"]
        except Exception as e:
            log.error(e)

    def drawing(self):
        plt.close()
        gc.collect()
        """根据x,y绘图"""
        if self.line_flag:
            self.plot()
        if self.scatter_flag:
            self.scatter()
        if self.bar_flag:
            self.bar()
        if self.grid_flag:
            plt.grid()

        # w = pg.plot(data=self.x, axisItems={'bottom': pg.DateAxisItem()})
        # w.showGrid(x=True, y=True)
        # w.show()

        # plt.xlim(left=self.x.min() * self.x_LL, right=self.x.max() * self.x_UL)
        # plt.ylim(bottom=list(map(min, self.ys))[0] * self.y_LL, top=list(map(max, self.ys))[0] * self.y_UL)
        plt.legend()
        del self.data
        gc.collect()
        plt.show()

    def plot(self):
        """绘制折线图"""
        for y_data, y_label in zip(self.ys, self.y_labels):
            plt.plot(self.x, y_data, label=y_label)

        plt.xlabel(self.x_label)

    def scatter(self):
        """绘制散点图"""
        for y_data, y_label in zip(self.ys, self.y_labels):
            plt.scatter(self.x, y_data, label=y_label)
        plt.xlabel(self.x_label)

    def bar(self):
        """绘制条形图"""
        for y_data, y_label in zip(self.ys, self.y_labels):
            plt.bar(self.x, y_data, label=y_label, width=0.5)
        plt.xlabel(self.x_label)

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

    # labels = ['娱乐', '育儿', '饮食', '房贷', '交通', '其它']
    # sizes = [2, 5, 12, 70, 2, 9]
    # explode = (0, 0, 0, 0.1, 0, 0)
    # plt.plot([1, 2, 3, 4, 5])
    # plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=False, startangle=150)
    # plt.title("饼图示例-8月份家庭支出")
    # plt.show()

    # # 画第1个图：折线图
    # x = np.arange(1, 100)
    # plt.subplot(221)
    # plt.plot(x, x * x)
    #
    # # 画第2个图：散点图
    # plt.subplot(222)
    # plt.scatter(np.arange(0, 10), np.random.rand(10))
    #
    # # 画第3个图：饼图
    # plt.subplot(223)
    # plt.pie(x=[15, 30, 45, 10], labels=list('ABCD'), autopct='%.0f', explode=[0, 0.05, 0, 0])
    #
    # # 画第4个图：条形图 plt.subplot(224) y = range(1, 17) plt.bar(np.arange(16), y, alpha=0.5, width=0.3, color='yellow',
    # edgecolor='red', label='The First Bar', lw=1) plt.bar(np.arange(16) + 0.4, y, alpha=0.2, width=0.3,
    # color='green', edgecolor='blue', label='The Second Bar', lw=1) plt.legend(loc='upper left') plt.show()
