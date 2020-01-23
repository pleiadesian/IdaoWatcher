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


class NeckLine:
    def __init__(self, storage):
        self.neckline = dict()
        self.storage = storage
        for code in tm.ts_mapping:
            info = self.storage.get_realtime_storage_single(code)
            high = float(info[4])
            self.neckline[code] = [high]

    # def detect_neckline(self, code):
    #     """
    #     update the state of neckline
    #     :param code: stock code
    #     """
    #     info = self.storage.get_realtime_storage_single(code)
    #     price = float(info[3])
    #     high = float(info[4])
    #     time = info[31]
    #     if price == high:
    #         self.neckline[code] = time
    def detect_neckline(self, matched):
        """
        NB: ONLY used after 10:30
        :param matched: matched list by time share explosion filter
        :return: filtered matched list by neckline detection
        """
        # TODO: deal with first 1 hour
        start = time.time()
        df_list = self.storage.get_realtime_chart(matched)
        selected = []

        def take_second(elem):
            return elem[1]
        for df in df_list:
            open = df.iloc[0]['close']
            close = df.iloc[-1]['close']
            code = df.iloc[0]['code']

            minus_step = 10
            step = 20
            neckline_list = [open * (1 + ratio * 0.1 / step) for ratio in range(-minus_step, step)]
            neckline_select = []
            df = df.iloc[:-10]
            df = df.set_index('high')
            df = df.sort_index()
            # df_power = df[df.index <= open]
            # if len(df_power) > int(len(df) / 2):
            #     continue
            df_temp_last = None
            for i in range(1, step+minus_step):
                # df_temp = df.iloc[float(neckline_list[i - 1]):float(neckline_list[i])]
                df_temp = df[df.index > neckline_list[i - 1]]
                df_temp = df_temp[df_temp.index <= neckline_list[i]]
                if df_temp_last is not None and len(df_temp_last) - len(df_temp) > 3: # and len(df_temp_last) >= 5:
                    time_array = []
                    for tic in df_temp_last['day'].values:
                         time_array.append(datetime.datetime.strptime(tic, '%Y-%m-%d %H:%M:%S'))
                    # df_temp_last['day'] = datetime.datetime.strptime(df_temp_last['day'].values, '%Y-%m-%d %H:%M:%S')

                    if (max(time_array) - min(time_array)).seconds > 45 * 60:
                        df_area = df.loc[(df['day'] > min(time_array).strftime('%Y-%m-%d %H:%M:%S'))
                                         & (df['day'] < max(time_array).strftime('%Y-%m-%d %H:%M:%S'))]
                        lowest = min(df_area['low'].values)
                        highest = neckline_list[i - 1]
                        if (highest - lowest) / open < 0.03:
                            neckline_select.append((i-1, sum(df_temp_last['volume'])))
                df_temp_last = df_temp
            neckline_select.sort(key=take_second)
            neckline_select = neckline_select[-3:]
            print([neckline_list[k[0]] for k in neckline_select])
            for neckline in neckline_select:
                if neckline_list[neckline[0]] * 0.98 <= close <= neckline_list[neckline[0]] * 1.015:
                    selected.append(code)
                    break
        end = time.time()
        print("neckline:" + str(end -start))
        return selected


    # def high_to_curr(self, code):
    #     curr_time_str = self.storage.get_realtime_storage_single(code)[31]
    #     curr_time = curr_time_str.split(':')
    #     if code not in self.neckline:
    #         self.neckline[code] = curr_time_str
    #     high_time_str = self.neckline[code]
    #     high_time = high_time_str.split(':')
    #     if (9 <= int(high_time[0]) <= 11 and 9 <= int(curr_time[0]) <= 11) or \
    #             (13 <= int(high_time[0]) <= 15 and 13 <= int(curr_time[0]) <= 15):
    #         return (datetime.datetime.strptime(curr_time_str[:5], "%H:%M") -
    #                 datetime.datetime.strptime(high_time_str[:5], "%H:%M")).seconds / 60
    #     else:
    #         return (datetime.datetime.strptime(curr_time_str[:5], "%H:%M") -
    #                 datetime.datetime.strptime('13:00', "%H:%M")).seconds / 60 + \
    #                (datetime.datetime.strptime('11:30', "%H:%M") -
    #                 datetime.datetime.strptime(high_time_str[:5], "%H:%M")).seconds / 60


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    neckline = NeckLine(storage)
    # neckline.detect_neckline(['603920'])
    neckline.detect_neckline(['300088','300623','300373','300453'])
    # neckline.detect_neckline(['603337', '300560', '600885', '300115', '002449'])
    # neckline.detect_neckline(['300721','600171','600866','601066','300513','603938','300671'])
    # neckline.high_to_curr('000001')
