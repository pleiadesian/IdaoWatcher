"""
@ File:     main_ui.py.py
@ Author:   pleiadesian
@ Datetime: 2020-02-02 11:02
"""
import sys
import time
import multiprocessing
import main as backend
from random import randint
from multiprocessing import Value, Manager
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from frontend import main as frontend


class MainUi(QMainWindow, frontend.Ui_Dialog):
    def __init__(self):
        super(MainUi, self).__init__()
        self.setupUi(self)


def start_ui(codes):
    # main_ui = MainUi()
    # main_ui.show()
    while True:
        print(codes)
        time.sleep(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_ui = MainUi()
    main_ui.show()
    app.exec_()
