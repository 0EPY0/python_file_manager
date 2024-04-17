import datetime
import socket
import sys
import os
import errno
import time
from subprocess import Popen, PIPE
import psutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence, QCursor, QDesktopServices


import QTextEdit
import Qt5Player
import QAudioPlayer
import QImageViewer
import QWebViewer
from zipfile import ZipFile
import shutil
from threading import Thread
from multiprocessing import Process

import log


class helpWindow(QMainWindow):
    def __init__(self):
        super(helpWindow, self).__init__()
        self.setWindowIcon(QIcon("images/info.png"))
        self.helpText = """
        <p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
        <!--StartFragment-->
        <span style=" font-family:'Helvetica'; font-size:11pt; font-weight:600; text-decoration: underline; color:#2e3436;">
        Горячие клавиши:</span></p><br>
        <p>Копировать файл(ы) (Ctrl+C)<br>
        Вставить файл(ы) (Ctrl+V)<br>
        Вырезать файл(ы) (Ctrl+X)<br>
        Переместить файл(ы) в корзину(Del)<br>
        Удалить файл(ы) (Shift+Del)<br>
        Найти файл(ы) (Ctrl+F)<br>
        Переименовать файл (F2)<br>
        Открыть в TextEditor (F6)<br>
        Открыть терминал (F7)<br>
        Обновить (F5) <br>
        Справка (F1) <br>
        Назад (Backspace)<br>
        Диспетчер задач (Ctrl+Alt+F) <br>
        <!--EndFragment--></p>
        """

        self.helpViewer = QLabel(self.helpText, self)
        self.helpViewer.setAlignment(Qt.AlignLeft)

        self.btnAbout = QPushButton("Об авторе")
        self.btnAbout.setFixedWidth(80)
        self.btnAbout.clicked.connect(self.aboutApp)

        self.btnClose = QPushButton("Закрыть")
        self.btnClose.setFixedWidth(80)
        self.btnClose.clicked.connect(self.close)

        widget = QWidget(self)
        layout = QVBoxLayout(widget)

        layout.addWidget(self.helpViewer)
        layout.addStretch()
        layout.addWidget(self.btnAbout)
        layout.addWidget(self.btnClose)
        self.setCentralWidget(widget)

        self.setWindowTitle("Справка")

    def aboutApp(self):
        sysinfo = QSysInfo()
        myMachine = "Архитектура системы: " + sysinfo.currentCpuArchitecture() \
                    + "<br>" + sysinfo.prettyProductName() \
                    + "<br>" + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        title = "Об авторе"
        message = "Дисциплина: Операционные системы и оболочки<br>" \
                  "Разработано: Красильников А.А.<br>" \
                  "Группа: МОИС-01<br>" \
                  "Номера заданий: 26, 31, 37<br><br>" + myMachine
        self.infobox(title, message)

    def infobox(self, title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                    Qt.Dialog | Qt.NoDropShadowWindowHint).show()


class Exception(QMainWindow):
    def __init__(self):
        super(Exception, self).__init__()
        self.setWindowIcon(QIcon("images/error.png"))
        self.exceptText = """
        <span style=" font-family:'Helvetica'; font-size:11pt; font-weight:600; color:#2e3436;"> Системная ошибка</span>
        """
        self.exceptViewer = QLabel(self.exceptText, self)

        self.btnClose = QPushButton("Закрыть")
        self.btnClose.setFixedWidth(80)
        self.btnClose.clicked.connect(self.close)

        widget = QWidget(self)
        layout = QVBoxLayout(widget)

        layout.addWidget(self.exceptViewer, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.btnClose, alignment=Qt.AlignCenter)
        self.setCentralWidget(widget)

        self.setWindowTitle("Сообщение")


