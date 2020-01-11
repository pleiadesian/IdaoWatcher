"""
@ File:     watch_limit.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 14:22
监听特定股票的封停是否有打开的迹象
"""
import tushare as ts

CODE = '600075'
CODE1 = '300541'


def get_new_a1p():
    return float(ts.get_realtime_quotes(CODE)['a1_p'].values[0])  # Single stock symbol


a1_p = get_new_a1p()
a1_v_prev = None

# use a1_p == 0.00 to judge if limit has been broken
if a1_p == 0:
    # limit keeped, watch its volume
    print("封停")
else:
    print("未封停")
