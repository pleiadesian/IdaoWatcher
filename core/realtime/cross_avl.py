import tushare as ts


class Dataframe:
    def __init__(self):
        self.price = dict()
        self.volume = dict()
        self.amount = dict()

    def crossline(self, code):
        df = ts.get_realtime_quotes(code)
        price2 = float(df.price)
        volume2 = float(df.volume)
        amount2 = float(df.amount)
        if code not in self.price:
            assert code not in self.amount and code not in self.volume
            self.price[code] = price2
            self.amount[code] = amount2
            self.volume[code] = volume2
        elif self.price[code] < self.amount[code]/self.volume[code] and price2 > amount2/volume2:
            print("RedLine!")


if __name__ == '__main__':
    dataframe = Dataframe()
    dataframe.crossline("000001")
