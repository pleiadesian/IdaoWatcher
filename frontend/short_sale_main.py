"""
@ File:     short_sale_main.py
@ Author:   pleiadesian
@ Datetime: 2020-02-28 17:55
"""
import os
import sys
import pickle
import datetime
from xlwt import Workbook
import tushare as ts
import frontend.short_sale as ss

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget


class Trade:
    amount = 0
    loan_time = None
    sell_price = None
    sell_time = None
    buy_price = None
    buy_time = None
    closed = False


class ShortSaleMain(QMainWindow, ss.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ShortSaleMain, self).__init__(parent)
        self.setupUi(self)
        self.codes = dict()

        path = os.getenv('PROJPATH')
        self.target = path + 'short_sale.dat'
        if os.path.isfile(self.target) and os.path.getsize(self.target) > 0:
            with open(self.target, 'rb') as f:
                unpickler = pickle.Unpickler(f)
                self.codes = unpickler.load()
        self.display()

    def save(self):
        with open(self.target, 'wb') as f:
            pickle.dump(self.codes, f)
        w = Workbook()
        ws = w.add_sheet('1')
        ws.write(0, 0, '股票代码')
        ws.write(0, 1, '持仓量')
        ws.write(0, 2, '融券时间')
        ws.write(0, 3, '卖出价格')
        ws.write(0, 4, '卖出时间')
        ws.write(0, 5, '买入价格')
        ws.write(0, 6, '买入时间')
        ws.write(0, 7, '平仓状态')
        ws.write(0, 8, '净利润')
        i = 1
        for code, trade in self.codes.items():
            ws.write(i, 0, code)
            ws.write(i, 1, str(trade.amount))
            ws.write(i, 2, trade.loan_time.strftime('%Y-%m-%d %H:%M:%S'))
            if trade.sell_price is not None:
                ws.write(i, 3, str(trade.sell_price))
                ws.write(i, 4, trade.sell_time.strftime('%Y-%m-%d %H:%M:%S'))
            if trade.buy_price is not None:
                ws.write(i, 5, str(trade.sell_price))
                ws.write(i, 6, trade.sell_time.strftime('%Y-%m-%d %H:%M:%S'))
            if trade.closed:
                profit = (trade.sell_price - trade.buy_price) / trade.amount
                ws.write(i, 7, '是')
                ws.write(i, 8, str(profit))
            else:
                ws.write(i, 7, '否')
            i += 1
        w.save('short_sale.xls')

    def flush(self):
        self.display()

    def loan(self):
        code_text = self.lineEdit_code.text()
        amount_text = self.lineEdit_amount.text()
        info = ts.get_realtime_quotes(code_text)
        if info is None:
            QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        if amount_text == '':
            QMessageBox.question(self, "警告", "检测到数量输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        price = float(info['price'])
        amount = float(amount_text)
        stock_amount = amount // price // 100 * 100
        curr_time = datetime.datetime.now()
        trade = Trade()
        trade.amount = stock_amount
        trade.loan_time = curr_time
        # stock has been traded, modify the key of old trade
        if code_text in self.codes:
            trade_date = str(self.codes[code_text].loan_time)
            if trade_date[:10] == datetime.datetime.now().strftime("%Y-%m-%d"):
                QMessageBox.question(self, "警告", "当日已融券！",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                return
            self.codes[code_text + ' ' + trade_date] = self.codes[code_text]
        self.codes[code_text] = trade
        self.display()

    def closeout(self):
        code_text = self.lineEdit_code.text()
        if code_text not in self.codes or self.codes[code_text].closed is True:
            QMessageBox.question(self, "警告", "无持仓",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        if self.codes[code_text].sell_price is None or self.codes[code_text].buy_price is None:
            QMessageBox.question(self, "警告", "还未进行交易",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        self.codes[code_text].closed = True
        self.display()

    def sell(self):
        code_text = self.lineEdit_code.text()
        info = ts.get_realtime_quotes(code_text)
        if info is None:
            QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        if code_text not in self.codes or self.codes[code_text].closed is True:
            QMessageBox.question(self, "警告", "无持仓",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        if self.codes[code_text].sell_price is not None:
            QMessageBox.question(self, "警告", "已卖出",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        price = float(info['price'])
        self.codes[code_text].sell_time = datetime.datetime.now()
        self.codes[code_text].sell_price = price
        self.display()

    def buy(self):
        code_text = self.lineEdit_code.text()
        info = ts.get_realtime_quotes(code_text)
        if info is None:
            QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        if code_text not in self.codes or self.codes[code_text].closed is True:
            QMessageBox.question(self, "警告", "无持仓",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        if self.codes[code_text].sell_price is None:
            QMessageBox.question(self, "警告", "还未卖出",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        price = float(info['price'])
        self.codes[code_text].buy_time = datetime.datetime.now()
        self.codes[code_text].buy_price = price
        self.display()

    def display(self):
        label_text = ''
        for code, trade in self.codes.items():
            if trade.closed is True:
                continue
            line_text = code + ' ' + '融券时间：' + trade.loan_time.strftime('%Y-%m-%d %H:%M:%S') + ' 数量：' + \
                str(trade.amount) + '股\n'
            if trade.sell_price is not None:
                line_text += '\t卖出时间：' + trade.sell_time.strftime('%Y-%m-%d %H:%M:%S') + ' 卖出价格：' + \
                             str(trade.sell_price) + '\n'
                if trade.buy_price is None:
                    info = ts.get_realtime_quotes(code)
                    price = float(info['price'])
                    profit = (trade.sell_price - price) * trade.amount
                    line_text += '\t现价：' + str(price) + ' 净利润：' + str(profit) + '\n'
            if trade.buy_price is not None:
                line_text += '\t买入时间：' + trade.sell_time.strftime('%Y-%m-%d %H:%M:%S') + ' 买入价格：' + \
                             str(trade.sell_price) + '\n'
                profit = (trade.sell_price - trade.buy_price) * trade.amount
                line_text += '\t成交价：' + str(trade.buy_price) + ' 净利润：' + str(profit) + '\n'
            label_text += line_text
        self.label_display.setText(label_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    short_sale_main = ShortSaleMain()
    short_sale_main.show()
    app.exec_()
