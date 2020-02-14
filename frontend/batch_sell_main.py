"""
@ File:     batch_sell_main.py
@ Author:   pleiadesian
@ Datetime: 2020-02-14 08:55
"""
import sys
import tushare as ts
import frontend.batch_sell as bs
from frontend import setfocus
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget


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

    def confirm(self):
        price = self.lineEdit_price.text()
        code_text = self.lineEdit_stock.text()
        self.label_stock.setText(code_text)
        codes = code_text.split(' ')
        if price > 10:
            QMessageBox.question(self, "警告", "价格设置过低！",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        a1_ps = get_new_a1p(self.codes)
        if len(a1_ps) != len(codes):
            QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入（注意股票代码之间必须有且仅有1个空格）",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        sell_ps = [p * (1 - price / 100) for p in a1_ps]
        for code, sell_price in zip(codes, sell_ps):
            setfocus.sell_code(code, sell_price, self.window_info)
        QMessageBox.question(self, "警告", "批量委托卖出完毕",
                             QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    batch_sell_main = BatchSellMain()
    batch_sell_main.show()
    app.exec_()
