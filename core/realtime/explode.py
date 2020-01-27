"""
@ File:     explode.py
@ Author:   pleiadesian
@ Datetime: 2020-01-16 20:51
@ Desc:     time share exploding detection
"""
import datetime
import tushare as ts
import api.ts_map as tm
import api.storage as st

DEBUG = 0

# TODO: print more info in log for debug

OPEN_UPPER_LIMIT = 0.1  # default 0.03
OPEN_LOWER_LIMIT = -0.03  # default -0.02

RUSH_LOWER_LIMIT = -0.05  # default -0.03

AMOUNT_THRESHOLD = 100  # 1,000,000 volume of transaction
TURNOVER_THRESHOLD = 2.5  # turnover rate 2.5%, default %0.6
VOLUME_RATIO_THRESHOLD = 0.6

# EXPLODE_RISE_RATIO_THRESHOLD = 0.0158
ACCER_THRESHOLD = 0.01  # ￥0.01
LARGE_ACCER_THRESHOLD = 0.01  # %2

RELATIVE_LARGE_VOLUME_THRESHOLD = 50  # default 58
SMALL_ABSOLUTE_LARGE_VOLUME_THRESHOLD = 3.5
ABSOLUTE_LARGE_VOLUME_THRESHOLD = 1.27  # default 127%
BIG_ABSOLUTE_LARGE_VOLUME_THRESHOLD = 0.5

SMALL_FREE_SHARE = 12000
LARGE_FREE_SHARE = 50000


class TimeShareExplosion:
    def __init__(self):
        self.deal_volume = dict()
        self.deal_price = dict()
        for code in tm.ts_mapping:
            self.deal_volume[code] = (0.0, datetime.datetime.now())
            self.deal_price[code] = 0.0

    def detect_timeshare_explode(self, storage, code):
        assert(isinstance(code, list) is False)
        basic_infos = storage.get_basicinfo_single(tm.ts_mapping[code])
        hist_data = storage.get_histdata_single(tm.ts_mapping[code])
        info = storage.get_realtime_storage_single(code)

        volume = float(info[8]) / 100  # calculation by Lot
        volume_ma5 = sum([serie['vol'] for serie in hist_data]) / len(hist_data)
        volume_ma5_deal = sum([serie['vol'] for serie in hist_data]) / (len(hist_data) * 240 * 20)
        today_open = float(info[1])
        pre_close = float(info[2])
        price = float(info[3])
        high = float(info[4])
        low = float(info[5])
        amount = float(info[9])
        free_share = basic_infos['free_share']

        time = info[31]
        time = datetime.datetime.strptime(time, "%H:%M:%S")
        sec_delta = (time - self.deal_volume[code][1]).seconds
        # in case of re-fetch same data
        if sec_delta == 0:
            return False
        # in case of time delta
        curr_deal_volume = (volume - self.deal_volume[code][0]) / sec_delta * 3
        curr_deal_accer = (price - self.deal_price[code]) / sec_delta * 3
        curr_deal_accer_percent = (price - self.deal_price[code]) / sec_delta * 3 / pre_close
        if time <= datetime.datetime.strptime('11:30:00', "%H:%M:%S"):
            minutes_elapse = (time - datetime.datetime.strptime('9:30:00', "%H:%M:%S")).seconds / 60
        else:
            minutes_elapse = 120 + (time - datetime.datetime.strptime('13:00:00', "%H:%M:%S")).seconds / 60

        turnover_rate = volume * 240 / free_share / minutes_elapse  # customized turnover_rate
        volume_ratio = volume * 240 / volume_ma5 / minutes_elapse
        deal_volume_ratio = curr_deal_volume / volume_ma5_deal
        deal_turnover_rate = curr_deal_volume * 20 * 240 / free_share / 100

        open_ratio = (today_open - pre_close) / pre_close
        rise_ratio = (price - pre_close) / pre_close
        high_ratio = (high - pre_close) / pre_close
        low_ratio = (low - pre_close) / pre_close

        rush_not_broken = OPEN_LOWER_LIMIT <= open_ratio <= OPEN_UPPER_LIMIT
        rush_not_broken &= low_ratio >= RUSH_LOWER_LIMIT

        relative_large_volume = deal_volume_ratio > RELATIVE_LARGE_VOLUME_THRESHOLD
        if free_share < SMALL_FREE_SHARE:
            absolute_large_volume = deal_turnover_rate > SMALL_ABSOLUTE_LARGE_VOLUME_THRESHOLD
        elif free_share < LARGE_FREE_SHARE:
            absolute_large_volume = deal_turnover_rate > ABSOLUTE_LARGE_VOLUME_THRESHOLD
        else:
            absolute_large_volume = deal_turnover_rate > BIG_ABSOLUTE_LARGE_VOLUME_THRESHOLD

        exploded = amount / 10000 > AMOUNT_THRESHOLD
        exploded &= turnover_rate >= TURNOVER_THRESHOLD
        exploded &= volume_ratio > VOLUME_RATIO_THRESHOLD

        exploded &= rush_not_broken
        # exploded &= rise_ratio >= EXPLODE_RISE_RATIO_THRESHOLD
        exploded &= (curr_deal_accer >= ACCER_THRESHOLD or
                     curr_deal_accer_percent >= LARGE_ACCER_THRESHOLD or
                     (free_share >= LARGE_FREE_SHARE and curr_deal_accer >= 0.0))
        exploded &= (relative_large_volume or absolute_large_volume)
        # if code == '000955':
        #     print(str(time) + ' '+str(curr_deal_volume))

        self.deal_volume[code] = (volume, time)
        self.deal_price[code] = price

        # in case of booming
        if curr_deal_accer_percent >= LARGE_ACCER_THRESHOLD and rise_ratio >= EXPLODE_RISE_RATIO_THRESHOLD:
            return 2
        return exploded


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    time_share_explotion = TimeShareExplosion()
    ret = time_share_explotion.detect_timeshare_explode(storage, '300303')
    print(ret)


