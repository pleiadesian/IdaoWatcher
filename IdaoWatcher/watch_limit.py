"""
@ File:     watch_limit.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 14:22
监听特定股票的封停是否有打开的迹象
"""
import tushare as ts
import time
import watch_limit_main
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk

CODE = '600075'
CODE1 = '300541'
INTERVAL = 1
THRESHOLD = 0.95
DISPLAY = 3


# def _async_raise(tid, exctype):
#     """raises the exception, performs cleanup if needed"""
#     tid = ctypes.c_long(tid)
#     if not inspect.isclass(exctype):
#         exctype = type(exctype)
#     res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
#     if res == 0:
#         raise ValueError("invalid thread id")
#     elif res != 1:
#         # """if it returns a number greater than one, you're in trouble,
#         # and you should call it again with exc=NULL to revert the effect"""
#         ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
#         raise SystemError("PyThreadState_SetAsyncExc failed")
#
#
# def stop_thread(thread):
#     _async_raise(thread.ident, SystemExit)


def get_new_a1p():
    return float(ts.get_realtime_quotes(CODE)['a1_p'].values[0])


def get_new_b1v():
    return int(ts.get_realtime_quotes(CODE)['b1_v'].values[0])


def alert(code):
    messagebox.showinfo("提示", code + " 出现开板迹象")
#
#
# def auto_alert(code):
#     t1 = threading.Thread(target=alert, args=(CODE,))
#     t1.start()
#     time.sleep(DISPLAY)
#     stop_thread(t1)


# assume following logic happens every INTERVAL seconds
i = 0
root = tk.Tk()
root.withdraw()
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
                print(1)
        else:
            print("未封停")
