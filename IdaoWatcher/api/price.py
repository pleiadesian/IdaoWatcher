"""
@ File:     price.py
@ Author:   pleiadesian
@ Datetime: 2020-01-16 23:13
"""
import time
import tushare as ts
from random import randint
from urllib.request import urlopen, Request


def random(n=13):
    start = 10**(n-1)
    end = (10**n)-1
    return str(randint(start, end))


pro = ts.pro_api()
data = pro.daily(trade_date='20200116').values

code_list = ['', '', '', '', '', '', '', '']
i = 0
for code in data:
    i += 1
    if code[0][-2:] == 'SH':
        code_list[int(i / 500)] += 'sh' + code[0][:6] + ','
    else:
        code_list[int(i / 500)] += 'sz' + code[0][:6] + ','
for j in range(0, 8):
    code_list[j] = code_list[j][:-1]
start_time = time.time()
for j in range(0, 8):
    request = Request('%shq.%s/rn=%s&list=%s' % ('http://', 'sinajs.cn',
                                                 random(), code_list[j]))
    text = urlopen(request, timeout=10).read()
end_time = time.time()
print(end_time - start_time)