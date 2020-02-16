"""
@ File:     main_ui.py.py
@ Author:   pleiadesian
@ Datetime: 2020-02-02 11:02
"""
import sys
import time
import multiprocessing
import main as backend
import frontend.main as frontend
from frontend import setfocus
from random import randint
from multiprocessing import Value, Manager
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PyQt5.QtCore import QTimer, Qt

INTERVAL = 1000
INTERVAL_CLEAR = 5000
INTERVAL_RECENT = 60000
BUTTON_X = 60
BUTTON_NONE_X = -200


class MainUi(QMainWindow, frontend.Ui_Dialog):
    def __init__(self):
        super(MainUi, self).__init__()
        self.setupUi(self)

        self.button_list = [self.pushButton_0, self.pushButton_1, self.pushButton_2, self.pushButton_3,
                            self.pushButton_4, self.pushButton_5, self.pushButton_6, self.pushButton_7,
                            self.pushButton_8, self.pushButton_9, self.pushButton_10, self.pushButton_11]
        self.code_list = [''] * 12
        self.spilled_codes = []
        self.recent_codes = []
        self.clear_signals = []
        self.replay_code = '000001'
        # TODO: replay button
        for button in self.button_list:
            button.move(BUTTON_NONE_X, button.y())
        self.window_info = setfocus.init_fs()
        self.pushButton_0.clicked.connect(lambda: self.click_code(0))
        self.pushButton_1.clicked.connect(lambda: self.click_code(1))
        self.pushButton_2.clicked.connect(lambda: self.click_code(2))
        self.pushButton_3.clicked.connect(lambda: self.click_code(3))
        self.pushButton_4.clicked.connect(lambda: self.click_code(4))
        self.pushButton_5.clicked.connect(lambda: self.click_code(5))
        self.pushButton_6.clicked.connect(lambda: self.click_code(6))
        self.pushButton_7.clicked.connect(lambda: self.click_code(7))
        self.pushButton_8.clicked.connect(lambda: self.click_code(8))
        self.pushButton_9.clicked.connect(lambda: self.click_code(9))
        self.pushButton_10.clicked.connect(lambda: self.click_code(10))
        self.pushButton_11.clicked.connect(lambda: self.click_code(11))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkall)
        self.timer.start(INTERVAL)
        self.timer_clear = QTimer(self)
        self.timer_clear.timeout.connect(self.clear_code)
        self.timer_clear.start(INTERVAL_CLEAR)
        self.timer_recent = QTimer(self)
        self.timer_recent.timeout.connect(self.clear_recent)
        self.timer_recent.start(INTERVAL_RECENT)

    def reset(self):
        self.code_list = [''] * 12
        self.spilled_codes = []
        self.recent_codes = []
        self.clear_signals = []

    def replay(self):
        setfocus.open_code(self.replay_code, self.window_info)

    def click_code(self, code_slot):
        setfocus.open_code(self.code_list[code_slot], self.window_info)
        self.recent_codes.append(self.code_list[code_slot])
        self.clear_signals.append(self.code_list[code_slot])
        self.replay_code = self.code_list[code_slot]

    def clear_code(self):
        i = 0
        for button, code in zip(self.button_list, self.code_list):
            if code in self.clear_signals:
                button.setText('None')
                button.move(BUTTON_NONE_X, self.button_list[i].y())
                self.code_list[i] = ''
            i += 1
        self.clear_signals = []

    def clear_recent(self):
        self.recent_codes = []

    def checkall(self):
        new_codes = list(set(codes) - set(self.code_list))
        # TODO: get code in code_list except ''
        displaying_codes = [code for code in self.code_list if code != '']
        display_codes = displaying_codes + new_codes + self.spilled_codes
        display_codes = list(set(display_codes))
        print(str(displaying_codes) + str(new_codes) + str(self.spilled_codes) + str(display_codes) + str(self.code_list))
        if len(display_codes) > 12:
            self.spilled_codes = display_codes[12:]
            display_codes = display_codes[:12]
        else:
            self.spilled_codes = []
        i = 0
        display_codes = list(set(display_codes) - set(self.recent_codes))
        display_codes.sort()
        for button, code in zip(self.button_list, display_codes):
            button.setText(code)
            self.code_list[i] = code
            button.move(BUTTON_X, button.y())
            i += 1
        alert_codes = len(display_codes)
        for button in self.button_list:
            alert_codes -= 1
            if alert_codes < 0:
                button.setText('None')
                button.move(BUTTON_NONE_X, button.y())
        # print('after check:' + str(self.code_list))

    def select_zx(self):
        if self.radioButton_zx.isChecked():
            self.window_info = setfocus.change_fs('中信')

    def select_ct(self):
        if self.radioButton_ct.isChecked():
            self.window_info = setfocus.change_fs('财通')

    def select_tdx(self):
        if self.radioButton_tdx.isChecked():
            self.window_info = setfocus.change_fs('通达')

    def ask5(self):
        setfocus.open_code('.+5', self.window_info)

    def ask4(self):
        setfocus.open_code('.+4', self.window_info)

    def ask3(self):
        setfocus.open_code('.+3', self.window_info)

    def ask2(self):
        setfocus.open_code('.+2', self.window_info)

    def ask1(self):
        setfocus.open_code('.+1', self.window_info)

    def bid1(self):
        setfocus.open_code('.-1', self.window_info)

    def bid2(self):
        setfocus.open_code('.-2', self.window_info)

    def bid3(self):
        setfocus.open_code('.-3', self.window_info)

    def bid4(self):
        setfocus.open_code('.-4', self.window_info)

    def bid5(self):
        setfocus.open_code('.-5', self.window_info)


if __name__ == '__main__':
    manager = Manager()
    codes = manager.list()
    p = multiprocessing.Process(target=backend.mainloop, args=(codes,))
    p.start()
    app = QApplication(sys.argv)
    main_ui = MainUi()
    main_ui.show()
    app.exec_()

