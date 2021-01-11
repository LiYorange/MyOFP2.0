# -------------------------------------------------------------------------------
# Name:         log
# Description:
# Author:       A07567
# Date:         2021/1/9
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtCore import QThread, Signal
from PySide2.QtUiTools import QUiLoader
import json
import csv
import os
import sys
import traceback
from core import my_log

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class Log(QThread):
    log_signal = Signal(tuple)

    def __init__(self):
        super(Log, self).__init__()
        self.window = QUiLoader().load("../res/ui/log.ui")
        self.function_name = None
        self.log_signal.connect(self.receive_mmessage)
        self.number_flag = 0
        self.get_function_name()

    def run(self):
        pass

    def receive_mmessage(self, message):
        dic = {}
        self.number_flag += 1
        # log.error((message["message"]["function"], self.number_flag))
        msg = message["message"]
        file = msg["file_name"]
        dic["file"] = file
        if self.number_flag == 1:
            # file = msg["file_name"]
            # dic["file"] = file
            pass
        elif self.number_flag >= 81:
            self.number_flag = 0

        number = msg["function"]
        fun_name, func_number = self.function_name[number], number
        dic["fun_number"] = func_number
        dic["fun_name"] = fun_name
        fun_result = msg["result"]
        if fun_result == 1:
            result = ("正常", [])
        elif fun_result == 0:
            result = ("异常", msg["details"])
        elif fun_result == -1:
            result = ("缺失标签点", [])
        dic["fun_result"] = result

        self.write_log(logs=dic)

    def write_log(self, logs: dict):
        # 添加文件名
        if self.number_flag == 1:
            self.window.gb_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.window.ge_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.window.pitch_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.window.co_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.window.hy_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.window.se_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.window.summary_plainTextEdit.appendHtml(
                "<p><font color='green'>{}</font></p>".format(logs["file"]))
            self.save_log(file=logs["file"], Type="txt")
        number = logs["fun_number"]
        fun_name = logs["fun_name"]
        fun_result = logs["fun_result"]
        if 0 <= number <= 34:
            if fun_result[0] == "正常":
                self.window.gb_plainTextEdit.appendHtml("<p><font color='green'>{}:正常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:正常'.format(fun_name))
            elif fun_result[0] == "异常":
                self.window.gb_plainTextEdit.appendHtml("<p><font color='red'>{}:异常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:异常'.format(fun_name))

                self.window.summary_plainTextEdit.appendHtml(
                    "<p><font color='red'>{}报警次数：{}</font></p>".format(fun_name, len(fun_result[1])))
                self.save_log(file=logs['file'], Type='csv', text='{}--{}'.format(fun_name, len(fun_result[1])))
                for e in fun_result[1]:
                    self.window.gb_plainTextEdit.appendHtml("<p><font color='red'>{}</font></p>".format(e))
            elif fun_result[0] == "缺失标签点":
                self.window.gb_plainTextEdit.appendHtml("<p><font color='gray'>{}:缺失标签点</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:缺失标签点'.format(fun_name))
        elif 35 <= number <= 47:
            if fun_result[0] == "正常":
                self.window.ge_plainTextEdit.appendHtml("<p><font color='green'>{}:正常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:正常'.format(fun_name))
            elif fun_result[0] == "异常":
                self.window.ge_plainTextEdit.appendHtml("<p><font color='red'>{}:异常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:异常'.format(fun_name))

                self.window.summary_plainTextEdit.appendHtml(
                    "<p><font color='red'>{}报警次数：{}</font></p>".format(fun_name, len(fun_result[1])))
                self.save_log(file=logs['file'], Type='csv', text='{}--{}'.format(fun_name, len(fun_result[1])))
                for e in fun_result[1]:
                    self.window.ge_plainTextEdit.appendHtml("<p><font color='red'>{}</font></p>".format(e))
            elif fun_result[0] == "缺失标签点":
                self.window.ge_plainTextEdit.appendHtml("<p><font color='gray'>{}:缺失标签点</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:缺失标签点'.format(fun_name))
        elif 48 <= number <= 55:
            if fun_result[0] == "正常":
                self.window.pitch_plainTextEdit.appendHtml("<p><font color='green'>{}:正常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:正常'.format(fun_name))
            elif fun_result[0] == "异常":
                self.window.pitch_plainTextEdit.appendHtml("<p><font color='red'>{}:异常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:异常'.format(fun_name))

                self.window.summary_plainTextEdit.appendHtml(
                    "<p><font color='red'>{}报警次数：{}</font></p>".format(fun_name, len(fun_result[1])))
                self.save_log(file=logs['file'], Type='csv', text='{}--{}'.format(fun_name, len(fun_result[1])))
                for e in fun_result[1]:
                    self.window.pitch_plainTextEdit.appendHtml("<p><font color='red'>{}</font></p>".format(e))
            elif fun_result[0] == "缺失标签点":
                self.window.pitch_plainTextEdit.appendHtml("<p><font color='gray'>{}:缺失标签点</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:缺失标签点'.format(fun_name))
        elif 56 <= number <= 62:
            if fun_result[0] == "正常":
                self.window.co_plainTextEdit.appendHtml("<p><font color='green'>{}:正常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:正常'.format(fun_name))
            elif fun_result[0] == "异常":
                self.window.co_plainTextEdit.appendHtml("<p><font color='red'>{}:异常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:异常'.format(fun_name))

                self.window.summary_plainTextEdit.appendHtml(
                    "<p><font color='red'>{}报警次数：{}</font></p>".format(fun_name, len(fun_result[1])))
                self.save_log(file=logs['file'], Type='csv', text='{}--{}'.format(fun_name, len(fun_result[1])))
                for e in fun_result[1]:
                    self.window.co_plainTextEdit.appendHtml("<p><font color='red'>{}</font></p>".format(e))
            elif fun_result[0] == "缺失标签点":
                self.window.co_plainTextEdit.appendHtml("<p><font color='gray'>{}:缺失标签点</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:缺失标签点'.format(fun_name))
        elif 63 <= number <= 73:
            if fun_result[0] == "正常":
                self.window.hy_plainTextEdit.appendHtml("<p><font color='green'>{}:正常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:正常'.format(fun_name))
            elif fun_result[0] == "异常":
                self.window.hy_plainTextEdit.appendHtml("<p><font color='red'>{}:异常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:异常'.format(fun_name))

                self.window.summary_plainTextEdit.appendHtml(
                    "<p><font color='red'>{}报警次数：{}</font></p>".format(fun_name, len(fun_result[1])))
                self.save_log(file=logs['file'], Type='csv', text='{}--{}'.format(fun_name, len(fun_result[1])))
                for e in fun_result[1]:
                    self.window.hy_plainTextEdit.appendHtml("<p><font color='red'>{}</font></p>".format(e))
            elif fun_result[0] == "缺失标签点":
                self.window.hy_plainTextEdit.appendHtml("<p><font color='gray'>{}:缺失标签点</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:缺失标签点'.format(fun_name))
        elif 74 <= number <= 81:
            if fun_result[0] == "正常":
                self.window.se_plainTextEdit.appendHtml("<p><font color='green'>{}:正常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:正常'.format(fun_name))
            elif fun_result[0] == "异常":
                self.window.se_plainTextEdit.appendHtml("<p><font color='red'>{}:异常</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:异常'.format(fun_name))

                self.window.summary_plainTextEdit.appendHtml(
                    "<p><font color='red'>{}报警次数：{}</font></p>".format(fun_name, len(fun_result[1])))
                self.save_log(file=logs['file'], Type='csv', text='{}--{}'.format(fun_name, len(fun_result[1])))
                for e in fun_result[1]:
                    self.window.se_plainTextEdit.appendHtml("<p><font color='red'>{}</font></p>".format(e))
            elif fun_result[0] == "缺失标签点":
                self.window.se_plainTextEdit.appendHtml("<p><font color='gray'>{}:缺失标签点</font></p>".format(fun_name))
                self.save_log(file=logs['file'], text='{}:缺失标签点'.format(fun_name))

    def get_function_name(self):
        f = open("../db/function_tickets.json", 'r', encoding='utf8')
        dic = dict(json.load(f))
        self.function_name = list(dic.keys())
        f.close()

    def save_log(self, file="E:/桌面/Py/MyOFP2.0/db/60004036_20200930（外罗）.csv", Type='txt', text=''):

        try:
            path = os.getcwd() + "\\log\\{}".format(os.path.basename(file).split(".")[0])
            if not os.path.exists(path):
                os.makedirs(path)
            if Type == "txt":
                f = open(path + r"/日志.txt", mode="a+", encoding="gbk")
                f.write("\n{}".format(text))
                f.close()
            elif Type == "csv":
                if os.path.isfile(path + r"/日志.csv"):
                    f = open(path + r"/日志.csv", mode="a+", encoding="gbk", newline='')
                    csv_writer = csv.writer(f)
                    # csv_writer.writerow(['模型', '报警次数'])
                    text = text.split("--")
                    csv_writer.writerow(text)
                else:
                    f = open(path + r"/日志.csv", mode="a+", encoding="gbk", newline='')
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(['模型', '报警次数'])
                    text = text.split("--")
                    csv_writer.writerow(text)
                f.close()
        except Exception as e:
            log.error(e)


if __name__ == '__main__':
    app = QApplication([])
    win = Log()
    win.window.show()
    app.exec_()
