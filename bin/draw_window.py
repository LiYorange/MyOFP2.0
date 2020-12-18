# -------------------------------------------------------------------------------
# Name:         draw
# Description:
# Author:       A07567
# Date:         2020/12/17
# Description:  
# -------------------------------------------------------------------------------

import logging
from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtUiTools import QUiLoader
from functools import partial
import matplotlib.pylab as plt


class DrawWindow(QWidget):
    """绘图界面"""

    def __init__(self):
        super(DrawWindow, self).__init__()
        self.window = QUiLoader().load('../res/ui/draw.ui')
        self.window.data_tickets_listWidget.itemClicked.connect(partial(self.itemClicked))
        self.window.x_listWidget.itemClicked.connect(partial(self.itemClicked))
        self.window.y_listWidget.itemClicked.connect(partial(self.itemClicked))
        self.window.plot_pushButton.clicked.connect(self.plot)

    def plot(self):
        """拿到数据，绘图"""
        plt.plot([1, 2, 3, 4, 5])
        plt.show()

    def itemClicked(self, QListWidgetItem):
        """ itemClicked(self, QListWidgetItem) [signal] """
        print(QListWidgetItem.text())


if __name__ == '__main__':
    app = QApplication([])
    draw_window = DrawWindow()
    draw_window.window.show()
    app.exec_()
