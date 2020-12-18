# -------------------------------------------------------------------------------
# Name:         launch
# Description:
# Author:       A07567
# Date:         2020/12/16
# Description:  
# -------------------------------------------------------------------------------
import logging
from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtUiTools import QUiLoader


class DrawWindow(QWidget):
    def __init__(self):
        super(DrawWindow, self).__init__()
        self.window = QUiLoader().load('../res/ui/launch.ui')

    def plot(self):
        pass


if __name__ == '__main__':
    app = QApplication([])
    draw_window = DrawWindow()
    draw_window.window.show()
    app.exec_()
