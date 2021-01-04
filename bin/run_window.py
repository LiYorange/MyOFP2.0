# -------------------------------------------------------------------------------
# Name:         run_window
# Description:
# Author:       A07567
# Date:         2020/12/21
# Description:  
# -------------------------------------------------------------------------------

from PySide2.QtWidgets import QWidget, QApplication, QMenu, QAction, QTableWidgetItem, QTableWidget, QHeaderView
from PySide2.QtCore import Qt, QThread
from PySide2.QtGui import QCursor, QColor
from PySide2.QtUiTools import QUiLoader
import os
import sys
import draw_window
from post_man import PostMan
from core import my_log
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class RunWindow(QThread):
    def __init__(self, files: list, postman: PostMan):
        super(RunWindow, self).__init__()
        self.window = QUiLoader().load('../res/ui/run.ui')

        self.post_man = postman
        self.post_man.send_to_RW.connect(self.add_cell)
        self.files = files
        """需要设置列的数量，文件名"""
        self.init_table(header_labels=self.files)
        self.window.window().show()

    def init_table(self, header_labels: list):
        self.window.tableWidget.setColumnCount(len(header_labels))
        self.window.tableWidget.setHorizontalHeaderLabels(header_labels)
        # 设置自适应列宽
        self.window.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
            popMenu = QMenu()
            popMenu.addAction(QAction(u'绘制曲线', self))
            popMenu.addAction(QAction(u'模型原理', self))
            popMenu.addAction(QAction(u'排查方案', self))
            popMenu.triggered[QAction].connect(self.right_menu)
            popMenu.exec_(QCursor.pos())

    def right_menu(self, event):

        if event.text() == "绘制曲线":
            plot_window = draw_window.DrawWindow()
            plot_window.window.show()
        # self.window.tableWidget.setColumnCount(self.window.treeWidget.columnCount() + 1)

    def add_cell(self, message: dict):
        # newItem = QTableWidgetItem("正常")
        try:
            msg = message["message"]
            row = msg["function"]
            col = msg["file"]
            result = msg["result"]
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

    def change_cell_color(self):
        """改变指定行指定列的单元格文本以及颜色"""

    def run(self):
        pass


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
    manage = ModelManager(["../db/60005064_20200930（南鹏岛）.csv", "../db/60005064_20200930（南鹏岛） (2).csv"],
                          [gearbox, generator],
                          postman)
    run_window = RunWindow(["南鹏岛111111111111", "外罗1111111111"], postman)
    manage.start()

    app.exec_()
