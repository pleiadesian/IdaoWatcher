"""
@ File:     storage.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:47
@ Desc:     Scratching, cleaning and storing data
"""
import re
import os
import time
import json
import pickle
import datetime
import requests
import pandas as pd
from random import randint
from multiprocessing.pool import ThreadPool
import tushare as ts
import api.ts_map as tm


DEBUG = 1

DATA_COLS = ['name', 'open', 'pre_close', 'price', 'high', 'low', 'bid', 'ask', 'volume', 'amount', 'b1_v', 'b1_p',
             'b2_v', 'b2_p', 'b3_v', 'b3_p', 'b4_v', 'b4_p', 'b5_v', 'b5_p', 'a1_v', 'a1_p', 'a2_v', 'a2_p', 'a3_v',
             'a3_p', 'a4_v', 'a4_p', 'a5_v', 'a5_p', 'date', 'time', 's']

token = os.getenv('TOKEN')
ts.set_token(token)
pro = ts.pro_api(token)


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
    realtime_info = dict()
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
            realtime_info[syms[index]] = [astr for astr in row.split(',')[:33]]
    assert syms_list
    df = pd.DataFrame(data_list, columns=DATA_COLS)
    df = df.drop('s', axis=1)
    df['code'] = syms_list
    ls = [cls for cls in df.columns if '_v' in cls]  # bid and ask volume should / 100
    for txt in ls:
        df[txt] = df[txt].map(lambda x: x[:-2])
    return realtime_info, df


def process_json(codes):
    df_date = pro.trade_cal(exchange='SSE', start_date=datetime.datetime.now().strftime('%Y') + '0101', is_open=1)
    pretrade_df = df_date[df_date.cal_date < datetime.datetime.now().strftime('%Y%m%d')]
    if len(pretrade_df) == 0:
        # consider the trade date after New Year's day
        df_date = pro.trade_cal(exchange='SSE', start_date='20200101',
                                is_open=1)
        pretrade_df = df_date[df_date.cal_date < datetime.datetime.now().strftime('%Y%m%d')]
    pretrade_date = pretrade_df['cal_date'].values[-1]
    pretrade_date = pretrade_date[:4] + '-' + pretrade_date[4:6] + '-' + pretrade_date[6:]

    cols = ['date', 'open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change',
            'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']  # only for daily
    df_curr = pd.DataFrame(columns=cols)
    for code in codes:
        url = '%sapi.finance.%s/%s/?code=%s&type=last' % ('http://', 'ifeng.com', 'akdaily', code)
        not_get = True
        resp = None
        while not_get:
            try:
                resp = requests.get(url, timeout=3)
                not_get = False
                if resp is None or len(resp.text) == 0:
                    time.sleep(1)
                    not_get = True
            except requests.exceptions.RequestException as e:
                time.sleep(1)
                not_get = True
        text = resp.text
        js = json.loads(text)
        df = pd.DataFrame(js['record'], columns=cols)
        df = df[df.date >= pretrade_date]  # only for daily
        if len(df) > 1:
            # in case of replay
            df = df[df.date > pretrade_date]
        df.insert(0, 'code', code[2:])
        df['code'] = code[2:]
        df = df.applymap(lambda x: x.replace(u',', u''))  # only for daily
        df[df == ''] = 0  # only for daily
        for col in cols[1:]:
            df[col] = df[col].astype(float)
        df_curr = pd.concat([df_curr, df])
    return df_curr


def process_json_realtime(code):
    cols = ['day', 'open', 'high', 'low', 'close', 'volume']
    url = 'https://quotes.sina.cn/cn/api/json_v2.php/' \
          'CN_MarketDataService.getKLineData?symbol=%s&scale=1&ma=no&datalen=240' % code
    not_get = True
    resp = None
    while not_get:
        try:
            resp = requests.get(url, timeout=3)
            not_get = False
            if resp is None or len(resp.text) == 0:
                time.sleep(1)
                not_get = True
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            not_get = True
    text = resp.text
    js = json.loads(text)
    df = pd.DataFrame(js, columns=cols)
    df = df[df.day >= js[-1]['day'][:10] + ' 09:00:00']
    for col in cols[1:]:
        df[col] = df[col].astype(float)
    df.insert(0, 'code', code[2:])
    df['code'] = code[2:]
    return df


def process_json_realtime_long(code):
    cols = ['day', 'open', 'high', 'low', 'close', 'volume']
    url = 'https://quotes.sina.cn/cn/api/json_v2.php/' \
          'CN_MarketDataService.getKLineData?symbol=%s&scale=1&ma=no&datalen=480' % code
    not_get = True
    resp = None
    while not_get:
        try:
            resp = requests.get(url, timeout=3)
            not_get = False
            if resp is None or len(resp.text) == 0:
                time.sleep(1)
                not_get = True
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            not_get = True
    text = resp.text
    js = json.loads(text)
    df = pd.DataFrame(js, columns=cols)
    for col in cols[1:]:
        df[col] = df[col].astype(float)
    df.insert(0, 'code', code[2:])
    df['code'] = code[2:]
    return df


