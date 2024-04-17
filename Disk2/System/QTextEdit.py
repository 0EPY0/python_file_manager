import sys

from PyQt5.QtCore import QFile, QFileInfo, QPoint, QSettings, QSize,\
                         Qt, QTextStream, QStandardPaths
from PyQt5.QtGui import QIcon, QKeySequence, QTextCursor
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMainWindow,\
                            QMessageBox, QTextEdit, QPushButton,\
                            QLineEdit, QInputDialog, QDialog
from PyQt5 import QtPrintSupport


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setStyleSheet(myStyleSheet(self))
        self.MaxRecentFiles = 5
        self.windowList = []
        self.recentFileActs = []
        self.curFile = ''
        self.setAcceptDrops(True)
        self.settings = QSettings("QTextEdit", "QTextEdit")
        self.myeditor = QTextEdit()
        self.myeditor.setAcceptRichText(False)
        self.myeditor.setUndoRedoEnabled(True)
        self.myeditor.setStyleSheet(myStyleSheet(self))
        self.myeditor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.myeditor.customContextMenuRequested.connect(self.contextMenuRequested)

        self.createActions()
        self.createToolBars()
        self.createMenus()
        self.createStatusBar()

        self.setWindowIcon(QIcon("images/word.png"))

        self.readSettings()
        self.myeditor.document().contentsChanged.connect(self.documentWasModified)
        self.setCurrentFile('')
        self.setCentralWidget(self.myeditor)
        self.myeditor.setFocus()

    def closeEvent(self, event):
        try:
            if self.maybeSave():
                self.writeSettings()
                event.accept()
            else:
                event.ignore()
        except:
            pass

    def newFile(self):
        try:
            if self.maybeSave():
                self.myeditor.clear()
                self.setCurrentFile('')
        except:
            pass

    def open(self):
        try:
            if self.maybeSave():
                documents = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
                fileName, _ = QFileDialog.getOpenFileName(self, "Открыть файл", documents,
                                                          "Text Files (*.txt *.csv *.sh *.py) ;; all Files (*.*)")
                if fileName:
                    self.loadFile(fileName)
                else:
                    self.statusBar().showMessage("Не удалось открыть файл", 3000)
        except:
            pass

    def save(self):
        try:
            if not self.myeditor.toPlainText() == "":
                if self.myeditor.document().isModified():
                    if self.curFile:
                        return self.saveFile(self.curFile)
                    else:
                        return self.saveAs()
                else:
                    self.statusBar().showMessage("Файл " + self.curFile + " успешно сохранен", 3000)
            else:
                self.statusBar().showMessage("Файл пуст")
        except:
            pass

    def saveAs(self):
        try:
            if not self.myeditor.toPlainText() == "":
                if self.curFile:
                    fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить как...",
                                                              self.curFile,
                                                              "Text Files (*.txt)")
                else:
                    documents = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
                    fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить как...",
                                                              documents + "/newDocument.txt",
                                                              "Text Files (*.txt)")
                if fileName:
                    return self.saveFile(fileName)
                return False
            else:
                self.statusBar().showMessage("Файл пуст")
        except:
            pass

    def contextMenuRequested(self, point):
        try:
            cmenu = self.myeditor.createStandardContextMenu()
            if not self.myeditor.textCursor().selectedText() == "":
                cmenu.addSeparator()
                cmenu.addAction("Заменить все найденые", self.replaceThis)
            cmenu.exec_(self.myeditor.mapToGlobal(point))
        except:
            pass

    def replaceThis(self):
        try:
            if not self.myeditor.textCursor().selectedText() == "":
                rtext = self.myeditor.textCursor().selectedText()
                dlg = QInputDialog(self, Qt.Dialog)
                dlg.setOkButtonText("Заменить")
                text = dlg.getText(self, "Заменить", "заменить " + rtext + " на:", QLineEdit.Normal, "")
                oldtext = self.myeditor.document().toPlainText()
                if not (text[0] == ""):
                    newtext = oldtext.replace(rtext, text[0])
                    self.myeditor.setPlainText(newtext)
                    self.myeditor.document().setModified(True)
        except:
            pass

    def documentWasModified(self):
        try:
            self.setWindowModified(self.myeditor.document().isModified())
        except:
            pass

    def createActions(self):
        self.newAct = QAction("Новый документ", self, shortcut=QKeySequence.New,
                              statusTip="Новый документ", triggered=self.newFile)
        self.openAct = QAction("Открыть", self, shortcut=QKeySequence.Open,
                               statusTip="Открыть", triggered=self.open)
        self.saveAct = QAction("Сохранить", self, shortcut=QKeySequence.Save,
                               statusTip="Сохранить", triggered=self.save)
        self.saveAsAct = QAction("Сохранить как...", self, shortcut=QKeySequence.SaveAs,
                                 statusTip="Сохранить как...", triggered=self.saveAs)
        self.exitAct = QAction("Выйти", self, shortcut="Ctrl+Q",
                               statusTip="Выйти", triggered=self.close)
        self.cutAct = QAction("Вырезать", self, shortcut=QKeySequence.Cut,
                              statusTip="Вырезать", triggered=self.myeditor.cut)
        self.copyAct = QAction("Копировать", self, shortcut=QKeySequence.Copy,
                               statusTip="Копировать", triggered=self.myeditor.copy)
        self.pasteAct = QAction("Вставить", self, shortcut=QKeySequence.Paste,
                                statusTip= "Вставить", triggered=self.myeditor.paste)
        self.undoAct = QAction("Назад", self, shortcut=QKeySequence.Undo,
                               statusTip="Назад", triggered=self.myeditor.undo)
        self.redoAct = QAction("Вперед", self, shortcut=QKeySequence.Redo,
                               statusTip="Вперед", triggered=self.myeditor.redo)

        self.repAllAct = QPushButton("Заменить все")
        self.repAllAct.setFixedWidth(100)
        self.repAllAct.setStatusTip("Заменить все")
        self.repAllAct.clicked.connect(self.replaceAll)

        self.cutAct.setEnabled(False)
        self.copyAct.setEnabled(False)
        self.myeditor.copyAvailable.connect(self.cutAct.setEnabled)
        self.myeditor.copyAvailable.connect(self.copyAct.setEnabled)
        self.undoAct.setEnabled(False)
        self.redoAct.setEnabled(False)
        self.myeditor.undoAvailable.connect(self.undoAct.setEnabled)
        self.myeditor.redoAvailable.connect(self.redoAct.setEnabled)

        self.printPreviewAct = QAction("Предпросмотр печати", self, shortcut=QKeySequence.Print,
                                       statusTip="Предпросмотр печати", triggered=self.handlePrintPreview)
        self.printAct = QAction("Печать", self, shortcut=QKeySequence.Print,
                                statusTip="Печатать документ", triggered=self.handlePrint)

        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(QAction(self, visible=False, triggered=self.openRecentFile))

    def findText(self):
        try:
            word = self.findfield.text()
            if self.myeditor.find(word):
                self.statusBar().showMessage("Найдено " + word + "", 2000)
            else:
                self.myeditor.moveCursor(QTextCursor.Start)
                if self.myeditor.find(word):
                    return
                else:
                     self.statusBar().showMessage("Не найдено", 3000)
        except:
            pass

    def replaceAll(self):
        try:
            oldtext = self.findfield.text()
            newtext = self.replacefield.text()
            if not oldtext == "":
                h = self.myeditor.toHtml().replace(oldtext, newtext)
                self.myeditor.setText(h)
                self.myeditor.document().setModified(True)
                self.statusBar().showMessage("Все файлы заменены", 3000)
            else:
                self.statusBar().showMessage("Нечего заменить", 3000)
        except:
            pass

    def replaceOne(self):
        try:
            oldtext = self.findfield.text()
            newtext = self.replacefield.text()
            if not oldtext == "":
                h = self.myeditor.toHtml().replace(oldtext, newtext, 1)
                self.myeditor.setText(h)
                self.myeditor.document().setModified(True)
                self.statusBar().showMessage("Заменен", 3000)
            else:
                self.statusBar().showMessage("Нечего заменить", 3000)
        except:
            pass

    def openRecentFile(self):
        try:
            action = self.sender()
            if action:
                if self.maybeSave():
                    self.loadFile(action.data())
        except:
            pass

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&Файл")
        self.separatorAct = self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        for i in range(self.MaxRecentFiles):
            self.fileMenu.addAction(self.recentFileActs[i])
        self.updateRecentFileActions()
        self.fileMenu.addSeparator()
        self.clearRecentAct = QAction("Очистить недавние", self, triggered=self.clearRecentFiles)
        self.fileMenu.addAction(self.clearRecentAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.editMenu = self.menuBar().addMenu("&Правка")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.menuBar().addSeparator()

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("Файл")
        self.fileToolBar.setIconSize(QSize(16, 16))
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.saveAsAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.printPreviewAct)
        self.fileToolBar.addAction(self.printAct)
        self.fileToolBar.setStyleSheet("QToolBar { border: 0px }")
        self.fileToolBar.setMovable(False)
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.editToolBar = self.addToolBar("Правка")
        self.editToolBar.setIconSize(QSize(16, 16))
        self.editToolBar.addAction(self.undoAct)
        self.editToolBar.addAction(self.redoAct)
        self.editToolBar.addSeparator()
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)
        self.editToolBar.setMovable(False)
        self.editToolBar.setStyleSheet("QToolBar { border: 0px }")

        self.addToolBarBreak()
        self.findToolBar = self.addToolBar("")
        self.findToolBar.setIconSize(QSize(16, 16))
        self.findfield = QLineEdit()
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(200)
        self.findfield.setPlaceholderText("Найти")
        self.findfield.setStatusTip("Нажмите ENTER для поиска")
        self.findfield.setText("")
        self.findfield.returnPressed.connect(self.findText)
        self.findToolBar.addWidget(self.findfield)
        self.replacefield = QLineEdit()
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(200)
        self.replacefield.setPlaceholderText("Заменить на")
        self.replacefield.setStatusTip("Нажмите ENTER для замены")
        self.replacefield.returnPressed.connect(self.replaceOne)
        self.findToolBar.addSeparator()
        self.findToolBar.addWidget(self.replacefield)
        self.findToolBar.addSeparator()
        self.findToolBar.addWidget(self.repAllAct)
        self.findToolBar.setMovable(False)
        self.findToolBar.setStyleSheet("QToolBar { border: 0px }")

    def createStatusBar(self):
        try:
            self.statusBar().setStyleSheet(myStyleSheet(self))
        except:
            pass

    def readSettings(self):
        try:
            pos = self.settings.value("pos", QPoint(200, 200))
            size = self.settings.value("size", QSize(400, 400))
            self.resize(size)
            self.move(pos)
        except:
            pass

    def writeSettings(self):
        try:
            self.settings.setValue("pos", self.pos())
            self.settings.setValue("size", self.size())
        except:
            pass

    def maybeSave(self):
        try:
            if self.myeditor.document().isModified():
                ret = QMessageBox.warning(self, "Сообщение",
                                          "Документ изменён\nСохранить изменения?",
                                           QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                           defaultButton=QMessageBox.Save)
                if ret == QMessageBox.Save:
                    return self.save()
                if ret == QMessageBox.Cancel:
                    return False
            return True
        except:
            pass

    def loadFile(self, fileName):
        try:
            file = QFile(fileName)
            if not file.open(QFile.ReadOnly | QFile.Text):
                QMessageBox.warning(self, "Сообщение",
                                    "Невозможно чтение файла %s:\n%s." % (fileName, file.errorString()))
                return
            infile = QTextStream(file)
            infile.setCodec("UTF-8")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.myeditor.setPlainText(infile.readAll())
            QApplication.restoreOverrideCursor()

            self.setCurrentFile(fileName)
            self.statusBar().showMessage("Файл " + fileName + " загружен", 3000)
        except:
            pass

    def saveFile(self, fileName):
        try:
            file = QFile(fileName)
            if not file.open(QFile.WriteOnly | QFile.Text):
                QMessageBox.warning(self, "Сообщение",
                                    "Невозможно записать в файл %s:\n%s." % (fileName, file.errorString()))
                return False
            outfile = QTextStream(file)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            outfile << self.myeditor.toPlainText()
            QApplication.restoreOverrideCursor()

            self.setCurrentFile(fileName)
            self.statusBar().showMessage("Файл " + fileName + " сохранён", 3000)
            return True
        except:
            pass

    def setCurrentFile(self, fileName):
        try:
            self.curFile = fileName
            self.myeditor.document().setModified(False)
            self.setWindowModified(False)
            if self.curFile:
                self.setWindowTitle(self.strippedName(self.curFile) + "[*]")
            else:
                self.setWindowTitle('Новый.txt' + "[*]")

            files = self.settings.value('recentFileList', [])
            if not files == "":
                try:
                    files.remove(fileName)
                except ValueError:
                    pass
                if fileName:
                    files.insert(0, fileName)
                    del files[self.MaxRecentFiles:]
                    self.settings.setValue('recentFileList', files)
                    self.updateRecentFileActions()
        except:
            pass

    def updateRecentFileActions(self):
        try:
            files = self.settings.value('recentFileList', [])
            numRecentFiles = min(len(files), self.MaxRecentFiles)
            for i in range(numRecentFiles):
                text = "&%d %s" % (i + 1, self.strippedName(files[i]))
                self.recentFileActs[i].setText(text)
                self.recentFileActs[i].setData(files[i])
                self.recentFileActs[i].setVisible(True)

            for j in range(numRecentFiles, self.MaxRecentFiles):
                self.recentFileActs[j].setVisible(False)

            self.separatorAct.setVisible((numRecentFiles > 0))
        except:
            pass

    def clearRecentFiles(self):
        try:
            self.settings.clear()
            self.updateRecentFileActions()
        except:
            pass

    def strippedName(self, fullFileName):
        try:
            return QFileInfo(fullFileName).fileName()
        except:
            pass

    def msgbox(self, message):
        try:
            QMessageBox.warning(self, "Сообщение", message)
        except:
            pass

    def handlePrint(self):
        try:
            if self.myeditor.toPlainText() == "":
                self.statusBar().showMessage("Нет текста для печати")
                self.msgbox("Нет текста для печати")
            else:
                dialog = QtPrintSupport.QPrintDialog()
                if dialog.exec_() == QDialog.Accepted:
                    self.handlePaintRequest(dialog.printer())
                    self.statusBar().showMessage("Документ напечатан")
        except:
            pass

    def handlePrintPreview(self):
        try:
            if self.myeditor.toPlainText() == "":
                self.statusBar().showMessage("Нет текста для предварительного просмотра")
                self.msgbox("Нет текста для превью")
            else:
                dialog = QtPrintSupport.QPrintPreviewDialog()
                dialog.setGeometry(10, 0, self.width() - 60, self.height() - 60)
                dialog.paintRequested.connect(self.handlePaintRequest)
                dialog.exec_()
                self.statusBar().showMessage("Предварительный просмотр закрыт")
        except:
            pass

    def handlePaintRequest(self, printer):
        try:
            printer.setDocName(self.curFile)
            document = self.myeditor.document()
            document.print_(printer)
        except:
            pass

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()
        except:
            pass

    def dropEvent(self, event):
        try:
            f = str(event.mimeData().urls()[0].toLocalFile())
            self.loadFile(f)
        except:
            pass


def myStyleSheet(self):
    return """
QTextEdit
    {
        background: #eeeeec;
        color: #202020;
    }
QStatusBar
    {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E1E1E1, stop: 0.4 #e5e5e5, stop: 0.5 #e9e9e9,stop: 1.0 #d2d2d2);
        font-size: 8pt;
        color: #555753;
    }
QMenuBar
    {
        background: transparent;
        border: 0px;
    }
QToolBar
    {
        background: transparent;
        border: 0px;
    }   
QMainWindow
    {   
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E1E1E1, stop: 0.4 #DDDDDD, stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    }
QLineEdit
    {   
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E1E1E1, stop: 0.4 #e5e5e5, stop: 0.5 #e9e9e9, stop: 1.0 #d2d2d2);
    }
QPushButton
    {
        background: #D8D8D8;
    }
QLCDNumber
    {
        color: #204a87;
    }
    """
