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

NECKLINE_UPPER_BOUND = 1.005
NECKLINE_LOWER_BOUND = 0.99
NECKLINE_STEP = 20
NECKLINE_MINUS_STEP = 10


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
        # TODO: deal with first 1 hour
        start = time.time()
        df_list = self.storage.get_realtime_chart(matched + boomed)
        selected = []

        def take_second(elem):
            return elem[1]
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
                    if neckline_list[neckline[0]] * 0.98 <= close <= neckline_list[neckline[0]] * 1.03:
                        selected.append(code)
                        break
            else:
                # normal stock is around neckline
                for neckline in neckline_select:
                    if neckline_list[neckline[0]] * 0.98 <= close <= neckline_list[neckline[0]] * 1.015:
                        selected.append(code)
                        break
        end = time.time()
        print("neckline:" + str(end-start))
        return selected

    def detect_lower_neckline(self, boomed):
        """
        NB: ONLY used after 10:30
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
        NB: ONLY used after 10:30
        :param matched:
        :param boomed:
        :return:
        """

    def detect_morning_neckline(self, matched, boomed):
        """
        NB: ONLY used before 11:00
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return:
        """

    def detect_neckline(self, matched, boomed):
        """
        :param matched: matched list by time share explosion filter
        :param boomed: high speed rising
        :return: filtered matched list by neckline detection
        """
        boomed = self.detect_lower_neckline(boomed)
        selected = self.detect_general_neckline(matched, boomed)
        return selected


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    neckline = NeckLine(storage)
    # neckline.detect_neckline(['600630'],[])
    neckline.detect_neckline(['600789', '000078', '300342', '601999', '000700', '300030'], [])
    # neckline.detect_neckline(['603315', '600988', '002352', '600332', '000570'], [])
    # code_list = []
    # for code in tm.ts_mapping:
    #     code_list.append(code)
    # neckline.detect_neckline(code_list, [])
