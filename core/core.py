# -------------------------------------------------------------------------------
# Name:         core
# Description:
# Author:       A07567
# Date:         2020/12/18
# Description:  所有的功能实现核心
# -------------------------------------------------------------------------------
import time
import json
import pandas as pd
import numpy as np
import logging


def get_en_tickets(file, project_name):
    try:
        f = open(file, 'r', encoding='utf8')
        tickets_data = dict(json.load(f))
        return list(tickets_data[project_name].values())
    except KeyError as e:
        logging.debug(e)
    except FileNotFoundError as e:
        logging.debug(e)


def read_csv(file, use_cols):
    """读取csv"""
    # 读取整个文件的第一行(标签行)，用于与查找到的英文标签对比
    df_head = pd.DataFrame()
    df_head = pd.read_csv(file, encoding='gbk', engine='python', nrows=0)
    return get_df(df_head, use_cols, file)


def read_excel(file, use_cols):
    """还未写"""
    # 读取整个文件的第一行(标签行)，用于与查找到的英文标签对比
    df_head = pd.DataFrame()
    df_head = pd.read_excel(file, encoding='gbk', engine='python', nrows=0)
    return get_df(df_head, use_cols, file)


def get_df(df_head, use_cols, file):
    """
    2. 创建一个miss_data_list 用于存放丢失数据的位置，保证插入数据时在指定位置
    3.创建一个exist_data_list 用于真正读取csv文件
    4.在读取好的csv文件中按照丢失数据的位置插入 numpy的NAN数据
    :return: 返回一个df
    """
    try:
        def judge_miss(li):
            return list(df_head.columns.isin([li]))
        miss_data_list = []
        exist_data_list = []
        result = list(map(judge_miss, use_cols))
        for i in range(len(result)):
            if not any(result[i]):
                # 如果不全为false,则缺失数据，记录此时英文标签的位置
                miss_data_list.append(i)
            else:
                exist_data_list.append(use_cols[i])
        data = pd.read_csv(file, usecols=exist_data_list, chunksize=10000, encoding='gbk',
                           engine='python')
        df = pd.concat(data, ignore_index=True)
        return df
    except Exception as e:
        logging.debug(e)


if __name__ == '__main__':
    x = get_en_tickets('../db/tickets.my', "外罗")
    y = read_csv('../db/60004036_20200930（外罗）.csv', x[0:1])
    print(y)
