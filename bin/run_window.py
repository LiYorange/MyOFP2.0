# -------------------------------------------------------------------------------
# Name:         run_window
# Description:
# Author:       A07567
# Date:         2020/12/21
# Description:  
# -------------------------------------------------------------------------------

from PySide2.QtWidgets import QWidget, QApplication, QMenu, QAction, QTableWidgetItem, QTableWidget, QHeaderView
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor, QColor
from PySide2.QtUiTools import QUiLoader
import draw_window
from post_man import PostMan


class RunWindow(QWidget):
    def __init__(self, files: list):
        super(RunWindow, self).__init__()
        self.window = QUiLoader().load('../res/ui/run.ui')
        self.files = files
        """需要设置列的数量，文件名"""
        self.init_table(header_labels=self.files)

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

    def add_cell(self, row, col, text):
        """添加指定行指定列的单元格文本以及颜色"""
        newItem = QTableWidgetItem(text)
        self.window.tableWidget.setItem(row, col, newItem)
        del newItem

    def change_cell_color(self):
        """改变指定行指定列的单元格文本以及颜色"""


if __name__ == '__main__':
    app = QApplication([])
    run_window = RunWindow(["南鹏岛111111111111", "外罗1111111111", "沙扒1111111", "金湾"])
    run_window.window.show()
    app.exec_()
