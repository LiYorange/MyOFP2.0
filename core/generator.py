# -------------------------------------------------------------------------------
# Name:         generator
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:  
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, Signal
import os
import sys
sys.path.append('..')
import pandas as pd
from core import cores
from core import my_log
import tool
import gloable_var as gl
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class Generator(QThread):
    def __init__(self, pm):
        super(Generator, self).__init__()
        self.postman = pm
        self.df = None
        self.project_name = None
        self.tickets = None
        self.function_list = [
            self.get_df,
            self.generator_winding_PT100,
            self.generator_winding_temperature,
            self.generator_gearbox_bearing_temperature,
            self.generator_nacelle_bearing_temperature,
            self.generator_bearing_temperature_sensor,
            self.generator_inRecycle_inlet_temperature_sensor,
            self.generator_inRecycle_outlet_temperature_sensor,
            self.generator_outRecycle_inlet_temperature_sensor,
            self.generator_outRecycle_outlet_temperature_sensor,
            self.generator_inRecycle_inlet_temperature,
            self.generator_inRecycle_outlet_temperature,
            self.generator_inRecycle_temperature_difference,
            self.generator_outRecycle_temperature_difference,
            self.over
        ]

    def get_df(self):
        tickets_list = ["时间",
                        "机组运行模式",
                        "发电机绕组温度1",
                        "发电机绕组温度2",
                        "发电机绕组温度3",
                        "发电机绕组温度4",
                        "发电机绕组温度5",
                        "发电机绕组温度6",
                        "发电机齿轮箱侧轴承温度",
                        "发电机机舱侧轴承温度",
                        "变流器功率",
                        "发电机空空冷内循环入口温度1",
                        "发电机空空冷内循环入口温度2",
                        "发电机空空冷内循环出口温度1",
                        "发电机空空冷内循环出口温度2",
                        "发电机空空冷外循环入口温度1",
                        "发电机空空冷外循环入口温度2",
                        "发电机空空冷外循环出口温度1",
                        "发电机空空冷外循环出口温度2"
                        ]
        self.project_name = str(os.path.basename(gl.now_file)).split(".")[-2].split("_")[0][:5]
        self.tickets = cores.get_en_tickets("../db/tickets.my", self.project_name, tickets_list)
        for li in self.tickets:
            if li is not None:
                self.tickets[self.tickets.index(li)] = li[1]
            else:
                self.tickets[self.tickets.index(li)] = False
        if gl.df is None:

            # self.tickets = [li[1] is not None for li in self.tickets]

            self.df = cores.read_csv(gl.now_file, tickets_list)
            self.df.insert(0, "time", pd.to_datetime(self.df[self.tickets[0]]))
        else:
            self.df = gl.df

    def send_message(self, message: dict):
        message["from"] = "generator"
        message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def run(self):
        log.info("发电机开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 36 发电机绕组PT100接线异常
    def generator_winding_PT100(self):
        """
        1≤机组运行模式≤14，6个发电机绕组中任意两个变量值差值的绝对值>10，且持续10min
        """
        log.info("发动机正在处理")
        try:
            # 获取  0时间  1机组模式  2-7发电机绕组温度1-6
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2], self.tickets[3], self.tickets[4],
                       self.tickets[5], self.tickets[6], self.tickets[7]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3],
                          tickets[4], tickets[5], tickets[6], tickets[7]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数36")
            self.send_message({"message": {"function": 35, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 35, "result": 1}})
        else:
            # 6个发电机绕组中任意两个变量值差值的绝对值>10，且持续10min
            """
            1-2 1-3 1-4 1-5 1-6
            2-3 2-4 2-5 2-6
            3-4 -3-5 -3-6
            4-5 4-6
            5-6
            做差
            """
            # df = df.drop(df[(df[tickets[1]] != 14)].index)
            df['绕组1-绕组2'] = (df[tickets[2]] - df[tickets[3]]).abs()
            df['绕组1-绕组3'] = (df[tickets[2]] - df[tickets[4]]).abs()
            df['绕组1-绕组4'] = (df[tickets[2]] - df[tickets[5]]).abs()
            df['绕组1-绕组5'] = (df[tickets[2]] - df[tickets[6]]).abs()
            df['绕组1-绕组6'] = (df[tickets[2]] - df[tickets[7]]).abs()
            df['绕组2-绕组3'] = (df[tickets[3]] - df[tickets[4]]).abs()
            df['绕组2-绕组4'] = (df[tickets[3]] - df[tickets[5]]).abs()
            df['绕组2-绕组5'] = (df[tickets[3]] - df[tickets[6]]).abs()
            df['绕组2-绕组6'] = (df[tickets[3]] - df[tickets[7]]).abs()
            df['绕组3-绕组4'] = (df[tickets[4]] - df[tickets[5]]).abs()
            df['绕组3-绕组5'] = (df[tickets[4]] - df[tickets[6]]).abs()
            df['绕组3-绕组6'] = (df[tickets[4]] - df[tickets[7]]).abs()
            df['绕组4-绕组5'] = (df[tickets[5]] - df[tickets[6]]).abs()
            df['绕组4-绕组6'] = (df[tickets[5]] - df[tickets[7]]).abs()
            df['绕组5-绕组6'] = (df[tickets[6]] - df[tickets[7]]).abs()
            df = df[(df["绕组1-绕组2"] > 10) |
                    (df["绕组1-绕组3"] > 10) |
                    (df["绕组1-绕组4"] > 10) |
                    (df["绕组1-绕组5"] > 10) |
                    (df["绕组1-绕组6"] > 10) |
                    (df["绕组2-绕组3"] > 10) |
                    (df["绕组2-绕组4"] > 10) |
                    (df["绕组2-绕组5"] > 10) |
                    (df["绕组2-绕组6"] > 10) |
                    (df["绕组3-绕组4"] > 10) |
                    (df["绕组3-绕组5"] > 10) |
                    (df["绕组3-绕组6"] > 10) |
                    (df["绕组4-绕组5"] > 10) |
                    (df["绕组4-绕组6"] > 10) |
                    (df["绕组5-绕组6"] > 10)
                    ]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 35, "result": 1}})
            else:
                # ------------------判断连续性 持续10min
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机绕组PT100温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 35, "result": 1}})
                else:
                    self.send_message({"message": {"function": 35, "result": 0, "details": result[1]}})

    # 37 发电机绕组温度高
    def generator_winding_temperature(self):
        """
        机组运行模式 = 14，发电机绕组温度(1-6) > 105℃，持续10min
        """
        try:
            # 获取  1时间  2机组运行模式  2-7发电机绕组温度(1-6)
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2], self.tickets[3], self.tickets[4],
                       self.tickets[5], self.tickets[6], self.tickets[7]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4], tickets[5],
                          tickets[6], tickets[7]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数37")
            self.send_message({"message": {"function": 36, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 36, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 105) | (df[tickets[3]] > 105) | (df[tickets[4]] > 105) | (
                    df[tickets[5]] > 105) | (df[tickets[6]] > 105) | (df[tickets[7]] > 105)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 36, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机绕组温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 36, "result": 1}})
                else:
                    self.send_message({"message": {"function": 36, "result": 0, "details": result[1]}})

    # 38 发电机齿轮箱侧轴承温度高
    def generator_gearbox_bearing_temperature(self):
        """
        12 ≤ 机组运行模式 ≤ 14，发电机齿轮箱侧轴承温度 > 83℃，持续10min
        """
        try:
            # 获取  0时间  1机组模式  8发电机齿轮箱侧轴承温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[8]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数38")
            self.send_message({"message": {"function": 37, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 37, "result": 1}})
        else:
            # 删除温度<=83
            df = df.drop(df[(df[tickets[2]] <= 83)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 37, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机齿轮箱侧轴承温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 37, "result": 1}})
                else:
                    self.send_message({"message": {"function": 37, "result": 0, "details": result[1]}})

    # 39 发电机机舱侧轴承温度高
    def generator_nacelle_bearing_temperature(self):
        """
        12 ≤ 机组运行模式 ≤ 14，发电机机舱侧轴承温度 > 83℃，持续10min
        """
        try:
            # 获取  0时间  1机组模式  9发电机机舱侧轴承温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[9]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数39")
            self.send_message({"message": {"function": 38, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 38, "result": 1}})
        else:
            # 删除温度<=83
            df = df.drop(df[(df[tickets[2]] <= 83)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 38, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机机舱侧轴承温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 38, "result": 1}})
                else:
                    self.send_message({"message": {"function": 38, "result": 0, "details": result[1]}})

    # 40 发电机轴承温度传感器异常
    def generator_bearing_temperature_sensor(self):
        """
        变流器功率 ＞ 4500KW，发电机机舱侧轴承温度 - 发电机齿轮箱侧轴承温度 ＜ 5℃，持续10min
        """
        try:
            # 获取  0时间  10变流器功率   9发电机机舱侧轴承温度   8发电机齿轮箱侧轴承温度
            tickets = [self.tickets[0], self.tickets[10], self.tickets[9], self.tickets[8]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数40")
            self.send_message({"message": {"function": 39, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 4500)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 39, "result": 1}})
        else:
            # 删除 2-3 >= 5
            df = df.drop(df[(df[tickets[2]] - df[tickets[3]] >= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 39, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机轴承温度传感器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 39, "result": 1}})
                else:
                    self.send_message({"message": {"function": 39, "result": 0, "details": result[1]}})

    # 41 发电机内冷入口温度传感器异常
    def generator_inRecycle_inlet_temperature_sensor(self):
        """
        机组运行模式 = 14,发电机内冷入口温度1 和 发电机内冷入口温度2的 温差绝对值 > 5℃, 持续时间1min
        """
        try:
            # 获取  0时间  1机组运行模式  11发电机空空冷内循环入口温度1   12发电机空空冷内循环入口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[11], self.tickets[12]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数41")
            self.send_message({"message": {"function": 40, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 40, "result": 1}})
        else:
            # 删除 (2-3).abs <= 5℃
            df = df.drop(df[((df[tickets[2]] - df[tickets[3]]).abs() <= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 40, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机内冷入口温度传感器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 40, "result": 1}})
                else:
                    self.send_message({"message": {"function": 40, "result": 0, "details": result[1]}})

    # 42 发电机内冷出口温度传感器异常
    def generator_inRecycle_outlet_temperature_sensor(self):
        """
        机组运行模式 = 14,发电机内冷出口温度1 和 发电机内冷出口温度2的 温差绝对值 > 5℃,持续时间1min"
        """
        try:
            # 获取  0时间  1机组运行模式   13发电机空空冷内循环出口温度1   14发电机空空冷内循环出口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[13], self.tickets[14]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数42")
            self.send_message({"message": {"function": 41, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 41, "result": 1}})
        else:
            # 删除 (2-3).abs() <= 5
            df = df.drop(df[((df[tickets[2]] - df[tickets[3]]).abs() <= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 41, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机内冷出口温度传感器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 41, "result": 1}})
                else:
                    self.send_message({"message": {"function": 41, "result": 0, "details": result[1]}})

    # 43 发电机外冷入口温度传感器异常
    def generator_outRecycle_inlet_temperature_sensor(self):
        """
        机组运行模式 = 14,发电机外冷入口温度1 和 发电机外冷入口温度2的 温差绝对值 > 5℃, 持续时间1min
        """
        try:
            # 获取  0时间  1机组运行模式  15发电机空空冷外循环入口温度1   16发电机空空冷外循环入口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[15], self.tickets[16]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数43")
            self.send_message({"message": {"function": 42, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 42, "result": 1}})
        else:
            # 删除 (2-3).abs <= 5℃
            df = df.drop(df[((df[tickets[2]] - df[tickets[3]]).abs() <= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 42, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机外冷入口温度传感器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 42, "result": 1}})
                else:
                    self.send_message({"message": {"function": 42, "result": 0, "details": result[1]}})

    # 44 发电机外冷出口温度传感器异常
    def generator_outRecycle_outlet_temperature_sensor(self):
        """
        机组运行模式 = 14,发电机外冷出口温度1 和 发电机外冷出口温度2的 温差绝对值 > 5℃,持续时间1min"
        """
        try:
            # 获取  0时间  1机组运行模式   17发电机空空冷外循环出口温度1   18发电机空空冷外循环出口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[17], self.tickets[18]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数44")
            self.send_message({"message": {"function": 43, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 43, "result": 1}})
        else:
            # 删除 (2-3).abs() <= 5
            df = df.drop(df[((df[tickets[2]] - df[tickets[3]]).abs() <= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 43, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机外冷出口温度传感器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 43, "result": 1}})
                else:
                    self.send_message({"message": {"function": 43, "result": 0, "details": result[1]}})

    # 45 发电机内冷入口温度高
    def generator_inRecycle_inlet_temperature(self):
        """
        机组运行模式 = 14,发电机内冷入口温度1 和 发电机内冷入口温度2 任意一个 > 70℃，持续时间 1min
        """
        try:
            # 获取   0时间  1机组运行模式   11发电机空空冷内循环入口温度1  12发电机空空冷内循环入口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[11], self.tickets[12]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数45")
            self.send_message({"message": {"function": 44, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 44, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 70) | (df[tickets[3]] > 70)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 44, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机内冷入口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 44, "result": 1}})
                else:
                    self.send_message({"message": {"function": 44, "result": 0, "details": result[1]}})

    # 46 发电机内冷出口温度高
    def generator_inRecycle_outlet_temperature(self):
        """
        机组运行模式 = 14, 发电机内冷出口温度1 和 发电机内冷出口温度2 任意一个 > 60℃,持续时间1min
        """
        try:
            # 获取  0时间  1机组运行模式   13发电机空空冷内循环出口温度1   14发电机空空冷内循环出口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[13], self.tickets[14]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数46")
            self.send_message({"message": {"function": 45, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 45, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 60) | (df[tickets[3]] > 60)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 45, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/发电机内冷出口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 45, "result": 1}})
                else:
                    self.send_message({"message": {"function": 45, "result": 0, "details": result[1]}})

    # 47 发电机内冷温差异常
    def generator_inRecycle_temperature_difference(self):
        """
        机组运行模式 = 14, 发电机绕组温度（任选一个） > 90℃,
        发电机内冷入口温度1 - 发电机内冷出口温度1 ≤ 10 或 发电机内冷入口温度2 - 发电机内冷出口温度2 ≤ 10 ，持续时间10min
        """
        try:
            # 获取  0时间  1机组运行模式  2-7发电机绕组温度(1-6)
            # 11发电机空空冷内循环入口温度1  12发电机空空冷内循环入口温度2  13发电机空空冷内循环出口温度1  14发电机空空冷内循环出口温度2英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2], self.tickets[3], self.tickets[4],
                       self.tickets[5], self.tickets[6], self.tickets[7], self.tickets[11], self.tickets[12],
                       self.tickets[13], self.tickets[14]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4], tickets[5],
                          tickets[6], tickets[7], tickets[8], tickets[9], tickets[10], tickets[11]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数47")
            self.send_message({"message": {"function": 46, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 46, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 90) | (df[tickets[3]] > 90) | (df[tickets[4]] > 90) | (
                    df[tickets[5]] > 90) | (df[tickets[6]] > 90) | (df[tickets[7]] > 90)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 46, "result": 1}})
            else:
                df = df[(df[tickets[8]] - df[tickets[10]] <= 10) | (df[tickets[9]] - df[tickets[11]] <= 10)]
                if df.empty:
                    log.info("正常")
                    self.send_message({"message": {"function": 46, "result": 1}})
                else:
                    # ------------------判断连续性
                    result = tool.duration_calculation_to_csv(tickets,
                                                              df,
                                                              600,
                                                              str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                              '/发电机内冷温差异常.csv')
                    if result[0]:
                        log.info("正常")
                        self.send_message({"message": {"function": 46, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 46, "result": 0, "details": result[1]}})

    # 48 发电机外冷温差异常
    def generator_outRecycle_temperature_difference(self):
        """
        机组运行模式 = 14, 发电机内冷入口温度1 和 发电机内冷入口温度2都 > 60℃
        发电机外冷出口温度1 - 发电机外冷入口温度1 ≤ 5 或 发电机外冷出口温度2 - 发电机外冷入口温度2 ≤ 10 ，持续时间10min
        """
        try:
            # 获取  0时间  1机组运行模式  11发电机空空冷内循环入口温度1  12发电机空空冷内循环入口温度2
            # 15发电机空空冷外循环入口温度1  16发电机空空冷外循环入口温度2  17发电机空空冷外循环出口温度1  18发电机空空冷外循环出口温度2英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[11], self.tickets[12],
                       self.tickets[15], self.tickets[16], self.tickets[17], self.tickets[18]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4],
                          tickets[5], tickets[6], tickets[7]]]
        except Exception as e:
            log.warning(e)
            log.warning("发电机跳过函数48")
            self.send_message({"message": {"function": 47, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 47, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 60) & (df[tickets[3]] > 60)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 47, "result": 1}})
            else:
                df = df[(df[tickets[6]] - df[tickets[4]] <= 5) | (df[tickets[7]] - df[tickets[5]] <= 10)]
                if df.empty:
                    log.info("正常")
                    self.send_message({"message": {"function": 47, "result": 1}})
                else:
                    # ------------------判断连续性
                    result = tool.duration_calculation_to_csv(tickets,
                                                              df,
                                                              600,
                                                              str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                              '/发电机外冷温差异常.csv')
                    if result[0]:
                        log.info("正常")
                        self.send_message({"message": {"function": 47, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 47, "result": 0, "details": result[1]}})

    def over(self):
        # # #  ************************ # # #
        self.df = None
        # # #  ************************ # # #
        log.info("发电机处理完成")
        self.postman.send_to_MM.emit(
            {"from": "generator", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )


if __name__ == '__main__':
    g = Generator(pm=None)
    g.send_message({"message": {"function": 0, "result": 1}})
