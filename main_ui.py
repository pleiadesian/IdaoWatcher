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
BUTTON_X = 60
BUTTON_NONE_X = -200

manager = Manager()
codes = manager.list()


class MainUi(QMainWindow, frontend.Ui_Dialog):
    def __init__(self):
        super(MainUi, self).__init__()
        self.setupUi(self)

        self.button_list = [self.pushButton_0, self.pushButton_1, self.pushButton_2, self.pushButton_3,
                            self.pushButton_4, self.pushButton_5, self.pushButton_6, self.pushButton_7,
                            self.pushButton_8, self.pushButton_9, self.pushButton_10, self.pushButton_11]
        self.code_list = [''] * 10
        for button in self.button_list:
            button.move(BUTTON_NONE_X, button.y())
        self.window_info = setfocus.init_fs()
        self.pushButton_0.clicked.connect(lambda: setfocus.open_code(self.code_list[0], self.window_info))
        self.pushButton_1.clicked.connect(lambda: setfocus.open_code(self.code_list[1], self.window_info))
        self.pushButton_2.clicked.connect(lambda: setfocus.open_code(self.code_list[2], self.window_info))
        self.pushButton_3.clicked.connect(lambda: setfocus.open_code(self.code_list[3], self.window_info))
        self.pushButton_4.clicked.connect(lambda: setfocus.open_code(self.code_list[4], self.window_info))
        self.pushButton_5.clicked.connect(lambda: setfocus.open_code(self.code_list[5], self.window_info))
        self.pushButton_6.clicked.connect(lambda: setfocus.open_code(self.code_list[6], self.window_info))
        self.pushButton_7.clicked.connect(lambda: setfocus.open_code(self.code_list[7], self.window_info))
        self.pushButton_8.clicked.connect(lambda: setfocus.open_code(self.code_list[8], self.window_info))
        self.pushButton_9.clicked.connect(lambda: setfocus.open_code(self.code_list[9], self.window_info))
        self.pushButton_10.clicked.connect(lambda: setfocus.open_code(self.code_list[10], self.window_info))
        self.pushButton_11.clicked.connect(lambda: setfocus.open_code(self.code_list[11], self.window_info))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkall)
        self.timer.start(INTERVAL)

    def checkall(self):
        i = 0
        for button, code in zip(self.button_list, codes):
            button.setText(code)
            self.code_list[i] = code
            button.move(BUTTON_X, button.y())
        alert_codes = len(codes)
        for button in self.button_list:
            alert_codes -= 1
            if alert_codes < 0:
                button.setText('None')
                button.move(BUTTON_NONE_X, button.y())


if __name__ == '__main__':
    p = multiprocessing.Process(target=backend.mainloop, args=(codes,))
    p.start()
    app = QApplication(sys.argv)
    main_ui = MainUi()
    main_ui.show()
    app.exec_()

