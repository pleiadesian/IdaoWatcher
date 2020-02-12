"""
@ File:     stock_retest.py
@ Author:   Cei1ing
@ Datetime: 2020-02-011 
"""

import tushare as ts

def stock_retest(start,end,stock_ids):
    """
    
    start: a string in format YYYY-MM-DD indicating the start date of decrease
    end: a string in format YYYY-MM-DD indicating the end date of decrease
    stock_ids: a list containing strings of stock ids
    
    return: a list, elements are [id,change_rate] in format [string,float]
    
    """
    return_list = []
    for id_ in stock_ids:
        df = ts.get_hist_data(id_,start=start,end=end)
        close_data = list(df['close'])
        change_rate = (close_data[-1]-close_data[0])/close_data[0]
        return_list.append([id_,change_rate])
    return return_list

if __name__ == '__main__':
    ids = ['600052','000058','600812','300379','000038','002417','002201','300061','000595','601519']
    print(stock_retest('2019-09-16','2019-10-06',ids))
