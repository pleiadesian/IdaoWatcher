"""
@ File:     neckline.py
@ Author:   pleiadesian
@ Datetime: 2020-01-17 07:20
@ Desc:     Maintaining the state of neckline of stock in time share
"""
import tushare as ts

neckline = dict()


def detect_neckline(code):
    """
    update the state of neckline
    :param code: stock code
    """
    info = ts.get_realtime_quotes(code).values[0]
    price = info[3]
    high = info[4]
    time = info[31]
    if price == high:
        neckline[code] = time


if __name__ == '__main__':
    detect_neckline('000001')
