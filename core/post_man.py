# -------------------------------------------------------------------------------
# Name:         post_man
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtCore import QObject, Signal
import sys
sys.path.append("..")
from core import my_log
log = my_log.Log(__name__).getlog()


class PostMan(QObject):
    """用于TM与MM M与MM MM与RW之间通讯"""
    send_to_TM = Signal(dict)
    send_to_MM = Signal(dict)
    send_to_RW = Signal(dict)

    def __init__(self):
        super(PostMan, self).__init__()
