from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import uic
import os
import sys
import traceback
from core import my_log

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class WebWindow:
    def __init__(self, url):
        self.window = uic.loadUi('../res/ui/web.ui')

        self.window.setFont(QFont("宋体", 18))
        self.window.centralwidget.resize(900, 600)
        self.url = os.path.join(os.path.abspath(os.path.dirname(os.getcwd())) + "\\res\\html", url + ".html")
        # self.url = "/".join(self.url.split("\\"))
        self.view = QWebEngineView()
        self.view.load(QUrl(QFileInfo(self.url).absoluteFilePath()))
        self.window.setCentralWidget(self.view)


if __name__ == "__main__":
    app = QApplication([])
    # open("../res/html/齿轮箱A1口压力异常.html")
    window = WebWindow('齿轮箱A1口压力')
    window.window.showMaximized()
    sys.exit(app.exec_())
