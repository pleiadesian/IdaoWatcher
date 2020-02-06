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
INTERVAL_CLEAR = 3000
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
        self.clear_signals = [False] * 12
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

    def click_code(self, code_slot):
        setfocus.open_code(self.code_list[code_slot], self.window_info)
        self.clear_signals[code_slot] = True

    def clear_code(self):
        i = 0
        for signal in self.clear_signals:
            if signal:
                self.button_list[i].setText('None')
                self.button_list[i].move(BUTTON_NONE_X, self.button_list[i].y())
                self.code_list[i] = ''
                self.clear_signals[i] = False
            i += 1

    def checkall(self):
        new_codes = list(set(codes) - set(self.code_list))
        # TODO: get code in code_list except ''
        displaying_codes = [code for code in self.code_list if code != '']
        display_codes = new_codes + displaying_codes + self.spilled_codes
        if len(display_codes) > 12:
            self.spilled_codes = display_codes[12:]
            display_codes = display_codes[:12]
        i = 0
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


if __name__ == '__main__':
    manager = Manager()
    codes = manager.list()
    p = multiprocessing.Process(target=backend.mainloop, args=(codes,))
    p.start()
    app = QApplication(sys.argv)
    main_ui = MainUi()
    main_ui.show()
    app.exec_()