def process_histdata(date):
    not_get = True
    while not_get:
        try:
            df = pro.daily(ts_code='', start_date=date, end_date=date)
            return df
        except requests.exceptions.RequestException or json.decoder.JSONDecodeError as e:
            time.sleep(1)
            not_get = True


class Storage:
    def __init__(self):
        self.pro = ts.pro_api(token)
        self.realtime_quotes = None
        self.realtime_quotes_opt = None
        self.stock_daily = None
        self.reg = re.compile(r'\="(.*?)\";')
        self.reg_sym = re.compile(r'(?:sh|sz)(.*?)\=')
        self.peak_info = dict()
        self.basic_info = dict()
        self.hist_data = dict()
        self.basic_info_opt = None
        self.ts_mapping = None
        self.detail_code_list = None
        self.code_list = None
        self.ts_lower_mapping = None

        # self.init_neckline_storage()
        path = os.getenv('PROJPATH')
        load_from_disk = True
        target_bi = path + 'basicinfo.dat'
        target_hd = path + 'histdata.dat'
        if not os.path.isfile(target_bi) or not os.path.isfile(target_hd):
            load_from_disk = False
        if load_from_disk:
            if os.path.getsize(target_bi) > 0 and os.path.getsize(target_hd) > 0:
                with open(target_bi, "rb") as f:
                    unpickler = pickle.Unpickler(f)
                    self.basic_info = unpickler.load()
                with open(target_hd, "rb") as f:
                    unpickler = pickle.Unpickler(f)
                    self.hist_data = unpickler.load()
            load_trade_date = self.basic_info['000001.SZ']['trade_date']
            df_date = self.pro.trade_cal(exchange='SSE', end_date=datetime.datetime.now().strftime('%Y%m%d'), is_open=1)
            pre_trade_date = df_date.iloc[-2]['cal_date']
            if pre_trade_date != load_trade_date:
                load_from_disk = False
                self.basic_info = dict()
                self.hist_data = dict()
        if not load_from_disk:
            self.init_basicinfo()
            self.init_histdata()
            with open(path + 'basicinfo.dat', 'wb') as f:
                pickle.dump(self.basic_info, f)
            with open(path + 'histdata.dat', 'wb') as f:
                pickle.dump(self.hist_data, f)
        self.init_ts_map()
        self.init_opt()

    def get_realtime_chart(self, code_list):
        """
        :param code_list: stock code_list
        :return: stock realtime chart list in this day
        """
        ts_code_list = [tm.ts_lower_mapping[k] for k in code_list]
        p = ThreadPool()
        df_list = p.map(process_json_realtime, ts_code_list)
        return df_list

    def get_realtime_chart_long(self, code_list):
        """
        :param code_list: stock code_list
        :return: stock realtime chart list in 3 days
        """
        ts_code_list = [tm.ts_lower_mapping[k] for k in code_list]
        p = ThreadPool()
        df_list = p.map(process_json_realtime_long, ts_code_list)
        return df_list

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
        return self.realtime_quotes[code]
        # return self.realtime_quotes.loc[code]

    def get_basicinfo_single(self, ts_code):
        """
        :param ts_code: stock code
        :return: basic information for code
        """
        assert self.basic_info is not None
        return self.basic_info[ts_code]

    def get_histdata_single(self, ts_code):
        """
        :param ts_code: stock ts code
        :return: stock history data
        """
        assert self.hist_data is not None
        # return self.hist_data.loc[ts_code]
        return self.hist_data[ts_code]

    def update_realtime_storage(self):
        """
        scratch realtime data and store it locally
        """
        args = []
        for i in range(0, 5):
            args.append((i, self.reg, self.reg_sym))
        not_create = True
        while not_create:
            try:
                p = ThreadPool()
                not_create = False
            except RuntimeError as e:
                time.sleep(3)
                not_create = True

        ret = p.starmap(process_plaintext, args)

        dict_list = [k[0] for k in ret]
        df = [k[1] for k in ret]

        args_remain = []
        for i in range(5, tm.CODE_SEGMENT_NUM):
            args_remain.append((i, self.reg, self.reg_sym))
        ret_remain = p.starmap(process_plaintext, args_remain)

        dict_list_remain = [k[0] for k in ret_remain]
        df_remain = [k[1] for k in ret_remain]

        dict_curr = {k:v for dic in dict_list for k,v in dic.items()}
        dict_curr_remain = {k:v for dic in dict_list_remain for k,v in dic.items()}
        self.realtime_quotes = {**dict_curr, **dict_curr_remain}
        self.realtime_quotes_opt = pd.concat(df + df_remain)

    def update_realtime_storage_backtest(self, moment):
        # TODO: fetch from Wind api
        pass

    def update_basicinfo_backtest(self, date):
        """
        used in backtest
        :param date: backtest date (%Y%m%d)
        """
        self.basic_info = dict()
        # get daily basic information
        df_date = self.pro.trade_cal(exchange='SSE', end_date=date, is_open=1)
        pretrade_date = df_date['cal_date'].values[-2]
        not_get = True
        while not_get:
            try:
                df_basicinfo = self.pro.daily_basic(ts_code='', trade_date=pretrade_date)
                for index, row in df_basicinfo.iterrows():
                    self.basic_info[row['ts_code']] = row
                not_get = False
            except requests.exceptions.RequestException as e:
                time.sleep(1)
                not_get = True

    def update_histdata_backtest(self, date):
        """
        used in backtest
        :param date: backtest date (%Y%m%d)
        """
        self.hist_data = dict()
        days = 365
        df_date = self.pro.trade_cal(exchange='SSE', end_date=date, is_open=1)
        df_pretrade = df_date[:-1]
        df_pre5 = df_pretrade[-days:]
        pretrade_date = df_pre5['cal_date'].values

        p = ThreadPool()
        df_list = p.map(process_histdata, pretrade_date)

        df_histdata = pd.concat(df_list)
        gb = df_histdata.set_index(['trade_date']).sort_index().groupby('ts_code')
        for ts_code in tm.ts_mapping.values():
            self.hist_data[ts_code] = gb.get_group(ts_code)

    def init_opt(self):
        self.basic_info_opt = pd.DataFrame(self.basic_info.values())
        # TODO: add volume-related data into basic_info_opt

    def init_basicinfo(self):
        """
        initialize stock basic info
        """
        # get daily basic information
        df_date = self.pro.trade_cal(exchange='SSE', end_date=datetime.datetime.now().strftime('%Y%m%d'), is_open=1)
        pretrade_date = df_date['cal_date'].values[-2]
        not_get = True
        while not_get:
            try:
                df_basicinfo = self.pro.daily_basic(ts_code='', trade_date=pretrade_date)
                for index, row in df_basicinfo.iterrows():
                    self.basic_info[row['ts_code']] = row
                not_get = False
            except requests.exceptions.RequestException as e:
                time.sleep(1)
                not_get = True

    def init_histdata(self):
        """
        initialize data in certain days
        """
        days = 365
        df_date = self.pro.trade_cal(exchange='SSE', end_date=datetime.datetime.now().strftime('%Y%m%d'), is_open=1)
        df_pretrade = df_date[:-1]
        df_pre5 = df_pretrade[-days:]
        pretrade_date = df_pre5['cal_date'].values

        p = ThreadPool()
        df_list = p.map(process_histdata, pretrade_date)

        df_histdata = pd.concat(df_list)
        gb = df_histdata.set_index(['trade_date']).sort_index().groupby('ts_code')
        rm_codes = []
        for ts_code in tm.ts_mapping.values():
            try:
                self.hist_data[ts_code] = gb.get_group(ts_code)
            except KeyError as e:
                rm_codes.append(ts_code)
        for ts_code in rm_codes:
            tm.detail_code_list.remove('sh' + ts_code[:6] if ts_code.endswith('SH') else 'sz' + ts_code[:6])
            del tm.ts_mapping[ts_code[:6]]
            del tm.ts_lower_mapping[ts_code[:6]]
            del tm.name_mapping[ts_code[:6]]

    def init_ts_map(self):
        # hit stock that suspended trading yesterday, load it
        df_date = self.pro.trade_cal(exchange='SSE', end_date=datetime.datetime.now().strftime('%Y%m%d'), is_open=1)
        rm_codes = []
        for ts_code in tm.ts_mapping.values():
            if ts_code not in self.basic_info:
                delta = 1
                while True:
                    df_basicinfo = self.pro.daily_basic(ts_code=ts_code,
                                                        trade_date=df_date['cal_date'].values[-2-delta])
                    if len(df_basicinfo) == 0:
                        delta += 1
                        if delta > 5:
                            # suspended for a long time, delete it
                            rm_codes.append(ts_code)
                            break
                        continue
                    temp_series = df_basicinfo.loc[0]
                    self.basic_info[ts_code] = temp_series
                    break
        for ts_code in rm_codes:
            tm.detail_code_list.remove('sh' + ts_code[:6] if ts_code.endswith('SH') else 'sz' + ts_code[:6])
            del tm.ts_mapping[ts_code[:6]]
            del tm.ts_lower_mapping[ts_code[:6]]
            del tm.name_mapping[ts_code[:6]]

    def init_neckline_storage(self):
        """
        initialize neckline in time share chart
        """
        # TODO: this api cannot get current data, consider to check Wind api
        args = []
        step = int(len(tm.detail_code_list) / 12)
        for i in range(0, 12):
            if step * (i+1) > len(tm.detail_code_list):
                args.append(tm.detail_code_list[step * i:])
            else:
                args.append(tm.detail_code_list[step * i:step * (i+1)])
        p = ThreadPool()
        peak_infos = p.map(process_json, args)
        self.peak_info = {k:v for dic in peak_infos for k,v in dic.items()}


if __name__ == '__main__':
    storage = Storage()
    while True:
        time.sleep(2)
        storage.update_realtime_storage()
        print(storage.get_realtime_storage())
