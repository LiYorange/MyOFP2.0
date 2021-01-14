# -------------------------------------------------------------------------------
# Name:         post_man
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:  
# -------------------------------------------------------------------------------
from PyQt5.QtCore import QObject, pyqtSignal
from core import my_log
log = my_log.Log(__name__).getlog()


class PostMan(QObject):
    """用于TM与MM M与MM MM与RW之间通讯"""
    send_to_TM = pyqtSignal(dict)
    send_to_MM = pyqtSignal(dict)
    send_to_RW = pyqtSignal(dict)

    def __init__(self):
        super(PostMan, self).__init__()
