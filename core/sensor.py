# -------------------------------------------------------------------------------
# Name:         sensor
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, Signal
import my_log
import time
import os
import sys
import pandas as pd
import cores
import tool
import gloable_var as gl
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    log.critical("Unhandled exception: %s", text)
sys.excepthook = log_except_hook


class Sensor(QThread):
    def __init__(self, pm):
        super(Sensor, self).__init__()
        self.postman = pm
        self.df = None
        self.project_name = None
        self.tickets = None
        self.function_list = [
            self.get_df,
            self.sensor_tower_base_transformer_temperature,
            self.sensor_tower_base_cabinet_temperature,
            self.sensor_tower_cabin_heart,
            self.sensor_nacelle_power_distribution_cabinet_temperature,
            self.sensor_nacelle_cabin_heart,
            self.sensor_nacelle_signal_cabinet_temperature,
            self.sensor_nacelle_signal_cabinet_heart,
            self.sensor_yaw_driver_cabinet_temperature,
            self.over
        ]

    def get_df(self):
        tickets_list = ["时间",
                        "机组运行模式",
                        "塔基变压器温度",
                        "塔筒第一层平台温度",
                        "塔基柜温度",
                        "机舱高压柜温度",
                        "机舱温度",
                        "机舱低压柜温度",
                        "变频器温度1",
                        "变频器温度2",
                        "变频器温度3",
                        "变频器温度4",
                        "变频器温度5",
                        "变频器温度6",
                        "变频器温度7",
                        "变频器温度8",
                        "变频器温度9",
                        "变频器温度10",
                        "变频器温度11",
                        "变频器温度12",
                        "变频器温度13",
                        "变频器温度14",
                        "变频器温度15",
                        "变频器温度16",
                        "变频器温度17"
                        ]
        self.project_name = str(os.path.basename(gl.now_file)).split(".")[-2].split("_")[0][:5]
        self.tickets = cores.get_en_tickets("../db/tickets.my", self.project_name, tickets_list)
        # self.tickets = [li[1] is not None for li in self.tickets]
        for li in self.tickets:
            if li is not None:
                self.tickets[self.tickets.index(li)] = li[1]
            else:
                self.tickets[self.tickets.index(li)] = False
        self.df = cores.read_csv(gl.now_file, tickets_list)
        self.df.insert(0, "time", pd.to_datetime(self.df[self.tickets[0]]))

    def send_message(self, message: dict):
        message["from"] = "sensor"
        message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def run(self):
        log.info("传感器开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 75 塔基变压器温度异常
    def sensor_tower_base_transformer_temperature(self):
        """
        塔基变压器温度≠0时，塔基变压器温度>80℃或者<10℃，持续1min
        """
        try:
            # 获取  0时间  2塔基变压器温度
            tickets = [self.tickets[0], self.tickets[2]]
            df = self.df[['time', tickets[0], tickets[1]]]
        except Exception as e:
            log.warning(e)
            log.warning("传感器跳过函数75")
            self.send_message({"message": {"function": 74, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] == 0)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 74, "result": 1}})
        else:
            df = df[(df[tickets[1]] > 80) | (df[tickets[1]] < 10)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 74, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/塔基变压器温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 74, "result": 1}})
                else:
                    self.send_message({"message": {"function": 74, "result": 0, "details": result[1]}})

    # 76 塔基柜温度异常
    def sensor_tower_base_cabinet_temperature(self):
        """
        11≤ 机组运行模式 ≤14，塔基控制柜温度 > 45°，且塔基第一层温度 < 40°，且异常持续时间超过 5min
        """
        try:
            # 获取 0时间  1机组运行模式  3塔筒第一层平台温度  4塔基柜温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[3], self.tickets[4]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.info("跳过函数76")
            self.send_message({"message": {"function": 75, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 75, "result": 1}})
        else:
            df = df[(df[tickets[3]] > 45) & (df[tickets[2]] < 40)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 75, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/塔基柜温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 75, "result": 1}})
                else:
                    self.send_message({"message": {"function": 75, "result": 0, "details": result[1]}})

    # 77 塔基柜加热器异常
    def sensor_tower_cabin_heart(self):
        """
        11≤ 机组运行模式 ≤14，塔基控制柜温度 < 5℃，持续3min
        """
        try:
            # 获取 0时间  1机组运行模式  4塔基柜温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[4]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.info("跳过函数77")
            self.send_message({"message": {"function": 76, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 76, "result": 1}})
        else:
            df = df.drop(df[(df[tickets[2]] >= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 76, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          180,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/塔基柜加热器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 76, "result": 1}})
                else:
                    self.send_message({"message": {"function": 76, "result": 0, "details": result[1]}})

    # 78 机舱动力柜温度异常
    def sensor_nacelle_power_distribution_cabinet_temperature(self):
        """
        11≤机组运行模式≤14，机舱动力柜温度>45°，且机舱温度<40°，且异常持续时间超过5min
        """
        try:
            # 获取 0时间  1机组运行模式 5机舱高压柜温度  6机舱温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[5], self.tickets[6]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.info("跳过函数78")
            self.send_message({"message": {"function": 77, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 77, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 45) & (df[tickets[3]] < 40)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 77, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/机舱动力柜温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 77, "result": 1}})
                else:
                    self.send_message({"message": {"function": 77, "result": 0, "details": result[1]}})

    # 79 机舱动力柜加热器异常
    def sensor_nacelle_cabin_heart(self):
        """
        11≤ 机组运行模式 ≤14，塔基控制柜温度 < 5℃，持续3min
        """
        try:
            # 获取 0时间  1机组运行模式 5机舱高压柜温度 英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[5]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.info("跳过函数79")
            self.send_message({"message": {"function": 78, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 78, "result": 1}})
        else:
            df = df.drop(df[(df[tickets[2]] >= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 78, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          180,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/机舱动力柜加热器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 78, "result": 1}})
                else:
                    self.send_message({"message": {"function": 78, "result": 0, "details": result[1]}})

    # 80 机舱信号柜温度异常
    def sensor_nacelle_signal_cabinet_temperature(self):
        """
        11≤ 机组运行模式 ≤14，机舱信号柜温度 >45°，且机舱温度 <40°，且异常持续时间超过5min
        """
        try:
            # 获取 0时间  1机组运行模式  7机舱低压柜温度  6机舱温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[7], self.tickets[6]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.info("跳过函数6")
            self.send_message({"message": {"function": 79, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 79, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 45) & (df[tickets[3]] < 40)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 79, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/机舱信号柜温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 79, "result": 1}})
                else:
                    self.send_message({"message": {"function": 79, "result": 0, "details": result[1]}})

    # 81 机舱信号柜加热器异常
    def sensor_nacelle_signal_cabinet_heart(self):
        """
        11≤ 机组运行模式 ≤14，机舱信号柜温度 < 5℃，持续3min
        """
        try:
            # 获取 0时间  1机组运行模式  7机舱低压柜温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[7]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.info("跳过函数81")
            self.send_message({"message": {"function": 80, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 80, "result": 1}})
        else:
            df = df.drop(df[(df[tickets[2]] >= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 80, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          180,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/机舱信号柜加热器异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 80, "result": 1}})
                else:
                    self.send_message({"message": {"function": 80, "result": 0, "details": result[1]}})

    # 82 偏航驱动柜温度异常
    def sensor_yaw_driver_cabinet_temperature(self):
        """
        变频器1温度 至 变频器17温度中 的最大值≠0 且 >60℃，持续10min
        """
        try:
            # 获取 1 时间   8-24变频器1-17温度
            tickets = [self.tickets[0], self.tickets[8], self.tickets[9], self.tickets[10], self.tickets[11],
                       self.tickets[12], self.tickets[13], self.tickets[14], self.tickets[15], self.tickets[16],
                       self.tickets[17], self.tickets[18], self.tickets[19], self.tickets[20], self.tickets[21],
                       self.tickets[22], self.tickets[23], self.tickets[24]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4], tickets[5],
                          tickets[6], tickets[7], tickets[8], tickets[9], tickets[10], tickets[11], tickets[12],
                          tickets[13], tickets[14], tickets[15], tickets[16], tickets[17]]]

        except Exception as e:
            log.warning(e)
            log.info("跳过函数82")
            self.send_message({"message": {"function": 81, "result": -1}})
            return

        df['maxvalue'] = df.loc[:, [tickets[1], tickets[2], tickets[3], tickets[4], tickets[5], tickets[6], tickets[7],
                                    tickets[8], tickets[9], tickets[10], tickets[11], tickets[12], tickets[13],
                                    tickets[14], tickets[15], tickets[16], tickets[17]]].max(axis=1, skipna=True)
        df = df[(df['maxvalue'] > 60) & (df['maxvalue'] != 0)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 81, "result": 1}})
        else:
            # ------------------判断连续性
            result = tool.duration_calculation_to_csv(tickets,
                                                      df,
                                                      600,
                                                      str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                      '/偏航驱动柜温度异常.csv')
            if result[0]:
                log.info("正常")
                self.send_message({"message": {"function": 81, "result": 1}})
            else:
                self.send_message({"message": {"function": 81, "result": 0, "details": result[1]}})

    def over(self):
        log.info("传感器处理完成")
        self.postman.send_to_MM.emit(
            {"from": "sensor", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )