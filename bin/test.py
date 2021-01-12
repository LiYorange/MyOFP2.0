# ############################################# 合并df
# import pandas as pd
# import numpy as np
#
# df2 = pd.DataFrame({"id": np.random.random(500000) * 1000000})
# df2.to_csv("test1.csv", sep=',', index=False)
# print(df2.info())
# print("*" * 40)
# df3 = df2.astype("float16", copy=False)
# print(df3.info())
# print("*" * 40)
# df3.to_csv("test2.csv", sep=',', index=False)
# df4 = pd.read_csv("test2.csv", sep=',').astype("float32", copy=False)
# print(df4.info())

# ############################################ 测试元组
# int_li = []
# flot_li = []
# li = [(100, "float"), (200, "int"), (1.1, "float"), (1.2, "float")]
# for i, j in zip(li, range(len(li))):
#     if i[1] == "int":
#         int_li.append((i[0], li.index(i)))
#     elif i[1] == "float":
#         flot_li.append((i[0], li.index(i)))
# print(int_li)
# print(flot_li)

# ############################################ 字符串错误测试
# s = "abc"
# print(s.strip("_")[8])


# ############################################ 字典测试

# d = {"a": 1}
# x = d.get("a")
#
# print(d)

# ############################################ 通讯
# from PySide2.QtCore import QThread, QObject, Signal
# from PySide2.QtWidgets import QApplication
# import sys
# import time
# import my_log
#
#
# class TM(QThread):
#     receive_signal = Signal(dict)
#
#     def __init__(self, M):
#         super(TM, self).__init__()
#         self.M = M
#         self.M.send_signal.connect(self.receive_message)
#
#     def receive_message(self, message):
#         print(message)
#         self.send_message()
#
#     def send_message(self):
#         self.M.receive_signal.emit({"wo": "收到"})
#
#     def run(self):
#         pass
#
#
# class MM(QThread):
#     send_signal = Signal(str)
#
#     def __init__(self, M):
#         super(MM, self).__init__()
#         self.M = M
#         self.M.receive_signal.connect(self.receive_message)
#
#     def send_message(self):
#         self.M.send_signal.emit({"to": "thread_manager", "messgae": {"thread_name": "123"}})
#
#     def receive_message(self, message):
#         print(message)
#
#     def run(self):
#         self.send_message()
#
#
# class Message(QObject):
#     receive_signal = Signal(dict)
#     send_signal = Signal(dict)
#
#     def __init__(self):
#         super(Message, self).__init__()
#         self.receive_signal.connect(self.receive_message)
#         self.send_signal.connect(self.send_message)
#
#     def send_message(self, message: dict):
#        pass
#
#     def receive_message(self, message):
#         pass
#
#
# if __name__ == '__main__':
#     app = QApplication([])
#     m = Message()
#     tm = TM(m)
#     mm = MM(m)
#     tm.start()
#     mm.start()
#     app.exec_()


# import sys
# import logging
#
# logger = logging.getLogger(__name__)
# handler = logging.StreamHandler(stream=sys.stdout)
# logger.addHandler(handler)
#
#
# def handle_exception(exc_type, exc_value, exc_traceback):
#     if issubclass(exc_type, KeyboardInterrupt):
#         sys.__excepthook__(exc_type, exc_value, exc_traceback)
#         return
#
#     logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
#
#
# sys.excepthook = handle_exception
#
# if __name__ == "__main__":
#     print(1/0)

