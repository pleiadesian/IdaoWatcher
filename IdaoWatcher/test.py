"""
@ File:     test.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 13:50
"""
import tushare as ts

ts.set_token('dd8f916cd8c513589798cd4578639a341d6f8eee8fa926e6a9e986b0')

pro = ts.pro_api()

# 日线数据
# df = pro.daily(ts_code='300541.SZ', start_date='20200108', end_date='20200110')

# 实时数据
df = ts.get_realtime_quotes('000581')  # Single stock symbol
a = df