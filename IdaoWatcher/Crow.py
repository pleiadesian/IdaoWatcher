from threading import Timer
import tushare as ts
import time


class Dataframe:
    def __init__(self):
        df = ts.get_realtime_quotes("000001")
        self.price = float(df.price)
        self.volume = float(df.volume)
        self.amount = float(df.amount)

    def crossline(self):
        while True:
            time.sleep(1)
            df = ts.get_realtime_quotes("000001")
            price2 = float(df.price)
            volume2 = float(df.volume)
            amount2 = float(df.amount)
            if self.price < self.amount/self.volume and price2 > amount2/volume2:
                print("RedLine!")


if __name__ == '__main__':
    dataframe = Dataframe()
    dataframe.crossline()
