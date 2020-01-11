"""
@ File:     watch_limit.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 14:22
监听特定股票的封停是否有打开的迹象
"""
import tushare as ts
import time
from tkinter import messagebox

CODE = '600075'
CODE1 = '300541'
INTERVAL = 1
THRESHOLD = 0.95


def get_new_a1p():
    return float(ts.get_realtime_quotes(CODE)['a1_p'].values[0])


def get_new_b1v():
    return int(ts.get_realtime_quotes(CODE)['b1_v'].values[0])


# assume following logic happens every INTERVAL seconds
if __name__ == '__main__':
    b1_v_prev = None
    while True:
        time.sleep(INTERVAL)
        a1_p = get_new_a1p()
        b1_v = get_new_b1v()

        # use a1_p == 0.00 to judge if limit has been broken
        if a1_p == 0:
            # limit keeped, watch its volume
            print("封停")
            if a1_p is None:
                b1_v_prev = b1_v
            else:
                # if b1_v / b1_v_prev < THRESHOLD:
                messagebox.showinfo("提示", CODE + " 出现开板迹象")
        else:
            print("未封停")
