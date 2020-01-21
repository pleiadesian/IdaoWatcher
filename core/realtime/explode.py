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

OPEN_UPPER_LIMIT = 0.03
OPEN_LOWER_LIMIT = -0.02

RUSH_UPPER_LIMIT = 0.09  # default 0.05
RUSH_LOWER_LIMIT = -0.03

MINUTE_LIMIT_THRESHOLD = 100  # 100 million volume of transaction

EXPLODE_RISE_RATIO_THRESHOLD = 0.0158

LARGE_VOLUME = 61.8


class TimeShareExplosion:
    def __init__(self):
        self.deal_volume = dict()
        for code in tm.ts_mapping:
            self.deal_volume[code] = (0.0, datetime.datetime.now())

    # TODO: scale to 30 codes
    def detect_timeshare_explode(self, storage, code, high_to_curr):
        assert(isinstance(code, list) is False)
        # info = ts.get_realtime_quotes(code)
        # info = storage.get_realtime_storage_single(code)
        # info = info.values[0]
        # info = info.values
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
        # not_get = True
        # hist_data = None
        # basic_infos = None
        # while not_get:
            # basic_infos = pro.daily_basic(ts_code=tm.ts_mapping[code],
            #                               trade_date=datetime.datetime.now().strftime('%Y%m%d'))
            # hist_data = ts.get_hist_data(code)
            # if hist_data is None or basic_infos is None:
            #     continue
            # not_get = False

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

        time = info[31]
        time = datetime.datetime.strptime(time, "%H:%M:%S")
        sec_delta = (time - self.deal_volume[code][1]).seconds
        # in case of re-fetch same data
        if sec_delta == 0:
            return False
        # in case of time delta
        curr_deal_volume = (volume - self.deal_volume[code][0]) / sec_delta * 3
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

        float_share = basic_infos['float_share']
        turnover_rate = volume / float_share / 100
        volume_ratio = volume * 240 / volume_ma5 / minutes_lapse / 100

        open_ratio = (today_open - pre_close) / pre_close
        rise_ratio = (price - pre_close) / pre_close
        high_ratio = (high - pre_close) / pre_close
        low_ratio = (low - pre_close) / pre_close

        deal_volume_ratio = curr_deal_volume / volume_ma5_deal

        # rush_not_broken = OPEN_LOWER_LIMIT <= open_ratio <= OPEN_UPPER_LIMIT
        rush_not_broken = high_ratio <= RUSH_UPPER_LIMIT
        rush_not_broken = rush_not_broken and low_ratio >= RUSH_LOWER_LIMIT

        exploded = amount / 10000 > MINUTE_LIMIT_THRESHOLD
        exploded = exploded and rise_ratio >= EXPLODE_RISE_RATIO_THRESHOLD
        # exploded = exploded and price >= high
        # exploded = exploded and high_to_curr >= high_to_curr_threshold
        exploded = exploded and turnover_rate >= 0.6
        exploded = exploded and volume_ratio > 0.6
        exploded = exploded and rush_not_broken
        exploded = exploded and deal_volume_ratio > LARGE_VOLUME
        if code == '600216':
            print(str(time) + ' '+str(curr_deal_volume))

        self.deal_volume[code] = (volume, time)
        return exploded


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    time_share_explotion = TimeShareExplosion()
    exploded = time_share_explotion.detect_timeshare_explode(storage, '000792', 29)
    print(exploded)


