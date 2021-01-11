import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
import os
import sys
import traceback
from core import my_log
log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook

class WebWindow(QMainWindow):
    def __init__(self, url, parent=None):
        super(WebWindow, self).__init__(parent)
        self.resize(900, 600)
        # self.showMaximized()
        self.setWindowTitle("模型原理及排查方案")
        self.setFont(QFont("宋体", 18))

        self.url = os.path.join(os.path.abspath(os.path.dirname(os.getcwd())) + "\\res\\html", url + ".html")
        self.url = "/".join(self.url.split("\\"))
        self.view = QWebEngineView()
        # self.view.load(QUrl("https://www.baidu.com"))
        # print(os.path.abspath("../db/2.叶轮转速超速.html"))
        self.view.load(QUrl(QFileInfo(self.url).absoluteFilePath()))
        # self.view.load(QUrl("C:/Users/A07417/PycharmProjects/MyOFP2.0/db/2.叶轮转速超速.html"))
        # self.view.show()
        self.setCentralWidget(self.view)


if __name__ == "__main__":
    app = QApplication([])
    # open("../res/html/齿轮箱A1口压力异常.html")
    window = WebWindow('../res/html/齿轮箱A1口压力.html')
    window.showMaximized()
    sys.exit(app.exec_())
