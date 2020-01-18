from threading import Timer
import tushare as ts
import time
df = ts.get_realtime_quotes("000001")
print(df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']])


def launchTime():
    if ((df[['price']])-(df[['amount']/['volume']]):
        print('THE LINE LAUNCH ALARM')
    else:
        print(df[['code', 'name', 'price', 'bid',
                  'ask', 'volume', 'amount', 'time']])
    Timer(1.0, launchTime).start()


t = Timer(1.0, launchTime)
t.start()

while True:
    print('我在爬数据')
    time.sleep(1)
