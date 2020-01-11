"""
@ File:     test.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 13:50
"""


pro = ts.pro_api()

df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20180718')