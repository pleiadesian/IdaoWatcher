import tushare as ts
import datetime


hzsunmoon_num=0        #初始化阳线根数为0
stock_ticker='000807' #设置股票代码

now_time=datetime.datetime.now().strftime('%Y-%m-%d') #今天的日期（年-月-日）
past_time=(datetime.datetime.now()-datetime.timedelta(days=3)).strftime('%Y-%m-%d') #认为不可能连着12根阳线，只往前推3周

a=ts.get_hist_data(stock_ticker,start=past_time,end=now_time,ktype='60')
#######print(a)
for i in range(11):
    if(a.iat[i,2]>a.iat[i,0]+0.01)and(a.iat[i+1,2]>a.iat[i+1,0]+0.01):
        hzsunmoon_num+=1
    elif(a.iat[i,2]>a.iat[i,0]):
        hzsunmoon_num+=1
    else: break

print(hzsunmoon_num) #输出阳线的根数