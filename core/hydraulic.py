# -------------------------------------------------------------------------------
# Name:         hydraulic
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:
# -------------------------------------------------------------------------------
from PyQt5.QtCore import QThread

import os
import sys
from core import my_log
import pandas as pd
from core import cores
from core import tool
from core import gloable_var as gl
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook


class Hydraulic(QThread):
    def __init__(self, pm):
        super(Hydraulic, self).__init__()
        self.postman = pm
        self.df = None
        self.project_name = None
        self.tickets = None
        self.function_list = [
            self.get_df,
            self.hydraulic_sys,
            self.hydraulic_stop,
            self.hydraulic_yaw_brake_open_half_pressure1,
            self.hydraulic_yaw_brake_open_half_pressure2,
            self.hydraulic_oil_temperature,
            self.hydraulic_pump_outlet_pressure,
            self.hydraulic_rotor_lock_pressure,
            self.hydraulic_rotor_lock_actived_accumlator_pressure,
            self.yaw_brake_pressure,
            self.hydraulic_yaw_brake1,
            self.hydraulic_yaw_brake2,
            self.over
        ]

    def get_df(self):
        tickets_list = ["时间",
                        "机组运行模式",
                        "液压系统压力",
                        "液压泵1开",
                        "液压泵2开",
                        "顺时针偏航",
                        "逆时针偏航",
                        "偏航制动出口压力1",
                        "偏航制动出口压力2",
                        "偏航制动入口压力1",
                        "偏航制动入口压力2",
                        "偏航半释放阀",
                        "液压主泵处油温",
                        "液压泵出口压力",
                        "液压回油口油温",
                        "叶轮锁定压力1",
                        "叶轮锁定压力2",
                        "叶轮锁蓄能器压力1",
                        "叶轮锁蓄能器压力2"
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
        message["from"] = "hydraulic"
        message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def run(self):
        log.info("液压系统开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 64 液压系统压力异常
    def hydraulic_sys(self):
        """
        12≤ 机组运行模式 ≤14，液压系统压力 < 150bar 或 > 175bar, 持续20s
        """
        try:
            # 获取 0时间  1机组运行模式  2液压系统压力
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数64")
            self.send_message({"message": {"function": 63, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 12))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 63, "result": 1}})
        else:
            df = df[(df[tickets[2]] > 175) | (df[tickets[2]] < 150)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 63, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          20,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/液压系统压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 63, "result": 1}})
                else:
                    self.send_message({"message": {"function": 63, "result": 0, "details": result[1]}})

    # 65 液压泵频繁启停异常
    def hydraulic_stop(self):
        """
        机组运行模式=14,机组未偏航期间（偏航CW和偏航CCW都为0）,液压泵未启动时，
        液压系统压力值的瞬时值与上一秒瞬时值差值的绝对值≥0.1bar，持续1min
        """
        try:
            # 获取 0时间  1机组运行模式  2液压系统压力  3液压泵1开  4液压泵2开  5顺时针偏航  6逆时针偏航
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2], self.tickets[3],
                       self.tickets[4], self.tickets[5], self.tickets[6]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3],
                          tickets[4], tickets[5], tickets[6]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数65")
            self.send_message({"message": {"function": 64, "result": -1}})
            return

        df = df[(df[tickets[1]] == 14) & (df[tickets[3]] == 0) & (df[tickets[4]] == 0)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 64, "result": 1}})
        else:
            df = df[(df[tickets[5]] == 0) & (df[tickets[6]] == 0)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 64, "result": 1}})
            else:
                # 液压系统压力值的瞬时值与上一秒瞬时值差值的绝对值≥0.1bar, 持续1min
                # df['shift'] = df[tickets[2]].shift(1)
                df['diff'] = df[tickets[2]].diff(1).abs()
                # df = df[(df['shift'] >= 0.1)]
                df = df[(df['diff'] >= 0.1)]
                if df.empty:
                    log.info("正常")
                    self.send_message({"message": {"function": 64, "result": 1}})
                else:
                    # ------------------判断连续性
                    result = tool.duration_calculation_to_csv(tickets,
                                                              df,
                                                              60,
                                                              str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                              '/液压泵频繁启停异常.csv')
                    if result[0]:
                        log.info("正常")
                        self.send_message({"message": {"function": 64, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 64, "result": 0, "details": result[1]}})

    # 66 偏航半释放压力1异常
    def hydraulic_yaw_brake_open_half_pressure1(self):
        """
        1.偏航半释放阀为1时，液压偏航制动入口压力1和液压偏航制动出口压力1最小值超出[25, 47]范围，
        2.液压偏航制动入口压力1和液压偏航制动出口压力1差值大于2或小于 - 1，持续3秒。
        满足其一
        """
        try:
            # 获取  0时间  11偏航半释放阀 9偏航制动入口压力1  7偏航制动出口压力1
            tickets = [self.tickets[0], self.tickets[11], self.tickets[9], self.tickets[7]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数66")
            self.send_message({"message": {"function": 65, "result": -1}})
            return

        # 情况1 偏航半释放阀为1时，液压偏航制动入口压力1和液压偏航制动出口压力1最小值超出[25, 47]范围，
        df_h = df.drop(df[(df[tickets[1]] != 1)].index).copy()
        # #  获得 每一秒 液压偏航制动入口压力1和液压偏航制动出口压力1最小值,判断是否在[25, 47]范围
        df_h['minvalue'] = df_h.loc[:, [tickets[2], tickets[3]]].min(axis=1, skipna=True)
        df_h = df_h[(df_h['minvalue'] > 47) | (df_h['minvalue'] < 25)]
        # 情况2 液压偏航制动入口压力1和液压偏航制动出口压力1差值大于2或小于 - 1，持续3秒
        df_l = df[(df[tickets[2]] - df[tickets[3]] < -1) | (df[tickets[2]] - df[tickets[3]] > 2)].copy()
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 65, "result": 1}})
        else:
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航半释放压力1异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 65, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 65, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          3,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航半释放压力1异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 65, "result": 1}})
                else:
                    self.send_message({"message": {"function": 65, "result": 0, "details": result[1]}})

    # 67 偏航半释放压力2异常
    def hydraulic_yaw_brake_open_half_pressure2(self):
        """
        1.偏航半释放阀为1时，液压偏航制动入口压力2和液压偏航制动出口压力2最小值超出[25,47]范围，
        2.液压偏航制动入口压力2和液压偏航制动出口压力2差值大于2或小于-1，持续3秒。
        满足其一
        """
        try:
            # 获取  0时间  11偏航半释放阀 10偏航制动入口压力2  8偏航制动出口压力2
            tickets = [self.tickets[0], self.tickets[11], self.tickets[10], self.tickets[8]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数67")
            self.send_message({"message": {"function": 66, "result": -1}})
            return

        # 情况1 偏航半释放阀为1时，液压偏航制动入口压力2和液压偏航制动出口压力2最小值超出[25, 47]范围，
        df_h = df.drop(df[(df[tickets[1]] != 1)].index).copy()
        # #  获得 每一秒 液压偏航制动入口压力2和液压偏航制动出口压力2最小值,判断是否在[25, 47]范围
        df_h['min'] = df_h.loc[:, [tickets[2], tickets[3]]].min(axis=1, skipna=True)
        df_h = df_h[(df_h['min'] > 47) | (df_h['min'] < 25)]
        # 情况2 液压偏航制动入口压力2和液压偏航制动出口压力2差值大于2或小于 - 1，持续3秒
        df_l = df[(df[tickets[2]] - df[tickets[3]] < -1) | (df[tickets[2]] - df[tickets[3]] > 2)].copy()
        if df_h.empty and df_l.empty:
            log.info("正常")
            self.send_message({"message": {"function": 66, "result": 1}})
        else:
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航半释放压力2异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 66, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 66, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          3,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航半释放压力2异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 66, "result": 1}})
                else:
                    self.send_message({"message": {"function": 66, "result": 0, "details": result[1]}})

    # 68 液压系统油温异常
    def hydraulic_oil_temperature(self):
        """
        12≤机组运行模式≤14，液压泵主泵处油温和液压回油口油温≠0，两者最小值<20℃，最大值>60℃，持续1min
        """
        try:
            # 获取  0时间  1机组运行模式  12液压主泵处油温  14液压回油口油温
            tickets = [self.tickets[0], self.tickets[1], self.tickets[12], self.tickets[14]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数68")
            self.send_message({"message": {"function": 67, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 12))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 67, "result": 1}})
        else:
            df = df[(df[tickets[2]] != 0) & (df[tickets[3]] != 0)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 67, "result": 1}})
            else:
                # 判断两者最小值<20℃，最大值>60℃
                df['min'] = df.loc[:, [tickets[2], tickets[3]]].min(axis=1, skipna=True)
                df['max'] = df.loc[:, [tickets[2], tickets[3]]].max(axis=1, skipna=True)
                df = df[(df['min'] < 20) & (df['max'] > 60)]
                if df.empty:
                    log.info("正常")
                    self.send_message({"message": {"function": 67, "result": 1}})
                else:
                    # ------------------判断连续性 持续1min
                    result = tool.duration_calculation_to_csv(tickets,
                                                              df,
                                                              60,
                                                              str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                              '/液压系统油温异常.csv')
                    if result[0]:
                        log.info("正常")
                        self.send_message({"message": {"function": 67, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 67, "result": 0, "details": result[1]}})

    # 69 液压泵出口压力异常
    def hydraulic_pump_outlet_pressure(self):
        """
        液压泵1启动 或 液压泵2启动 = 1时，液压泵出口压力 <150bar 或 >175bar，持续10s
        """
        try:
            # 获取 0时间  3液压泵1开  4液压泵2开  13液压泵出口压力
            tickets = [self.tickets[0], self.tickets[3], self.tickets[4], self.tickets[13]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数69")
            self.send_message({"message": {"function": 68, "result": -1}})
            return

        df = df[(df[tickets[1]] == 1) | (df[tickets[2]] == 1)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 68, "result": 1}})
        else:
            df = df[(df[tickets[3]] > 175) | (df[tickets[3]] < 150)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 68, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          10,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/液压泵出口压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 68, "result": 1}})
                else:
                    self.send_message({"message": {"function": 68, "result": 0, "details": result[1]}})

    # 70 液压叶轮锁定压力异常
    def hydraulic_rotor_lock_pressure(self):
        """
        液压系统压力 > 150时，液压叶轮锁定压力1 和 液压叶轮锁定压力2 >120bar 或 <80bar，持续1min
        """
        try:
            # 获取 0时间  2液压系统压力  15叶轮锁定压力1  16叶轮锁定压力2
            tickets = [self.tickets[0], self.tickets[2], self.tickets[15], self.tickets[16]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数70")
            self.send_message({"message": {"function": 69, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] <= 150)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 69, "result": 1}})
        else:
            df = df[((df[tickets[2]] > 120) | (df[tickets[2]] < 80)) & (
                    (df[tickets[3]] > 120) & (df[tickets[3]] < 80))]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 69, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/液压叶轮锁定压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 69, "result": 1}})
                else:
                    self.send_message({"message": {"function": 69, "result": 0, "details": result[1]}})

    # 71 叶轮锁定储能罐压力异常
    def hydraulic_rotor_lock_actived_accumlator_pressure(self):
        """
        1.液压系统压力>150时，叶轮锁定储能罐压力1和叶轮锁定储能罐压力2>120bar或<70bar，持续1min
        2.液压叶轮锁定压力1 < 50bar且≠0时，叶轮锁定储能罐压力1 < 70bar
        3.液压叶轮锁定压力2 < 50bar且≠0时，叶轮锁定储能罐压力2 < 70bar
        满足其一，报出叶轮锁定储能罐压力异常
        """
        try:
            # 获取 0时间  2液压系统压力  15叶轮锁定压力1  16叶轮锁定压力2  17叶轮锁蓄能器压力1  18叶轮锁蓄能器压力2
            tickets = [self.tickets[0], self.tickets[2], self.tickets[15], self.tickets[16], self.tickets[17],
                       self.tickets[18]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4], tickets[5]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数71")
            self.send_message({"message": {"function": 70, "result": -1}})
            return

        # 情况1 1>150 & (4>120 | 4<70) & (5>120 | 5<70)
        df_h = df[((df[tickets[1]] > 150) & ((df[tickets[4]] > 120) | (df[tickets[4]] < 70)) & (
                (df[tickets[5]] > 120) | (df[tickets[5]] < 70)))].copy()
        # 情况2 2<50 & 2!=0 & 4<70
        df_l = df[((df[tickets[2]] < 50) & (df[tickets[2]] != 0) & (df[tickets[4]] < 70))].copy()
        # 情况3 3<50 & 3!=0 & 5<70
        df_e = df[((df[tickets[3]] < 50) & (df[tickets[3]] != 0) & (df[tickets[5]] < 70))].copy()
        # 判断是否未空
        if df_h.empty and df_l.empty and df_e.empty:
            log.info("正常")
            self.send_message({"message": {"function": 70, "result": 1}})
        else:
            # ------------------判断连续性
            flag = False
            if not df_h.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_h,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/叶轮锁定储能罐压力异常1.csv')
                if result[0]:
                    flag = True
                    log.info("正常")
                    self.send_message({"message": {"function": 70, "result": 1}})
                else:
                    flag = False
                    self.send_message({"message": {"function": 70, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_l.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_l,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/叶轮锁定储能罐压力异常2.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 70, "result": 1}})
                        flag = True
                else:
                    flag = False
                    self.send_message({"message": {"function": 70, "result": 0, "details": result[1]}})
            else:
                flag = True
            if not df_e.empty:
                result = tool.duration_calculation_to_csv(tickets,
                                                          df_e,
                                                          1,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/叶轮锁定储能罐压力异常3.csv')
                if result[0]:
                    if flag:
                        log.info("正常")
                        self.send_message({"message": {"function": 70, "result": 1}})
                else:
                    self.send_message({"message": {"function": 70, "result": 0, "details": result[1]}})

    # 72 偏航压力异常
    def yaw_brake_pressure(self):
        """
        机组运行模式=14，机组不偏航时（偏航CW和偏航CCW都为0），
        液压偏航制动入口压力1、液压偏航制动出口压力1、液压偏航制动入口压力2、液压偏航制动出口压力2最小值< 150bar或最大值>175bar，持续20s
        """
        try:
            # 获取 0时间  1机组运行模式  5顺时针偏航  6逆时针偏航  7偏航制动出口压力1  9偏航制动入口压力1
            # 8偏航制动出口压力2  10偏航制动入口压力2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[5], self.tickets[6],
                       self.tickets[7], self.tickets[9], self.tickets[8], self.tickets[10]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3],
                          tickets[4], tickets[5], tickets[6], tickets[7]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数72")
            self.send_message({"message": {"function": 71, "result": -1}})
            return

        df = df[(df[tickets[1]] == 14) & ((df[tickets[2]] == 0) & (df[tickets[3]] == 0))]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 71, "result": 1}})
        else:
            # 获取4个的最大最小值
            df['max'] = df.loc[:, [tickets[4], tickets[5], tickets[6], tickets[7]]].max(axis=1, skipna=True)
            df['min'] = df.loc[:, [tickets[4], tickets[5], tickets[6], tickets[7]]].min(axis=1, skipna=True)
            df = df[((df['min'] < 150) | (df['max'] > 175))]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 71, "result": 1}})
            else:
                # ------------------判断连续性 20s
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          20,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航压力异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 71, "result": 1}})
                else:
                    self.send_message({"message": {"function": 71, "result": 0, "details": result[1]}})

    # 73 偏航制动器1异常
    def hydraulic_yaw_brake1(self):
        """
        机组运行模式 = 14，液压偏航制动入口压力1 > 150时，液压偏航制动入口压力1 - 液压偏航制动出口压力1 > 2bar，持续 10 s
        """
        try:
            # 获取 0时间  1机组运行模式  9偏航制动入口压力1  7偏航制动出口压力1
            tickets = [self.tickets[0], self.tickets[1], self.tickets[9], self.tickets[7]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数73")
            self.send_message({"message": {"function": 72, "result": -1}})
            return

        df = df[(df[tickets[1]] == 14) & (df[tickets[2]] > 150)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 72, "result": 1}})
        else:
            df = df[(df[tickets[2]] - df[tickets[3]] > 2)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 72, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          10,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航制动器1异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 72, "result": 1}})
                else:
                    self.send_message({"message": {"function": 72, "result": 0, "details": result[1]}})

    # 74 偏航制动器2异常
    def hydraulic_yaw_brake2(self):
        """
        机组运行模式 = 14，液压偏航制动入口压力1 > 150时，液压偏航制动入口压力1 - 液压偏航制动出口压力1 > 2bar，持续 10 s
        """
        try:
            # 获取 0时间  1机组运行模式  10偏航制动入口压力2  8偏航制动出口压力2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[10], self.tickets[8]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("液压跳过函数74")
            self.send_message({"message": {"function": 73, "result": -1}})
            return

        df = df[(df[tickets[1]] == 14) & (df[tickets[2]] > 150)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 73, "result": 1}})
        else:
            df = df[(df[tickets[2]] - df[tickets[3]] > 2)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 73, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          10,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/偏航制动器2异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 73, "result": 1}})
                else:
                    self.send_message({"message": {"function": 73, "result": 0, "details": result[1]}})

    def over(self):
        # # #  ************************ # # #
        self.df = None
        # # #  ************************ # # #
        log.info("液压系统处理完成")
        self.postman.send_to_MM.emit(
            {"from": "hydraulic", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )
