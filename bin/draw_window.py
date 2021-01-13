# -------------------------------------------------------------------------------
# Name:         draw
# Description:
# Author:       A07567
# Date:         2020/12/17
# Description:  
# -------------------------------------------------------------------------------

import logging
from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtCore import QTimer
from PySide2.QtUiTools import QUiLoader
from PyQt5 import uic
from functools import partial

import psutil
import os
import sys
sys.path.append('..')
from conf import config_draw_setting
from core import draw
from conf import main_icons
from core import my_log
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class DrawWindow(QWidget):
    """绘图界面"""

    def __init__(self, file, tickets: list):
        """
        """
        super(DrawWindow, self).__init__()
        self.window = uic.loadUi('../res/ui/draw.ui')
        # self.window = QUiLoader().load('../res/ui/draw.ui')
        self.file = file
        self.window.data_tickets_groupBox.setTitle(str("当前文件：" + file))

        # # ---------------------初始化绘图参数
        default_setting = config_draw_setting.read_cfg()
        # # #
        try:
            self.line = default_setting[0].get("line")
            self.scatter = default_setting[0].get("scatter")
            self.bar = default_setting[0].get("bar")
            self.grid = default_setting[0].get("grid")
            # # #
            self.x_L = default_setting[1].get("x_L")
            self.y_L = default_setting[1].get("y_L")
            self.r_s = default_setting[1].get("r_s")
        except Exception as e:
            log.error(e)
        # 初始化listWidget
        self.init_listWidget(tickets)
        # 初始化checkBox
        self.init_checkBox()
        # 初始化doubleSpinBox
        self.init_doubleSpinBox()

        # 初始化button
        self.init_button()
        # x轴flag
        self.x_flag = False
        # # ---------------------初始化绘图参数结束
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status_bar)
        self.timer.start(1000)
        self.window.closeEvent = self.closeEvent

        # self.window.data_tickets_listWidget.installEventFilter(self.window)

    def init_listWidget(self, tickets):
        self.window.data_tickets_listWidget.addItems(tickets)
        self.window.data_tickets_listWidget.itemClicked.connect(partial(self.itemClicked))
        # self.window.x_listWidget.itemClicked.connect(partial(self.itemClicked))
        # x_拖入
        self.window.x_listWidget.itemChanged.connect(self.drop_in_x)
        # x_拖出
        self.window.x_listWidget.currentItemChanged.connect(self.change_x_flag)

        self.window.y_listWidget.itemClicked.connect(partial(self.itemClicked))
        self.window.plot_pushButton.clicked.connect(self.plot)

    def init_checkBox(self):
        """"""
        self.window.line_checkBox.setChecked(self.line)
        self.window.scatter_checkBox.setChecked(self.scatter)
        self.window.bar_checkBox.setChecked(self.bar)
        self.window.grid_checkBox.setChecked(self.grid)

        self.window.line_checkBox.stateChanged.connect(lambda: self.btn_state(self.window.line_checkBox))
        self.window.scatter_checkBox.stateChanged.connect(lambda: self.btn_state(self.window.scatter_checkBox))
        self.window.bar_checkBox.stateChanged.connect(lambda: self.btn_state(self.window.bar_checkBox))
        self.window.grid_checkBox.stateChanged.connect(lambda: self.btn_state(self.window.grid_checkBox))

    def init_doubleSpinBox(self):
        self.window.x_L_doubleSpinBox.setValue(self.x_L)
        self.window.y_L_doubleSpinBox.setValue(self.y_L)
        self.window.r_s_spinBox.setValue(self.r_s)

        self.window.x_L_doubleSpinBox.valueChanged.connect(self.dsb_value)

        self.window.y_L_doubleSpinBox.valueChanged.connect(self.dsb_value)

        self.window.r_s_spinBox.valueChanged.connect(self.dsb_value)


    def init_button(self):
        self.window.reset_pushButton.clicked.connect(self.reset)

    def dsb_value(self):

        self.x_L = self.window.x_L_doubleSpinBox.value()

        self.y_L = self.window.y_L_doubleSpinBox.value()
        self.r_s = self.window.r_s_spinBox.value()
        config_draw_setting.write_cfg(
            dic={
                "DrawSetting": {
                    "x_L": self.x_L,
                    "y_L": self.y_L,
                    "r_s": self.r_s,
                }
            })

    def btn_state(self, btn):
        self.line = self.window.line_checkBox.isChecked()
        self.scatter = self.window.scatter_checkBox.isChecked()
        self.bar = self.window.bar_checkBox.isChecked()
        self.grid = self.window.grid_checkBox.isChecked()
        config_draw_setting.write_cfg(
            dic={
                "DrawType": {
                    "line": self.line,
                    "scatter": self.scatter,
                    "bar": self.bar,
                    "grid": self.grid,
                }})

    @staticmethod
    def change_SB_state(sbs: list, flag: bool):
        if flag:
            [sb.setEnabled(True) for sb in sbs]
        else:
            [sb.setEnabled(False) for sb in sbs]

    def reset(self):
        default_setting = config_draw_setting.read_cfg(True)
        # # #
        try:
            self.line = default_setting[0].get("line")
            self.scatter = default_setting[0].get("scatter")
            self.bar = default_setting[0].get("bar")
            self.grid = default_setting[0].get("grid")
            self.window.line_checkBox.setChecked(default_setting[0].get("line"))
            self.window.scatter_checkBox.setChecked(default_setting[0].get("scatter"))
            self.window.bar_checkBox.setChecked(default_setting[0].get("bar"))
            self.window.grid_checkBox.setChecked(default_setting[0].get("grid"))

            self.x_L = default_setting[1].get("x_L")
            self.y_L = default_setting[1].get("y_L")
            self.window.x_L_doubleSpinBox.setValue(default_setting[1].get("x_L"))
            self.window.y_L_doubleSpinBox.setValue(default_setting[1].get("y_L"))
        except Exception as e:
            log.error(e)

    def plot(self):
        if self.window.x_listWidget.count() == 1 and self.window.y_listWidget.count() >= 1:
            y_tickets = [self.window.y_listWidget.item(i).text() for i in range(self.window.y_listWidget.count())]
            x_ticket = self.window.x_listWidget.item(0).text()
            win = draw.Draw(
                            data={
                                "file_name": self.file,
                                "x_ticket": x_ticket,
                                "y_tickets": y_tickets
                            },
                            line=self.line, scatter=self.scatter, bar=self.bar, grad=self.grid,
                            x_L=self.x_L, y_L=self.y_L, r_s=self.r_s)
            win.run()
            del win
            import gc
            gc.collect()

    def itemClicked(self, QListWidgetItem):
        """ itemClicked(self, QListWidgetItem) [signal] """
        print(QListWidgetItem.text())

    def drop_in_x(self):
        self.window.x_listWidget.setDragEnabled(False)
        self.window.x_listWidget.setDragDropMode(self.window.x_listWidget.DragOnly)

    def change_x_flag(self):
        self.window.x_listWidget.setDragEnabled(True)
        self.window.x_listWidget.setDragDropMode(self.window.x_listWidget.DragDrop)

    def update_status_bar(self):
        self.window.statusbar.showMessage(self.get_memory())

    @staticmethod
    def get_memory():
        mem = psutil.virtual_memory()
        # round方法进行四舍五入，然后转换成字符串 字节/1024得到kb 再/1024得到M
        total = str(round(mem.total / 1024 / 1024))
        used = str(round(mem.used / 1024 / 1024))
        use_per = str(round(mem.percent))
        free = str(round(mem.free / 1024 / 1024))
        process = psutil.Process(os.getpid())
        memInfo = process.memory_info()
        me = str(round(memInfo.rss / 1024 / 1024))
        message = "本机内存：{}M，已使用：{}M({}%)，本程序占用：{}M,可使用:{}M".format(total, used, use_per, me, free)
        return message

    def eventFilter(self, Object, event) -> bool:
        pass

    def closeEvent(self, QCloseEvent):
        import gc
        gc.collect()


if __name__ == '__main__':
    app = QApplication([])
    draw_window = DrawWindow("../db/60005064_20200930（南鹏岛）.csv", ["时间", "机组运行模式", "齿轮箱主轴承温度"])
    draw_window.window.show()
    sys.exit(app.exec_())
