"""
@ File:     intensity_eval.py
@ Author:   pleiadesian
@ Datetime: 2020-01-31 15:33
"""
import pandas as pd
import tushare as ts
import api.storage as st
import api.ts_map as tm

HALF_UP_THRESHOLD = 0.05
RISING_THRESHOLD = 0.03
FALLING_THRESHOLD = -0.03

BOX_HEIGHT = 0.15

TURNOVER_RATE_THRESHOLD = 0.10
HIGH_OPEN_RATIO = -0.03
HIGH_RUSH_RATIO = 0.03


def judge_doji(open_price, high, close, low):
    return abs(open_price - close) <= (high - low) * 0.5 or close <= open_price

# TODO: note that Seismic storage line should be on the first rising of price
# TODO: too specific. Consider active 60-K detection and fine daily-K detection


def eval_intensity(storage, code):
    """
    evaluation for Sanyi intense stock
    :param storage: local storage
    :param code: stock code
    :return: 0=不符合三1, 1=半根, 2=一根半, 3=两根半, 4=三流以上三一股
    """
    basic_infos = storage.get_basicinfo_single(tm.ts_mapping[code])
    df = storage.get_histdata_single(tm.ts_mapping[code])[-15:]
    df = df.iloc[::-1]
    pre_close = df['close']
    free_share = basic_infos['free_share']
    limit_set = [round(k * 1.1, 2) for k in pre_close][1:]

    for i in range(0, len(df)):
        pre_df = df.iloc[i]
        open_price = pre_df['open']
        high = pre_df['high']
        close = pre_df['close']
        low = pre_df['low']
        pre_close = pre_df['pre_close']
        open_ratio = (open_price - pre_close) / pre_close
        high_ratio = (high - pre_close) / pre_close
        volume = pre_df['vol'] / 100
        turnover_rate = volume / free_share
        price_ma5 = sum(df.iloc[i:i+5]['close']) / 5
        rush_high = high_ratio >= HIGH_RUSH_RATIO
        high_open = open_ratio >= HIGH_OPEN_RATIO
        high_open_ma5 = close >= price_ma5 and open_price >= price_ma5
        big_turnover_rate = turnover_rate >= TURNOVER_RATE_THRESHOLD

        if i < len(df)-1 and judge_doji(open_price, high, close, low) and close < limit_set[i]:
            if i+1 < len(df)-1 and df.iloc[i+1]['close'] >= limit_set[i+1]:
                pre_volume = df.iloc[i+1]['vol'] / 100
                amplify_volume = volume > pre_volume
                if i+2 < len(df)-1 and df.iloc[i+2]['close'] >= limit_set[i+2]:
                    if i+3 < len(df)-1 and df.iloc[i+3]['close'] >= limit_set[i+3]:
                        # print(code + ': 二流以上三1股')
                        return 4
                    else:
                        if i < 1 and big_turnover_rate and rush_high and high_open and high_open_ma5 and amplify_volume:
                            # print(code + ': 两根半')
                            return 3
                else:
                    if i < 1 and big_turnover_rate and rush_high and high_open and high_open_ma5 and amplify_volume:
                        # print(code + ': 一根半')
                        return 2
        else:
            break
    closes = df['close']
    pre_closes = df['pre_close']
    rise_ratio = (closes - pre_closes) / pre_closes
    rush = rise_ratio[(rise_ratio >= RISING_THRESHOLD) | (rise_ratio <= FALLING_THRESHOLD)]
    if len(rush) == 0:
        for i in range(0, 3):
            pre_df = df.iloc[i]
            open_price = pre_df['open']
            high = pre_df['high']
            close = pre_df['close']
            if (high - open_price) / open_price >= HALF_UP_THRESHOLD > (close - open_price) / open_price:
                return 1
    return 0


if __name__ == '__main__':
    storage = st.Storage()
    # intensity = [[], [], [], [], []]
    # for code in tm.ts_mapping:
    #     intensity[eval_intensity(storage, code)].append(code)
    # print('二流以上三1股 共' + str(len(intensity[4])) + '只')
    # print(str(intensity[4]))
    # print('两根半 共' + str(len(intensity[3])) + '只')
    # print(str(intensity[3]))
    # print('一根半 共' + str(len(intensity[2])) + '只')
    # print(str(intensity[2]))
    # print('半根 共' + str(len(intensity[1])) + '只')
    # print(str(intensity[1]))
    print(eval_intensity(storage, '300562'))
