# -------------------------------------------------------------------------------
# Name:         about_window
# Description:
# Author:       A07567
# Date:         2021/1/12
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from res.icon import main_icons


class AboutWindow:
    def __init__(self):
        self.window = QUiLoader().load('../res/ui/about.ui')


if __name__ == '__main__':
    app = QApplication([])
    win = AboutWindow()
    win.window.show()
    app.exec_()
