"""
@ File:     watch_limit.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 14:22
监听特定股票的封停是否有打开的迹象
"""
import tushare as ts
import time
import sys
import os
import winsound
import watch_limit_main
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# alert if bid1 amount has decreased more than 5% in 3 second
INTERVAL = 3000
THRESHOLD = 0.95


def get_new_a1p(codes):
    infos = ts.get_realtime_quotes(codes).values
    a1ps = []
    for info in infos:
        # get ask price 1
        a1ps.append(float(info[21]))
    return a1ps


def get_new_b1v(codes):
    infos = ts.get_realtime_quotes(codes).values
    b1vs = []
    for info in infos:
        # get bid volume 1
        b1vs.append(int(info[10]))
    return b1vs


class PictureView(QMainWindow, watch_limit_main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PictureView, self).__init__(parent)
        self.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkall)

        self.i = 0
        self.b1_v_prev = dict()
        self.codes = []
        self.timer.start(INTERVAL)
        self.started = False

    def checkall(self):
        if self.started is True:
            self.label.setText("")
            new_text = ""
            a1_ps = get_new_a1p(self.codes)
            b1_vs = get_new_b1v(self.codes)
            for code, a1_p, b1_v in zip(self.codes, a1_ps, b1_vs):
                # use a1_p == 0.00 to judge if limit has been broken
                if a1_p == 0:
                    # limit keeped, watch its volume
                    print(code + " 封停")
                    if code not in self.b1_v_prev:
                        self.b1_v_prev[code] = b1_v
                    else:
                        if b1_v / self.b1_v_prev[code] < THRESHOLD:
                            new_text = new_text + code + " 出现开板迹象\n"
                            self.b1_v_prev[code] = b1_v
                            os.system('say "warning"')
                            winsound.Beep(500, 500)
                else:
                    print(code + " 未封停")
                    new_text = new_text + code + " 已经开板\n"
            self.label.setText(new_text)

    def addcode(self):
        text = self.lineEdit.text()
        self.label_watch.setText(text)
        self.codes = text.split(' ')

    def startrun(self):
        self.started = True
        self.label.setText("正在运行")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setText("正在运行")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    picView = PictureView()
    picView.show()
    app.exec_()

