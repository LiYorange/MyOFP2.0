# -------------------------------------------------------------------------------
# Name:         about_window
# Description:
# Author:       A07567
# Date:         2021/1/12
# Description:  
# -------------------------------------------------------------------------------
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from conf import main_icons


class AboutWindow:
    def __init__(self):
        self.window = uic.loadUi('../res/ui/about.ui')


if __name__ == '__main__':
    app = QApplication([])
    win = AboutWindow()
    win.window.show()
    app.exec_()
