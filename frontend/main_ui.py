"""
@ File:     main_ui.py.py
@ Author:   pleiadesian
@ Datetime: 2020-02-02 11:02
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from frontend import main


class MainUi(QMainWindow, main.Ui_Dialog):
    def __init__(self):
        super(MainUi, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_ui = MainUi()
    main_ui.show()
    app.exec_()
