# -------------------------------------------------------------------------------
# Name:         gearbox
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, Signal
import my_log
import time
import os
import pandas as pd
import cores
import tool
import gloable_var as gl

log = my_log.Log(__name__).getlog()


class GearBox(QThread):
    def __init__(self, pm):
        super(GearBox, self).__init__()
        self.postman = pm
        self.df = None
        self.project_name = None
        self.tickets = None
        self.function_list = [
            self.get_df,
            self.gearbox_main_bearing_temperature,
            self.over
        ]

    def get_df(self):
        tickets_list = ["时间",
                        "机组运行模式",
                        "齿轮箱主轴承温度",
                        "齿轮箱轮毂侧轴承温度",
                        "齿轮箱发电机侧轴承温度",
                        "齿轮箱油温",
                        "齿轮箱离线过滤泵处油温",
                        "齿轮箱主泵处油温",
                        "润滑油冷却器入口油温",
                        "润滑油冷却器出口油温",
                        "齿轮箱水泵出口温度",
                        "齿轮箱水泵入口温度1",
                        "齿轮箱水泵入口温度2",
                        "齿轮箱A1口温度",
                        "齿轮箱A2口温度",
                        "齿轮箱A3口温度",
                        "齿轮箱A4口温度",
                        "齿轮箱主泵1_1高速",
                        "齿轮箱主泵1_2高速",
                        "齿轮箱主泵1_1低速",
                        "齿轮箱主泵1_2低速",
                        "齿轮箱A1口压力",
                        "齿轮箱主泵2_1高速",
                        "齿轮箱主泵2_2高速",
                        "齿轮箱主泵2_1低速",
                        "齿轮箱主泵2_2低速",
                        "齿轮箱A2口压力",
                        "齿轮箱A3口压力",
                        "发电机润滑泵3_1",
                        "发电机润滑泵3_2",
                        "齿轮箱A4口压力",
                        "齿轮箱主泵1_1出口压力",
                        "齿轮箱主泵1_2出口压力",
                        "齿轮箱主泵2_1出口压力",
                        "齿轮箱主泵2_2出口压力",
                        "齿轮箱冷却泵出口压力",
                        "齿轮箱冷却泵",
                        "齿轮箱过滤泵",
                        "齿轮箱过滤泵出口压力",
                        "齿轮箱油位",
                        "齿轮箱水泵1启动",
                        "齿轮箱水冷风扇1高速启动",
                        "齿轮箱水泵2启动",
                        "齿轮箱水冷风扇2高速启动",
                        "齿轮箱水泵1出口压力",
                        "齿轮箱水泵1入口压力",
                        "齿轮箱水泵2出口压力",
                        "齿轮箱水泵2入口压力",

                        ]
        self.project_name = str(os.path.basename(gl.now_file)).split(".")[-2].split("_")[0][:5]
        self.tickets = cores.get_en_tickets("../db/tickets.my", self.project_name, tickets_list)
        # self.tickets = [li[1] is not None for li in self.tickets]
        for li in self.tickets:
            if li is not None:
                self.tickets[self.tickets.index(li)] = li[1]
            else:
                self.tickets[self.tickets.index(li)] = False
        if gl.df is not None:
            self.df = gl.df
            gl.df.insert(0, "time", pd.to_datetime(self.df[self.tickets[0]]))
        else:
            self.df = cores.read_csv(gl.now_file, tickets_list)
            gl.df.insert(0, "time", pd.to_datetime(self.df[self.tickets[0]]))

    def run(self):
        log.info("齿轮箱开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 1 齿轮箱主轴承温度高
    def gearbox_main_bearing_temperature(self):
        log.info("齿轮箱正在处理")
        try:
            # 获取 1 时间 2 机组模式 3 齿轮箱主轴承温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2]]
            print(tickets)
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.error(e)
            log.error("齿轮箱齿轮箱跳过函数1")
            return
        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            # self.handle_signal_and_log([1, 0], [1, [1, "齿轮箱主轴承温度正常"]])

        else:
            # 删除温度小于67.5
            df = df.drop(df[(df[tickets[2]] < 17.5)].index)
            if df.empty:
                log.info("正常")
                # self.handle_signal_and_log([1, 0], [1, [1, "齿轮箱主轴承温度正常"]])

            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱主轴承温度高.csv')
                if result[0]:
                    log.info("正常")
                    # self.handle_signal_and_log([1, 0], [1, [1, "齿轮箱主轴承温度正常"]])

                else:
                    log.info("异常")
                    # self.handle_signal_and_log([0, 0], [1, [0, "齿轮箱主轴承温度高"]])
                    # self.handle_signal_and_log([0, 0], [0, [0, "齿轮箱主轴承温度高报警次数{}".format(len(result[1]))]])
                    for i in result[1]:
                        print(i)
                        #self.signal_gb_write_log.emit([1, [0, i]])
                    #self.signal_gb_write_log.emit([1, [-1, "*" * 40]])
        self.postman.send_to_MM.emit(
            {"from": "gearbox", "to": "model_manager",
             "message": {"function": 1,
                         "result": True}})

    def over(self):
        log.info("齿轮箱处理完成")
        self.postman.send_to_MM.emit(
            {"from": "gearbox", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )
