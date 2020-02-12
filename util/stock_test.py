"""
@ File:     stock_test.py
@ Author:   Cei1ing
@ Datetime: 2020-02-011 
"""

import tushare as ts
import numpy as np

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
        change_rate = (close_data[-1]-close_data[0])/close_data[-1]
        return_list.append([id_,change_rate])
    return return_list

def short_sell_test(start,end,stock_ids):
    """
    
    start: a string in format YYYY-MM-DD indicating the start date of short
    end: a string in format YYYY-MM-DD indicating the end date of short
    stock_ids: a list containing strings of stock ids to short
        
    return: profit margin of the short

    """
    price_data = []
    for id_ in stock_ids:
        df = ts.get_hist_data(id_,start=start,end=end)
        close_data = list(df['close'])
        price_data.append([close_data[-1],close_data[0]])
    price_data = np.array(price_data)
    buy_num = 1/price_data[:,0]
    profit_margin = len(stock_ids)/((buy_num*price_data[:,1]).sum())-1
    return profit_margin   

if __name__ == '__main__':
    ids = ['600052','000058','600812','300379','000038','002417','002201','300061','000595','601519']
    print("Change rates are\n",stock_retest('2019-09-16','2019-10-06',ids))
    print("Short sell profit margin =",short_sell_test('2019-09-16','2019-10-06',ids))
