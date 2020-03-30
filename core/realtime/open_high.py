"""
@ File:     open_high.py
@ Datetime: 2020-01-18 18:27
@ Desc:     本模块用于在9：15~9：25集合竞价期间对高开股票进行检测
@ Author:   pleiadesian
"""
import time
import pandas as pd
import api.ts_map as tm
import api.storage as st
import tushare as ts
import datetime

RECENT_PEAK = 2  # 往前计算，直到2天前

PEAK_DELTA = 0.99

SUPERSMALL_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD = 100  # default 10000%
SMALL_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD = 29  # default 3900%
NORMAL_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD = 10.6  # default 1100%
BIG_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD = 7  # default 700% | 330%
SUPERBIG_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD = 3.3  # default 700%

SUPERSMALL_FREE_SHARE = 5000
SMALL_FREE_SHARE = 12000
LARGE_FREE_SHARE = 50000
SUPERLARGE_FREE_SHARE = 200000

NORMAL_OPEN_HIGH_THRESHOLD = 0.02
LARGE_OPEN_HIGH_THRESHOLD = 0.005


def calc_peak(code):
    """
    not used
    计算股票近RECENT_PEAK天的极值，作为detect_high_open的子程序
    :param code: 股票代码
    :return: 最高价，出现在几天前
    """
    now_time = ts.get_realtime_quotes(code).values[0][30]  # 今天的日期（年-月-日）
    past_time = (datetime.datetime.strptime(now_time, '%Y-%m-%d') - datetime.timedelta(days=RECENT_PEAK)).strftime(
        '%Y-%m-%d')

    all_info = ts.get_hist_data(code, start=past_time, end=now_time, ktype='D')
    delta = 0
    while all_info is None or len(all_info) < 3:
        delta += 1
        past_time = (datetime.datetime.strptime(now_time, '%Y-%m-%d') - datetime.timedelta(days=delta)).strftime(
            '%Y-%m-%d')  # 遇到跨双休日、节假日的情况，持续往前推，直到获得3天的数据
        all_info = ts.get_hist_data(code, start=past_time, end=now_time, ktype='D')
    high_price = all_info['high']
    peak_day = 0
    peak_value = 0

    for i in range(3):
        if high_price[i] > peak_value:
            peak_value = high_price[i]
            peak_day = i + 1

    return peak_value, peak_day


def detect_high_open(storage, code):
    """
    检测到股票当前开在近RECENT_PEAK天的极值之上
    :param storage: 本地缓存
    :param code: 股票代码
    :return: 检测到发生高开（True or False）
    """
    df_hist = pd.DataFrame([serie for serie in storage.get_histdata_single(tm.ts_mapping[code])])
    df_rt = storage.get_realtime_storage_single(code)
    basic_infos = storage.get_basicinfo_single(tm.ts_mapping[code])
    df_recent = df_hist.iloc[-RECENT_PEAK:].reset_index().sort_values(by=['high'])
    df_high = df_recent.iloc[-1]
    peak_value = df_high['high']
    price_now = float(df_rt[6])  # current bid price
    pre_close = float(df_rt[2])
    open_ratio = (price_now - pre_close) / pre_close
    free_share = basic_infos['free_share']

    if free_share < LARGE_FREE_SHARE:
        high_open = open_ratio >= NORMAL_OPEN_HIGH_THRESHOLD
    else:
        high_open = open_ratio >= LARGE_OPEN_HIGH_THRESHOLD
    peak_open = price_now >= peak_value * PEAK_DELTA
    return peak_open and high_open


def detect_high_open_explosion(storage, code):
    """
    used during call auction
    :param storage: local storage
    :param code: stock code
    :return: if high-open explosion is detected on timeshare
    """
    basic_infos = storage.get_basicinfo_single(tm.ts_mapping[code])
    hist_data = storage.get_histdata_single(tm.ts_mapping[code])[-5:]
    info = storage.get_realtime_storage_single(code)

    pre_close = float(info[2])
    price = float(info[21])
    volume = float(info[8]) / 100
    free_share = basic_infos.values[15]
    pct_chg_yesterday = float(hist_data.values[-1][7])

    if pct_chg_yesterday > 9.75:
        return False

    open_ratio = (price - pre_close) / pre_close
    open_turnover_rate = volume * 100 / free_share

    if free_share < SUPERSMALL_FREE_SHARE:
        absolute_large_volume = open_turnover_rate > SUPERSMALL_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD
        open_high = open_ratio >= NORMAL_OPEN_HIGH_THRESHOLD
    elif free_share < SMALL_FREE_SHARE:
        absolute_large_volume = open_turnover_rate > SMALL_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD
        open_high = open_ratio >= NORMAL_OPEN_HIGH_THRESHOLD
    elif free_share < LARGE_FREE_SHARE:
        absolute_large_volume = open_turnover_rate > NORMAL_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD
        open_high = open_ratio >= NORMAL_OPEN_HIGH_THRESHOLD
    elif free_share < SUPERLARGE_FREE_SHARE:
        absolute_large_volume = open_turnover_rate > BIG_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD
        open_high = open_ratio >= LARGE_OPEN_HIGH_THRESHOLD
    else:
        absolute_large_volume = open_turnover_rate > SUPERBIG_ABSOLUTE_OPEN_LARGE_VOLUME_THRESHOLD
        open_high = open_ratio >= LARGE_OPEN_HIGH_THRESHOLD

    return absolute_large_volume and open_high


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    # cold run
    for code in tm.ts_mapping:
        detect_high_open_explosion(storage, code)
    start = time.time()
    for code in tm.ts_mapping:
        detect_high_open_explosion(storage, code)
    end = time.time()
    print(end - start)
