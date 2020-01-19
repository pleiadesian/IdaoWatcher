"""
@ File:     stock_basic.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 00:01
"""
import tushare as ts
pro = ts.pro_api()
data = pro.daily(trade_date='20200116').values
a = data