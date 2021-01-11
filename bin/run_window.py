# -------------------------------------------------------------------------------
# Name:         run_window
# Description:
# Author:       A07567
# Date:         2020/12/21
# Description:  
# -------------------------------------------------------------------------------
import psutil
from PySide2.QtWidgets import QWidget, QApplication, QMenu, QAction, QTableWidgetItem, QTableWidget, QHeaderView
from PySide2.QtCore import Qt, QThread, QTimer
from PySide2.QtGui import QCursor, QColor
from PySide2.QtUiTools import QUiLoader
import os
import sys
import draw_window
import web_window
from post_man import PostMan
import log_window
from core import my_log
import traceback
import json

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class RunWindow(QThread):
    def __init__(self, files: list, PM: PostMan):
        super(RunWindow, self).__init__()
        self.window = QUiLoader().load('../res/ui/run.ui')
        self.post_man = PM
        self.log_window = log_window.Log()
        self.log_window.start()
        self.post_man.send_to_RW.connect(self.receive_message)
        self.files = files
        self.right_file, self.right_function = None, None
        self.web = None
        """需要设置列的数量，文件名"""
        self.init_table(header_labels=self.files)
        self.window.log_pushButton.clicked.connect(self.log)
        # 进度条
        self.progress_total_number = len(self.files) * 81
        self.progress_now_number = 1
        # 状态栏
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status_bar)
        self.timer.start(1000)
        self.window.window().show()

    def init_table(self, header_labels: list):
        self.window.tableWidget.setColumnCount(len(header_labels))
        self.window.tableWidget.setHorizontalHeaderLabels(header_labels)
        # 设置自适应列宽
        # self.window.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.window.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # QTableWidget
        # 右击菜单
        self.window.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.window.tableWidget.customContextMenuRequested.connect(self.tableWidget_right_click)  # 绑定事件
        # 单机事件

    def tableWidget_right_click(self, pos):
        item = self.window.tableWidget.currentItem()
        item1 = self.window.tableWidget.itemAt(pos)
        if item is not None and item1 is not None:
            col = self.window.tableWidget.currentItem().column()
            row = self.window.tableWidget.currentItem().row()
            self.right_file = self.window.tableWidget.horizontalHeaderItem(col).text()
            self.right_function = self.window.tableWidget.verticalHeaderItem(row).text()
            popMenu = QMenu()
            popMenu.addAction(QAction(u'绘制曲线', self))
            popMenu.addAction(QAction(u'模型原理', self))
            popMenu.addAction(QAction(u'排查方案', self))
            popMenu.triggered[QAction].connect(self.right_menu)
            popMenu.exec_(QCursor.pos())

    def right_menu(self, event):
        if event.text() == "绘制曲线":
            tickets = self.get_plot_tickets(self.right_function)
            plot_window = draw_window.DrawWindow(self.right_file, tickets)
            plot_window.window.show()
            del tickets
        elif event.text() == "模型原理" or event.text() == "排查方案":
            self.web = web_window.WebWindow(self.right_function)
            self.web.show()

    def add_cell(self, row, col, result):
        try:
            newItem = QTableWidgetItem()
            if result == -1:
                newItem = QTableWidgetItem("缺失")
                newItem.setTextColor(QColor('gray'))
            elif result == 0:
                newItem = QTableWidgetItem("异常")
                newItem.setTextColor(QColor('red'))
            elif result == 1:
                newItem = QTableWidgetItem("正常")
                newItem.setTextColor(QColor('green'))
            self.window.tableWidget.setItem(row, col, newItem)
            del result
            del row
            del col
            del newItem
        except Exception as e:
            log.error(e)

    def progress(self, value: int):
        self.window.progressBar.setValue(value)
        # if value >= 100:
        #     self.progress_now_number = 1

    def update_status_bar(self):
        self.window.statusbar.showMessage(self.get_memory())

    @staticmethod
    def get_plot_tickets(function_name):
        f = open("../db/function_tickets.json", 'r', encoding='utf8')
        tickets_data = dict(json.load(f))
        d = tickets_data.get(function_name)
        return d

    def receive_message(self, message: dict):
        """收到消息"""
        msg = message["message"]
        row = msg["function"]
        col = msg["file"]
        result = msg["result"]
        self.add_cell(row, col, result)
        self.log_window.log_signal.emit(message)
        self.progress_now_number += 1
        value = float(self.progress_now_number / self.progress_total_number) * 100
        self.progress(value)

    def run(self):
        pass

    def close(self, event):
        print(event)

    def log(self):
        self.log_window.window.show()

    @staticmethod
    def get_memory():
        mem = psutil.virtual_memory()
        # round方法进行四舍五入，然后转换成字符串 字节/1024得到kb 再/1024得到M
        total = str(round(mem.total / 1024 / 1024))
        used = str(round(mem.used / 1024 / 1024))
        use_per = str(round(mem.percent))
        free = str(round(mem.free / 1024 / 1024))
        process = psutil.Process(os.getpid())
        memInfo = process.memory_info()
        me = str(round(memInfo.rss / 1024 / 1024))
        message = "本机内存：{}M，已使用：{}M({}%)，本程序占用：{}M,可使用:{}M".format(total, used, use_per, me, free)
        return message


if __name__ == '__main__':
    from thread_manager import ThreadManage
    from gearbox import GearBox
    from generator import Generator
    from model_manager import ModelManager
    import time

    app = QApplication([])
    postman = PostMan()
    # 创建线程管理者，并雇佣postman
    thread_manager = ThreadManage(postman)
    thread_manager.start()
    gearbox = GearBox(postman)
    generator = Generator(postman)
    # 创建模块管理者，并雇佣postman
    manage = ModelManager(["../db/60005064_20200930（南鹏岛）.csv"],
                          [gearbox, generator],
                          postman)

    run_window = RunWindow(["南鹏岛111111111111"], postman)
    manage.start()

    app.exec_()
