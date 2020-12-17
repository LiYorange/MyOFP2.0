# -------------------------------------------------------------------------------
# Name:         draw
# Description:
# Author:       A07567
# Date:         2020/12/17
# Description:  
# -------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import logging

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']


class Draw:
    def __init__(self):
        pass

    def read_df(self, file_name):
        """拿到file读取为df"""
        pass

    def get_x(self):
        """从df中拿到x"""
        pass

    def get_y(self):
        """从df中拿到y,y的值也许是多个"""
        pass

    def drawing(self):
        """根据x,y绘图"""
        pass
    plt.plot()
    # @staticmethod
    # def get_x_y(file_name, x, y):
    #     data = pd.read_csv(file_name, usecols=[x, y], chunksize=10000, encoding='gbk',
    #                        engine='python')
    #     time1 = time.time()
    #     df = pd.concat(data, ignore_index=True)
    #     time2 = time.time()
    #     logging.warning(str(time2 - time1))
    #     return df
