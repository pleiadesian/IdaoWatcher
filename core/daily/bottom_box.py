"""
@ File:     bottom_box.py
@ Author:   pleiadesian
@ Datetime: 2020-01-30 19:45
"""
import datetime
import numpy as np
import tushare as ts
import api.ts_map as tm

BACKTRACE_DAYS = 365
SHORT_BACKTRACE_DAYS = 180
RECENT_DAYS = 60
START_WATER_LEVEL = 1.1
WATERING_STEP = 1.02
WATERSHED_MIN_WIDTH = 10
WATERSHED_RATIO_THRESHOLD = 0.1

# TODO: batch history data


def detect_bottom_neckline(code, df):
    close = df.iloc[0]['close']
    peak_price = max(df['high'])
    peak_day = df[df.high >= peak_price].index.values[-1]
    df_recent = df[df.index >= peak_day]
    if len(df_recent) <= RECENT_DAYS:
        print(code + '(bottom neckline): RECENT PEAK')
        if len(df) > RECENT_DAYS:
            df_recent = df[:-RECENT_DAYS]
        else:
            print(code + '(bottom neckline): new stock')
            return True
    df = df_recent

    valley_price = min(df['low'])
    water_level = valley_price * START_WATER_LEVEL
    while water_level < close:
        next_water_level = water_level * WATERING_STEP
        df_watershed = df[(df['high'] >= water_level) & (df['low'] <= next_water_level)]
        if len(df_watershed) == 0:
            print(code + '(bottom neckline): ' + str(water_level))
            return close >= water_level
        day_left = df_watershed.index.values[-1]
        day_right = df_watershed.index.values[0]
        df_area = df[(df.index <= day_right) & (df.index >= day_left)]
        df_outliner = df_area[df_area.high > next_water_level]
        if len(df_area) > WATERSHED_MIN_WIDTH and len(df_outliner) / len(df_area) <= 0.1:
            print(code + '(bottom neckline):' + str(water_level))
            return close >= water_level
        water_level = next_water_level
    print(code + '(bottom neckline): None')
    return False


def detect_bottom_box(codes):
    for code in codes:
        df = ts.get_hist_data(code)
        if len(df) > BACKTRACE_DAYS:
            df_bt = df.iloc[:BACKTRACE_DAYS]
        else:
            df_bt = df
        print(code + '(year): ' + str(detect_bottom_neckline(code, df_bt)))
        if len(df) > SHORT_BACKTRACE_DAYS:
            df_bt = df.iloc[:SHORT_BACKTRACE_DAYS]
        else:
            df_bt = df
        print(code + '(month):' + str(detect_bottom_neckline(code, df_bt)))


if __name__ == '__main__':
    # print(detect_bottom_neckline('000518'))
    # code_list = ['000078', '300342', '603022', '601999', '000700', '000518']
    code_list = ['603203', '002756']
    # code_list = ['603489']
    # code_list = tm.ts_mapping
    detect_bottom_box(code_list)
    # for code in tm.ts_mapping:
    #     print(detect_bottom_neckline(code))

