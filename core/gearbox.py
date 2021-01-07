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
            self.gearbox_hub_side_bearing_temperature,
            self.gearbox_generator_side_bearing_temperature,
            self.gearbox_oil_temperature,
            self.gearbox_cooler_inlet_oil_temperature,
            self.gearbox_cooler_outlet_oil_temperature,
            self.gearbox_water_pump_outlet_temperature,
            self.gearbox_water_pump_inlet_temperature,
            self.gearbox_A1_port_temperature,
            self.gearbox_A2_port_temperature,
            self.gearbox_A3_port_temperature,
            self.gearbox_A4_port_temperature,
            self.gearbox_A1_port_pressure,
            self.gearbox_A2_port_pressure,
            self.gearbox_A3_port_pressure,
            self.gearbox_A4_port_pressure,
            self.gearbox_main_pump1_1_outlet_oil_pressure,
            self.gearbox_main_pump1_2_outlet_oil_pressure,
            self.gearbox_main_pump2_1_outlet_oil_pressure,
            self.gearbox_main_pump2_2_outlet_oil_pressure,
            self.gearbox_main_pump_filter1_1_oil_pressure_difference,
            self.gearbox_main_pump_filter1_2_oil_pressure_difference,
            self.gearbox_main_pump_filter2_1_oil_pressure_difference,
            self.gearbox_main_pump_filter2_2_oil_pressure_difference,
            self.gearbox_cooling_pump_outlet_oil_pressure,
            self.gearbox_bypass_pump_outlet_oil_pressure,
            self.gearbox_oil_level,
            self.gearbox_water_pump1_temperature_difference,
            self.gearbox_water_pump2_temperature_difference,
            self.gearbox_water_pump1_outlet_oil_pressure,
            self.gearbox_water_pump1_inlet_oil_pressure,
            self.gearbox_water_pump2_outlet_oil_pressure,
            self.gearbox_water_pump2_inlet_oil_pressure,
            self.gearbox_water_pump1_oil_pressure_difference,
            self.gearbox_water_pump2_oil_pressure_difference,
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
                        "齿轮箱水泵2入口压力"
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
        message["from"] = "gearbox"
        message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def run(self):
        log.info("齿轮箱开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 1 齿轮箱主轴承温度高
    def gearbox_main_bearing_temperature(self):
        """
        12 ≤ 机组运行模式 ≤ 14，齿轮箱主轴承温度 > 67.5℃，持续 10min
        """
        log.info("齿轮箱正在处理")
        try:
            # 获取 1 时间 2 机组模式 3 齿轮箱主轴承温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数1")
            self.send_message({"message": {"function": 0, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 0, "result": 1}})
        else:
            # 删除温度<=67.5
            df = df.drop(df[(df[tickets[2]] <= 67.5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 0, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱主轴承温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 0, "result": 1}})
                else:
                    self.send_message({"message": {"function": 0, "result": 0, "details": result[1]}})

    # 2 齿轮箱轮毂侧轴承温度高
    def gearbox_hub_side_bearing_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱轮毂侧轴承温度>67.5℃，持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱轮毂侧轴承温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[3]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数2")
            self.send_message({"message": {"function": 1, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 1, "result": 1}})
        else:
            # 删除温度<=67.5
            df = df.drop(df[(df[tickets[2]] <= 67.5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 1, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱轮毂侧轴承温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 1, "result": 1}})
                else:
                    self.send_message({"message": {"function": 1, "result": 0, "details": result[1]}})

    # 3 齿轮箱发电机侧轴承温度高
    def gearbox_generator_side_bearing_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱发电机侧轴承温度>67.5℃，持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱发电机侧轴承温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[4]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数3")
            self.send_message({"message": {"function": 2, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 2, "result": 1}})
        else:
            # 删除温度<=67.5
            df = df.drop(df[(df[tickets[2]] <= 67.5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 2, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱发电机侧轴承温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 2, "result": 1}})
                else:
                    self.send_message({"message": {"function": 2, "result": 0, "details": result[1]}})

    # 4 齿轮箱油温高
    def gearbox_oil_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱油温、齿轮箱过滤泵处油温、齿轮箱主泵处油温任意一个>58℃，且持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱油温 齿轮箱离线过滤泵处油温 齿轮箱主泵处油温英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[5], self.tickets[6], self.tickets[7]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数4")
            self.send_message({"message": {"function": 3, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 3, "result": 1}})
        else:
            # 删除所有温度<=58
            df = df.drop(df[(df[tickets[2]] <= 58) & (df[tickets[3]] <= 58) & (df[tickets[4]] <= 58)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 3, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱油温高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 3, "result": 1}})
                else:
                    self.send_message({"message": {"function": 3, "result": 0, "details": result[1]}})

    # 5 齿轮箱冷却器入口油温
    def gearbox_cooler_inlet_oil_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱冷却器入口油温>58℃，且持续10min
        """
        try:
            # 获取 1时间 2模式 8润滑油冷却器入口油温英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[8]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数5")
            self.send_message({"message": {"function": 4, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 4, "result": 1}})
        else:
            # 删除温度<=58
            df = df.drop(df[(df[tickets[2]] <= 58)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 4, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱冷却器入口油温高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 4, "result": 1}})
                else:
                    self.send_message({"message": {"function": 4, "result": 0, "details": result[1]}})

    # 6 齿轮箱冷却器出口油温
    def gearbox_cooler_outlet_oil_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱冷却器出口油温>53℃，且持续10min
        """
        try:
            # 获取 1时间 2模式 9润滑油冷却器出口油温英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[9]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数6")
            self.send_message({"message": {"function": 5, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 5, "result": 1}})
        else:
            # 删除温度<=53
            df = df.drop(df[(df[tickets[2]] <= 53)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 5, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱冷却器出口油温高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 5, "result": 1}})
                else:
                    self.send_message({"message": {"function": 5, "result": 0, "details": result[1]}})

    # 7 齿轮箱水泵出口温度
    def gearbox_water_pump_outlet_temperature(self):
        """
        12≤运行模式≤14，齿轮箱水泵出口温度＞48℃，且持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱水泵出口温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[10]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数7")
            self.send_message({"message": {"function": 6, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 6, "result": 1}})
        else:
            # 删除温度<=48
            df = df.drop(df[(df[tickets[2]] <= 48)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 6, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱水泵出口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 6, "result": 1}})
                else:
                    self.send_message({"message": {"function": 6, "result": 0, "details": result[1]}})

    # 8 齿轮箱水泵入口温度
    def gearbox_water_pump_inlet_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱水泵入口温度1和齿轮箱水泵入口温度2任意一个＞45℃，
        或齿轮箱水泵入口温度1和齿轮箱水泵入口温度2差值绝对值>5，持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱水泵入口温度1 齿轮箱水泵入口温度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[11], self.tickets[12]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数8")
            self.send_message({"message": {"function": 7, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 7, "result": 1}})
        else:
            # 删除所有温度<=45 & abs()<=5
            df = df.drop(df[(df[tickets[2]] <= 45) & (df[tickets[3]] <= 45) & (
                    (df[tickets[2]] - df[tickets[3]]).abs() <= 5)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 7, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱水泵入口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 7, "result": 1}})
                else:
                    self.send_message({"message": {"function": 7, "result": 0, "details": result[1]}})

    # 9 齿轮箱A1口温度
    def gearbox_A1_port_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱A1口温度>56℃，且持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱A1口温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[13]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数9")
            self.send_message({"message": {"function": 8, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 8, "result": 1}})
        else:
            # 删除温度<=56
            df = df.drop(df[(df[tickets[2]] <= 56)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 8, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱A1口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 8, "result": 1}})
                else:
                    self.send_message({"message": {"function": 8, "result": 0, "details": result[1]}})

    # 10 齿轮箱A2口温度高
    def gearbox_A2_port_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱A2口温度>56℃，且持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱A2口温度高英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[14]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数10")
            self.send_message({"message": {"function": 9, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 9, "result": 1}})
        else:
            # 删除温度<=56
            df = df.drop(df[(df[tickets[2]] <= 56)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 9, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱A2口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 9, "result": 1}})
                else:
                    self.send_message({"message": {"function": 9, "result": 0, "details": result[1]}})

    # 11 齿轮箱A3口温度高
    def gearbox_A3_port_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱A3口温度>56℃，且持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱A3口温度高英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[15]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数11")
            self.send_message({"message": {"function": 10, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 10, "result": 1}})
        else:
            # 删除温度<=56
            df = df.drop(df[(df[tickets[2]] <= 56)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 10, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱A3口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 10, "result": 1}})
                else:
                    self.send_message({"message": {"function": 10, "result": 0, "details": result[1]}})

        # 12 齿轮箱A4口温度高

    # 12 齿轮箱A4口温度高
    def gearbox_A4_port_temperature(self):
        """
        12≤机组运行模式≤14，齿轮箱A4口温度>56℃，且持续10min
        """
        try:
            # 获取 时间 模式 齿轮箱A4口温度
            tickets = [self.tickets[0], self.tickets[1], self.tickets[16]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数12")
            self.send_message({"message": {"function": 11, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 11, "result": 1}})
        else:
            # 删除温度<=56
            df = df.drop(df[(df[tickets[2]] <= 56)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 11, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          600,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱A4口温度高.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 11, "result": 1}})
                else:
                    self.send_message({"message": {"function": 11, "result": 0, "details": result[1]}})

    # 13 齿轮箱A1口压力异常
    def gearbox_A1_port_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵1_1高速=1或齿轮箱主泵1_2高速=1，A1口压力<4或>6.5，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵1_1低速=1或齿轮箱主泵1_2低速=1，A1口压力<2.5或>5，且持续30s
        满足以上其一报出A1口压力异常
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵1_1高速"17,"齿轮箱主泵1_2高速"18,"齿轮箱主泵1_1低速"19,"齿轮箱主泵1_2低速"20,"齿轮箱A1口压力",21英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[17], self.tickets[18],
                       self.tickets[19], self.tickets[20], self.tickets[21]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4],
                          tickets[5], tickets[6]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数13")
            self.send_message({"message": {"function": 12, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 12, "result": 1}})
        else:
            # 情况1 高速模式  1 3 ：1_1 1_2模式高速，6：压力在<4或>6.5
            df_h = df[((df[tickets[1]] == 1) | (df[tickets[3]] == 1)) &
                      ((df[tickets[6]] < 4) | (df[tickets[6]] > 6.5))].copy()
            # 情况2 低速模式  4 5 ：1_1 1_2模式低速，6：压力在<2.5或>5
            df_l = df[((df[tickets[4]] == 1) | (df[tickets[5]] == 1)) &
                      ((df[tickets[6]] < 2.5) | (df[tickets[6]] > 5))].copy()
            # 判断是否未空
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 12, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱A1口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 12, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 12, "result": 0, "details": result1[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱A1口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 12, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 12, "result": 0, "details": result2[1]}})

    # 14 齿轮箱A2口压力异常
    def gearbox_A2_port_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵2_1高速=1或齿轮箱主泵2_2高速=1，A2口压力<4或>9，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵2_1低速=1或齿轮箱主泵2_2低速=1，A2口压力<2.5或>7.5，且持续30s
        满足以上其一
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵2_1高速22, 齿轮箱主泵2_2高速,23 齿轮箱主泵2_1低速24,齿轮箱主泵2_2低速25,齿轮箱A2口压力26英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[22], self.tickets[23],
                       self.tickets[24], self.tickets[25], self.tickets[26]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4],
                          tickets[5], tickets[6]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数14")
            self.send_message({"message": {"function": 13, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            self.send_message({"message": {"function": 13, "result": 1}})
        else:
            # 情况1 高速模式  1 3 ：2_1 2_2模式高速，6：压力在<4或>9
            df_h = df[((df[tickets[1]] == 1) | (df[tickets[3]] == 1)) &
                      ((df[tickets[6]] < 4) | (df[tickets[6]] > 9))].copy()
            # 情况2 低速模式  4 5 ：2_1 2_2模式低速，6：压力在<2.5或>7.5
            df_l = df[((df[tickets[4]] == 1) | (df[tickets[5]] == 1)) &
                      ((df[tickets[6]] < 2.5) | (df[tickets[6]] > 7.5))].copy()
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 13, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱A2口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 13, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 13, "result": 0, "details": result1[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱A2口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 13, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 13, "result": 0, "details": result2[1]}})

    # 15 齿轮箱A3口压力异常
    def gearbox_A3_port_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵2_1高速=1或齿轮箱主泵2_2高速=1，A3口压力<0.4或>0.7，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵2_1低速=1或齿轮箱主泵2_2低速=1，A3口压力<0.25或>0.4，且持续30s
        满足以上其一
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵2_1高速22, 齿轮箱主泵2_2高速,23 齿轮箱主泵2_1低速24,齿轮箱主泵2_2低速25,齿轮箱A2口压力26英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[22], self.tickets[23],
                       self.tickets[24], self.tickets[25], self.tickets[27]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4],
                          tickets[5], tickets[6]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数15")
            self.send_message({"message": {"function": 14, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 14, "result": 1}})
        else:
            # 情况1 高速模式  1 3 ：2_1 2_2模式高速，0.4：压力在<4或>0.7
            df_h = df[((df[tickets[1]] == 1) | (df[tickets[3]] == 1)) &
                      ((df[tickets[6]] < 0.4) | (df[tickets[6]] > 0.7))].copy()
            # 情况2 低速模式  4 5 ：2_1 2_2模式低速，0.25：压力在<2.5或>0.4
            df_l = df[((df[tickets[4]] == 1) | (df[tickets[5]] == 1)) &
                      ((df[tickets[6]] < 0.25) | (df[tickets[6]] > 0.4))].copy()
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 14, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱A3口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 14, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 14, "result": 0, "details": result1[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱A3口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 14, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 14, "result": 0, "details": result2[1]}})

    # 16 齿轮箱A4口压力异常
    def gearbox_A4_port_pressure(self):
        """
        齿轮箱油温>50，发电机润滑泵3_1或发电机润滑泵3_2=1,A4口压力<2或>5，且持续30s
        """
        try:
            # 获取 时间 "齿轮箱油温"5,发电机润滑泵3_1或发电机润滑泵3_2=1  28 29 A4口压力 30英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[28], self.tickets[29],
                       self.tickets[30]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数16")
            self.send_message({"message": {"function": 15, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            self.send_message({"message": {"function": 15, "result": 1}})
        else:
            # 发电机润滑泵3_1或发电机润滑泵3_2=1,A4口压力<2或>5
            df = df[((df[tickets[2]] == 1) | (df[tickets[3]] == 1)) &
                    ((df[tickets[4]] < 2) | (df[tickets[4]] > 5))].copy()
            # 判断是否未空
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 15, "result": 1}})
            else:
                # ------------------判断连续性
                # 高速模式连续时长判断
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[
                                                              0] +
                                                          '/齿轮箱A4口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 15, "result": 1}})
                else:
                    self.send_message({"message": {"function": 15, "result": 0, "details": result[1]}})

    # 17 齿轮箱主泵1_1出口压力异常
    def gearbox_main_pump1_1_outlet_oil_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵1_1高速=1，齿轮箱主泵1_1出口压力<4或>6.5，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵1_1低速=1，齿轮箱主泵1_1出口压力<2.5或>5，且持续30s
        满足以上其一
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵1_1高速"17,"齿轮箱主泵1_1低速"19,"齿轮箱主泵1_1出口压力" 31,英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[17], self.tickets[19], self.tickets[31]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数17")
            self.send_message({"message": {"function": 16, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 16, "result": 1}})
        else:
            # 情况1 齿轮箱油温>50，齿轮箱主泵1_1高速=1，齿轮箱主泵1_1出口压力<4或>6.5，且持续30s
            df_h = df[(df[tickets[2]] == 1) &
                      ((df[tickets[4]] < 4) | (df[tickets[4]] > 6.5))].copy()
            # 齿轮箱油温>50，齿轮箱主泵1_1低速=1，齿轮箱主泵1_1出口压力<2.5或>5，且持续30s
            df_l = df[(df[tickets[3]] == 1) &
                      ((df[tickets[4]] < 2.5) | (df[tickets[4]] > 5))].copy()
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 16, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱主泵1_1出口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 16, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 16, "result": 0, "details": result1[1]}})
                flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱主泵1_1出口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 16, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 16, "result": 0, "details": result2[1]}})

    # 18 齿轮箱主泵1_2出口压力异常
    def gearbox_main_pump1_2_outlet_oil_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵1_2高速=1，齿轮箱主泵1_2出口压力<4或>6.5，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵1_2低速=1，齿轮箱主泵1_2出口压力<2.5或>5，且持续30s
        满足以上其一
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵1_2高速"18,"齿轮箱主泵1_2低速"20,"齿轮箱主泵1_2出口压力" 32,英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[18], self.tickets[20], self.tickets[32]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数18")
            self.send_message({"message": {"function": 17, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 17, "result": 1}})
        else:
            # 情况1 齿轮箱油温>50，齿轮箱主泵1_1高速=1，齿轮箱主泵1_1出口压力<4或>6.5，且持续30s
            df_h = df[(df[tickets[2]] == 1) &
                      ((df[tickets[4]] < 4) | (df[tickets[4]] > 6.5))].copy()
            # 齿轮箱油温>50，齿轮箱主泵1_1低速=1，齿轮箱主泵1_1出口压力<2.5或>5，且持续30s
            df_l = df[(df[tickets[3]] == 1) &
                      ((df[tickets[4]] < 2.5) | (df[tickets[4]] > 5))].copy()
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 17, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱主泵1_2出口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 17, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 17, "result": 0, "details": result1[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱主泵1_2出口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 17, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 17, "result": 0, "details": result2[1]}})

    # 19 齿轮箱主泵2_1出口压力异常
    def gearbox_main_pump2_1_outlet_oil_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵2_1高速=1，齿轮箱主泵2_1出口压力<4或>8，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵2_1低速=1，齿轮箱主泵2_1出口压力<2或>4，且持续30s
        满足以上其一
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵2_1高速"22,"齿轮箱主泵2_1低速"24,"齿轮箱主泵2_1出口压力" 33,英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[22], self.tickets[24], self.tickets[33]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数19")
            self.send_message({"message": {"function": 18, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 18, "result": 1}})
        else:
            # 情况1 齿轮箱油温>50，齿轮箱主泵2_1高速=1，齿轮箱主泵2_1出口压力<4或>8，且持续30s
            df_h = df[(df[tickets[2]] == 1) &
                      ((df[tickets[4]] < 4) | (df[tickets[4]] > 8))].copy()
            # 情况2 齿轮箱油温>50，齿轮箱主泵2_1低速=1，齿轮箱主泵2_1出口压力<2或>4，且持续30s
            df_l = df[(df[tickets[3]] == 1) &
                      ((df[tickets[4]] < 2) | (df[tickets[4]] > 4))].copy()
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 18, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱主泵2_1出口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 18, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 18, "result": 0, "details": result1[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                               '/齿轮箱主泵2_1出口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 18, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 18, "result": 0, "details": result2[1]}})

    # 20 齿轮箱主泵2_2出口压力异常
    def gearbox_main_pump2_2_outlet_oil_pressure(self):
        """
        1、齿轮箱油温>50，齿轮箱主泵2_2高速=1，齿轮箱主泵2_2出口压力<4或>8，且持续30s
        2、齿轮箱油温>50，齿轮箱主泵2_2低速=1，齿轮箱主泵2_2出口压力<2或>4，且持续30s
        满足以上其一
        """
        try:
            # 获取 时间 "齿轮箱油温"5,"齿轮箱主泵2_2高速"23,"齿轮箱主泵2_2低速"25,"齿轮箱主泵2_2出口压力" 34,英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[23], self.tickets[25], self.tickets[34]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数20")
            self.send_message({"message": {"function": 19, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 19, "result": 1}})
        else:
            # 情况1 齿轮箱油温>50，齿轮箱主泵2_2高速=1，齿轮箱主泵2_2出口压力<4或>8，且持续30s
            df_h = df[(df[tickets[2]] == 1) &
                      ((df[tickets[4]] < 4) | (df[tickets[4]] > 8))].copy()
            # 情况2 齿轮箱油温>50，齿轮箱主泵2_2低速=1，齿轮箱主泵2_2出口压力<2或>4，且持续30s
            df_l = df[(df[tickets[3]] == 1) &
                      ((df[tickets[4]] < 2) | (df[tickets[4]] > 4))].copy()
            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 19, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result1 = tool.duration_calculation_to_csv(tickets,
                                                               df_h,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[
                                                                   0] +
                                                               '/齿轮箱主泵2_2出口高速模式压力异常.csv')
                    if result1[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 19, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 19, "result": 0, "details": result1[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result2 = tool.duration_calculation_to_csv(tickets,
                                                               df_l,
                                                               30,
                                                               str(gl.now_file).split(r'/')[-1].split('.')[
                                                                   0] +
                                                               '/齿轮箱主泵2_2出口低速模式压力异常.csv')
                    if result2[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 19, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 19, "result": 0, "details": result2[1]}})

    # 21 齿轮箱主泵滤芯压差1_1异常
    def gearbox_main_pump_filter1_1_oil_pressure_difference(self):
        """
        齿轮箱油温>45，齿轮箱主泵1_1出口压力≠0，齿轮箱主泵1_1高速=1，齿轮箱主泵1_1出口压力-齿轮箱A1口压力＞3.5，且持续5min
        """
        try:
            # 获取 时间 0 齿轮箱油温 5 齿轮箱主泵1_1出口压力 31 齿轮箱主泵1_1高速 17  齿轮箱A1口压力 21 英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[31], self.tickets[17],
                       self.tickets[21]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数21")
            self.send_message({"message": {"function": 20, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 45)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 20, "result": 1}})
        else:
            # 删除齿轮箱主泵1_1出口压力=0
            df = df.drop(df[(df[tickets[2]] == 0)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 20, "result": 1}})
            else:
                # 判断压差 齿轮箱主泵1_1高速=1，齿轮箱主泵1_1出口压力-齿轮箱A1口压力＞3.5，且持续5min
                df = df[(df[tickets[3]] == 1) & (df[tickets[2]] - df[tickets[4]] > 3.5)]
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[
                                                              0] + '/齿轮箱主泵滤芯压差1_1异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 20, "result": 1}})
                else:
                    self.send_message({"message": {"function": 20, "result": 0, "details": result[1]}})

    # 22 齿轮箱主泵滤芯压差1_2异常
    def gearbox_main_pump_filter1_2_oil_pressure_difference(self):
        """
        齿轮箱油温>45，齿轮箱主泵1_2出口压力≠0，齿轮箱主泵1_2高速=1，齿轮箱主泵1_2出口压力-齿轮箱A1口压力＞3.5，且持续5min
        """
        try:
            # 获取 时间 0 齿轮箱油温 5 齿轮箱主泵1_2出口压力 32 齿轮箱主泵1_2高速 18  齿轮箱A1口压力 21 英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[32], self.tickets[18],
                       self.tickets[21]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数22")
            self.send_message({"message": {"function": 21, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 45)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 21, "result": 1}})
        else:
            # 删除齿轮箱主泵1_1出口压力=0
            df = df.drop(df[(df[tickets[2]] == 0)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 21, "result": 1}})
            else:
                # 判断压差 齿轮箱主泵1_2高速=1，齿轮箱主泵1_2出口压力-齿轮箱A1口压力＞3.5，且持续5min
                df = df[(df[tickets[3]] == 1) & (df[tickets[2]] - df[tickets[4]] > 3.5)]
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱主泵滤芯压差1_2异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 21, "result": 1}})
                else:
                    self.send_message({"message": {"function": 21, "result": 0, "details": result[1]}})

    # 23 齿轮箱主泵滤芯压差2_1异常
    def gearbox_main_pump_filter2_1_oil_pressure_difference(self):
        """
        齿轮箱油温>45，齿轮箱主泵2_1出口压力≠0，齿轮箱主泵2_1高速=1，齿轮箱主泵2_1出口压力-齿轮箱A2口压力＞3.5，且持续5min
        """
        try:
            # 获取 时间 0 齿轮箱油温 5 齿轮箱主泵2_1出口压力 33 齿轮箱主泵2_1高速 22  齿轮箱A2口压力 26 英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[33], self.tickets[22],
                       self.tickets[26]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数23")
            self.send_message({"message": {"function": 22, "result": -1}})

        df = df.drop(df[(df[tickets[1]] <= 45)].index)
        if df.empty:
            self.send_message({"message": {"function": 22, "result": 1}})
        else:
            # 删除齿轮箱主泵1_1出口压力=0
            df = df.drop(df[(df[tickets[2]] == 0)].index)
            if df.empty:
                self.send_message({"message": {"function": 22, "result": 1}})
            else:
                # 判断压差 齿轮箱主泵2_1高速=1，齿轮箱主泵2_1出口压力-齿轮箱A1口压力＞3.5，且持续5min
                df = df[(df[tickets[3]] == 1) & (df[tickets[2]] - df[tickets[4]] > 3.5)]
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱主泵滤芯压差2_1异常.csv')
                if result[0]:
                    self.send_message({"message": {"function": 22, "result": 1}})
                else:
                    self.send_message({"message": {"function": 22, "result": 0, "details": result[1]}})

    # 24 齿轮箱主泵滤芯压差2_2异常
    def gearbox_main_pump_filter2_2_oil_pressure_difference(self):
        """
        齿轮箱油温>45，齿轮箱主泵2_2出口压力≠0，齿轮箱主泵2_2高速=1，齿轮箱主泵2_2出口压力-齿轮箱A2口压力＞3.5，且持续5min
        """
        try:
            # 获取 时间 0 齿轮箱油温 5 齿轮箱主泵2_2出口压力 34 齿轮箱主泵2_2高速 23  齿轮箱A2口压力 26 英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[34], self.tickets[23],
                       self.tickets[26]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数24")
            self.send_message({"message": {"function": 23, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 45)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 23, "result": 1}})
        else:
            # 删除齿轮箱主泵1_1出口压力=0
            df = df.drop(df[(df[tickets[2]] == 0)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 23, "result": 1}})
            else:
                # 判断压差 齿轮箱主泵2_1高速=1，齿轮箱主泵2_1出口压力-齿轮箱A1口压力＞3.5，且持续5min
                df = df[(df[tickets[3]] == 1) & (df[tickets[2]] - df[tickets[4]] > 3.5)]
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          300,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱主泵滤芯压差2_2异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 23, "result": 1}})
                else:
                    self.send_message({"message": {"function": 23, "result": 0, "details": result[1]}})

    # 25 齿轮箱冷却泵出口压力异常
    def gearbox_cooling_pump_outlet_oil_pressure(self):
        """
        齿轮箱油温>55，齿轮箱冷却泵出口压力≠0，齿轮箱冷却泵=1，齿轮箱冷却泵出口压力<2或>7，且持续30s
        """
        try:
            # 获取 时间 齿轮箱油温 5 齿轮箱冷却泵出口压力 35 齿轮箱冷却泵 36 英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[35], self.tickets[36]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数25")
            self.send_message({"message": {"function": 24, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 55)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 24, "result": 1}})
        else:
            # 删除齿轮箱冷却泵出口压力=0
            df = df.drop(df[(df[tickets[2]] == 0)].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 24, "result": 1}})
            else:
                # 判断 齿轮箱冷却泵=1，齿轮箱冷却泵出口压力<2或>7，且持续30s
                df = df[(df[tickets[3]] == 1) & ((df[tickets[2]] < 2) | (df[tickets[2]] > 7))]
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱冷却泵出口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 24, "result": 1}})
                else:
                    self.send_message({"message": {"function": 24, "result": 0, "details": result[1]}})

    # 26 齿轮箱过滤泵出口压力异常
    def gearbox_bypass_pump_outlet_oil_pressure(self):
        """
        齿轮箱油温>50，齿轮箱过滤泵=1，齿轮箱过滤泵出口压力<1或>4，且持续30s
        """
        try:
            # 获取 时间 齿轮箱油温 5 齿轮箱过滤泵 37 齿轮箱过滤泵出口压力 38 英文标签
            tickets = [self.tickets[0], self.tickets[5], self.tickets[37], self.tickets[38]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数26")
            self.send_message({"message": {"function": 25, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 50)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 25, "result": 1}})
        else:
            # 判断 齿轮箱过滤泵=1，齿轮箱过滤泵出口压力<1或>4，且持续30s
            df = df[(df[tickets[2]] == 1) & ((df[tickets[3]] < 1) | (df[tickets[3]] > 4))]
            # ------------------判断连续性
            result = tool.duration_calculation_to_csv(tickets,
                                                      df,
                                                      30,
                                                      str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                      '/齿轮箱过滤泵出口压力异常.csv')
            if result[0]:
                log.info("正常")
                self.send_message({"message": {"function": 25, "result": 1}})
            else:
                self.send_message({"message": {"function": 25, "result": 0, "details": result[1]}})

    # 27 齿轮箱油位异常
    def gearbox_oil_level(self):
        """
        12≤运行模式≤14，齿轮箱油位>80%或<30%，持续30s
        """
        try:
            # 获取 1 时间 2 机组模式 3 齿轮箱主轴承温度英文标签
            tickets = [self.tickets[0], self.tickets[1], self.tickets[39]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数27")
            self.send_message({"message": {"function": 26, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 12)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 26, "result": 1}})
        else:
            # 删除齿轮箱油位<=80%且>=30%
            df = df.drop(df[(df[tickets[2]] >= 30 & (df[tickets[2]] <= 80))].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 26, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱油位异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 26, "result": 1}})
                else:
                    self.send_message({"message": {"function": 26, "result": 0, "details": result[1]}})

    # 28 齿轮箱水泵1温差异常
    def gearbox_water_pump1_temperature_difference(self):
        """
        齿轮箱水泵1启动=1，齿轮箱水冷风扇1高速启动=1，齿轮箱水泵出口温度-齿轮箱水泵入口温度1＜2.2
        """
        try:
            # 获取 时间 0 齿轮箱水泵1启动 40 齿轮箱水冷风扇1高速启动 41 齿轮箱水泵出口温度 10 齿轮箱水泵入口温度1 11 英文标签
            tickets = [self.tickets[0], self.tickets[40], self.tickets[41], self.tickets[10],
                       self.tickets[11]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数28")
            self.send_message({"message": {"function": 27, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 27, "result": 1}})
        else:
            # 判断 齿轮箱水冷风扇1高速启动=1，齿轮箱水泵出口温度-齿轮箱水泵入口温度1＜2.2
            df = df[(df[tickets[2]] == 1) & (df[tickets[3]] - df[tickets[4]] < 2.2)]
            # ------------------判断连续性
            result = tool.duration_calculation_to_csv(tickets,
                                                      df,
                                                      1,
                                                      str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                      '/齿轮箱水泵1温差异常.csv')
            if result[0]:
                log.info("正常")
                self.send_message({"message": {"function": 27, "result": 1}})
            else:
                self.send_message({"message": {"function": 27, "result": 0, "details": result[1]}})

    # 29 齿轮箱水泵2温差异常
    def gearbox_water_pump2_temperature_difference(self):
        """
        齿轮箱水泵2启动=1，齿轮箱水冷风扇2高速启动=1，齿轮箱水泵出口温度-齿轮箱水泵入口温度2＜2.2
        """
        try:
            # 获取 时间 0 齿轮箱水泵2启动 42 齿轮箱水冷风扇2高速启动 43 齿轮箱水泵出口温度 10 齿轮箱水泵入口温度2 12 英文标签
            tickets = [self.tickets[0], self.tickets[42], self.tickets[43], self.tickets[10],
                       self.tickets[12]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数29")
            self.send_message({"message": {"function": 28, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 28, "result": 1}})
        else:
            # 判断 齿轮箱水冷风扇2高速启动=1，齿轮箱水泵出口温度-齿轮箱水泵入口温度2＜2.2
            df = df[(df[tickets[2]] == 1) & (df[tickets[3]] - df[tickets[4]] < 2.2)]
            # ------------------判断连续性
            result = tool.duration_calculation_to_csv(tickets,
                                                      df,
                                                      1,
                                                      str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                      '/齿轮箱水泵2温差.csv')
            if result[0]:
                log.info("正常")
                self.send_message({"message": {"function": 28, "result": 1}})
            else:
                self.send_message({"message": {"function": 28, "result": 0, "details": result[1]}})

    # 30 齿轮箱水泵1出口压力异常
    def gearbox_water_pump1_outlet_oil_pressure(self):
        """
        齿轮箱水泵1启动=1，齿轮箱水泵1出口压力小于3或者大于6，持续30s
        """
        try:
            # 获取  时间 0 齿轮箱水泵1启动 40 齿轮箱水泵1出口压力 44 英文标签
            tickets = [self.tickets[0], self.tickets[40], self.tickets[44]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数30")
            self.send_message({"message": {"function": 29, "result": -1}})
            return
        # 删除齿轮箱水泵1启动 !=1
        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 29, "result": 1}})
        else:
            # 齿轮箱水泵1出口压力小于3或者大于6，持续30s
            df = df.drop(df[(df[tickets[2]] >= 3 & (df[tickets[2]] <= 6))].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 29, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱水泵1出口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 29, "result": 1}})
                else:
                    self.send_message({"message": {"function": 29, "result": 0, "details": result[1]}})

    # 31 齿轮箱水泵1入口压力异常
    def gearbox_water_pump1_inlet_oil_pressure(self):
        """
        齿轮箱水泵1启动=1，齿轮箱水泵1入口压力小于1或大于3，持续30s
        """
        try:
            # 获取  时间 0 齿轮箱水泵1启动 40 齿轮箱水泵1入口压力 45 英文标签
            tickets = [self.tickets[0], self.tickets[40], self.tickets[45]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数31")
            self.send_message({"message": {"function": 30, "result": -1}})
            return
        # 删除齿轮箱水泵1启动 !=1
        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 30, "result": 1}})
        else:
            # 齿轮箱水泵1入口压力小于1或大于3，持续30s
            df = df.drop(df[(df[tickets[2]] >= 1 & (df[tickets[2]] <= 3))].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 30, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱水泵1入口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 30, "result": 1}})
                else:
                    self.send_message({"message": {"function": 30, "result": 0, "details": result[1]}})

    # 32 齿轮箱水泵2出口压力异常
    def gearbox_water_pump2_outlet_oil_pressure(self):
        """
        齿轮箱水泵2启动=1，齿轮箱水泵2出口压力小于3或者大于6，持续30s
        """
        try:
            # 获取  时间 0 齿轮箱水泵2启动 42 齿轮箱水泵2出口压力 46 英文标签
            tickets = [self.tickets[0], self.tickets[42], self.tickets[46]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数32")
            self.send_message({"message": {"function": 31, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 31, "result": 1}})
        else:
            # 齿轮箱水泵1出口压力小于3或者大于6，持续30s
            df = df.drop(df[(df[tickets[2]] >= 3 & (df[tickets[2]] <= 6))].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 31, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱水泵2出口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 31, "result": 1}})
                else:
                    self.send_message({"message": {"function": 31, "result": 0, "details": result[1]}})

    # 33 齿轮箱水泵2入口压力异常
    def gearbox_water_pump2_inlet_oil_pressure(self):
        """
        齿轮箱水泵2启动=1，齿轮箱水泵2入口压力小于1或者大于3，持续30s
        """
        try:
            # 获取  时间 0 齿轮箱水泵2启动 42 齿轮箱水泵2入口压力 47 英文标签
            tickets = [self.tickets[0], self.tickets[42], self.tickets[47]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数33")
            self.send_message({"message": {"function": 32, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 32, "result": 1}})
        else:
            # 齿轮箱水泵1入口压力小于1或大于3，持续30s
            df = df.drop(df[(df[tickets[2]] >= 1 & (df[tickets[2]] <= 3))].index)
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 32, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          30,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/齿轮箱水泵2入口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 32, "result": 1}})
                else:
                    self.send_message({"message": {"function": 32, "result": 0, "details": result[1]}})

    # 34 齿轮箱水泵1压力差异常
    def gearbox_water_pump1_oil_pressure_difference(self):
        """
        齿轮箱水泵1启动=1，齿轮箱水泵1出口压力减去入口压力＜1或者齿轮箱水泵1出口压力减去入口压力＞4，持续30s
        """
        try:
            # 获取 时间 0 齿轮箱水泵1启动 40 齿轮箱水泵1出口压力 44 齿轮箱水泵1入口压力 45 英文标签
            tickets = [self.tickets[0], self.tickets[40], self.tickets[44], self.tickets[45]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数34")
            self.send_message({"message": {"function": 33, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 33, "result": 1}})
        else:
            # 判断 齿轮箱水泵1出口压力减去入口压力＜1或者齿轮箱水泵1出口压力减去入口压力＞4，持续30s
            df = df[(df[tickets[2]] - df[tickets[3]] < 1) | (df[tickets[2]] - df[tickets[3]] > 4)]
            # ------------------判断连续性
            result = tool.duration_calculation_to_csv(tickets,
                                                      df,
                                                      1,
                                                      str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                      '/齿轮箱水泵1压力差异常.csv')
            if result[0]:
                log.info("正常")
                self.send_message({"message": {"function": 33, "result": 1}})
            else:
                self.send_message({"message": {"function": 33, "result": 0, "details": result[1]}})

    # 35 齿轮箱水泵2压力差异常
    def gearbox_water_pump2_oil_pressure_difference(self):
        """
        齿轮箱水泵2启动=1，齿轮箱水泵2出口压力减去入口压力＜1或者齿轮箱水泵2出口压力减去入口压力＞4，持续30s
        """
        try:
            # 获取 时间 0 齿轮箱水泵1启动 40 齿轮箱水泵2出口压力 44 齿轮箱水泵2入口压力 45 英文标签
            tickets = [self.tickets[0], self.tickets[40], self.tickets[46], self.tickets[47]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("齿轮箱跳过函数35")
            self.send_message({"message": {"function": 34, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 1)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 34, "result": 1}})
        else:
            # 判断 齿轮箱水泵1出口压力减去入口压力＜1或者齿轮箱水泵1出口压力减去入口压力＞4，持续30s
            df = df[(df[tickets[2]] - df[tickets[3]] < 1) | (df[tickets[2]] - df[tickets[3]] > 4)]
            # ------------------判断连续性
            result = tool.duration_calculation_to_csv(tickets,
                                                      df,
                                                      1,
                                                      str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                      '/齿轮箱水泵2压力差异常.csv')
            if result[0]:
                log.info("正常")
                self.send_message({"message": {"function": 34, "result": 1}})
            else:
                self.send_message({"message": {"function": 34, "result": 0, "details": result[1]}})

    def over(self):
        log.info("齿轮箱处理完成")
        self.postman.send_to_MM.emit(
            {"from": "gearbox", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )


if __name__ == '__main__':
    g = GearBox(pm=None)
    g.send_message({"message": {"function": 0, "result": 1}})
