"""
@ File:     open_high.py
@ Author:   pleiadesian
@ Datetime: 2020-01-18 18:27
@ Desc:     本模块用于在9：15~9：25集合竞价期间对高开股票进行检测
"""
import tushare as ts

RECENT_PEAK = 3  # 往前计算，直到3天前


def calc_peak(code):
    """
    计算股票近RECENT_PEAK天的极值，作为detect_high_open的子程序
    :param code: 股票代码
    :return: 最高价，出现在几天前
    """


def detect_high_open(code):
    """
    检测到股票当前开在近RECENT_PEAK天的极值之上
    :param code: 股票代码
    :return: 检测到发生高开（True or False）
    """
    # TODO: 调用接口获得对应数据
    df_hist = ts.get_hist_data(code)
    df_rt = ts.get_realtime_quotes(code)

    # TODO: 核心逻辑判断部分

    # TODO: 返回结果


if __name__ == '__main__':
    # 运行本文件时，会执行的代码
    # 输入的股票代码可以修改，便于跑出来结果和实际情况对比
    detect_high_open('300703')

