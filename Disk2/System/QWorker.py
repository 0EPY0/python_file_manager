#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from QFileManager import myWindow
import socket


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setFixedSize(700, 550)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.labelData = QtWidgets.QLabel(self.centralwidget)
        self.labelData.setGeometry(QtCore.QRect(10, 10, 150, 20))
        self.labelData.setText("Список процессов:")
        self.info = QtWidgets.QTextEdit(self.centralwidget)
        self.info.setGeometry(QtCore.QRect(10, 40, 680, 150))
        self.info.setReadOnly(True)
        self.labelInput = QtWidgets.QLabel(self.centralwidget)
        self.labelInput.setGeometry(QtCore.QRect(10, 200, 45, 15))
        self.labelInput.setText("Ввод:")
        self.input = QtWidgets.QLineEdit(self.centralwidget)
        self.input.setGeometry(QtCore.QRect(10, 220, 680, 20))
        self.labelOutput = QtWidgets.QLabel(self.centralwidget)
        self.labelOutput.setGeometry(QtCore.QRect(10, 310, 45, 15))
        self.labelOutput.setText("Вывод:")
        self.output = QtWidgets.QTextEdit(self.centralwidget)
        self.output.setGeometry(QtCore.QRect(10, 330, 680, 150))
        self.output.setReadOnly(True)
        self.btnLocalData = QtWidgets.QPushButton(self.centralwidget)
        self.btnLocalData.setGeometry(QtCore.QRect(615, 10, 75, 20))
        self.btnLocalData.setText("Вывести")
        self.btnerr = QtWidgets.QPushButton(self.centralwidget)
        self.btnerr.setGeometry(QtCore.QRect(10, 250, 90, 40))
        self.btnerr.setText("Вывести\nстр ошибки")
        self.btnCPU = QtWidgets.QPushButton(self.centralwidget)
        self.btnCPU.setGeometry(QtCore.QRect(600, 250, 90, 40))
        self.btnCPU.setText("Загрузка\nЦП")
        self.labelPrior = QtWidgets.QLabel(self.centralwidget)
        self.labelPrior.setGeometry(QtCore.QRect(612, 290, 90, 15))
        self.labelPrior.setText("   (NAME)")
        self.btnExit = QtWidgets.QPushButton(self.centralwidget)
        self.btnExit.setGeometry(QtCore.QRect(320, 490, 60, 25))
        self.btnExit.setText("Выйти")
        self.btnPid = QtWidgets.QPushButton(self.centralwidget)
        self.btnPid.setGeometry(QtCore.QRect(310, 250, 90, 40))
        self.btnPid.setText("Дочерние\nпроцессы")
        self.labelPrior = QtWidgets.QLabel(self.centralwidget)
        self.labelPrior.setGeometry(QtCore.QRect(330, 290, 50, 15))
        self.labelPrior.setText("   (PID)")
        self.btnData = QtWidgets.QPushButton(self.centralwidget)
        self.btnData.setGeometry(QtCore.QRect(125, 10, 75, 20))
        self.btnData.setText("Вывести")
        self.labelLocalData = QtWidgets.QLabel(self.centralwidget)
        self.labelLocalData.setGeometry(QtCore.QRect(360, 10, 250, 20))
        self.labelLocalData.setText("Список процессов файлового менеджера:")
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("Задание по варианту")

        self.btnExit.clicked.connect(self.close)
        self.btnData.clicked.connect(self.processes)
        self.btnLocalData.clicked.connect(self.local_processes)
        self.btnerr.clicked.connect(self.error)
        self.btnPid.clicked.connect(self.PID)
        self.btnCPU.clicked.connect(self.cpu)

        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.update_status)
        self.timer.start()

    def processes(self):
        try:
            self.output.clear()
            myWindow.processes(self)
            client_socket, client_address = server.accept()
            data = client_socket.recv(s)
            data = data.decode()
            self.info.append(data)
        except:
            self.info.append("Ошибка")

    def local_processes(self):
        try:
            self.output.clear()
            myWindow.local_processes(self)
            client_socket, client_address = server.accept()
            data = client_socket.recv(s)
            data = data.decode()
            self.info.append(data)
        except:
            self.info.append("Ошибка")

    def update_status(self):
        myWindow.update_status(self)
        client_socket, client_address = server.accept()
        data = client_socket.recv(s)
        data = data.decode()
        self.statusBar().showMessage(data, 0)
        self.statusBar().setSizeGripEnabled(False)

    def PID(self):
        try:
            self.output.clear()
            myWindow.PID(self)
            client_socket, client_address = server.accept()
            data = client_socket.recv(s)
            data = data.decode()
            self.output.append(data)
        except:
            self.output.append("PID не введено")

    def error(self):
        try:
            myWindow.error(self)
            client_socket, client_address = server.accept()
            data = client_socket.recv(s)
            data = data.decode()
            self.output.append(data)

        except:
            pass

    def cpu(self):
        try:
            myWindow.cpu(self)
            client_socket, client_address = server.accept()
            data = client_socket.recv(s)
            data = data.decode()
            self.output.clear()
            if data:
                self.output.append(data)
            else:
                self.output.append("Ну ты шутник, я не могу")

        except:
            self.output.append("Ошибка")


class Variant(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("images/gears.png"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Variant()
    s = 10 ** 8
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 6500))
    server.listen()
    w.show()
    sys.exit(app.exec_())
