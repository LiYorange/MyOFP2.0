# -------------------------------------------------------------------------------
# Name:         load_draw_setting
# Description:
# Author:       A07567
# Date:         2021/1/6
# Description:  
# -------------------------------------------------------------------------------
import configparser
import os
import sys
import my_log
import traceback

log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook

cur_path = os.path.dirname(os.path.realpath(__file__))
default_cfg_path = os.path.join(cur_path, "default_draw_setting.ini")
user_cfg_path = os.path.join(cur_path, "user_draw_setting.ini")


def read_cfg(flag=False):
    """
    :param flag: 强制读取default
    :return:
    """
    # 创建管理对象
    conf = configparser.ConfigParser()
    # 读ini文件
    try:
        if os.path.isfile(user_cfg_path):
            conf.read(user_cfg_path, encoding="utf-8")  # python3
        else:
            conf.read(default_cfg_path, encoding="utf-8")
        if flag:
            conf.read(default_cfg_path, encoding="utf-8")
    except Exception as e:
        log.error(e)

    draw_type = {}
    draw_setting = {}
    try:
        draw_type.update(
            line=conf.getboolean('DrawType', 'line'),
            scatter=conf.getboolean('DrawType', 'scatter'),
            bar=conf.getboolean('DrawType', 'bar'),
            subplot=conf.getboolean('DrawType', 'subplot'),
            grid=conf.getboolean('DrawType', 'grid')
        )
        draw_setting.update(
            x_LL=conf.getfloat('DrawSetting', 'x_LL'),
            x_UL=conf.getfloat('DrawSetting', 'x_UL'),
            y_LL=conf.getfloat('DrawSetting', 'y_LL'),
            y_UL=conf.getfloat('DrawSetting', 'y_UL'),
            l_s=conf.getint('DrawSetting', 'l_s')
        )
        return draw_type, draw_setting
    except Exception as e:
        log.error(e)
        return


def write_cfg(dic: dict):
    try:
        conf = configparser.ConfigParser()
        conf.read(user_cfg_path)
        for d in dic.keys():
            for dd in dic[d]:
                conf.set(d, dd, str(dic[d][dd]))
        conf.write(open(user_cfg_path, "w+"))
    except Exception as e:
        log.error(e)


if __name__ == '__main__':
    read_cfg()
    write_cfg({1: 1})