class myWindow(QMainWindow):
    def __init__(self):
        super(myWindow, self).__init__()

        docs = os.path.dirname(os.path.abspath(os.path.dirname(sys.argv[0])))

        self.setWindowTitle("FileManager")
        self.setWindowIcon(QIcon("images/folder.png"))

        self.settings = QSettings("QFileManager", "QFileManager")
        self.clip = QApplication.clipboard()
        self.isInEditMode = False

        self.treeview = QTreeView()
        self.listview = QTreeView()

        self.cut = False
        self.hiddenEnabled = False
        self.folder_copied = ""

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)

        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)

        wid = QWidget()
        wid.setLayout(hlay)
        self.setCentralWidget(wid)
        self.createStatusBar()
        self.resize(900, 500)

        self.copyPath = ""
        self.copyList = []
        self.copyListNew = ""

        self.createActions()

        self.findfield = QLineEdit()
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(320)
        self.findfield.setToolTip("Нажмите SHIFT+ENTER для перехода в директорию")
        self.findfield.setText("")
        self.findfield.returnPressed.connect(self.openDir)
        self.findfield.installEventFilter(self)

        self.tBar = self.addToolBar("Инструменты")
        self.tBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tBar.setMovable(False)
        self.tBar.setIconSize(QSize(20, 20))
        self.tBar.addAction(self.helpAction)
        self.tBar.addSeparator()
        self.tBar.addAction(self.btnHome)
        self.tBar.addSeparator()
        self.tBar.addAction(self.btnBack)
        self.tBar.addAction(self.btnUp)
        self.tBar.addWidget(self.findfield)
        self.tBar.addAction(self.findFilesAction)
        self.tBar.addSeparator()
        self.tBar.addAction(self.terminalAction)
        self.tBar.addAction(self.btnTasker)
        self.tBar.addAction(self.btnVar)
        self.tBar.addAction(self.btnLog)

        self.dirModel = QFileSystemModel()
        self.dirModel.setReadOnly(False)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives | QDir.AllEntries)
        self.dirModel.setRootPath(docs)
        self.dirModel.setResolveSymlinks(False)

        self.fileModel = QFileSystemModel()
        self.fileModel.setResolveSymlinks(False)
        self.fileModel.setReadOnly(False)
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.AllEntries)

        self.treeview.setModel(self.dirModel)
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)
        self.treeview.setRowHidden(0, self.treeview.selectionModel().currentIndex(), True)

        self.listview.setModel(self.fileModel)
        self.listview.setRootIsDecorated(False)

        self.listview.header().resizeSection(0, 320)
        self.listview.header().resizeSection(1, 80)
        self.listview.header().resizeSection(2, 80)
        self.listview.setSortingEnabled(True)
        self.treeview.setSortingEnabled(True)

        self.treeview.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        self.listview.doubleClicked.connect(self.list_doubleClicked)

        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setTreePosition(0)
        self.treeview.setUniformRowHeights(True)
        self.treeview.setExpandsOnDoubleClick(True)
        self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeview.setIndentation(12)
        self.treeview.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.sortByColumn(0, Qt.AscendingOrder)

        self.splitter.setSizes([20, 160])

        self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listview.setDragDropMode(QAbstractItemView.InternalMove)
        self.listview.setDragEnabled(True)
        self.listview.setAcceptDrops(True)
        self.listview.setDropIndicatorShown(True)
        self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.setIndentation(10)
        self.listview.sortByColumn(0, Qt.AscendingOrder)

        self.workingDirectory = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.workingDirectory = self.workingDirectory.replace("\\", "/")

        self.readSettings()
        self.enableHidden()
        self.getRowCount()

        self.List_New = []
        self.blacklist = []
        s = open("blackList.txt", "r").read()
        for p in s.split('\n'):
            self.blacklist.append(p)

    def getRowCount(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            path = QDir(self.dirModel.fileInfo(index).absoluteFilePath())
            count = len(path.entryList(QDir.Files))
            self.statusBar().showMessage("%s %s" % ("Файлов:", count), 0)
            return count
        except:
            pass

    def closeEvent(self, e):
        try:
            self.writeSettings()
        except:
            pass

    def readSettings(self):
        try:
            if self.settings.contains("pos"):
                pos = self.settings.value("pos", QPoint(200, 200))
                self.move(pos)
            else:
                self.move(0, 26)
            if self.settings.contains("size"):
                size = self.settings.value("size", QSize(800, 600))
                self.resize(size)
            else:
                self.resize(800, 600)
            if self.settings.contains("hiddenEnabled"):
                if self.settings.value("hiddenEnabled") == "false":
                    self.hiddenEnabled = True
                else:
                    self.hiddenEnabled = False
        except:
            pass

    def writeSettings(self):
        try:
            self.settings.setValue("pos", self.pos())
            self.settings.setValue("size", self.size())
            self.settings.setValue("hiddenEnabled", self.hiddenEnabled, )
        except:
            pass

    def enableHidden(self):
        try:
            if not self.hiddenEnabled:
                self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs | QDir.Files)
                self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs)
                self.hiddenEnabled = True
                self.hiddenAction.setChecked(True)
            else:
                self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
                self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
                self.hiddenEnabled = False
                self.hiddenAction.setChecked(False)
        except:
            pass

    def createActions(self):
        self.btnBack = QAction("Назад", triggered=self.goBack)
        self.btnBack.setIcon(QIcon("images/left-arrow.png"))
        self.btnUp = QAction("Вверх", triggered=self.goUp)
        self.btnUp.setIcon(QIcon("images/up-arrow.png"))
        self.btnHome = QAction("Домой", triggered=self.goHome)
        self.btnHome.setIcon(QIcon("images/home.png"))
        self.btnTasker = QAction("Диспетчер задач", triggered=self.startTasker)
        self.btnTasker.setIcon(QIcon("images/technical-support.png"))
        self.btnTasker.setShortcut(QKeySequence("Ctrl+Alt+F"))
        self.openAction = QAction("Открыть файл", triggered=self.openFile)
        self.openAction.setShortcut(QKeySequence(Qt.Key_Return))
        self.openAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.openAction)

        self.btnVar = QAction("Задание по варианту", triggered=self.openVar)
        self.btnVar.setIcon(QIcon("images/gears.png"))
        self.btnLog = QAction("Сохранить протокол", triggered=self.saveLog)

        self.openActionText = QAction("Открыть файл с помощью Texteditor", triggered=self.openFileText)
        self.openActionText.setIcon(QIcon("images/word.png"))
        self.openActionText.setShortcut(QKeySequence(Qt.Key_F6))
        self.openActionText.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.openActionText)

        self.renameAction = QAction("Переименовать файл", triggered=self.renameFile)
        self.renameAction.setShortcut(QKeySequence(Qt.Key_F2))
        self.renameAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.renameAction)
        self.treeview.addAction(self.renameAction)

        self.renameFolderAction = QAction("Переименовть директорию", triggered=self.renameFolder)
        self.treeview.addAction(self.renameFolderAction)

        self.copyAction = QAction("Копировать файл(ы)", triggered=self.copyFile)
        self.copyAction.setShortcut(QKeySequence("Ctrl+c"))
        self.copyAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.copyAction)

        self.copyFolderAction = QAction("Копировать директорию", triggered=self.copyFolder)
        self.treeview.addAction(self.copyFolderAction)

        self.pasteFolderAction = QAction("Вставить директорию", triggered=self.pasteFolder)
        self.treeview.addAction(self.pasteFolderAction)

        self.cutAction = QAction("Вырезать файл(ы)", triggered=self.cutFile)
        self.cutAction.setShortcut(QKeySequence("Ctrl+x"))
        self.cutAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.cutAction)

        self.pasteAction = QAction("Вставить файл(ы)", triggered=self.pasteFile)
        self.pasteAction.setShortcut(QKeySequence("Ctrl+v"))
        self.pasteAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.pasteAction)

        self.delAction = QAction("Удалить файл(ы)", triggered=self.deleteFile)
        self.delAction.setShortcut(QKeySequence("Shift+Del"))
        self.delAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.delAction)

        self.delFolderAction = QAction("Удалить директорию", triggered=self.deleteFolder)
        self.treeview.addAction(self.delFolderAction)

        self.delActionTrash = QAction("Переместить в корзину", triggered=self.deleteFileTrash)
        self.delActionTrash.setShortcut(QKeySequence("Del"))
        self.delActionTrash.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.delActionTrash)

        self.imageAction = QAction("Открыть в ImageViewer", triggered=self.showImage)
        self.imageAction.setIcon(QIcon("images/photoshop.png"))
        self.listview.addAction(self.imageAction)

        self.urlAction = QAction("Открыть в WebViewer", triggered=self.showURL)
        self.urlAction.setIcon(QIcon("images/microsoft.png"))
        self.listview.addAction(self.urlAction)

        self.findFilesAction = QAction("Поиск", triggered=self.findFiles)
        self.findFilesAction.setIcon(QIcon("images/search.png"))
        self.findFilesAction.setShortcut(QKeySequence("Ctrl+f"))
        self.findFilesAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.findFilesAction)

        self.zipAction = QAction("Добавить директорию в архив...", triggered=self.createZipFromFolder)
        self.zipAction.setIcon(QIcon("images/archive.png"))
        self.treeview.addAction(self.zipAction)

        self.zipFilesAction = QAction("Добавить файл(ы) в архив...", triggered=self.createZipFromFiles)
        self.zipFilesAction.setIcon(QIcon("images/archive.png"))
        self.listview.addAction(self.zipFilesAction)

        self.unzipHereAction = QAction("Разархивировать здесь...", triggered=self.unzipHere)
        self.unzipHereAction.setIcon(QIcon("images/archive.png"))
        self.listview.addAction(self.unzipHereAction)

        self.unzipToAction = QAction("Разархивировать в...", triggered=self.unzipTo)
        self.unzipToAction.setIcon(QIcon("images/archive.png"))
        self.listview.addAction(self.unzipToAction)

        self.playAction = QAction("Открыть в VideoPlayer", triggered=self.playMedia)
        self.playAction.setIcon(QIcon("images/youtube.png"))
        self.playAction.setShortcut(QKeySequence(Qt.Key_F3))
        self.playAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.playAction)

        self.playlistPlayerAction = QAction("Воспроизвести в AudioPlayer", triggered=self.playPlaylist)
        self.playlistPlayerAction.setIcon(QIcon("images/spotify.png"))
        self.listview.addAction(self.playlistPlayerAction)

        self.refreshAction = QAction("Обновить", triggered=self.refreshList, shortcut="F5")
        self.refreshAction.setIcon(QIcon("images/refresh.png"))
        self.refreshAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.refreshAction)

        self.hiddenAction = QAction("Показать скрытые файлы", triggered=self.enableHidden)
        self.hiddenAction.setShortcut(QKeySequence("Ctrl+h"))
        self.hiddenAction.setShortcutVisibleInContextMenu(True)
        self.hiddenAction.setCheckable(True)
        self.listview.addAction(self.hiddenAction)

        self.goBackAction = QAction("Обратно", triggered=self.goBack)
        self.goBackAction.setShortcut(QKeySequence(Qt.Key_Backspace))
        self.goBackAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.goBackAction)

        self.helpAction = QAction("Справка", triggered=self.showHelp)
        self.helpAction.setIcon(QIcon("images/info.png"))
        self.helpAction.setShortcut(QKeySequence(Qt.Key_F1))
        self.helpAction.setShortcutVisibleInContextMenu(True)
        self.listview.addAction(self.helpAction)

        self.terminalAction = QAction("Командная строка", triggered=self.startInTerminal)
        self.terminalAction.setIcon(QIcon("images/command.png"))
        self.terminalAction.setShortcut(QKeySequence(Qt.Key_F7))
        self.terminalAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.terminalAction)
        self.listview.addAction(self.terminalAction)

        self.createFolderAction = QAction("Создать новую директорию", triggered=self.createNewFolder)
        self.createFolderAction.setShortcut(QKeySequence("Shift+Ctrl+n"))
        self.createFolderAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.createFolderAction)

        self.createFileAction = QAction("Создать новый файл", triggered=self.createNewFile)
        self.createFileAction.setShortcut(QKeySequence("Shift+Ctrl+m"))
        self.createFileAction.setShortcutVisibleInContextMenu(True)
        self.treeview.addAction(self.createFileAction)

    def playPlaylist(self):
        try:
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath()
                self.player = QAudioPlayer.Player("")
                self.player.resize(500, 350)
                self.player.show()
                self.player.clearList()
                self.player.openOnStart(path)
                create = open("log.txt", "at")
                create.write("Open file: " + os.path.basename(path) + "\t" + " Open time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def showImage(self):
        try:
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath()
                self.win = QImageViewer.ImageViewer()
                self.win.show()
                self.win.filename = path
                self.win.loadFile(path)
                create = open("log.txt", "at")
                create.write("Open file: " + os.path.basename(path) + "\t" + " Open time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def checkIsApplication(self, path):
        try:
            case = [".htm", ".html", ".png", "jpg", ".jpeg", ".bmp", "tif", ".tiff",
                    ".pnm", ".svg", ".exif", ".gif", ".mp4", "mpg", ".m4a", ".mpeg", "avi",
                    ".mkv", ".webm", ".wav", ".ogg", ".flv ", ".vob", ".ogv", ".ts",
                    ".m2v", "m4v", "3gp", ".f4v", ".mp3", ".wav", ".zip", ".tar.gz", ".txt",
                    ".doc", ".docx", ".exe", ".lnk", ".bat"]
            flag = None
            for i in case:
                if i in path:
                    flag = 1
                    break
                else:
                    flag = 0
            if flag == 1:
                return True
            else:
                return False
        except:
            pass

    def startInTerminal(self):
        try:
            create = open("Protocol.txt", "at")
            create.write("Start process: " + "QTerminal.py" + "\t" + " Open time: "
                         + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
            create.close()
            self.terminal = QProcess(self)
            self.terminal.start("py", ['QTerminalFolder.py'])
        except:
            pass

    def createZipFromFolder(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).filePath()
            fname = self.dirModel.fileInfo(index).fileName()
            self.copyFile()
            target, _ = QFileDialog.getSaveFileName(self, "Сохранить как...",
                                                    path + "/" + fname, "zip files (*.zip)")
            if target != "":
                shutil.make_archive(target, "zip", path)
        except:
            pass

    def createZipFromFiles(self):
        try:
            if self.listview.selectionModel().hasSelection():
                index = self.treeview.selectionModel().currentIndex()
                path = self.dirModel.fileInfo(index).filePath()
                self.copyFile()
                target, _ = QFileDialog.getSaveFileName(self, "Сохранить как...",
                                                        path + "/" + "archive.zip", "zip files (*.zip)")
                if target != "":
                    with ZipFile(target, "w") as myzip:
                        for file in self.copyList:
                            fname = os.path.basename(file)
                            myzip.write(file, fname)
        except:
            pass

    def unzipHere(self):
        try:
            if self.listview.selectionModel().hasSelection():
                file_index = self.listview.selectionModel().currentIndex()
                file_path = self.fileModel.fileInfo(file_index).filePath()
                folder_index = self.treeview.selectionModel().currentIndex()
                folder_path = self.dirModel.fileInfo(folder_index).filePath()
                with ZipFile(file_path, "r") as zipObj:
                    zipObj.extractall(folder_path)
        except:
            pass

    def unzipTo(self):
        try:
            file_index = self.listview.selectionModel().currentIndex()
            file_path = self.fileModel.fileInfo(file_index).filePath()
            dirpath = QFileDialog.getExistingDirectory(self, "Выберите директорию",
                                                       QDir.homePath(), QFileDialog.ShowDirsOnly)
            if dirpath:
                with ZipFile(file_path, "r") as zipObj:
                    zipObj.extractall(dirpath)
        except:
            pass

    def openDir(self):
        try:
            self.treeview.selectionModel().clearSelection()
            index = self.treeview.selectionModel().currentIndex()
            path = self.findfield.text()
            if "C:" in path:
                self.showException()
                self.goHome()
            else:
                self.listview.setRootIndex(self.fileModel.setRootPath(path))
                self.currentPath = path
                self.findfield.setText(path)
                self.findfield.setPlaceholderText(path)
                self.getRowCount()
        except:
            pass

    def findFiles(self):
        try:
            create = open("Protocol.txt", "at")
            create.write("Start process: " + "FindFiles.py" + "\t" + " Open time: "
                         + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
            create.close()
            self.p = QProcess(self)
            self.p.start("py", ['findFilesWindow.py'])
        except:
            pass

    def refreshList(self):
        try:
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).path()
            self.treeview.setCurrentIndex(self.fileModel.index(path))
            self.treeview.setFocus()
        except:
            pass

    def showHelp(self):
        try:
            self.w = helpWindow()
            self.w.setWindowModality(Qt.ApplicationModal)
            self.w.setFixedSize(240, 300)
            self.w.show()
        except:
            pass

    def openVar(self):
        try:
            create = open("Protocol.txt", "at")
            create.write("Start process: " + "QWorker.py" + "\t" + " Open time: "
                         + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
            create.close()
            self.p = QProcess(self)
            self.p.start("py", ['QWorker.py'])
        except:
            pass

    def on_clicked(self):
        try:
            if self.treeview.selectionModel().hasSelection():
                index = self.treeview.selectionModel().currentIndex()
                if not (self.treeview.isExpanded(index)):
                    self.treeview.setExpanded(index, True)
                else:
                    self.treeview.setExpanded(index, False)
        except:
            pass

    def getFolderSize(self):
        try:
            size = sum(os.path.getsize(f) for f in os.listdir(os.getcwd()) if os.path.isfile(f))
            return size
        except:
            pass

    def on_selectionChanged(self):
        try:
            self.treeview.selectionModel().clearSelection()
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            self.listview.setRootIndex(self.fileModel.setRootPath(path))
            self.currentPath = path
            if "C:/" in path:
                self.findfield.setText(path[3:])
                self.findfield.setPlaceholderText(path[3:])
            else:
                self.findfield.setText(path)
                self.findfield.setPlaceholderText(path)
            self.getRowCount()
        except:
            pass

    def openFile(self):
        try:
            if self.listview.hasFocus():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath()
                self.copyFile()
                for files in self.copyList:
                    QDesktopServices.openUrl(QUrl(files, QUrl.TolerantMode | QUrl.EncodeUnicode))
                    create = open("log.txt", "at")
                    create.write("Open file: " + os.path.basename(files) + "\t" + " Open time: "
                                 + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                    create.close()
        except:
            pass

    def openFileText(self):
        try:
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath()
                self.texteditor = QTextEdit.MainWindow()
                self.texteditor.show()
                self.texteditor.loadFile(path)
                create = open("log.txt", "at")
                create.write("Open file: " + os.path.basename(path) + "\t" + " Open time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def playMedia(self):
        try:
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).filePath()
                self.statusBar().showMessage("%s '%s'" % ("Файл:", path))
                self.player = Qt5Player.VideoPlayer("")
                self.player.show()
                self.player.loadFilm(path)
                create = open("log.txt", "at")
                create.write("Open file: " + os.path.basename(path) + "\t" + " Open time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def showURL(self):
        try:
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath()
                self.webview = QWebViewer.MainWindow()
                self.webview.show()
                self.webview.load_url(path)
                create = open("log.txt", "at")
                create.write("Open file: " + os.path.basename(path) + "\t" + " Open time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def list_doubleClicked(self):
        try:
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            if not self.fileModel.fileInfo(index).isDir():
                if self.checkIsApplication(path):
                    self.openFile()
            else:
                self.treeview.setCurrentIndex(self.dirModel.index(path))
                self.treeview.setFocus()
                if "C:" in path:
                    self.findfield.setText(path[3:])
                    self.findfield.setPlaceholderText(path[3:])
                else:
                    self.findfield.setText(path)
                    self.findfield.setPlaceholderText(path)
        except:
            pass

    def goBack(self):
        try:
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).path()
            self.treeview.setCurrentIndex(self.dirModel.index(path))
        except:
            pass

    def goUp(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).path()
            if path != "C:/" and path != "D:/":
                self.treeview.setCurrentIndex(self.dirModel.index(path))
        except:
            pass

    def goHome(self):
        try:
            docs = os.path.dirname(os.path.abspath(os.path.dirname(sys.argv[0])))
            self.treeview.setCurrentIndex(self.dirModel.index(docs))
            self.treeview.setFocus()
        except:
            pass

    def infobox(self, message):
        try:
            title = "FileManager"
            QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                        Qt.Dialog | Qt.NoDropShadowWindowHint).show()
        except:
            pass

    def contextMenuEvent(self, event):
        try:
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.menu = QMenu(self.listview)
            if self.listview.hasFocus():
                self.menu.addAction(self.createFolderAction)
                self.menu.addAction(self.createFileAction)
                self.menu.addAction(self.openAction)
                self.menu.addAction(self.openActionText)
                self.menu.addSeparator()

                url_extension = [".htm", ".html"]
                for ext in url_extension:
                    if ext in path:
                        self.menu.addAction(self.urlAction)
                        self.menu.addSeparator()

                image_extension = [".png", "jpg", ".jpeg", ".bmp", "tif", ".tiff", ".pnm", ".svg", ".exif", ".gif"]
                for ext in image_extension:
                    if ext in path or ext.upper() in path:
                        self.menu.addAction(self.imageAction)
                        self.menu.addSeparator()

                extensions = [".mp4", "mpg", ".m4a", ".mpeg", ".avi", ".mkv",
                              ".webm", ".wav", ".ogg", ".flv ", ".vob",
                              ".ogv", ".ts", ".m2v", ".m4v", ".3gp", ".f4v"]
                for ext in extensions:
                    if ext in path or ext.upper() in path:
                        self.menu.addAction(self.playAction)
                        self.menu.addSeparator()

                extensions = [".mp3", ".wav"]
                for ext in extensions:
                    if ext in path or ext.upper() in path:
                        self.menu.addAction(self.playlistPlayerAction)
                        self.menu.addSeparator()

                self.menu.addAction(self.copyAction)
                self.menu.addAction(self.cutAction)
                self.menu.addAction(self.pasteAction)
                self.menu.addSeparator()
                self.menu.addAction(self.renameAction)
                self.menu.addSeparator()
                self.menu.addAction(self.delActionTrash)
                self.menu.addAction(self.delAction)
                self.menu.addSeparator()
                self.menu.addAction(self.hiddenAction)
                self.menu.addAction(self.refreshAction)
                self.menu.addAction(self.zipFilesAction)
                zip_extension = [".zip", ".tar.gz"]
                for ext in zip_extension:
                    if ext in path:
                        self.menu.addAction(self.unzipHereAction)
                        self.menu.addAction(self.unzipToAction)
                self.menu.addSeparator()
                self.menu.addAction(self.helpAction)
                self.menu.popup(QCursor.pos())
            else:
                index = self.treeview.selectionModel().currentIndex()
                path = self.dirModel.fileInfo(index).absoluteFilePath()
                self.menu = QMenu(self.treeview)
                if os.path.isdir(path):
                    self.menu.addAction(self.createFolderAction)
                    self.menu.addAction(self.renameFolderAction)
                    self.menu.addAction(self.copyFolderAction)
                    self.menu.addAction(self.pasteFolderAction)
                    self.menu.addAction(self.delFolderAction)
                    self.menu.addSeparator()
                    self.menu.addAction(self.findFilesAction)
                    self.menu.addAction(self.zipAction)
                self.menu.popup(QCursor.pos())
        except:
            pass

    def createNewFolder(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            dlg = QInputDialog(self)
            foldername, ok = dlg.getText(self, "Создать", "Введите название директории:",
                                         QLineEdit.Normal, "", Qt.Dialog)
            if ok:
                success = QDir(path).mkdir(foldername)
                create = open("log.txt", "at")
                create.write("Create folder: " + foldername + "\t" + " Create time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def createNewFile(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            dlg = QInputDialog(self)
            filename, ok = dlg.getText(self, "Создать", "Введите название файла с расширением:",
                                       QLineEdit.Normal, "", Qt.Dialog)
            if ok:
                file = open(path + "/" + filename, "w+")
                file.close()
                create = open("log.txt", "at")
                create.write("Create file: " + filename + "\t" + " Create time: "
                             + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
                create.close()
        except:
            pass

    def renameFile(self):
        try:
            if self.listview.hasFocus():
                if self.listview.selectionModel().hasSelection():
                    index = self.listview.selectionModel().currentIndex()
                    path = self.fileModel.fileInfo(index).absoluteFilePath()
                    basepath = self.fileModel.fileInfo(index).path()
                    oldName = self.fileModel.fileInfo(index).fileName()
                    dlg = QInputDialog()
                    newName, ok = dlg.getText(self, "Переименовать", path, QLineEdit.Normal, oldName, Qt.Dialog)
                    if ok:
                        newpath = basepath + "/" + newName
                        QFile.rename(path, newpath)
            elif self.treeview.hasFocus():
                self.renameFolder()
        except:
            pass

    def renameFolder(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            basepath = self.dirModel.fileInfo(index).path()
            oldName = self.dirModel.fileInfo(index).fileName()
            dlg = QInputDialog()
            newName, ok = dlg.getText(self, "Переименовать", path, QLineEdit.Normal, oldName, Qt.Dialog)
            if ok:
                newpath = basepath + "/" + newName
                nd = QDir(path)
                check = nd.rename(path, newpath)
        except:
            pass

    def copyFile(self):
        self.copyList = []
        selected = self.listview.selectionModel().selectedRows()
        for index in selected:
            path = self.currentPath + "/" + self.fileModel.data(index, self.fileModel.FileNameRole)
            if path != self.workingDirectory:
                self.copyList.append(path)
                self.clip.setText("\n".join(self.copyList))
            else:
                self.showException()

    def copyFolder(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            folderpath = self.dirModel.fileInfo(index).absoluteFilePath()
            self.folder_copied = folderpath
            self.copyList = []
        except:
            pass

    def pasteFolder(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            target = self.folder_copied
            destination = self.dirModel.fileInfo(index).absoluteFilePath() \
                          + "/" + QFileInfo(self.folder_copied).fileName()
            try:
                shutil.copytree(target, destination)
            except OSError as e:
                if e.errno == errno.ENOTDIR:
                    shutil.copy(target, destination)
                else:
                    self.showException()
        except:
            pass

    def pasteFile(self):
        try:
            if len(self.copyList) > 0:
                index = self.treeview.selectionModel().currentIndex()
                for target in self.copyList:
                    try:
                        destination = self.dirModel.fileInfo(index).absoluteFilePath() \
                                      + "/" + QFileInfo(target).fileName()
                        if os.path.isdir(target) and target != os.path.basename(self.workingDirectory):
                            shutil.copytree(target, destination)
                        else:
                            shutil.copy(target, destination)
                    except:
                        self.showException()
                if self.cut:
                    for t in range(len(self.copyList)):
                        self.fileModel.remove(self.fileModel.index(self.copyList[t]))
                        if t == len(self.copyList):
                            self.cut = False
        except:
            pass

    def cutFile(self):
        try:
            self.cut = True
            self.copyFile()
        except:
            pass

    def deleteFolder(self):
        try:
            index = self.treeview.selectionModel().currentIndex()
            delFolder = self.dirModel.fileInfo(index).absoluteFilePath()
            delList = delFolder.split("/")
            msg = QMessageBox.question(self, "Сообщение",
                                       "Вы действительно хотите безвозвратно удалить файл(ы)?\n" + delFolder,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if msg == QMessageBox.Yes and os.path.basename(self.workingDirectory) not in delList:
                self.statusBar().showMessage("%s %s" % ("Файл(ы) удален(ы)", delFolder), 0)
                self.fileModel.remove(index)
            else:
                self.showException()
        except:
            pass

    def deleteFile(self):
        try:
            self.copyFile()
            msg = QMessageBox.question(self, "Сообщение",
                                       "Вы действительно хотите безвозвратно удалить файл(ы)?\n"
                                       + "\n".join(self.copyList),
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if msg == QMessageBox.Yes and self.currentPath != self.workingDirectory:
                index = self.listview.selectionModel().currentIndex()
                self.copyPath = self.fileModel.fileInfo(index).absoluteFilePath()
                self.statusBar().showMessage("%s %s" % ("Файл(ы) удален(ы)", self.copyPath), 0)
                for delFile in self.listview.selectionModel().selectedIndexes():
                    if self.copyPath != self.workingDirectory and "System" not in self.copyPath:
                        self.fileModel.remove(delFile)
                    else:
                        self.showException()
            else:
                self.showException()
        except:
            pass

    def deleteFileTrash(self):
        try:
            self.copyList = []
            selected = self.listview.selectionModel().selectedRows()
            for index in selected:
                path = self.currentPath + "/" + self.fileModel.data(index, self.fileModel.FileNameRole)
                self.copyList.append(path)
                self.clip.setText("\n".join(self.copyList))
            if len(self.copyList) > 0:
                for t in self.copyList:
                    try:
                        destination = "C:/Disk2/Trash" + "/" + QFileInfo(t).fileName()
                        if path != self.workingDirectory and "System" not in t:
                            shutil.move(t, destination)
                        else:
                            self.showException()
                    except:
                        self.showException()
        except:
            pass

    def startTasker(self):
        try:
            create = open("Protocol.txt", "at")
            create.write("Start process: " + "Tasker.exe" + "\t" + " Open time: "
                         + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
            create.close()
            os.startfile('taskmgr.exe')
        except:
            pass

    def showException(self):
        try:
            self.w = Exception()
            self.w.setWindowModality(Qt.ApplicationModal)
            self.w.setFixedSize(280, 100)
            self.w.show()
        except:
            pass

    def createStatusBar(self):
        try:
            sysinfo = QSysInfo()
            myMachine = "Архитектура системы: " + sysinfo.currentCpuArchitecture() + \
                        " *** " + sysinfo.prettyProductName() + " *** " \
                        + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
            self.statusBar().showMessage(myMachine, 0)
        except:
            pass

    def saveLog(self):
        try:
            dlg = QInputDialog()
            path = "C:\\Disk2\\System\\Logs\\protocol.txt"
            oldName = "protocol.txt"
            newName, ok = dlg.getText(self, "Задать имя протокола", "Введите имя протокола с расширением", QLineEdit.Normal, oldName, Qt.Dialog)
            if ok:
                newPath = "C:\\Disk2\\System\\Logs\\" + newName
                QFile.rename(path, newPath)
        except:
            pass

    def processes(self):
        try:
            client = myWindow.start_client(self)
            file = open("Logs/processes.txt", "w+")
            for line in Popen('tasklist', stdout=PIPE).stdout.readlines():
                file.write(str(line.decode('cp866', 'ignore')))
            file.close()

            file = open("Logs/processes.txt", "r")
            file = bytes(file.read(), encoding='utf-8')
            client.send(file)
            client.close()

        except:
            self.info.append("Ошибка")

    def local_processes(self):
        try:
            self.info.clear()
            client = myWindow.start_client(self)
            proc = psutil.Process().parent().pid
            p = psutil.Process(proc).parent()
            x = psutil.Process(p.pid).children()
            file = open("Logs/local.txt", "w+")
            file.write(str(f"Имя главного процесса: {p.name()}\t"
                           f"PID: {p.pid}\t"
                           f"Кол-во потоков: {p.num_threads()}\n"
                           ))
            for f in x:
                file.write(str(f"Имя дочернего процесса: {f.name()}\t"
                               f"PID: {f.pid}\t"
                               f"Кол-во потоков: {f.num_threads()}\n"
                               ))
            file.close()

            file = open("Logs/local.txt", "r")
            file = bytes(file.read(), encoding='utf-8')
            client.send(file)
            client.close()
        except:
            self.info.append("Ошибка")

    def PID(self):
        try:
            client = myWindow.start_client(self)
            self.output.clear()
            pid_name = int(self.input.text())
            children = psutil.Process(pid_name).children()
            if not children:
                self.output.append("Дочерних процессов не найдено")
            file = open("Logs/pid.txt", "w+")
            for proc in children:
                file.write(str(f"Имя процесса: {proc.name()}\t"
                               f"PID: {proc.pid}\t"
                               f"Время старта: {time.strftime('%H:%M:%S', time.localtime(proc.create_time()))}\n"))

            file.close()
            file = open("Logs/pid.txt", "r")
            file = bytes(file.read(), encoding='utf-8')
            client.send(file)
            client.close()

        except:
            self.output.append("PID не введено")

    def error(self):
        client = myWindow.start_client(self)
        self.output.clear()
        p = psutil.Process(os.getpid())
        data = f"Кол-во страничных ошибок файлового менеджера: {p.memory_info().num_page_faults}"
        data = bytes(data, encoding='utf-8')
        client.send(data)
        client.close()

    def cpu(self):
        try:
            client = myWindow.start_client(self)
            self.output.clear()
            pid_name = self.input.text()
            if len(pid_name) != 0:
                pid = []
                cpu = []
                sum = 0.0
                for proc in psutil.process_iter():
                    if proc.name() == pid_name:
                        pid.append(proc.pid)
                for proc in pid:
                    p = psutil.Process(proc)
                    cpu.append(p.cpu_percent(interval=0.5))
                for proc in cpu:
                    sum += proc
                s = f"Загрузка CPU данным процессом: {sum} %"
                s = bytes(s, encoding='utf-8')
                client.send(s)
                client.close()
            else:
                self.output.append("Данный процесс не найден")
        except:
            self.output.append("Не, я отказываюсь работать")

    def update_status(self):
        try:

            client = myWindow.start_client(self)
            cpu = psutil.Process(os.getpid()).cpu_percent(interval=0.5)
            err = psutil.Process(os.getpid()).memory_info().num_page_faults
            data = f"Загрузка ЦП: {cpu} %, Страничные ошибки: {err}"
            data = bytes(data, encoding='utf-8')

            client.send(data)
            client.close()
        except:
            pass

    def start_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 6500))
        return client

    def start_prot(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_prot)
        self.timer.start()

    def update_prot(self):
        for p in psutil.process_iter():
            if p.pid not in self.List and p not in self.List_New and p not in self.blacklist:
                self.List_New.append(p)
        f = open("Logs\protocol.txt", 'w+')
        for p in self.List_New:
            ptime = datetime.datetime.fromtimestamp(p.create_time()).strftime("%m-%d %H:%M")
            f.write(str(p.name()) + '\t' + str(p.pid) + '\t' + str(ptime) + '\n')
        #rint(self.List_New)

    def get_proc(self):
        self.List = []
        for p in psutil.process_iter():
            self.List.append(p.pid)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = myWindow()
    w.get_proc()
    w.show()
    w.start_prot()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        w.listview.setRootIndex(w.fileModel.setRootPath(path))
        w.treeview.setRootIndex(w.dirModel.setRootPath(path))
        w.setWindowTitle(path)
    sys.exit(app.exec())
