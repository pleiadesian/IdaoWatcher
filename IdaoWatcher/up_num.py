
import tushare as ts
import datetime


#def calc_60_up_num(code):
#    """
#    :param code: stock code
#    :return: the number of rising K60
#    """
hzsunmoon_num = 0  # 初始化阳线根数为0
stock_ticker='688036'
now_time=datetime.datetime.now().strftime('%Y-%m-%d') #今天的日期（年-月-日）
past_time=(datetime.datetime.now()-datetime.timedelta(days=3)).strftime('%Y-%m-%d') #认为不可能连着12根阳线，只往前推3天


all_info=ts.get_hist_data(stock_ticker,start=past_time,end=now_time,ktype='60')
open_price=all_info['open']
high_price=all_info['high']
close_price=all_info['close']
low_price=all_info['low']

#目前只考虑连续两天涨停的情况
limit_1_before=round(close_price[4]*1.1,2) #昨天的涨停limit
limit_2_before=round(close_price[8]*1.1,2) #前天的涨停limit
limit_set=[limit_1_before,limit_2_before]
#判断十字星
def judge_doji(i,open,high,close,low):
    if(abs(open[i]-close[i])<=(high[i]-low[i])*0.1)and(open[i]>low[i]+0.02)and(open[i]<high[i]-0.02)and(close[i]>low[i]+0.02)and(close[i]<high[i]-0.02):
        return 1 #收盘价与开盘价差的绝对值小于等于高低峰值差的0.1倍，且十字的一横不在最高或最低处，此时认为是十字星
    else: return 0




for i in range(11):
    if((close_price[i]>open_price[i]+0.01)and(judge_doji(i,open_price,high_price,close_price,low_price)==0)and(close_price[i+1]>open_price[i+1]+0.01))or(close_price[i]>=limit_set[i//4]):  #某一小时正常阳线，或涨停；且前一小时也涨了。
        hzsunmoon_num+=1
    elif((close_price[i]>open_price[i]+0.01)and(judge_doji(i,open_price,high_price,close_price,low_price)==0))or(close_price[i]>=limit_set[i//4]):#某小时正常阳线或涨停，前一小时不是阳线或涨停
        hzsunmoon_num+=1
    else: break

print(hzsunmoon_num)

#    stock_ticker = '000049'  # 设置股票代码
#    ret = calc_60_up_num(stock_ticker)
#    print(ret)
