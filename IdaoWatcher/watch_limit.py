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
import watch_limit_main, watch_limit_warn
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QDesktopWidget
from PyQt5.QtCore import QTimer

# alert if bid1 amount has decreased more than 5% in 3 second
INTERVAL = 3000
THRESHOLD = 0.95
HIGH_THRESHOLD = 0.80

DEBUG = 1


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


class MessageView(QWidget, watch_limit_warn.Ui_Dialog):
    def __init__(self):
        super(MessageView, self).__init__()
        self.setupUi(self)
        screen = QApplication.desktop()
        self.move(screen.width() - self.width(), screen.height() - self.height())

    def accept(self):
        self.showMinimized()

    def reject(self):
        self.showMinimized()

    def warn(self):
        self.showNormal()


class PictureView(QMainWindow, watch_limit_main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PictureView, self).__init__(parent)
        self.setupUi(self)
        self.dlg = MessageView()
        self.dlg.show()
        self.dlg.showMinimized()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkall)

        self.i = 0
        self.b1_v_prev = dict()
        self.broken_signal = dict()
        self.codes = []
        self.timer.start(INTERVAL)
        self.started = False

    def checkall(self):
        if self.started is True:
            new_text = ""
            new_text_broken = ""
            a1_ps = get_new_a1p(self.codes)
            b1_vs = get_new_b1v(self.codes)
            if len(a1_ps) != len(self.codes) or len(b1_vs) != len(self.codes):
                QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入",
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                self.started = False
                self.dlg.label.setText("暂停")
                self.pushButton_2.setEnabled(True)
                self.pushButton_2.setText("开始运行")
            signal = False
            for code, a1_p, b1_v in zip(self.codes, a1_ps, b1_vs):
                if code in self.broken_signal and self.broken_signal[code] > 0:
                    self.broken_signal[code] -= 1
                # use a1_p == 0.00 to judge if limit has been broken
                if a1_p == 0:
                    # limit keeped, watch its volume
                    # print(code + " 封停")
                    if code not in self.b1_v_prev:
                        self.b1_v_prev[code] = b1_v
                    else:
                        if b1_v / self.b1_v_prev[code] < THRESHOLD:
                            if b1_v / self.b1_v_prev[code] < HIGH_THRESHOLD or \
                                    (code in self.broken_signal and self.broken_signal[code] > 0):
                                new_text = new_text + code + " 出现开板迹象\n"
                                os.system('say "warning"')
                                winsound.Beep(500, 500)
                                signal = True
                            self.broken_signal[code] = 10
                        if DEBUG == 1:
                            new_text = new_text + code + " 出现开板迹象\n"
                            os.system('say "warning"')
                            # winsound.Beep(500, 500)
                            signal = True
                            self.broken_signal[code] = 10
                        self.b1_v_prev[code] = b1_v
                else:
                    # print(code + " 未封停")
                    new_text_broken = new_text_broken + code + " 已经开板\n"
                    if DEBUG == 1:
                        signal = True
            if signal is True:
                if self.dlg.isMinimized():
                    self.dlg.showNormal()
            self.dlg.label.setText(new_text)
            self.dlg.label_broken.setText(new_text_broken)

    def resetcode(self):
        self.lineEdit.setText(self.label_watch.text())

    def addcode(self):
        text = self.lineEdit.text()
        self.label_watch.setText(text)
        self.codes = text.split(' ')

    def startrun(self):
        self.started = True
        self.dlg.label.setText("正在运行")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setText("正在运行")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    picView = PictureView()
    picView.show()
    app.exec_()

