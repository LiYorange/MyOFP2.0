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
import os
import shutil
import my_log
import sys
sys.path.append("..")
from core import my_log
log = my_log.Log(__name__).getlog()



def get_en_tickets(file, project_name):
    try:
        f = open(file, 'r', encoding='utf8')
        tickets_data = dict(json.load(f))
        return list(tickets_data[project_name].values())
    except KeyError as e:
        log.info(e)

    except FileNotFoundError as e:
        log.info(e)
        


def read_csv(file, use_cols):
    """读取csv"""
    # 读取整个文件的第一行(标签行)，用于与查找到的英文标签对比
    df_head = pd.DataFrame()
    try:
        df_head = pd.read_csv(file, encoding='gbk', engine='python', nrows=0)
        return get_df(df_head, use_cols, file)
    except Exception as e:
        log.info(e)
        


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
        log.info(e)
        


def unpack(files) -> bool:
    """
    :param files:需要解压的文件
    生成一个data文件夹，用于存放解压数据，每次打开程序先清空该文件夹
    :return:
    """
    if files is not None:
        files = files
    else:
        return
    # 获得上一层目录
    data = os.path.abspath(os.path.dirname(os.getcwd())) + "\\data"
    # 主程序调用，不需要得到上层目录
    # data = os.getcwd() + "\\data"
    try:
        # 不存在则创建，存在则清空
        if not os.path.exists(data):
            os.makedirs(data)
        else:
            shutil.rmtree(data)
            os.mkdir(data)
    except Exception as e:
        log.info(e)
        
    try:
        result = []
        for file in files:
            cmd = str(
                os.path.abspath(os.path.dirname(os.getcwd())) + '/lib/bandzip/bz.exe x -o:{} {}'.format(data, file))
            result.append(os.system(cmd))
            """result =0 代表解压成功"""
            result = all(x == 0 for x in result)

        return result
    except Exception as e:
        log.info(e)
        


def merge(merge_files=None, compare_value=None):
    """
    传入一个选择的文件对应的项目对比值，如果在json文件中找到该对比值，则载入英文标签，合并数据
    :param merge_files: csv 文件
    :param compare_value: 对比值
    创建新的csv 将需要处理的csv通过pandas 写入新的csv中
    """
    try:
        # 获取英文标签
        en_tickets = load_en_tickets(compare_value)
        T = []
        temp = []
        turbld = []
        date = []
        dates = {}
        for i in range(len(merge_files)):
            temp.append(merge_files[i].split('/')[-1])
        for file in temp:
            t = os.path.splitext(file)[0]  # 将文件名和后缀分开，生成t
            T.append(t)
        for i in T:
            turbld.append(i.split('_')[0])  # 将机组编号和日期分开，生成turbld和date
        turbld = set(turbld)
        for j in turbld:
            for m in T:
                if m[0:8] == j:
                    date = date + [m[9:]]
            dates[j] = date
            date = []
        for k in turbld:
            datelist = []
            # if dates[k][0] == dates[k][-1]:
            #     newName = dates[k][0]
            # else:
            newName = dates[k][0] + '-' + dates[k][-1]
            newName = k + '_' + newName + '.csv'  # 合并后的文件名
            newName = os.path.join(r'..\data', newName)
            for f in temp:
                if f.split('_')[0] == k:
                    datelist.append(merge_files[temp.index(f)])
            # 读取第一个CSV文件并包含表头
            df = handle_csv(datelist[0], en_tickets)
            log.info("正在合并第一个文件")
            # 将读取的第一个CSV文件写入合并后的文件保存
            df.to_csv(newName, mode='a', index=False, sep=',', encoding='gbk')
            os.remove(f'{datelist[0]}')
            # 循环遍历列表中各个CSV文件名，并追加到合并后的文件
            for i in range(1, len(datelist)):
                df = handle_csv(datelist[i], en_tickets)
                log.info("正在合并第{}个文件".format(i + 1))
                df.to_csv(newName, mode='a', header=False, index=False, sep=',', encoding='gbk')
                os.remove(f'{datelist[i]}')
    except Exception as e:
        log.info(e)
        


def load_en_tickets(compare_value):
    try:
        # 读取json 得到英文标签
        with open(os.path.abspath(os.path.dirname(os.getcwd())) + "/db/FilterCondition.json", 'r',
                  encoding='utf8') as f:
            tickets_data = json.load(f)
        f.close()
        project_name = list(tickets_data.keys())
        # 如果在json的项目中则输出此时的项目序号位置，提取英文标签
        if compare_value in project_name:
            index = project_name.index(compare_value)
        # 得到英文标签
        en_tickets = tickets_data[project_name[index]]
        return en_tickets
    except Exception as e:
        log.info(e)
        


def handle_csv(file, usecols):
    """
    合并CSV
    合并之前先判断是否存在csv数据缺失现象，如果缺失则补充numpa.nan数值
    :param usecols:
    :return:
    """

    # 开始读取data
    data = pd.read_csv(file, usecols=usecols, chunksize=10000, encoding='gbk',
                       engine='python')
    # 将data 整合为df
    df = pd.concat(data, ignore_index=True)
    return df
