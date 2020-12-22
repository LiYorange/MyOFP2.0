# -------------------------------------------------------------------------------
# Name:         run_window
# Description:
# Author:       A07567
# Date:         2020/12/21
# Description:  
# -------------------------------------------------------------------------------

from PySide2.QtWidgets import QWidget, QApplication, QMenu, QAction, QTreeWidgetItem, QTreeWidget
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from PySide2.QtUiTools import QUiLoader


class RunWindow(QWidget):
    def __init__(self):
        super(RunWindow, self).__init__()
        self.window = QUiLoader().load('../res/ui/run.ui')
        """需要设置列的数量，文件名"""
        self.window.treeWidget.setColumnCount(4)
        self.window.treeWidget.setHeaderLabels(['模型', '文件1', '文件2', '文件3'])
        self.window.treeWidget.setColumnWidth(0, 200)
        # 右击菜单
        self.window.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.window.treeWidget.customContextMenuRequested.connect(self.treeWidgetItem_right_click)  # 绑定事件
        # 单机事件
        self.window.treeWidget.itemClicked['QTreeWidgetItem*', 'int'].connect(self.selectItem)
        # 修改事件
        self.window.treeWidget.itemSelectionChanged.connect(self.selectitem)
        print(self.window.treeWidget.topLevelItem(0).columnCount())


    def treeWidgetItem_right_click(self, pos):
        item = self.window.treeWidget.currentItem()
        item1 = self.window.treeWidget.itemAt(pos)
        if item is not None and item1 is not None:
            popMenu = QMenu()
            popMenu.addAction(QAction(u'绘制曲线', self))
            popMenu.addAction(QAction(u'模型原理', self))
            popMenu.addAction(QAction(u'排查方案', self))
            popMenu.triggered[QAction].connect(self.right_menu)
            popMenu.exec_(QCursor.pos())

    def right_menu(self, event):
        print(event)
        self.window.treeWidget.setColumnCount(self.window.treeWidget.columnCount() + 1)

    def selectItem(self, item, column):
        # print(item.checkState(1), item.text(0))
        print(item.text(0))

    def selectitem(self):
        for ii in self.window.treeWidget.selectedItems():
            ii.setText(2, "你好")
            ii.setForeground(2, Qt.green)  # 可将字体颜色变为绿色,更详细的设置请看QBrush

    def change_cell(self):
        """改变指定行指定列的单元格文本以及颜色"""


if __name__ == '__main__':
    app = QApplication([])
    draw_window = RunWindow()
    draw_window.window.show()
    app.exec_()
