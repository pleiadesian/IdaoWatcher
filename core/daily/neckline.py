"""
@ File:     neckline.py
@ Author:   pleiadesian
@ Datetime: 2020-01-19 21:28
"""
import tushare as ts


def detect_neckline(code):
    """
    detect the necklines in 120 days
    :param code: stock code
    :return: a list of neckline value
    """
    # api documentary: https://github.com/waditu/tushare/blob/faa771909937543e0969085c2cf6ec9f50d4ffc4/docs/trading.rst
    df = ts.get_hist_data(code)
    # TODO: complete this part, please


if __name__ == '__main__':
    # I want result containing 22.47±0.2 and 24.70±0.2
    detect_neckline("603888")
