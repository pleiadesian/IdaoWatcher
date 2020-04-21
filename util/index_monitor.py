"""
@ File:     index_monitor.py
@ Author:   pleiadesian
@ Datetime: 2020-04-21 09:01
"""
import time
import tushare as ts
from subprocess import call

while True:
    df = ts.get_realtime_quotes('sh')
    time.sleep(3)
    if float(df.price) > 2837.0:
        cmd = 'display notification \"' + \
              "At expected price" + '\" with title \"Price alert\"'
        call(["osascript", "-e", cmd])
