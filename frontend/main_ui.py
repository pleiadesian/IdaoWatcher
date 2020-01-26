"""
@ File:     main_ui.py
@ Author:   pleiadesian
@ Datetime: 2020-01-26 17:07
"""
import tushare as ts
import sys
import winsound
from frontend import watch_limit_warn, setfocus, watch_limit_main
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PyQt5.QtCore import QTimer, Qt
import main


INTERVAL = 3000
BUTTON_X = 60
BUTTON_NONE_X = -200


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
            # TODO: fetch codes from main.mainloop
            pass

    def resetcode(self):
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

