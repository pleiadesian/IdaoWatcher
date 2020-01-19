"""
@ File:     explode.py
@ Author:   pleiadesian
@ Datetime: 2020-01-16 20:51
@ Desc:     time share exploding detection
"""

import datetime
import tushare as ts
import api.ts_map

OPEN_UPPER_LIMIT = 0.03
OPEN_LOWER_LIMIT = -0.02

RUSH_UPPER_LIMIT = 0.05
RUSH_LOWER_LIMIT = -0.03

LAST_PEAK_GAP = 30  # need to be adaptive
MINUTE_LIMIT_THRESHOLD = 100  # 100 million volume of transaction

EXPLODE_RISE_RATIO_THRESHOLD = 0.0158


# TODO: outer scope should provide high_to_curr
# TODO: scale to 30 codes
def timeshare_explode(code, high_to_curr):
    assert(isinstance(code, list) is False)
    pro = ts.pro_api()
    info = ts.get_realtime_quotes(code).values[0]
    basic_infos = pro.daily_basic(ts_code=api.ts_map.ts_mapping[code],
                                  trade_date=datetime.datetime.now().strftime('%Y%m%d'),
                                  fields='turnover_rate,volume_ratio').values[0]  # should we use turnover_f?
    turnover_rate = basic_infos[0]
    volume_ratio = basic_infos[1]
    today_open = info[1]
    pre_close = info[2]
    price = info[3]
    high = info[4]
    low = info[5]
    amount = info[9]
    time = info[31]
    time = datetime.datetime.strptime(time, "%H:%M:%S")
    if datetime.datetime.strptime('09:30:00', "%H:%M:%S") <= time < datetime.datetime.strptime('09:50:00', "%H:%M:%S"):
        high_to_curr_threshold = 3
    elif datetime.datetime.strptime('09:50:00', "%H:%M:%S") <= time < datetime.datetime.strptime('10:30:00', "%H:%M:%S"):
        high_to_curr_threshold = 15
    else:
        high_to_curr_threshold = 60
    open_ratio = (today_open - pre_close) / pre_close
    rise_ratio = (price - pre_close) / pre_close
    rush_not_broken = OPEN_LOWER_LIMIT <= open_ratio <= OPEN_UPPER_LIMIT and high <= RUSH_UPPER_LIMIT \
                      and low >= RUSH_LOWER_LIMIT
    exploded = amount / 10000 and rise_ratio >= EXPLODE_RISE_RATIO_THRESHOLD and price > high and \
               high_to_curr >= high_to_curr_threshold and turnover_rate >= 6 and volume_ratio > 0.6 and rush_not_broken
    return exploded


if __name__ == '__main__':
    exploded0 = timeshare_explode('600230', 29)
    print(exploded0)


