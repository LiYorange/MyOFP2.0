# -------------------------------------------------------------------------------
# Name:         log
# Description:
# Author:       A07567
# Date:         2020/12/23
# Description:  
# -------------------------------------------------------------------------------
# !/usr/bin/python
# -*- coding:utf-8 -*-

import colorlog
import logging
import time
import os

log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


class Log(object):
    """
封装后的logging
    """

    def __init__(self, logger=None, log_cate='search'):
        """
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        """

        # 创建一个logger

        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        self.log_time = time.strftime("%Y_%m_%d")
        file_dir = os.getcwd()
        self.log_path = file_dir
        self.log_name = self.log_path + "/" + log_cate + "." + self.log_time + '.log'

        fh = logging.FileHandler(self.log_name, 'a')  # 追加模式  这个是python2的
        # fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        fh_formatter = logging.Formatter(
            '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s] -- %(message)s')
        ch_formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(filename)s:%(lineno)d] [%(levelname)s]- %(message)s',
            log_colors=log_colors_config)  # 日志输出格式
        fh.setFormatter(fh_formatter)
        ch.setFormatter(ch_formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        #  添加下面一句，在记录日志之后移除句柄
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()
        ch.close()

    def getlog(self):
        return self.logger
