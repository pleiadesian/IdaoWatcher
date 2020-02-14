"""
@ File:     batch_sell_main.py
@ Author:   pleiadesian
@ Datetime: 2020-02-14 08:55
"""
import sys
import tushare as ts
import frontend.batch_sell as bs
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget


class BatchSellMain(QMainWindow, bs.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BatchSellMain, self).__init__(parent)
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    batch_sell_main = BatchSellMain()
    batch_sell_main.show()
    app.exec_()
