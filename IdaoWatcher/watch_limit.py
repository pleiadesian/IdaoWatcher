"""
@ File:     watch_limit.py
@ Author:   pleiadesian
@ Datetime: 2020-01-11 14:22
监听特定股票的封停是否有打开的迹象
"""
import tushare as ts
import copy
import sys
import os
import winsound
import setfocus
import watch_limit_main, watch_limit_warn
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt

# alert if bid1 amount has decreased more than 5% in 3 second
INTERVAL = 3000
THRESHOLD = 0.98  # default 0.95
HIGH_THRESHOLD = 0.85  # default 0.80
BUTTON_X = 60
BUTTON_NONE_X = -200


DEBUG = 0


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
        self.move(screen.width() - self.width(), screen.height() - self.height() - 50)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        screen = QApplication.desktop()
        screen_count = QApplication.desktop().screenCount()
        if screen_count > 1:
            # for 3-screen setting
            self.screen_rect0 = QApplication.desktop().screenGeometry(0)
            self.screen_rect1 = QApplication.desktop().screenGeometry(1)
            self.screen_rect2 = QApplication.desktop().screenGeometry(2)
            max_width = max(self.screen_rect0.width(), self.screen_rect1.width(), self.screen_rect2.width())
            max_height = max(self.screen_rect0.height(), self.screen_rect1.height(), self.screen_rect2.height())
            self.screen_width = max_width
            self.screen_height = max_height
        else:
            self.screen_width = screen.width()
            self.screen_height = screen.height()
        self.move(self.screen_width - self.width(), self.screen_height - self.height() - 50)

    def accept(self):
        self.move(3000, 3000)

    def reject(self):
        self.move(3000, 3000)

    def warn(self):
        QApplication.processEvents()
        if self.x() != self.screen_width - self.width() or self.y() != self.screen_height - self.height() - 50:
            self.move(self.screen_width - self.width(), self.screen_height - self.height() - 50)


class PictureView(QMainWindow, watch_limit_main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PictureView, self).__init__(parent)
        self.setupUi(self)
        self.dlg = MessageView()
        self.dlg.show()
        self.button_list = [self.dlg.pushButton_0, self.dlg.pushButton_1, self.dlg.pushButton_2, self.dlg.pushButton_3,
                            self.dlg.pushButton_4, self.dlg.pushButton_5]
        self.code_list = ["", "", "", "", "", ""]
        for button in self.button_list:
            button.move(BUTTON_NONE_X, button.y())
        self.dlg.pushButton_0.clicked.connect(lambda: setfocus.open_code(self.code_list[0], self.window_info, self.dlg))
        self.dlg.pushButton_1.clicked.connect(lambda: setfocus.open_code(self.code_list[1], self.window_info, self.dlg))
        self.dlg.pushButton_2.clicked.connect(lambda: setfocus.open_code(self.code_list[2], self.window_info, self.dlg))
        self.dlg.pushButton_3.clicked.connect(lambda: setfocus.open_code(self.code_list[3], self.window_info, self.dlg))
        self.dlg.pushButton_4.clicked.connect(lambda: setfocus.open_code(self.code_list[4], self.window_info, self.dlg))
        self.dlg.pushButton_5.clicked.connect(lambda: setfocus.open_code(self.code_list[5], self.window_info, self.dlg))
        self.window_info = setfocus.init_fs()

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
            # new_text = ""
            new_text = []
            new_text_broken = ""
            QApplication.processEvents()
            a1_ps = get_new_a1p(self.codes)
            b1_vs = get_new_b1v(self.codes)
            if len(a1_ps) != len(self.codes) or len(b1_vs) != len(self.codes):
                if DEBUG == 1:
                    get_code = self.codes
                    append_code = ""
                    for codee in get_code:
                        append_code = append_code + ' ' + codee
                    for a1pss in self.a1_ps:
                        append_code = append_code + ' ' + a1pss
                    for b1vss in self.b1_vs:
                        append_code = append_code + ' ' + b1vss
                QMessageBox.question(self, "警告", "检测到股票代码输入错误，请重新输入" + append_code,
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                self.started = False
                self.dlg.label.setText("暂停")
                self.pushButton_2.setEnabled(True)
                self.pushButton_2.setText("开始运行")
            signal = False
            for code, a1_p, b1_v in zip(self.codes, a1_ps, b1_vs):
                QApplication.processEvents()
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
                                # new_text = new_text + code + " 出现开板迹象\n"
                                new_text.append(code)
                                # os.system('say "warning"')
                                winsound.Beep(500, 500)
                                signal = True
                            self.broken_signal[code] = 10
                        if DEBUG == 1:
                            # new_text = new_text + code + " 出现开板迹象\n"
                            new_text.append(code)
                            # os.system('say "warning"')
                            winsound.Beep(500, 500)
                            signal = True
                            self.broken_signal[code] = 10
                        self.b1_v_prev[code] = b1_v
                else:
                    # print(code + " 未封停")
                    new_text_broken = new_text_broken + code + " 已经开板\n"
                    if DEBUG == 1:
                        new_text.append(code)
                        signal = True
            if signal is True:
                self.dlg.warn()
            # assign alert code to buttons
            QApplication.processEvents()
            self.code_list = new_text
            for button, text in zip(self.button_list, new_text):
                button.setText(text)
                button.move(BUTTON_X, button.y())
            # button remained should be evicted
            alert_codes = len(new_text)
            for button in self.button_list:
                alert_codes -= 1
                if alert_codes < 0:
                    button.setText("none")
                    button.move(BUTTON_NONE_X, button.y())
            self.dlg.label_broken.setText(new_text_broken)
            if DEBUG == 1:
                self.lineEdit.setText(str(self.dlg.x()) + ' ' + str(self.dlg.y()) + ' ' +
                                      str(self.dlg.screen_width) + ' ' + str(self.dlg.screen_height))

    def resetcode(self):
        if DEBUG == 1:
            self.label_watch.setText(str(self.x()) + ' ' + str(self.y()) + ' ' +
                                     str(self.dlg.screen_width) + ' ' + str(self.dlg.screen_height))
            self.label_watch.setText(str(self.dlg.screen_rect0.x()) + ' ' + str(self.dlg.screen_rect0.y()) + ' ' +
                                     str(self.dlg.screen_rect0.width()) + ' ' + str(self.dlg.screen_rect0.height()) +
                                     '  ' + str(self.dlg.screen_rect1.x()) + ' ' + str(self.dlg.screen_rect1.y()) + ' '
                                     + str(self.dlg.screen_rect1.width()) + ' ' + str(self.dlg.screen_rect1.height()))
        # self.dlg.showMinimized()
        self.lineEdit.setText(self.label_watch.text())

    def addcode(self):
        text = self.lineEdit.text()
        self.label_watch.setText(text)
        self.codes = text.split(' ')

    def startrun(self):
        self.started = True
        # self.dlg.label.setText("正在运行")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setText("正在运行")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    picView = PictureView()
    picView.show()
    app.exec_()
