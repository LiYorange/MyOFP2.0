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

d = {"a": 1}
x = d.get("a")

print(d)

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
