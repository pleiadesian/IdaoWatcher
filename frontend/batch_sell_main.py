"""
@ File:     batch_sell_main.py
@ Author:   pleiadesian
@ Datetime: 2020-02-14 08:55
"""
import os
import sys
import math
import tushare as ts
import smtplib
import frontend.batch_sell as bs
import api.ts_map as tm
from email.mime.text import MIMEText
from email.header import Header
from frontend import setfocus
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PyQt5.QtCore import QTimer

INTERVAL = 3000


def get_new_a1p(codes):
    infos = ts.get_realtime_quotes(codes).values
    a1ps = []
    for info in infos:
        # get ask price 1
        a1ps.append(float(info[21]))
    return a1ps


class BatchSellMain(QMainWindow, bs.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BatchSellMain, self).__init__(parent)
        self.setupUi(self)
        self.window_info = setfocus.init_fs()
        self.codes = []
        self.price = dict()
        self.amount = dict()
        self.watch = dict()
        self.watching = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_watch)
        self.timer.start(INTERVAL)

    def confirm(self):
        price_text = self.lineEdit_price.text()
        code_text = self.lineEdit_stock.text()
        amount_text = self.lineEdit_amount.text()
        percent_text = self.lineEdit_percent.text()
        watch_text_low = self.lineEdit_watch_price_low.text()
        watch_text_high = self.lineEdit_watch_price_high.text()

        if watch_text_low == '':
            if price_text == '':
                QMessageBox.question(self, "警告", "卖出价格未设置！",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                return
            price = float(price_text)
            if price > 10.0:
                QMessageBox.question(self, "警告", "价格设置过低！",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                return
            if amount_text == '':
                amount_text = '全仓卖出'
                sell_amount = None
            else:
                amount = int(amount_text)
                if amount <= 0 or amount % 100 != 0:
                    QMessageBox.question(self, "警告", "持仓数填写错误！",
                                         QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                    return
                if percent_text == '':
                    percent = 1
                    percent_text = '1'
                else:
                    if float(percent_text) < 1:
                        QMessageBox.question(self, "警告", "卖出比例填写错误！",
                                             QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                        return
                    percent = 1 / float(percent_text)
                sell_amount = math.ceil(amount * percent / 100) * 100
                amount_text = '持仓' + amount_text + '股 卖出' + str(sell_amount) + '股' + '(1/' + percent_text + '仓位）'
            if code_text in self.codes:
                QMessageBox.question(self, "警告", "该股票已加入卖出计划！",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                return
            if code_text not in tm.name_mapping:
                QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                return

            new_line = code_text + ' ' + tm.name_mapping[code_text] + ' 低' + price_text + '%   ' + amount_text + '\n'
            self.label_stock.setText(self.label_stock.text() + new_line)
            self.codes.append(code_text)
            self.price[code_text] = price_text
            if sell_amount is not None:
                self.amount[code_text] = str(sell_amount)
        else:
            price_low = float(watch_text_low)
            price_high = float(watch_text_high)
            new_line = code_text + ' ' + tm.name_mapping[code_text] + ' 监控卖出 止损：' + watch_text_low + ' 止盈：' + \
                watch_text_high
            self.label_stock.setText(self.label_stock.text() + new_line)
            self.codes.append(code_text)
            self.watch[code_text] = (price_low, price_high)

    def delete(self):
        code_text = self.lineEdit_stock.text()
        stock_text = self.label_stock.text()
        if code_text not in self.codes:
            QMessageBox.question(self, "警告", "该股票代码未加入卖出计划",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        new_text = ''
        stocks = stock_text.split('\n')
        for stock in stocks:
            if stock.startswith(code_text):
                continue
            new_text += stock + '\n'
        self.label_stock.setText(new_text)
        self.codes.remove(code_text)
        del self.price[code_text]
        if code_text in self.amount:
            del self.amount[code_text]

    def check_watch(self):
        if self.watching:
            a1_ps = get_new_a1p(self.codes)
            if len(a1_ps) != len(self.codes) or len(self.codes) == 0:
                QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                self.pushButton_watch_sell.setText('监控卖出')
                self.watching = False
                return
            for code, ask_price in zip(self.codes, a1_ps):
                sell_price_low = self.watch[code][0]
                sell_price_high = self.watch[code][1]
                if sell_price_low > ask_price:
                    setfocus.sell_code(code, str(ask_price), None, self.window_info)
                    self.codes.remove(code)
                    del self.watch[code]
                elif sell_price_high < ask_price:
                    setfocus.sell_code(code, str(ask_price), None, self.window_info)
                    self.codes.remove(code)
                    del self.watch[code]

    def watch_sell_start(self):
        if self.pushButton_watch_sell.text() == '监控卖出':
            self.pushButton_watch_sell.setText('取消')
            self.watching = True
        else:
            self.pushButton_watch_sell.setText('监控卖出')
            self.watching = False

    def batch_sell_start(self):
        a1_ps = get_new_a1p(self.codes)
        if len(a1_ps) != len(self.codes) or len(self.codes) == 0:
            QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        for code, ask_price in zip(self.codes, a1_ps):
            sell_price = str(round(ask_price * (1 - float(self.price[code]) / 100), 2))
            if code in self.amount:
                amt = self.amount[code]
            else:
                amt = None
            setfocus.sell_code(code, sell_price, amt, self.window_info)
        QMessageBox.question(self, "提示", "批量委托卖出完毕",
                             QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)

    def send_email(self):
        sender = '574402791@qq.com'
        password = os.getenv('MAIL_PASSWORD')
        receivers = 'wzl574402791@outlook.com'
        smtp_server = 'smtp.qq.com'

        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        message = MIMEText('股价预警', 'plain', 'utf-8')
        message['From'] = Header(sender)
        message['To'] = Header(receivers)
        message['Subject'] = Header('股价预警', 'utf-8')

        while True:
            try:
                server = smtplib.SMTP_SSL()
                server.connect(smtp_server, 465)

                server.login(sender, password)
                server.sendmail(sender, receivers, message.as_string())
                break
            except smtplib.SMTPException:
                continue


if __name__ == '__main__':
    batch_sell_main = BatchSellMain()
    batch_sell_main.send_email()
    # app = QApplication(sys.argv)
    # batch_sell_main = BatchSellMain()
    # batch_sell_main.show()
    # app.exec_()
