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

DEBUG = 1

NECKLINE_UPPER_BOUND = 1.005
NECKLINE_LOWER_BOUND = 0.99
NECKLINE_STEP = 20
NECKLINE_MINUS_STEP = 10

BOOM_LOWER_BOUND = 0.98
BOOM_UPPER_BOUND = 1.03
NORMAL_LOWER_BOUND = 0.98
NORMAL_UPPER_BOUND = 1.015

NORMAL_OPEN_HIGH_THRESHOLD = 0.02
LARGE_OPEN_HIGH_THRESHOLD = 0.005
LARGE_FREE_SHARE = 50000

MINUTE_ABSOLUTE_VOLUME_THRESHOLD = 1.12  # default 112%

# TODO: add neckline-crossing detection
# TODO: morning turnover threshold


class NeckLine:
    def __init__(self, storage):
        self.storage = storage

    def detect_general_neckline(self, matched, boomed):
        """
        NB: ONLY used after 10:30
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by neckline detection
        """
        df_list = self.storage.get_realtime_chart(matched + boomed)
        selected = []
        for df in df_list:
            open_price = df.iloc[0]['close']
            limit = round(open_price * 1.1, 2)
            close = df.iloc[-1]['close']
            code = df.iloc[0]['code']

            neckline_list = [open_price * (1 + ratio * 0.1 / NECKLINE_STEP) for ratio in
                             range(-NECKLINE_MINUS_STEP, NECKLINE_STEP)]
            neckline_select = []
            df = df.iloc[:-10]
            df_recent = df.iloc[-45:]
            df = df.set_index('high')
            df = df.sort_index()
            df_recent = df_recent.set_index('high')
            df_recent = df_recent.sort_index()
            last_length = None
            for i in range(1, NECKLINE_STEP + NECKLINE_MINUS_STEP):
                df_temp = df[(df.index > neckline_list[i - 1]) & (df.index <= neckline_list[i])]
                # according to neckline defination
                if last_length is not None and last_length - len(df_temp) > 3:
                    neck_price = neckline_list[i - 1]
                    upper = neck_price * NECKLINE_UPPER_BOUND
                    lower = neck_price * NECKLINE_LOWER_BOUND
                    # global neckline or recent neckline
                    for df_curr in [df, df_recent]:
                        df_area = df_curr[(df_curr.index > lower) & (df_curr.index < upper)]
                        df_area = df_area[df_area.index < limit]  # do not count limit price
                        # neckline should be longer than 35 minutes
                        if len(df_area) >= 35:
                            df_area = df_area.sort_values(by='day')
                            df_area_morning = df_area[df_area['day'] <= (df_area.iloc[0]['day'][:10] + ' 11:30:00')]
                            df_area_afternoon = df_area[df_area['day'] >= (df_area.iloc[0]['day'][:10] + ' 13:00:00')]
                            # calculate confidence coefficient of this neckline
                            outliners = 0
                            for df_half in [df_area_morning, df_area_afternoon]:
                                for j in range(1, len(df_half)):
                                    min_elapse = (datetime.datetime.strptime(df_half.iloc[j]['day'],
                                                                             '%Y-%m-%d %H:%M:%S') -
                                                  datetime.datetime.strptime(df_half.iloc[j-1]['day'],
                                                                             '%Y-%m-%d %H:%M:%S'))\
                                                    .seconds / 60
                                    # separated neckline
                                    if min_elapse > 45 or min_elapse <= 1:
                                        continue
                                    outliners += min_elapse - 1
                            # too much outliner
                            if outliners / len(df_area) > 0.55:
                                continue
                            neckline_select.append((i - 1, code))
                            break
                last_length = len(df_temp)
            print([k[1] + ': '+str(neckline_list[k[0]]) for k in neckline_select])
            with open('../../stock.log', 'a') as f:
                f.write(str([k[1] + ': '+str(neckline_list[k[0]]) for k in neckline_select]) + '\n')
            if code in boomed and len(neckline_select) > 0:
                # boomed stock is over neckline
                for neckline in neckline_select:
                    if neckline_list[neckline[0]] * BOOM_LOWER_BOUND <= close <= \
                            neckline_list[neckline[0]] * BOOM_UPPER_BOUND:
                        selected.append(code)
                        break
            else:
                # normal stock is around neckline
                for neckline in neckline_select:
                    if neckline_list[neckline[0]] * NORMAL_LOWER_BOUND <= close <= \
                            neckline_list[neckline[0]] * NORMAL_UPPER_BOUND:
                        selected.append(code)
                        break
        return selected

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

    def detect_morning_neckline(self, matched, boomed):
        """
        NB: ONLY used before 11:00
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
            open_price = df.iloc[0]['close']
            open_price_today = df.iloc[1]['open']

            # morning neckline is effective on high-open stock
            if free_share >= LARGE_FREE_SHARE:
                open_threshold = LARGE_OPEN_HIGH_THRESHOLD
            else:
                open_threshold = NORMAL_OPEN_HIGH_THRESHOLD
            if (open_price_today - open_price) / open_price < open_threshold:
                continue

            close = df.iloc[-1]['close']
            df = df.iloc[1:]  # exclude yesterday data

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
            for i in range(0, 20):
                if neckline[i] > 0:
                    neckline_price = open_price * (1 + i * 0.1 / 20)
                    print(code + ":" + str(neckline_price))
                    with open('../../stock.log', 'a') as f:
                        f.write(code + ":" + str(neckline_price) + "\n")
                    if neckline_price * lower_bound <= close <= neckline_price * upper_bound:
                        selected.append(code)
                        if DEBUG == 1:
                            continue
                        else:
                            break
        return selected

    def detect_neckline(self, matched, boomed):
        """
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by neckline detection
        """
        selected = self.detect_morning_neckline(matched, boomed)
        selected = self.detect_general_neckline(matched, boomed)
        return selected


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    neckline = NeckLine(storage)
    neckline.detect_neckline(['300009'],[])
    # neckline.detect_neckline(['600789', '000078', '300342', '601999', '000700', '300030'], [])
    # neckline.detect_neckline(['603315', '600988', '002352', '600332', '000570'], [])
    code_list = []
    for code in tm.ts_mapping:
        code_list.append(code)
    neckline.detect_neckline(code_list, [])
