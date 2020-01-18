"""
@ File:     storage.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:47
@ Desc:     Scratching, cleaning and storing data
"""
import re
import time
import requests
import pandas as pd
from random import randint
from multiprocessing.pool import ThreadPool
from urllib.request import urlopen, Request
import tushare as ts
import api.ts_map as tm

DEBUG = 0

DATA_COLS = ['name', 'open', 'pre_close', 'price', 'high', 'low', 'bid', 'ask', 'volume', 'amount', 'b1_v', 'b1_p',
             'b2_v', 'b2_p', 'b3_v', 'b3_p', 'b4_v', 'b4_p', 'b5_v', 'b5_p', 'a1_v', 'a1_p', 'a2_v', 'a2_p', 'a3_v',
             'a3_p', 'a4_v', 'a4_p', 'a5_v', 'a5_p', 'date', 'time', 's']


def random(n=13):
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))


def process_plaintext(index, reg, reg_sym):
    """
    :param index: index for the bunch of stock
    :param reg: regular expression for data
    :param reg_sym: regular expression for symbols
    :return: data frame for a bunch of stock
    """
    # TODO: add index on code column
    resp = None
    not_get = True
    while not_get:
        try:
            # text = urlopen(request, timeout=1).read()
            resp = requests.get('%shq.%s/rn=%s&list=%s' % ('http://', 'sinajs.cn',
                                random(), tm.code_list[index]), timeout=3)
            not_get = False
            if resp is None:
                not_get = True
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            not_get = True

    text = resp.text
    # text = text.decode('GBK')
    data = reg.findall(text)
    syms = reg_sym.findall(text)
    data_list = []
    syms_list = []
    for index, row in enumerate(data):
        if len(row) > 1:
            data_list.append([astr for astr in row.split(',')[:33]])
            syms_list.append(syms[index])
    assert syms_list
    df = pd.DataFrame(data_list, columns=DATA_COLS)
    df = df.drop('s', axis=1)
    df['code'] = syms_list
    ls = [cls for cls in df.columns if '_v' in cls]
    for txt in ls:
        df[txt] = df[txt].map(lambda x: x[:-2])
    return df


class Storage:
    def __init__(self):
        with open('token/token.txt', "r") as f:  # 设置文件对象
            token = f.read()
        ts.set_token(token)
        self.realtime_quotes = None
        self.stock_daily = None
        self.reg = re.compile(r'\="(.*?)\";')
        self.reg_sym = re.compile(r'(?:sh|sz)(.*?)\=')

    def update_realtime_storage(self):
        """
        scratch realtime data and store it locally
        """
        if DEBUG == 1:
            start_time = time.time()
        args = []
        for i in range(0, 5):
            args.append((i, self.reg, self.reg_sym))
        p = ThreadPool()
        df_list = p.starmap(process_plaintext, args)

        args_remain = []
        for i in range(5, 8):
            args_remain.append((i, self.reg, self.reg_sym))
        df_list_remain = p.starmap(process_plaintext, args_remain)
        df_curr = pd.concat(df_list + df_list_remain)
        df_curr = df_curr.set_index('code')
        self.realtime_quotes = df_curr
        if DEBUG == 1:
            end_time = time.time()
            print(end_time - start_time)
            print('\n')

    def get_realtime_storage(self):
        """
        :return: realtime data
        """
        return self.realtime_quotes

    def get_realtime_storage_single(self, code):
        """
        :param code: stock code
        :return: realtime data for code
        """
        assert self.realtime_quotes is not None
        return self.realtime_quotes.loc[code]

    def update_daily_storage(self):
        """
        scratch daily data and store it locally
        """

    def update_neckline_storage(self):
        """
        initialize neckline in time share chart
        """
        curr_date = self.get_realtime_storage_single('000001')[30]
        curr_date = ''.join(curr_date.split('-'))
        for ts_code in tm.ts_mapping.values():
            df = ts.pro_bar(ts_code='000001.SH,399365.SZ', freq='1min', start_date=curr_date)
            print(df)


if __name__ == '__main__':
    storage = Storage()
    while True:
        time.sleep(2)
        storage.update_realtime_storage()
        storage.update_neckline_storage()
        print(storage.get_realtime_storage())
