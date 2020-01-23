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
        self.storage = storage

    def detect_neckline(self, matched, boomed):
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
            close = df.iloc[-1]['close']
            code = df.iloc[0]['code']

            minus_step = 10
            step = 20
            neckline_list = [open_price * (1 + ratio * 0.1 / step) for ratio in range(-minus_step, step)]
            neckline_select = []
            df = df.iloc[:-10]
            df = df.set_index('high')
            df = df.sort_index()
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
                        highest = max(df_area.index.values)
                        neck_price = neckline_list[i - 1]
                        df_area_high = df_area[df_area.index > neck_price]
                        if (neck_price - lowest) / open_price < 0.03 and (highest - neck_price) / open_price < 0.03:
                            neckline_select.append((i - 1, code))
                            df_temp_last = df_temp
                            continue
                        # fallback when neckline is at a high price
                        if (neck_price - open_price) / open_price < 0.03:
                            df_temp_last = df_temp
                            continue
                        df_area_first_half = df_area.sort_values(by=['day']).iloc[:int(len(df_area)/2)]
                        lowest_first = min(df_area_first_half['low'].values)
                        highest_first = max(df_area_first_half.index.values)
                        df_area_second_half = df_area.sort_values(by=['day']).iloc[int(len(df_area)/2):]
                        lowest_second = min(df_area_second_half['low'].values)
                        highest_second = max(df_area_second_half.index.values)
                        # recent price should agree on neckline
                        df_area_second_half_high = df_area_second_half[df_area_second_half.index > neck_price]
                        if len(df_area_second_half_high) * 2 / len(df_area) > 0.8:
                            df_temp_last = df_temp
                            continue
                        if ((neck_price - lowest_first) / open_price < 0.03 and
                            (highest_first - neck_price) / open_price < 0.03) \
                                or ((neck_price - lowest_second) / open_price < 0.03 and
                                    (highest_second - neck_price) / open_price < 0.03):
                            neckline_select.append((i - 1, code))
                            df_temp_last = df_temp
                            continue
                df_temp_last = df_temp
            # neckline_select.sort(key=take_second)
            # neckline_select = neckline_select[-3:]
            print([k[1] + ': '+str(neckline_list[k[0]]) for k in neckline_select])
            with open('../../stock.log', 'a') as f:
                f.write(str([k[1] + ': '+str(neckline_list[k[0]]) for k in neckline_select]) + '\n')
            # boomed stock is over neckline
            if code in boomed and len(neckline_select) > 0:
                selected.append(code)
                break
            # normal stock is around neckline
            for neckline in neckline_select:
                if neckline_list[neckline[0]] * 0.98 <= close <= neckline_list[neckline[0]] * 1.015:
                    selected.append(code)
                    break
        end = time.time()
        print("neckline:" + str(end-start))
        return selected


if __name__ == '__main__':
    storage = st.Storage()
    storage.update_realtime_storage()
    neckline = NeckLine(storage)
    # neckline.detect_neckline(['000700', '300662'],[])
    # neckline.detect_neckline(['300662'],[])
    # neckline.detect_neckline(['300088','300623','300373','300453'])
    # neckline.detect_neckline(['603337', '300560', '600885', '300115', '002449'])
    # neckline.detect_neckline(['300721','600171','600866','601066','300513','603938','300671'])
    # neckline.detect_neckline(['600789', '000078', '300342', '603022', '601999', '000700', '000518'], [])
    # neckline.detect_neckline(['603825', '300030', '300123', '600200', '002022', '002156', '002223'], [])
    code_list = []
    for code in tm.ts_mapping:
        code_list.append(code)
    neckline.detect_neckline(code_list, [])
    # neckline.high_to_curr('000001')
