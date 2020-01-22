"""
@ File:     open_high.py
@ Datetime: 2020-01-18 18:27
@ Desc:     本模块用于在9：15~9：25集合竞价期间对高开股票进行检测
@ Author:   pleiadesian
"""
import tushare as ts
import datetime
RECENT_PEAK = 3  # 往前计算，直到3天前





def calc_peak(code):
    """
    计算股票近RECENT_PEAK天的极值，作为detect_high_open的子程序
    :param code: 股票代码
    :return: 最高价，出现在几天前
    """

    now_time = ts.get_realtime_quotes(code).values[0][30]  # 今天的日期（年-月-日）
    past_time = (datetime.datetime.strptime(now_time, '%Y-%m-%d') - datetime.timedelta(days=RECENT_PEAK)).strftime(
        '%Y-%m-%d')

    all_info = ts.get_hist_data(code, start=past_time, end=now_time, ktype='D')
    while all_info is None or len(all_info) < 3:
        delta += 1
        past_time = (datetime.datetime.strptime(now_time, '%Y-%m-%d') - datetime.timedelta(days=delta)).strftime(
            '%Y-%m-%d')  # 遇到跨双休日、节假日的情况，持续往前推，直到获得3天的数据
        all_info = ts.get_hist_data(code, start=past_time, end=now_time, ktype='D')
    high_price = all_info['high']
    peak_day=0
    peak_value=0

    for i in range(3):
        if (high_price[i]>peak_value):
            peak_value=high_price[i]
            peak_day=i+1

    return(peak_value,',',peak_day)
def detect_high_open(code):
    """
    检测到股票当前开在近RECENT_PEAK天的极值之上
    :param code: 股票代码
    :return: 检测到发生高开（True or False）
    """
    # TODO: 调用接口获得对应数据

    now_time_1 = ts.get_realtime_quotes(code).values[0][30]  # 今天的日期（年-月-日）
    past_time_1 = (datetime.datetime.strptime(now_time_1, '%Y-%m-%d') - datetime.timedelta(days=RECENT_PEAK)).strftime(
        '%Y-%m-%d')

    df_hist = ts.get_hist_data(code, start=past_time_1, end=now_time_1, ktype='D')
    while df_hist is None or len(df_hist) < 3:
        delta += 1
        past_time_1 = (datetime.datetime.strptime(now_time_1, '%Y-%m-%d') - datetime.timedelta(days=delta)).strftime(
            '%Y-%m-%d')  # 遇到跨双休日、节假日的情况，持续往前推，直到获得3天的数据
        df_hist = ts.get_hist_data(code, start=past_time_1, end=now_time_1, ktype='D')
    high_price_1 = df_hist['high']
    peak_value_1=max(high_price_1)
    df_rt = ts.get_realtime_quotes(code)
    price_now=float(df_rt.values[0][3])

    if(price_now>peak_value_1):
        return(True)
    else: return(False)

    # TODO: 核心逻辑判断部分

    # TODO: 返回结果


if __name__ == '__main__':
    # 运行本文件时，会执行的代码
    # 输入的股票代码可以修改，便于跑出来结果和实际情况对比
    detect_high_open('300703')
    calc_peak('300703')
