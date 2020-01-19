# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'watch_limit_main.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1186, 464)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(950, 80, 113, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 90, 911, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 5, 1001, 61))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(30, 150, 131, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_watch = QtWidgets.QLabel(self.centralwidget)
        self.label_watch.setGeometry(QtCore.QRect(180, 140, 961, 111))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_watch.setFont(font)
        self.label_watch.setWordWrap(True)
        self.label_watch.setObjectName("label_watch")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(460, 290, 181, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(1060, 80, 113, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1186, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(MainWindow.addcode)
        self.pushButton_2.clicked.connect(MainWindow.startrun)
        self.pushButton_3.clicked.connect(MainWindow.resetcode)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "确认"))
        self.label_2.setText(_translate("MainWindow", "输入您要监视的已涨停股票列表，每个股票代码之间用1个空格隔开（例如000001 000002 000003)"))
        self.label_3.setText(_translate("MainWindow", "正在监视："))
        self.label_watch.setText(_translate("MainWindow", "还未输入"))
        self.pushButton_2.setText(_translate("MainWindow", "开始运行"))
        self.pushButton_3.setText(_translate("MainWindow", "重置输入"))
