# -------------------------------------------------------------------------------
# Name:         pitch
# Description:
# Author:       A07567
# Date:         2020/12/29
# Description:
# -------------------------------------------------------------------------------
from PySide2.QtCore import QThread, Signal
import time
import os
import sys
sys.path.append("..")
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


class Pitch(QThread):
    def __init__(self, pm):
        super(Pitch, self).__init__()
        self.postman = pm
        self.df = None
        self.project_name = None
        self.tickets = None
        self.function_list = [
            self.get_df,
            self.pitch_rotor_speed,
            self.pitch_motor_temperature,
            self.pitch_box_temperature,
            self.pitch_box_temperature_difference,
            self.pitch_driver_ratiator_temperature,
            self.pitch_battery_box_temperature,
            self.pitch_battery_box_temperature_difference,
            self.over
        ]

    def get_df(self):
        tickets_list = ["时间",
                        "机组运行模式",
                        "变桨驱动柜温度1",
                        "变桨驱动柜温度2",
                        "变桨驱动柜温度3",
                        "桨叶角度1A",
                        "桨叶角度2A",
                        "桨叶角度3A",
                        "桨叶角度1B",
                        "桨叶角度2B",
                        "桨叶角度3B",
                        "叶轮速度1",
                        "叶轮速度2",
                        "风速",
                        "变桨电机温度1",
                        "变桨电机温度2",
                        "变桨电机温度3",
                        "变桨驱动柜散热器温度1",
                        "变桨驱动柜散热器温度2",
                        "变桨驱动柜散热器温度3",
                        "变桨后备电源柜温度1",
                        "变桨后备电源柜温度2",
                        "变桨后备电源柜温度3"]
        self.project_name = str(os.path.basename(gl.now_file)).split(".")[-2].split("_")[0][:5]
        self.tickets = cores.get_en_tickets("../db/tickets.my", self.project_name, tickets_list)
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
        message["from"] = "pitch"
        message["to"] = "model_manager"
        self.postman.send_to_MM.emit(message)

    def run(self):
        log.info("变桨系统开始处理：{}".format(gl.now_file))
        for (func, i) in zip(self.function_list, range(len(self.function_list))):
            func()

    # 49 桨叶顺桨异常
    def pitch_blade_feathering(self):
        pass

    # 50 叶轮转速超速
    def pitch_rotor_speed(self):
        """
        11≤ 机组运行模式 ≤14，叶轮转速1 和 叶轮转速2 都≥12.8rpm，持续 5s
        """
        try:
            # 获取  0时间  1机组运行模式  11叶轮速度1  12叶轮速度2
            tickets = [self.tickets[0], self.tickets[1], self.tickets[11], self.tickets[12]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数50")
            self.send_message({"message": {"function": 49, "result": -1}})
            return

        df = df.drop(df[((df[tickets[1]] > 14) | (df[tickets[1]] < 11))].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 49, "result": 1}})
        else:
            df = df[(df[tickets[2]] >= 12.8) & (df[tickets[3]] >= 12.8)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 49, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          5,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/叶轮转速超速.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 49, "result": 1}})
                else:
                    self.send_message({"message": {"function": 49, "result": 0, "details": result[1]}})

    # 51 桨叶电机温度异常
    def pitch_motor_temperature(self):
        """
        11≤ 机组运行模式 ≤14，单个桨叶电机温度 ＞ 120℃， 或两两温差绝对值≥30℃，持续1min
        """
        try:
            # 获取  0时间   1机组模式   14-16变桨电机温度1-3
            tickets = [self.tickets[0], self.tickets[1], self.tickets[14], self.tickets[15], self.tickets[16]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数51")
            self.send_message({"message": {"function": 50, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] > 14) | (df[tickets[1]] < 11)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 50, "result": 1}})
        else:
            df['桨叶电机1-桨叶电机2'] = (df[tickets[2]] - df[tickets[3]]).abs()
            df['桨叶电机1-桨叶电机3'] = (df[tickets[2]] - df[tickets[4]]).abs()
            df['桨叶电机2-桨叶电机3'] = (df[tickets[3]] - df[tickets[4]]).abs()
            # 情况1 单个桨叶电机温度 ＞ 120℃,1min
            df_h = df[(df[tickets[2]] > 120) | (df[tickets[3]] > 120) | (df[tickets[4]] > 120)].copy()
            # 情况2 两两温差绝对值≥30℃，且持续时间超过1min
            df_l = df[(df['桨叶电机1-桨叶电机2'] >= 30) | (df['桨叶电机1-桨叶电机3'] >= 30) | (df['桨叶电机2-桨叶电机3'] >= 30)].copy()

            if df_h.empty and df_l.empty:
                log.info("正常")
                self.send_message({"message": {"function": 50, "result": 1}})
            else:
                # ------------------判断连续性
                flag = False
                if not df_h.empty:
                    result = tool.duration_calculation_to_csv(tickets,
                                                              df_h,
                                                              60,
                                                              str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                              '/桨叶电机温度异常1.csv')
                    if result[0]:
                        flag = True
                        log.info("正常")
                        self.send_message({"message": {"function": 50, "result": 1}})
                    else:
                        flag = False
                        self.send_message({"message": {"function": 50, "result": 0, "details": result[1]}})
                else:
                    flag = True
                if not df_l.empty:
                    result = tool.duration_calculation_to_csv(tickets,
                                                              df_l,
                                                              60,
                                                              str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                              '/桨叶电机温度异常2.csv')
                    if result[0]:
                        if flag:
                            log.info("正常")
                            self.send_message({"message": {"function": 50, "result": 1}})
                    else:
                        self.send_message({"message": {"function": 50, "result": 0, "details": result[1]}})

    # 52 桨叶轴控箱温度异常
    def pitch_box_temperature(self):
        """
        单个桨叶轴控箱温度(变桨驱动柜温度1-3) ＞ 55℃ 或 ＜ -5℃，且 ≠ -40℃，持续1min；
        """
        try:
            # 获取  0时间  1机组运行模式  2-4变桨驱动柜温度1-3
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2], self.tickets[3], self.tickets[4]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], self.tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数52")
            self.send_message({"message": {"function": 51, "result": -1}})
            return

        df = df[(df[tickets[2]] != -40) & (df[tickets[3]] != -40) | (df[tickets[4]] != -40)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 51, "result": 1}})
        else:
            df = df[((df[tickets[2]] < -5) | (df[tickets[2]] > 55)) & ((df[tickets[3]] < -5) | (
                    df[tickets[3]] > 55)) & ((df[tickets[4]] < -5) | (df[tickets[4]] > 55))]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 51, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/桨叶轴控箱温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 51, "result": 1}})
                else:
                    self.send_message({"message": {"function": 51, "result": 0, "details": result[1]}})

    # 53 桨叶轴控箱温差异常
    def pitch_box_temperature_difference(self):
        """
        机组运行模式=14，两两桨叶轴控箱温差绝对值 ≥10℃，并且持续超过1min
        """
        try:
            # 获取  0时间   1机组模式  2-4变桨驱动柜温度1-3
            tickets = [self.tickets[0], self.tickets[1], self.tickets[2], self.tickets[3], self.tickets[4]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数53")
            self.send_message({"message": {"function": 52, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 52, "result": 1}})
        else:
            # 删除 绝对值 < 10℃，并且持续超过1min
            df['桨叶轴控箱1-桨叶轴控箱2'] = (df[tickets[2]] - df[tickets[3]]).abs()
            df['桨叶轴控箱1-桨叶轴控箱3'] = (df[tickets[2]] - df[tickets[4]]).abs()
            df['桨叶轴控箱2-桨叶轴控箱3'] = (df[tickets[3]] - df[tickets[4]]).abs()
            df = df[(df['桨叶轴控箱1-桨叶轴控箱2'] >= 10) | (df['桨叶轴控箱1-桨叶轴控箱3'] >= 10) | (df['桨叶轴控箱2-桨叶轴控箱3'] >= 10)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 52, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/桨叶轴控箱温差异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 52, "result": 1}})
                else:
                    self.send_message({"message": {"function": 52, "result": 0, "details": result[1]}})

    # 54 变桨驱动器散热器温度异常
    def pitch_driver_ratiator_temperature(self):
        """
        机组运行模式=14，驱动器1-3散热器温度 最大值与最小值差值超10℃，或最大值超过60℃，或最小值低于-5℃，但是不等于-40℃，并且持续超过1min
        """
        try:
            # 获取  0时间   1机组模式  17-19变桨驱动柜散热器温度1-3
            tickets = [self.tickets[0], self.tickets[1], self.tickets[17], self.tickets[18], self.tickets[19]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数54")
            self.send_message({"message": {"function": 53, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 53, "result": 1}})
        else:
            df['maxvalue'] = df[[tickets[2], tickets[3], tickets[4]]].max(axis=1)
            df['minvalue'] = df[[tickets[2], tickets[3], tickets[4]]].min(axis=1)
            df = df[(df['maxvalue'] - df['minvalue'] > 10) | (df['maxvalue'] > 60) | (
                    (df['minvalue'] < -5) & (df['minvalue'] != -40))]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 53, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/变桨驱动器散热器温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 53, "result": 1}})
                else:
                    self.send_message({"message": {"function": 53, "result": 0, "details": result[1]}})

    # 55 桨叶电池箱温度异常
    def pitch_battery_box_temperature(self):
        """
        单个桨叶电池箱温度(变桨后备电源柜温度1-3) ＞ 55℃ 或 ＜ -5℃，且 ≠ -40℃，持续1min；
        """
        try:
            # 获取  0时间  1机组运行模式   20-22变桨后备电源柜温度1-3
            tickets = [self.tickets[0], self.tickets[1], self.tickets[20], self.tickets[21], self.tickets[22]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数55")
            self.send_message({"message": {"function": 54, "result": -1}})
            return

        df = df[(df[tickets[2]] != -40) & (df[tickets[3]] != -40) & (df[tickets[4]] != -40)]
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 54, "result": 1}})

        else:
            df = df[(df[tickets[2]] < -5) | (df[tickets[2]] > 55) | (df[tickets[3]] < -5) | (
                    df[tickets[3]] > 55) | (df[tickets[4]] < -5) | (df[tickets[4]] > 55)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 54, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/桨叶电池箱温度异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 54, "result": 1}})
                else:
                    self.send_message({"message": {"function": 54, "result": 0, "details": result[1]}})

    # 56 桨叶电池箱温差异常
    def pitch_battery_box_temperature_difference(self):
        """
        机组运行模式=14，两两桨叶电池箱温差绝对值 ≥10℃，并且持续超过1min
        """
        try:
            # 获取 0时间  1机组模式 20-22变桨后备电源柜温度1-3
            tickets = [self.tickets[0], self.tickets[1], self.tickets[20], self.tickets[21], self.tickets[22]]
            df = self.df[['time', tickets[0], tickets[1], tickets[2], tickets[3], tickets[4]]]
        except Exception as e:
            log.warning(e)
            log.warning("变桨跳过函数56")
            self.send_message({"message": {"function": 55, "result": -1}})
            return

        df = df.drop(df[(df[tickets[1]] != 14)].index)
        if df.empty:
            log.info("正常")
            self.send_message({"message": {"function": 55, "result": 1}})
        else:
            # 绝对值 ≥10℃，并且持续超过1min
            df['电源柜1-电源柜2'] = (df[tickets[2]] - df[tickets[3]]).abs()
            df['电源柜1-电源柜3'] = (df[tickets[2]] - df[tickets[4]]).abs()
            df['电源柜2-电源柜3'] = (df[tickets[3]] - df[tickets[4]]).abs()
            df = df[(df['电源柜1-电源柜2'] >= 10) | (df['电源柜1-电源柜3'] >= 10) | (df['电源柜2-电源柜3'] >= 10)]
            if df.empty:
                log.info("正常")
                self.send_message({"message": {"function": 55, "result": 1}})
            else:
                # ------------------判断连续性
                result = tool.duration_calculation_to_csv(tickets,
                                                          df,
                                                          60,
                                                          str(gl.now_file).split(r'/')[-1].split('.')[0] +
                                                          '/桨叶电池箱温差异常.csv')
                if result[0]:
                    log.info("正常")
                    self.send_message({"message": {"function": 55, "result": 1}})
                else:
                    self.send_message({"message": {"function": 55, "result": 0, "details": result[1]}})

    def over(self):
        # # #  ************************ # # #
        self.df = None
        # # #  ************************ # # #
        log.info("变桨系统处理完成")
        self.postman.send_to_MM.emit(
            {"from": "pitch", "to": "thread_manager",
             "message": {"thread_name": self,
                         "do_what": "quit"}}
        )


if __name__ == '__main__':
    g = Pitch(pm=None)
    g.send_message({"message": {"function": 0, "result": 1}})
