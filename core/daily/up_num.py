import time
import pandas as pd
import tushare as ts
import datetime
import api.ts_map as tm
import api.storage as st

UNSAFE_PERIOD = 5
CALC_HOURS = 20


# 判断十字星
def judge_doji(i, open, high, close, low):
    if abs(open[i] - close[i]) <= (high[i] - low[i]) * 0.2:
        # and (open[i] > low[i] + 0.02) and (open[i] < high[i] - 0.02) and
        # (close[i] > low[i] + 0.02) and (close[i] < high[i] - 0.02):
        return 1  # 收盘价与开盘价差的绝对值小于等于高低峰值差的0.1倍，且十字的一横不在最高或最低处，此时认为是十字星
    else:
        return 0


def calc_60_up_num(storage, stock_ticker):
    """
    :param storage: local storage
    :param stock_ticker: stock code
    :return: the number of rising K60
    """
    hzsunmoon_num = 0  # 初始化阳线根数为0

    all_info = None
    while all_info is None:
        all_info = ts.get_hist_data(stock_ticker, ktype='60')
    all_info = all_info.iloc[:CALC_HOURS]
    pre_close = pd.DataFrame([serie for serie in storage.get_histdata_single(tm.ts_mapping[stock_ticker])])['pre_close']
    open_price = all_info['open']
    high_price = all_info['high']
    close_price = all_info['close']
    low_price = all_info['low']

    limit_set = [round(k * 1.1, 2) for k in pre_close]
    limit_set.reverse()

    for i in range(0, CALC_HOURS):
        if ((close_price[i] > open_price[i] + 0.01) and (
                judge_doji(i, open_price, high_price, close_price, low_price) == 0)) or (
                close_price[i] >= limit_set[i // 4]):  # 某小时正常阳线或涨停，前一小时不是阳线或涨停
            hzsunmoon_num += 1
        else:
            break

    print(stock_ticker + '(sun k-60): ' + str(hzsunmoon_num))
    with open('../../stock.log', 'a') as f:
        f.write(stock_ticker + '(sun k-60): ' + str(hzsunmoon_num) + '\n')
    return hzsunmoon_num


def detect_k60_period(storage, codes):
    """
    :param storage: local storage
    :param codes: stock code list
    :return: safe stock code list
    """
    safe = []
    for code in codes:
        if calc_60_up_num(storage, code) <= UNSAFE_PERIOD:
            safe.append(code)
    return safe


if __name__ == '__main__':
    storage = st.Storage()
    start = time.time()
    # num = calc_60_up_num(storage, '300499')
    print(detect_k60_period(storage, ['600789', '000078', '300342', '601999', '000700', '300030']))
    end = time.time()
    print(end - start)