# ---------------------------------------------命令行程序
# import sys
#
# import logging
#
# import traceback
# import pandas as pd
# import matplotlib.pyplot as plt
#
# import matplotlib as mpl  # import matplotlib as mpl
#
# # 设置汉字格式
# # sans-serif就是无衬线字体，是一种通用字体族。
# # 常见的无衬线字体有 Trebuchet MS, Tahoma, Verdana, Arial, Helvetica,SimHei 中文的幼圆、隶书等等
# mpl.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体
# mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
#
#
# def log_except_hook(*exc_info):
#     text = "".join(traceback.format_exception(*exc_info))
#
#     logging.error("Unhandled exception: %s", text)
#
#
# sys.excepthook = log_except_hook
#
# # df = pd.read_csv("../db/日志.csv", sep=',', encoding="gbk")
# # df.plot(kind='barh')
# # plt.show()
# coding:utf-8
# import sys
# import fire
# import matplotlib.pyplot as plt
# sys.argv = ['calculator.py', '1', '2', '3', '--Sum']
#
# builtin_sum = sum
#
#
# # 1. 业务逻辑
# # sum=False，暗示它是一个选项参数 --sum，不提供的时候为 False
# # *nums 暗示它是一个能提供任意数量的位置参数
# def calculator(Sum=False, *nums):
#     """Calculator Program."""
#     print(Sum, nums)  # 输出：True (1, 2, 3)
#     if Sum:
#         plt.plot([1,2,3,4,5])
#         plt.show()
#         result = builtin_sum(nums)
#     else:
#         result = max(nums)
#
#     print(result)  # 基于上文的 ['1', '2', '3', '--sum'] 参数，处理函数为 sum 函数，其结果为 6
#
#
# fire.Fire(calculator)

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
#
# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# df = pd.DataFrame({"x": np.random.randint(low=1, high=10, size=100)})
# x = df.describe(percentiles=[.1, .2, .3, .4, .5, .6, .7, .8, .9])
# x = x.drop(labels=["count", "mean", "std", "min", "max"])
# labels = x.index.tolist()
# sizes = x["x"].tolist()
# plt.subplot(121)
# plt.bar(labels, sizes, width=0.5)
# plt.subplot(122)
# explode = [0.2, 0.1, 0.1, 0.1, 0, 0, 0, 0, 0]
# plt.pie(sizes, labels=labels, explode=explode, autopct='%1.1f', shadow=False, startangle=150)
# plt.show()
# from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
# import matplotlib.pyplot as plt
#
# fig = plt.figure(1)
#
# host = HostAxes(fig, [0.15, 0.1, 0.65, 0.8])
# par1 = ParasiteAxes(host, sharex=host)
# par2 = ParasiteAxes(host, sharex=host)
# host.parasites.append(par1)
# host.parasites.append(par2)
#
# host.set_ylabel('Denstity')
# host.set_xlabel('Distance')
#
# host.axis['right'].set_visible(False)
# par1.axis['right'].set_visible(True)
# par1.set_ylabel('Temperature')
#
# par1.axis['right'].major_ticklabels.set_visible(True)
# par1.axis['right'].label.set_visible(True)
#
# par2.set_ylabel('Velocity')
# offset = (60, 0)
# new_axisline = par2._grid_helper.new_fixed_axis  # "_grid_helper"与"get_grid_helper()"等价，可以代替
#
# # new_axisline = par2.get_grid_helper().new_fixed_axis  # 用"get_grid_helper()"代替，结果一样，区别目前不清楚
# par2.axis['right2'] = new_axisline(loc='right', axes=par2, offset=offset)
#
# fig.add_axes(host)
#
# host.set_xlim(0, 2)
# host.set_ylim(0, 2)
#
# host.set_xlabel('Distance')
# host.set_ylabel('Density')
# host.set_ylabel('Temperature')
#
# p1, = host.plot([0, 1, 2], [0, 1, 2], label="Density")
# p2, = par1.plot([0, 1, 2], [0, 3, 2], label="Temperature")
# p3, = par2.plot([0, 1, 2], [50, 30, 15], label="Velocity")
#
# par1.set_ylim(0, 4)
# par2.set_ylim(1, 60)
#
# host.legend()
# # 轴名称，刻度值的颜色
# host.axis['left'].label.set_color(p1.get_color())
# par1.axis['right'].label.set_color(p2.get_color())
# par2.axis['right2'].label.set_color(p3.get_color())
# par2.axis['right2'].major_ticklabels.set_color(p3.get_color())  # 刻度值颜色
# par2.axis['right2'].set_axisline_style('-|>', size=1.5)  # 轴的形状色
# par2.axis['right2'].line.set_color(p3.get_color())  # 轴的颜色
# plt.show()
import pandas as pd
import numpy as np

df = pd.DataFrame({"A": -np.arange(1,10),
                   "B": np.arange(3, 12)})
df["diff"] = df["A"].diff(1).abs()
print(df)
