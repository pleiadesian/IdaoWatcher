"""
@ File:     explode.py
@ Author:   pleiadesian
@ Datetime: 2020-01-16 20:51
"""
import time
import tushare as ts
from random import randint
from urllib.request import urlopen, Request

OPEN_UPPER_LIMIT = 0.03
OPEN_LOWER_LIMIT = -0.02

RUSH_UPPER_LIMIT = 0.05
RUSH_LOWER_LIMIT = -0.03

LAST_PEAK_GAP = 30  # need to be adaptive
MINUTE_LIMIT_THRESHOLD = 100  # 1 million volume of transaction


# TODO: outer scope should provide high_to_curr
# TODO: scale to 30 codes
def timeshare_explode(code, high_to_curr):
    infos = ts.get_realtime_quotes(code).values
    assert(len(infos) == 1)
    info = infos[0]
    price = info[3]
    today_open = info[1]
    pre_close = info[2]

    open_ratio = (today_open - pre_close) / pre_close
    rise_ratio = (price - pre_close) / pre_close
    # rush_broken =
    return True


if __name__ == '__main__':
    exploded = timeshare_explode(['000001', '000002'], 29)
    print(exploded)


