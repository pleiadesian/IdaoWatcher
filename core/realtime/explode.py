"""
@ File:     explode.py
@ Author:   pleiadesian
@ Datetime: 2020-01-16 20:51
@ Desc:     time share exploding detection
"""

import datetime
import tushare as ts
import api.ts_map

DEBUG = 0

OPEN_UPPER_LIMIT = 0.03
OPEN_LOWER_LIMIT = -0.02

RUSH_UPPER_LIMIT = 0.05
RUSH_LOWER_LIMIT = -0.03

MINUTE_LIMIT_THRESHOLD = 100  # 100 million volume of transaction

EXPLODE_RISE_RATIO_THRESHOLD = 0.0158


# TODO: scale to 30 codes
def detect_timeshare_explode(code, high_to_curr):
    assert(isinstance(code, list) is False)
    pro = ts.pro_api()
    info = ts.get_realtime_quotes(code)
    info = info.values[0]
    # TODO: daily_basic prefetch at boot time
    # TODO: turnover rate and volume should based on realtime volume
    # TODO: should we use turnover_rate_f?
    # if DEBUG == 1:
    #     # basic_infos = pro.daily_basic(ts_code=api.ts_map.ts_mapping[code],
    #     #                               trade_date=datetime.datetime.now().strftime('20200117'),
    #     #                               fields='turnover_rate,volume_ratio').values[0]
    # else:
    #     basic_infos = pro.daily_basic(ts_code=api.ts_map.ts_mapping[code],
    #                                   trade_date=datetime.datetime.now().strftime('%Y%m%d'),
    #                                   fields='turnover_rate,volume_ratio').values[0]
    # turnover_rate = float(basic_infos[0])
    # volume_ratio = float(basic_infos[1])
    not_get = True
    hist_data = None
    basic_infos = None
    while not_get:
        basic_infos = pro.daily_basic(ts_code=api.ts_map.ts_mapping[code],
                                      trade_date=datetime.datetime.now().strftime('20200117'))
        hist_data = ts.get_hist_data(code)
        if hist_data is None or basic_infos is None:
            continue
        not_get = False

    volume = float(info[8])
    volume_ma5 = float(hist_data['v_ma5'][0])
    today_open = float(info[1])
    pre_close = float(info[2])
    price = float(info[3])
    high = float(info[4])
    low = float(info[5])
    amount = float(info[9])

    time = info[31]
    time = datetime.datetime.strptime(time, "%H:%M:%S")
    if time <= datetime.datetime.strptime('11:30:00', "%H:%M:%S"):
        minutes_lapse = (time - datetime.datetime.strptime('9:30:00', "%H:%M:%S")).seconds / 60
    else:
        minutes_lapse = 120 + (time - datetime.datetime.strptime('13:00:00', "%H:%M:%S")).seconds / 60
    if datetime.datetime.strptime('09:30:00', "%H:%M:%S") <= time < datetime.datetime.strptime('09:50:00', "%H:%M:%S"):
        high_to_curr_threshold = 3
    elif datetime.datetime.strptime('09:50:00', "%H:%M:%S") <= time < datetime.datetime.strptime('10:30:00', "%H:%M:%S"):
        high_to_curr_threshold = 15
    else:
        high_to_curr_threshold = 60

    float_share = basic_infos['float_share'][0]
    turnover_rate = volume / float_share / 100
    volume_ratio = volume * 240 / volume_ma5 / minutes_lapse / 100

    open_ratio = (today_open - pre_close) / pre_close
    rise_ratio = (price - pre_close) / pre_close

    rush_not_broken = OPEN_LOWER_LIMIT <= open_ratio <= OPEN_UPPER_LIMIT
    rush_not_broken = rush_not_broken and high <= RUSH_UPPER_LIMIT
    rush_not_broken = rush_not_broken and low >= RUSH_LOWER_LIMIT

    exploded = amount / 10000 > MINUTE_LIMIT_THRESHOLD
    exploded = exploded and rise_ratio >= EXPLODE_RISE_RATIO_THRESHOLD
    exploded = exploded and price > high
    # exploded = exploded and high_to_curr >= high_to_curr_threshold
    exploded = exploded and turnover_rate >= 0.6
    exploded = exploded and volume_ratio > 0.6
    exploded = exploded and rush_not_broken
    return exploded


if __name__ == '__main__':
    exploded = detect_timeshare_explode('300496', 29)
    print(exploded)


