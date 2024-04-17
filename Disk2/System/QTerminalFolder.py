import shutil
import sys
import os
import getpass
import socket
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QMainWindow, QAction
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QProcess, QSettings, QEvent, QPoint, QSize


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setAcceptDrops(True)
        self.shellWin = PlainTextEdit()
        self.setCentralWidget(self.shellWin)
        self.resize(700, 600)
        self.setWindowTitle("Командная строка")
        self.setWindowIcon(QIcon("images/command.png"))
        self.settings = QSettings("QTerminal", "QTerminal")
        self.readSettings()

    def closeEvent(self, e):
        try:
            self.writeSettings()
        except:
            pass

    def readSettings(self):
        try:
            if self.settings.contains("commands"):
                self.shellWin.commands = self.settings.value("commands")
            if self.settings.contains("pos"):
                pos = self.settings.value("pos", QPoint(200, 200))
                self.move(pos)
            if self.settings.contains("size"):
                size = self.settings.value("size", QSize(400, 400))
                self.resize(size)
        except:
            pass

    def writeSettings(self):
        try:
            self.settings.setValue("commands", self.shellWin.commands)
            self.settings.setValue("pos", self.pos())
            self.settings.setValue("size", self.size())
        except:
            pass


class PlainTextEdit(QPlainTextEdit):
    commandSignal = pyqtSignal(str)
    startDir = ""

    def __init__(self):
        super(PlainTextEdit, self).__init__()
        self.installEventFilter(self)
        self.setAcceptDrops(True)
        QApplication.setCursorFlashTime(1000)
        self.process = QProcess()
        self.workingDirectory = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.commands = []
        self.tracker = 0
        self.setStyleSheet("QPlainTextEdit{background-color: #212121; color: #f3f3f3; padding: 8;}")
        self.verticalScrollBar().setStyleSheet("background-color: #212121;")
        self.text = None
        self.setFont(QFont("Noto Sans Mono", 8))
        self.previousCommandLength = 0

        self.copySelectedTextAction = QAction("Копировать", shortcut="Shift+Ctrl+C", triggered=self.copyText)
        self.addAction(self.copySelectedTextAction)
        self.pasteTextAction = QAction("Вставить", shortcut="Shift+Ctrl+V", triggered=self.pasteText)
        self.addAction(self.pasteTextAction)
        self.startDir = "C:\\Disk"
        os.chdir(self.startDir)
        self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) + ":" + str(os.getcwd()) + " ")
        self.appendPlainText(self.name)

    def copyText(self):
        try:
            self.copy()
        except:
            pass

    def pasteText(self):
        try:
            self.paste()
        except:
            pass

    def eventFilter(self, source, event):
        try:
            if event.type() == QEvent.DragEnter:
                event.accept()
                return True
            elif event.type() == QEvent.Drop:
                self.setDropEvent(event)
                return True
            else:
                return False
        except:
            pass

    def setDropEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                f = str(event.mimeData().urls()[0].toLocalFile())
                self.insertPlainText(f)
                event.accept()
            elif event.mimeData().hasText():
                ft = event.mimeData().text()
                self.insertPlainText(ft)
                event.accept()
            else:
                event.ignore()
        except:
            pass

    def keyPressEvent(self, e):
        try:
            cursor = self.textCursor()

            if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_F:
                self.process.kill()
                self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) + ":" + str(os.getcwd()) + " ")
                self.appendPlainText("Процесс отменен")
                self.appendPlainText(self.name)
                self.textCursor().movePosition(QTextCursor.End)
                return

            if e.key() == Qt.Key_Return:
                text = self.textCursor().block().text()
                if text == self.name + text.replace(self.name, "") and text.replace(self.name, "") != "":
                    self.commands.append(text.replace(self.name, ""))
                self.handle(text)
                self.commandSignal.emit(text)
                self.appendPlainText(self.name)
                return

            if e.key() == Qt.Key_Up:
                try:
                    if self.tracker != 0:
                        cursor.select(QTextCursor.BlockUnderCursor)
                        cursor.removeSelectedText()
                        self.appendPlainText(self.name)
                    self.insertPlainText(self.commands[self.tracker])
                    self.tracker -= 1
                except IndexError:
                    self.tracker = 0
                return

            if e.key() == Qt.Key_Down:
                try:
                    cursor.select(QTextCursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    self.appendPlainText(self.name)
                    self.insertPlainText(self.commands[self.tracker])
                    self.tracker += 1
                except IndexError:
                    self.tracker = 0

            super().keyPressEvent(e)
            e.accept()
        except:
            pass

    def ispressed(self):
        try:
            return self.pressed
        except:
            pass

    def onReadyReadStandardError(self):
        try:
            self.error = self.process.readAllStandardError().data().decode()
            self.appendPlainText(self.error.strip("\n"))
        except:
            pass

    def onReadyReadStandardOutput(self):
        try:
            self.result = self.process.readAllStandardOutput().data().decode()
            self.appendPlainText(self.result.strip("\n"))
            self.state = self.process.state()
        except:
            pass

    def run(self, command):
        try:
            if not command == "ls":
                if self.process.state() != 2:
                    self.process.start(command)
                    if not self.process.exitStatus() != 0:
                        self.textCursor().movePosition(QTextCursor.End)
                        self.name = (str(getpass.getuser()) + "@" +
                                     str(socket.gethostname()) + ":" + str(os.getcwd()) + " ")
                        self.appendPlainText(self.name)
            else:
                if self.process.state() != 2:
                    self.process.start(command)
                    self.process.waitForFinished()
        except:
            pass

    def handle(self, command):
        try:
            real_command = command.replace(self.name, "")
            files = []

            for i in range(len(os.listdir(self.workingDirectory))):
                x = str(self.workingDirectory) + "\\" + str(os.listdir(self.workingDirectory)[i])
                files.append(x)

            if command == "True":
                if self.process.state() == 2:
                    self.process.kill()
                    self.appendPlainText("Процесс выполнения прерван, нажмите ENTER")

            if real_command != "":
                command_list = real_command.split()
            else:
                command_list = None

            if real_command == "cls":
                self.clear()

            elif command_list is not None and command_list[0] == "echo":
                self.appendPlainText(" ".join(command_list[1:]))

            elif command_list is not None and command_list[0] == "cd":
                try:
                    if len(command_list) > 1:
                        os.chdir(" ".join(command_list[1:]))
                        self.name = (str(getpass.getuser()) + "@" +
                                     str(socket.gethostname()) + ":" + str(os.getcwd()) + " ")
                        self.textCursor().movePosition(QTextCursor.End)
                    elif len(command_list) == 1:
                        os.chdir(str(Path.home()))
                        self.name = (str(getpass.getuser()) + "@" +
                                     str(socket.gethostname()) + ":" + str(os.getcwd()) + " ")
                        self.textCursor().movePosition(QTextCursor.End)
                except FileNotFoundError as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "del":
                try:
                    if " ".join(command_list[1:]) in files or os.getcwd() == self.workingDirectory or " ".join(command_list[1:]) == "System":
                        self.appendPlainText("Ошибка: недостаточно прав")
                    else:
                        os.remove(" ".join(command_list[1:]))
                        self.appendPlainText(f"{' '.join(command_list[1:])} удален")
                except FileNotFoundError as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "rd":
                try:
                    if " ".join(command_list[1:]) in files or os.getcwd() == self.workingDirectory or " ".join(command_list[1:]) == "System":
                        self.appendPlainText("Ошибка: недостаточно прав!")
                    else:
                        if os.path.isdir(" ".join(command_list[1:])):
                            shutil.rmtree(" ".join(command_list[1:]))
                            self.appendPlainText(f"{' '.join(command_list[1:])} удален")
                        else:
                            self.appendPlainText("Ошибка: выбран не каталог!")
                except FileNotFoundError as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "dir":
                try:
                    if len(command_list) == 1:
                        dir = "\n".join(os.listdir(os.getcwd()))
                        self.appendPlainText("Файлы в указанной директории: \n" + dir)
                    else:
                        dir = "\n".join(os.listdir(" ".join(command_list[1:])))
                        self.appendPlainText("Файлы в указанной директории: \n" + dir)
                except FileNotFoundError as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "replace":
                try:
                    if " ".join(command_list[1:]) in files or os.getcwd() == self.workingDirectory:
                        self.appendPlainText("Ошибка: недостаточно прав!")

                    elif " ".join(command_list[1:]) in os.listdir(os.getcwd()):
                        self.appendPlainText("Ошибка: такой файл уже существует")
                    else:
                        file = open(" ".join(command_list[1:]), "w+")
                        file.close()
                        self.appendPlainText("Файл создан")
                except BaseException as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "mkdir":
                try:
                    if " ".join(command_list[1:]) in files or os.getcwd() == self.workingDirectory:
                        self.appendPlainText("Ошибка: недостаточно прав!")

                    elif " ".join(command_list[1:]) in os.listdir(os.getcwd()):
                        self.appendPlainText("Ошибка: такая директория уже существует")
                    else:
                        os.mkdir(" ".join(command_list[1:]))
                        self.appendPlainText("Каталог создан")
                except BaseException as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "start":
                try:
                    if " ".join(command_list[1:]) in files or os.getcwd() == self.workingDirectory:
                        self.appendPlainText("Ошибка: недостаточно прав!")
                    else:
                        os.startfile(" ".join(command_list[1:]))
                        self.appendPlainText("Файл запущен")
                except FileNotFoundError as E:
                    self.appendPlainText(str(E))

            elif command_list is not None and command_list[0] == "help":
                self.appendPlainText("echo -- вывод текста на экран консоли\n"
                                     "cd -- смена каталога\n"
                                     "cls -- очистка экрана в командной строке\n"
                                     "replace -- создание файла\n"
                                     "mkdir -- создание каталога\n"
                                     "del -- удаление файла\n"
                                     "rd -- удаление каталога\n"
                                     "dir -- отображение списка файлов и каталогов\n"
                                     "start -- запуск исполняемого файла\n"
                                     "help -- помощь\n")

            else:
                self.appendPlainText("Ошибка: Такой команды не существует!")
        except:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
