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

CODE = '600075'
CODE1 = '300541'
INTERVAL = 5000
THRESHOLD = 0.95


def get_new_a1p():
    return float(ts.get_realtime_quotes(CODE)['a1_p'].values[0])


def get_new_b1v():
    return int(ts.get_realtime_quotes(CODE)['b1_v'].values[0])


class PictureView(QMainWindow, watch_limit_main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PictureView, self).__init__(parent)
        self.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)

        self.i = 0
        self.b1_v_prev = None
        self.timer.start(INTERVAL)

    def main_loop(self):
        a1_p = get_new_a1p()
        b1_v = get_new_b1v()

        # use a1_p == 0.00 to judge if limit has been broken
        if a1_p == 0:
            # limit keeped, watch its volume
            print("封停")
            if self.b1_v_prev is None:
                self.b1_v_prev = b1_v
            else:
                if b1_v / self.b1_v_prev < THRESHOLD:
                    self.label.setText(CODE + " 出现开板迹象")
                    self.b1_v_prev = b1_v
        else:
            print("未封停")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    picView = PictureView()
    picView.show()
    app.exec_()

