"""
@ File:     bottom_box.py
@ Author:   pleiadesian
@ Datetime: 2020-01-30 19:45
"""
import datetime
import numpy as np
import tushare as ts
import api.ts_map as tm

BACKTRACE_DAYS = 180
RECENT_DAYS = 60
START_WATER_LEVEL = 1.1
WATERING_STEP = 1.02
WATERSHED_MIN_WIDTH = 10
WATERSHED_RATIO_THRESHOLD = 0.1
# GOOD_PRICE_THRESHOLD = 0.99

# TODO: batch history data


def detect_bottom_neckline(code):
    df = ts.get_hist_data(code)
    close = df.iloc[0]['close']
    if len(df) > BACKTRACE_DAYS:
        df = df.iloc[:BACKTRACE_DAYS]
    peak_price = max(df['high'])
    peak_day = df[df.high >= peak_price].index.values[-1]
    df = df[df.index >= peak_day]
    if len(df) <= RECENT_DAYS:
        print(code + '(bottom neckline): RECENT PEAK')
        return True

    valley_price = min(df['low'])
    water_level = valley_price * START_WATER_LEVEL
    while water_level < close:
        next_water_level = water_level * WATERING_STEP
        df_watershed = df[(df['high'] <= next_water_level) & (df['high'] >= water_level)]
        if len(df_watershed) == 0:
            print(code + '(bottom neckline):' + str(water_level))
            return close >= water_level
        day_left = df_watershed.index.values[-1]
        day_right = df_watershed.index.values[0]
        df_area = df[(df.index <= day_right) & (df.index >= day_left)]
        df_outliner = df_area[df_area.high > next_water_level]
        if len(df_area) > WATERSHED_MIN_WIDTH and len(df_outliner) / len(df_area) <= 0.1:
            print(code + '(bottom neckline):' + str(water_level))
            return close >= water_level
        # time0 = [datetime.datetime.strptime(day, '%Y-%m-%d') for day in df_area.index[:-1].values]
        # time1 = [datetime.datetime.strptime(day, '%Y-%m-%d')for day in df_area.index[1:].values]
        # time_delta = np.array(time0) - np.array(time1)
        # watershed = time_delta[time_delta > datetime.timedelta(days=WATERSHED_MIN_WIDTH)]
        water_level = next_water_level
    print(code + '(bottom neckline): None')
    return False


if __name__ == '__main__':
    # print(detect_bottom_neckline('300593'))
    code_list = []
    for code in tm.ts_mapping:
        print(detect_bottom_neckline(code))

