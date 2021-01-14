# -------------------------------------------------------------------------------
# Name:         converter
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:
# -------------------------------------------------------------------------------
from PyQt5.QtCore import QThread
import os
import sys
import pandas as pd
from core import my_log
from core import cores
from core import tool
from core import gloable_var as gl
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class Converter(QThread):
    def __init__(self, pm):
        super(Converter, self).__init__()
        self.postman = pm
        self.df = None
        self.project_name = None
        self.tickets = None
        self.function_list = [
            self.get_df,
            self.converter_igbt1_temperature,
            self.converter_igbt2_temperature,
            self.converter_generator_speed,
            self.converter1_water_temperature,
            self.converter2_water_temperature,
            self.converter1_water_pressure,
            self.converter2_water_pressure,
            self.over
        ]

    def get_df(self):
        tickets_list = ["时间",
                        "机组运行模式",
                        "变频器主机igbt温度",
                        "变频器从机igbt温度",
                        "变流器发电机转速",
                        "叶轮速度2",
                        "变频器主机冷却液温度",
                        "变频器主机风扇运行1",
                        "变频器主机水泵运行",
                        "变频器从机冷却液温度",
                        "变频器从机风扇运行1",
                        "变频器从机水泵运行",
                        "变频器主机冷却液压力",
                        "变频器从机冷却液压力"
                        ]
        self.project_name = str(os.path.basename(gl.now_file)).split(".")[-2].split("_")[0][:5]
        self.tickets = cores.get_en_tickets("../db/tickets.my", self.project_name, tickets_list)
        # self.tickets = [li[1] is not None for li in self.tickets]
        for li in self.tickets:
            if li is not None:
                self.tickets[self.tickets.index(li)] = li[1]
            else:
                self.tickets[self.tickets.index(li)] = False
        if gl.df is None:
            self.df = cores.read_csv(gl.now_file, tickets_list)
            self.df.insert(0, "time", pd.to_datetime(self.df[self.tickets[0]]))
        else:
            self.df = gl.df

    def send_message(self, message: dict):
        message["from"] = "converter"
        message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def run(self):
        log.info("变频系统开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 57 变频器主机IGBT温度异常
    def converter_igbt1_temperature(self):
        """
        变频器主机IGBT温度 ≠ 0 且  >60℃ 或 <-10℃
        """
        try:
            # 获取  0时间  2变频器主机igbt温度
            tickets = [self.tickets[0], self.tickets[2]]
            df = self.df[['time', tickets[0], tickets[1]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数57")
            self.send_message({"message": {"function": 56, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] == 0)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 56, "result": 1}})
        else:
            df = df[(df[tickets[1]] < -10) | (df[tickets[1]] > 60)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 56, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器主机IGBT温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 56, "result": 1}})
                else:
                    self.send_message({"message": {"function": 56, "result": 0, "details": result[1]}})

    # 58 变频器从机IGBT温度异常
    def converter_igbt2_temperature(self):
        """
        变频器从机IGBT温度 ≠ 0 且  >60℃ 或 <-10℃
        """
        try:
            # 获取  0时间  3变频器从机igbt温度
            tickets = [self.tickets[0], self.tickets[3]]
            df = self.df[['time', tickets[0], tickets[1]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数58")
            self.send_message({"message": {"function": 57, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] == 0)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 57, "result": 1}})

        else:
            df = df[(df[tickets[1]] < -10) | (df[tickets[1]] > 60)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 57, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器从机IGBT温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 57, "result": 1}})
                else:
                    self.send_message({"message": {"function": 57, "result": 0, "details": result[1]}})

    # 59 变流器发电机转速异常
    def converter_generator_speed(self):
        """
        1、机组运行模式=14，（变流器发电机转速/齿轮箱变比（23.187）-叶轮转速2）>1.5，持续10s；
        2、变流器发电机转速>300rpm
        满足以上其一
        """
        try:
            # 获取  0时间   1机组运行模式  4变流器发电机转速  5叶轮转速2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[4], self.tickets[5]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数59")
            self.send_message({"message": {"function": 58, "result": -1}})
            return

        # 情况1 1=14，（2/23.187 - 3）>1.5，持续10s
        df_h = df[(df[tickets[1]] == 14) & (df[tickets[2]] / 23.187 - df[tickets[3]] > 1.5)].copy()
        # 情况2 2 > 300rpm
        df_l = df[(df[tickets[2]] > 300)].copy()
        # 判断是否未空
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 58, "result": 1}})
        else:
            # ------------------判断连续性
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          10,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变流器发电机转速异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 58, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 58, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变流器发电机转速异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 58, "result": 1}})
                else:
                    self.send_message({"message": {"function": 58, "result": 0, "details": result[1]}})

    # 60 变频器主机冷却液温度异常
    def converter1_water_temperature(self):
        """
        1、变频器主机冷却液温度 > 45℃ 且 变频器主机外循环风扇运行 = 1,变频器主机循环水泵运行 = 1时，持续10min
        2、任何情况下，变频器主机冷却液温度 > 48℃
        满足其一
        """
        try:
            # 获取  0时间  6变频器主机冷却液温度  7变频器主机风扇运行1  8变频器主机水泵运行
            tickets = [self.tickets[0], self.tickets[6], self.tickets[7], self.tickets[8]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数60")
            self.send_message({"message": {"function": 59, "result": -1}})
            return

        # 情况1 1>45℃ 且 2=1,3=1时，持续10min
        df_h = df[(df[tickets[1]] > 45) & (df[tickets[2]] == 1) & (df[tickets[3]] == 1)].copy()
        # 情况2 1>48℃
        df_l = df[(df[tickets[1]] > 48)].copy()
        # 判断是否未空
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 59, "result": 1}})
        else:
            # ------------------判断连续性
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器主机冷却液温度异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 59, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 59, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器主机冷却液温度异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 59, "result": 1}})
                else:
                    self.send_message({"message": {"function": 59, "result": 0, "details": result[1]}})

    # 61 变频器从机冷却液温度异常
    def converter2_water_temperature(self):
        """
        1、变频器从机冷却液温度 > 45℃ 且 变频器从机外循环风扇运行 = 1,变频器从机循环水泵运行 = 1时，持续10min
        2、任何情况下，变频器从机冷却液温度 > 48℃
        满足其一
        """
        try:
            # 获取 0时间  9变频器从机冷却液温度  10变频器从机风扇运行1  11变频器从机水泵运行
            tickets = [self.tickets[0], self.tickets[9], self.tickets[10], self.tickets[11]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数61")
            self.send_message({"message": {"function": 60, "result": -1}})
            return

        # 情况1 1>45℃ 且 2=1,3=1时，持续10min
        df_h = df[(df[tickets[1]] > 45) & (df[tickets[2]] == 1) & (df[tickets[3]] == 1)].copy()
        # 情况2 1>48℃
        df_l = df[(df[tickets[1]] > 48)].copy()
        # 判断是否未空
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 60, "result": 1}})
        else:
            # ------------------判断连续性
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器从机冷却液温度异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 60, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 60, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器从机冷却液温度异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 60, "result": 1}})
                else:
                    self.send_message({"message": {"function": 60, "result": 0, "details": result[1]}})

    # 62 变频器主机冷却液压力异常
    def converter1_water_pressure(self):
        """
        1、变频器主机循环水泵运行=1时，变频器主机冷却液压力>5.5bar或<3.5bar，持续10min
        2、变频器主机循环水泵运行=0时，变频器主机冷却液压力>3bar或<1.2bar，持续10min
        满足其一
        """
        try:
            # 获取 0时间  8变频器主机水泵运行  12变频器主机冷却液压力
            tickets = [self.tickets[0], self.tickets[8], self.tickets[12]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数62")
            self.send_message({"message": {"function": 61, "result": -1}})
            return

        # 情况1 2=1时，1>5.5bar或<3.5bar，持续10min
        df_h = df[(df[tickets[1]] == 1) & ((df[tickets[2]] > 5.5) | (df[tickets[2]] < 3.5))].copy()
        # 情况2 2=0时，1>3bar或<1.2bar，持续10min
        df_l = df[(df[tickets[1]] == 0) & ((df[tickets[2]] > 3) | (df[tickets[2]] < 1.2))].copy()
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 61, "result": 1}})
        else:
            # ------------------判断连续性
            flag = True
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器主机冷却液压力异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 61, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 61, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器主机冷却液压力异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 61, "result": 1}})
                else:
                    self.send_message({"message": {"function": 61, "result": 0, "details": result[1]}})

    # 63 变频器从机冷却液压力异常
    def converter2_water_pressure(self):
        """
        1、变频器从机循环水泵运行=1时，变频器从机冷却液压力>5.5bar或<3.5bar，持续10min
        2、变频器从机循环水泵运行=0时，变频器从机冷却液压力>3bar或<1.2bar，持续10min
        满足其一
        """
        try:
            # 获取 0时间  11变频器从机水泵运行  13变频器从机冷却液压力
            tickets = [self.tickets[0], self.tickets[11], self.tickets[13]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("变频器跳过函数63")
            self.send_message({"message": {"function": 62, "result": -1}})
            return

        # 情况1 1=1时，2>5.5bar或<3.5bar，持续10min
        df_h = df[(df[tickets[1]] == 1) & ((df[tickets[2]] > 5.5) | (df[tickets[2]] < 3.5))].copy()
        # 情况2 1=0时，2>3bar或<1.2bar，持续10min
        df_l = df[(df[tickets[1]] == 0) & ((df[tickets[2]] > 3) | (df[tickets[2]] < 1.2))].copy()
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 62, "result": 1}})
        else:
            # ------------------判断连续性
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器从机冷却液压力异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 62, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 62, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变频器从机冷却液压力异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 62, "result": 1}})
                else:
                    self.send_message({"message": {"function": 62, "result": 0, "details": result[1]}})

    def over(self):
        # # #  ************************ # # #
        self.df = None
        # # #  ************************ # # #
        log.info("变频系统处理完成")
        self.postman.send_to_MM.emit(
            {"from": "converter", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )


if __name__ == '__main__':
    g = Converter(pm=None)
    g.send_message({"message": {"function": 0, "result": 1}})
