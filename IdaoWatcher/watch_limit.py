"""
@ File:     watch_limit.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 14:22
监听特定股票的封停是否有打开的迹象
"""
import tushare as ts
import time
import sys
import watch_limit_main
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

CODES = ['600075', '300541', '002740']
INTERVAL = 2000
THRESHOLD = 0.95


def get_new_a1p(code):
    return float(ts.get_realtime_quotes(code)['a1_p'].values[0])


def get_new_b1v(code):
    return int(ts.get_realtime_quotes(code)['b1_v'].values[0])


class PictureView(QMainWindow, watch_limit_main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PictureView, self).__init__(parent)
        self.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkall)

        self.i = 0
        self.b1_v_prev = dict()
        self.timer.start(INTERVAL)

    def checkall(self):
        self.label.setText("")
        newText = ""
        for code in CODES:
            a1_p = get_new_a1p(code)
            b1_v = get_new_b1v(code)

            # use a1_p == 0.00 to judge if limit has been broken
            if a1_p == 0:
                # limit keeped, watch its volume
                print(code + " 封停")
                if code not in self.b1_v_prev:
                    self.b1_v_prev[code] = b1_v
                else:
                    if b1_v / self.b1_v_prev[code] < THRESHOLD:
                        newText = newText + code + " 出现开板迹象\n"
                        self.b1_v_prev[code] = b1_v
            else:
                print(code + " 未封停")
                newText = newText + code + " 已经开板\n"
        self.label.setText(newText)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    picView = PictureView()
    picView.show()
    app.exec_()

