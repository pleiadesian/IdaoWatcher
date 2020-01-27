"""
@ File:     neckline.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:20
@ Desc:     Maintaining the state of neckline of stock in time share
"""
import datetime
import time
import api.storage as st
import api.ts_map as tm

# TODO: print more info in log for debug

DEBUG = 1

NECKLINE_UPPER_BOUND = 1.005
NECKLINE_LOWER_BOUND = 0.99
NECKLINE_STEP = 20
NECKLINE_MINUS_STEP = 10

NECKLINE_LENGTH_THRESHOLD = 35
LONG_NECKLINE_LENGTH_THRESHOLD = 70
SEPARATED_NECKLINE_MIN_GAP = 45
OUTLINER_THRESHOLD = 0.55

BOOM_LOWER_BOUND = 0.99  # default 98%
BOOM_UPPER_BOUND = 1.03  # default 103%
NORMAL_LOWER_BOUND = 0.99  # default 98%
NORMAL_UPPER_BOUND = 1.01  # default 101.5%
HIGH_LOWER_BOUND = 0.995
HIGH_UPPER_BOUND = 1.005

NORMAL_OPEN_HIGH_THRESHOLD = 0.02
LARGE_OPEN_HIGH_THRESHOLD = 0.005
LARGE_FREE_SHARE = 50000

MINUTE_ABSOLUTE_VOLUME_THRESHOLD = 1.12  # default 112%


