"""
@ File:     boom_detect.py
@ Author:   pleiadesian
@ Datetime: 2020-01-18 17:49
"""
# 引用外部库
import tushare as ts


def detect_boom(code, date):
    """
    :param code: 股票代码
    :param date: 开始计算的日期（如：'2019-01-04'）
    :return: {（第一次连续涨停的开始日期，起跳价格，持续几天），（第二次连续涨停的开始日期，起跳价格，持续几天），……}
    """
    # TODO: 调用接口获得对应数据
    df = ts.get_hist_data(code)  # 本模块需要使用的接口，接下来需要将获得的数据进行分析

    # TODO: 核心逻辑判断部分

    # TODO: 返回结果


if __name__ == '__main__':
    # 运行本文件时，会执行的代码
    # 输入的股票代码可以修改，便于跑出来结果和实际情况对比
    detect_boom('300703', '2019-01-04')