class NeckLine:
    def __init__(self, storage):
        self.curr_price = dict()
        self.past_price = dict()
        self.pre_close = dict()
        self.storage = storage

    def detect_lower_neckline(self, boomed):
        """
        not used
        :param boomed: high speed rising
        :return: stock that broken high price
        """
        selected = []
        df_list = self.storage.get_realtime_chart(boomed)
        for df in df_list:
            # last 15 minutes rising do not count
            code = df.iloc[0]['code']
            df_hist = df.iloc[:-15]
            highest = max(df_hist['high'].values)
            price = float(self.storage.get_realtime_storage_single(code)[3])
            if price > highest:
                selected.append(code)
        return selected

    def detect_volume_neckline(self, matched, boomed):
        """
        not used
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by volume neckline detection
        """
        selected = []
        df_list = self.storage.get_realtime_chart(matched + boomed)
        for df in df_list:
            code = df.iloc[0]['code']
            close = df.iloc[-1]['close']
            open_price = df.iloc[0]['close']
            if code in boomed:
                lower_bound = BOOM_LOWER_BOUND
                upper_bound = BOOM_UPPER_BOUND
            else:
                lower_bound = NORMAL_LOWER_BOUND
                upper_bound = NORMAL_UPPER_BOUND
            df = df.iloc[11:]  # exclude yesterday data and morning data

            basic_infos = storage.get_basicinfo_single(tm.ts_mapping[code])
            free_share = basic_infos['free_share']
            # df_vol = df[df['volume'] * 240 / free_share / 100 > MINUTE_ABSOLUTE_VOLUME_THRESHOLD]
            # necklines = df_vol['high'].values
            # daytimes = df_vol['day'].values
            necklines = []
            # for daytime, neckline in zip(daytimes, necklines):
            for i in range(1, len(df)-1):
                # if df.iloc[i]['volume'] / 100 * 240 / free_share / 100 > MINUTE_ABSOLUTE_VOLUME_THRESHOLD and \
                #         df.iloc[i]['high'] > df.iloc[i-1]['high'] and df.iloc[i]['high'] > df.iloc[i+1]['high']:
                if df.iloc[i]['volume'] / 100 * 240 / free_share / 100 > MINUTE_ABSOLUTE_VOLUME_THRESHOLD:
                    necklines.append(df.iloc[i]['high'])

            selected_necklines = [0] * 20
            for neckline in necklines:
                neckline_idx = int(((neckline - open_price) / open_price) / 0.005) + 1
                if neckline_idx < 20:
                    selected_necklines[neckline_idx] += 1
            for i in range(0, 20):
                if selected_necklines[i] > 0:
                    neckline_price = open_price * (1 + i * 0.1 / 20)
                    print(code + ':' + str(neckline_price))
                    with open('../../stock.log', 'a') as f:
                        f.write(code + ':' + str(neckline_price) + "\n")
                    if neckline_price * lower_bound <= close <= neckline_price * upper_bound:
                        selected.append(code)
                        if DEBUG == 1:
                            continue
                        else:
                            break
        return selected

    def detect_general_neckline(self, matched, boomed):
        """
        ONLY used after 10:30
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by neckline detection
        """
        df_list = self.storage.get_realtime_chart(matched + boomed)
        selected = []
        for df in df_list:
            code = df.iloc[0]['code']
            close = self.curr_price[code]
            open_price = self.pre_close[code]
            limit = round(open_price * 1.1, 2)

            # TODO: average price line detection?

            neckline_list = [open_price * (1 + ratio * 0.1 / NECKLINE_STEP) for ratio in
                             range(-NECKLINE_MINUS_STEP, NECKLINE_STEP)]
            neckline_select = []
            df = df.iloc[:-10]
            # df_recent = df.iloc[-45:] if len(df) > 45 else df[-25:]
            df = df.set_index('high')
            df = df.sort_index()
            # df_recent = df_recent.set_index('high')
            # df_recent = df_recent.sort_index()
            last_length = None
            for i in range(1, NECKLINE_STEP + NECKLINE_MINUS_STEP):
                df_temp = df[(df.index > neckline_list[i - 1]) & (df.index <= neckline_list[i])]
                # according to neckline defination
                if last_length is not None and last_length - len(df_temp) > 3:
                    neck_price = neckline_list[i - 1]
                    upper = neck_price * NECKLINE_UPPER_BOUND
                    lower = neck_price * NECKLINE_LOWER_BOUND
                    # general neckline
                    df_area = df[(df.index > lower) & (df.index < upper)]
                    df_area = df_area[df_area.index < limit]  # do not count limit price
                    # neckline should be longer than 35 minutes
                    if len(df_area) >= NECKLINE_LENGTH_THRESHOLD:
                        df_area = df_area.sort_values(by=['day'])
                        # calculate confidence coefficient of this neckline
                        outliners = 0
                        for j in range(1, len(df_area)):
                            min_elapse = (datetime.datetime.strptime(df_area.iloc[j]['day'],
                                                                     '%Y-%m-%d %H:%M:%S') -
                                          datetime.datetime.strptime(df_area.iloc[j-1]['day'],
                                                                     '%Y-%m-%d %H:%M:%S'))\
                                            .seconds / 60
                            # separated neckline
                            if min_elapse > SEPARATED_NECKLINE_MIN_GAP or min_elapse <= 1:
                                continue
                            outliners += min_elapse - 1
                        # too much outliner
                        if outliners / len(df_area) <= OUTLINER_THRESHOLD:
                            neckline_select.append((i - 1, code))
                last_length = len(df_temp)

            # for log
            print([k[1] + ': '+str(neckline_list[k[0]]) for k in neckline_select])
            with open('../../stock.log', 'a') as f:
                f.write(str([k[1] + ': '+str(neckline_list[k[0]]) for k in neckline_select]) + '\n')
            if len(neckline_select) == 0:
                continue

            # detect neckline-crossing
            if code in self.past_price:
                past_deal = self.past_price[code]
                curr_deal = self.curr_price[code]
                for neckline in neckline_select:
                    if past_deal <= neckline_list[neckline[0]] <= curr_deal:
                        selected.append(code)
                        break
            else:
                # detect if price is in a box form
                if code in boomed:
                    lower_bound = BOOM_LOWER_BOUND
                    upper_bound = BOOM_UPPER_BOUND
                else:
                    lower_bound = NORMAL_LOWER_BOUND
                    upper_bound = NORMAL_UPPER_BOUND
                # boomed stock is over neckline
                for neckline in neckline_select:
                    if neckline_list[neckline[0]] * lower_bound <= close <= neckline_list[neckline[0]] * upper_bound:
                        selected.append(code)
                        break
        return selected

    def detect_morning_neckline(self, matched, boomed):
        """
        ONLY used before 11:00, effective on high-open stock
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by morning neckline detection
        """
        selected = []
        df_list = self.storage.get_realtime_chart(matched + boomed)

        if DEBUG == 1:
            df_list = [df[:30] for df in df_list]
        for df in df_list:
            neckline = [0] * 20
            code = df.iloc[0]['code']
            basic_infos = storage.get_basicinfo_single(tm.ts_mapping[code])
            free_share = basic_infos['free_share']
            open_price = self.pre_close[code]
            open_price_today = df.iloc[0]['open']
            close = self.curr_price[code]

            # morning neckline is effective on high-open stock
            if free_share >= LARGE_FREE_SHARE:
                open_threshold = LARGE_OPEN_HIGH_THRESHOLD
            else:
                open_threshold = NORMAL_OPEN_HIGH_THRESHOLD
            if (open_price_today - open_price) / open_price < open_threshold:
                continue

            # average price line can be an neckline for current price
            info = storage.get_realtime_storage_single(code)
            amount = float(info[9])
            volume = float(info[8])
            avl = amount / volume
            if code in boomed:
                lower_bound = BOOM_LOWER_BOUND
                upper_bound = BOOM_UPPER_BOUND
            else:
                lower_bound = NORMAL_LOWER_BOUND
                upper_bound = NORMAL_UPPER_BOUND
            if DEBUG == 0:
                if avl * lower_bound <= close <= avl * upper_bound:
                    selected.append(code)
                    continue

            # find every peak point
            highs = df['high'].values
            neckline_idx = int(((highs[0] - open_price) / open_price) / 0.005) + 1
            if neckline_idx < 20:
                neckline[int(((highs[0] - open_price) / open_price) / 0.005)+1] += 1
            for i in range(1, len(highs)-1):
                if highs[i] >= highs[i-1] and highs[i] >= highs[i+1]:
                    neckline_idx = int(((highs[i] - open_price) / open_price) / 0.005)+1
                    if neckline_idx < 20:
                        neckline[neckline_idx] += 1

            # log and select
            for i in range(0, 20):
                if neckline[i] > 0:
                    neckline_price = open_price * (1 + i * 0.1 / 20)
                    print(code + "(morning):" + str(neckline_price))
                    with open('../../stock.log', 'a') as f:
                        f.write(code + "(morning):" + str(neckline_price) + "\n")
                    # detect neckline-crossing
                    if code in self.past_price:
                        if self.past_price[code] <= neckline_price <= self.curr_price[code]:
                            selected.append(code)
                            if DEBUG == 1:
                                continue
                            else:
                                break
                    else:
                        if neckline_price * lower_bound <= close <= neckline_price * upper_bound:
                            selected.append(code)
                            if DEBUG == 1:
                                continue
                            else:
                                break
        return selected

    def detect_long_neckline(self, matched, boomed):
        """
        ONLY used before 10:30
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by long neckline detection
        """
        df_list = self.storage.get_realtime_chart_long(matched + boomed)
        if DEBUG == 1:
            df_list = [df[:-210] for df in df_list]
        selected = []
        for df in df_list:
            code = df.iloc[0]['code']
            open_price = self.pre_close[code]
            close = self.curr_price[code]
            limit = round(open_price * 1.1, 2)

            neckline_list = [open_price * (1 + ratio * 0.1 / NECKLINE_STEP) for ratio in
                             range(-NECKLINE_MINUS_STEP, NECKLINE_STEP)]
            neckline_select = []
            df = df.iloc[:-10]
            df = df.set_index('high')
            df = df.sort_index()
            last_length = None
            for i in range(1, NECKLINE_STEP + NECKLINE_MINUS_STEP):
                df_temp = df[(df.index > neckline_list[i - 1]) & (df.index <= neckline_list[i])]
                # according to neckline defination
                if last_length is not None and last_length - len(df_temp) > 3:
                    neck_price = neckline_list[i - 1]
                    upper = neck_price * NECKLINE_UPPER_BOUND
                    lower = neck_price * NECKLINE_LOWER_BOUND
                    df_area = df[(df.index > lower) & (df.index < upper)]
                    df_area = df_area[df_area.index < limit]  # do not count limit price
                    # neckline should be longer than 35 minutes
                    if len(df_area) >= LONG_NECKLINE_LENGTH_THRESHOLD:
                        df_area = df_area.sort_values(by=['day'])
                        outliners = 0
                        for j in range(1, len(df_area)):
                            past_minute = datetime.datetime.strptime(df_area.iloc[j-1]['day'], '%Y-%m-%d %H:%M:%S')
                            curr_minute = datetime.datetime.strptime(df_area.iloc[j]['day'], '%Y-%m-%d %H:%M:%S')
                            min_elapse = (curr_minute - past_minute).seconds / 60
                            # separated neckline
                            if min_elapse > SEPARATED_NECKLINE_MIN_GAP or min_elapse <= 1:
                                continue
                        # too much outliner
                        if outliners / len(df_area) > OUTLINER_THRESHOLD:
                            continue
                        neckline_select.append((i-1, code))
                last_length = len(df_temp)

            print([k[1] + '(long neckline): '+str(neckline_list[k[0]]) for k in neckline_select])
            with open('../../stock.log', 'a') as f:
                f.write(str([k[1] + '(long neckline): '+str(neckline_list[k[0]]) for k in neckline_select]) + '\n')
            if len(neckline_select) == 0:
                continue
            # detect neckline-crossing
            if code in self.past_price:
                past_deal = self.past_price[code]
                curr_deal = self.curr_price[code]
                for neckline in neckline_select:
                    if past_deal <= neckline_list[neckline[0]] <= curr_deal:
                        selected.append(code)
                        break
            else:
                # detect if price is in a box form
                if code in boomed:
                    lower_bound = BOOM_LOWER_BOUND
                    upper_bound = BOOM_UPPER_BOUND
                else:
                    lower_bound = NORMAL_LOWER_BOUND
                    upper_bound = NORMAL_UPPER_BOUND
                # boomed stock is over neckline
                for neckline in neckline_select:
                    if neckline_list[neckline[0]] * lower_bound <= close <= neckline_list[neckline[0]] * upper_bound:
                        selected.append(code)
                        break
        return selected

    def detect_high_neckline(self, matched, boomed):
        """
        used in all day
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by high neckline detection
        """
        selected = []
        df_list = self.storage.get_realtime_chart(matched + boomed)

        for df in df_list:
            code = df.iloc[0]['code']
            open_price = self.pre_close[code]
            close = self.curr_price[code]
            limit = round(open_price * 1.1, 2)

            # too early
            if code not in self.past_price or len(df) < 2:
                continue

            # too high
            if close >= limit:
                continue

            # high neckline should be at a high price
            rise_ratio = (close - open_price) / open_price
            if rise_ratio < 0.03:
                continue

            if len(df) > 20:
                df_recent = df[-20:-1]
            else:
                df_recent = df[:-1]

            # detect crossing
            past_deal = self.past_price[code]
            curr_deal = self.curr_price[code]
            highest = max(df_recent['high'].values)
            # log
            print(code + '(recent): ' + str(highest))
            with open('../../stock.log', 'a') as f:
                f.write(code + '(recent): ' + str(highest) + '\n')

            if past_deal <= highest <= curr_deal:
                selected.append(code)
                continue

            # detect if price is in a box form
            if code in boomed:
                lower_bound = BOOM_LOWER_BOUND
                upper_bound = BOOM_UPPER_BOUND
            else:
                lower_bound = HIGH_LOWER_BOUND
                upper_bound = HIGH_UPPER_BOUND
            if highest * lower_bound <= curr_deal <= highest * upper_bound:
                selected.append(code)
                continue

        return selected

    def update_local_price(self, matched, boomed):
        """
        update current price and price 3 second ago
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        """
        self.past_price = self.curr_price
        for code in matched + boomed:
            info = storage.get_realtime_storage_single(code)
            self.curr_price[code] = float(info[3])
            self.pre_close[code] = float(info[2])

    def detect_neckline(self, matched, boomed):
        """
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by neckline detection
        """
        if DEBUG == 1:
            self.update_local_price(matched, boomed)
            # self.update_local_price(matched, boomed)
            # selected_high = self.detect_high_neckline(matched, boomed)
            # selected_long = self.detect_long_neckline(matched, boomed)
            # selected_morning = self.detect_morning_neckline(matched, boomed)
            selected_general = self.detect_general_neckline(matched, boomed)
            # return selected_long + selected_general + selected_morning
            return selected_general
        self.update_local_price(matched, boomed)
        if datetime.datetime.now() < datetime.datetime.strptime('10:00:00', '%H:%M:%S'):
            selected = self.detect_morning_neckline(matched, boomed)
        elif datetime.datetime.now() < datetime.datetime.strptime('10:30:00', '%H:%M:%S'):
            selected_morning = self.detect_morning_neckline(matched, boomed)
            selected_long = self.detect_long_neckline(matched, boomed)
            selected = list(set(selected_morning) & set(selected_long))
        else:
            selected = self.detect_general_neckline(matched, boomed)
        selected_high = self.detect_high_neckline(matched, boomed)
        selected = list(set(selected) & set(selected_high))
        return selected


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    neckline = NeckLine(storage)
    # neckline.detect_neckline(['603333'],[])
    # neckline.detect_neckline(['600789', '000078', '300342', '601999', '000700', '300030'], [])
    # neckline.detect_neckline(['603315', '600988', '002352', '600332', '000570'], [])
    # neckline.detect_neckline(['603022', '601999', '002022', '600118', '300448'], [])
    code_list = []
    for code in tm.ts_mapping:
        code_list.append(code)
    ret = neckline.detect_neckline(code_list, [])
    print(ret)

