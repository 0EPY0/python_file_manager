import os.path
import sys

from PyQt5.QtCore import Qt, QDir, QFile, QUrl, QStandardPaths
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem,\
                            QCheckBox, QApplication, QAction, QMessageBox, QPushButton, QFileDialog,\
                            QHeaderView, QLineEdit, QAbstractItemView
from PyQt5.QtGui import QDesktopServices, QIcon

myblue = "#fce94f"
home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
username = home.rpartition("/")[-1]
media = "/Users/" + username

music = QStandardPaths.standardLocations(QStandardPaths.MusicLocation)[0]
videos = QStandardPaths.standardLocations(QStandardPaths.MoviesLocation)[0]
documents = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
pictures = QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0]
downloads = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0]
apps = QStandardPaths.standardLocations(QStandardPaths.ApplicationsLocation)[0]
temp = QStandardPaths.standardLocations(QStandardPaths.TempLocation)[0]
config = QStandardPaths.standardLocations(QStandardPaths.ConfigLocation)[0]
appdata = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0]


class ListBox(QMainWindow):
    def __init__(self):
        super(ListBox, self).__init__()
        self.fileList = []
        self.folderlist = []
        self.allFolders = []
        self.dir = QDir.homePath()
        self.subdir = QDir.homePath()
        self.setGeometry(0, 0, 800, 450)
        self.setMinimumSize(500, 300)
        self.setContentsMargins(10, 10, 10, 0)
        self.setWindowTitle("Поиск")
        self.setWindowIcon(QIcon("images/search.png"))

        self.tb = self.addToolBar("Tools")
        self.tb.setMovable(False)
        self.tb.setContextMenuPolicy(Qt.PreventContextMenu)
        self.findEdit = QLineEdit("")
        self.findAct = QAction(self, triggered=self.findMyFiles)
        self.findEdit.addAction(self.findAct, QLineEdit.LeadingPosition)
        self.findEdit.setPlaceholderText("Поиск")
        self.findEdit.setToolTip("Например: *слово*")
        self.findEdit.setStatusTip("Например: *слово*")
        self.tb.addWidget(self.findEdit)
        self.findEdit.returnPressed.connect(self.findMyFiles)

        self.tb.addSeparator()

        self.folderEdit = QLineEdit()
        self.folderAct = QAction(self, triggered=self.changeFolder)
        self.folderEdit.addAction(self.folderAct, QLineEdit.LeadingPosition)
        self.folderEdit.setPlaceholderText("Вставить путь к директории")
        self.folderEdit.setText(self.dir)
        self.folderEdit.returnPressed.connect(self.findMyFiles)
        self.tb.addWidget(self.folderEdit)

        self.tb.addSeparator()

        self.noDot = QCheckBox("Показать скрытые файлы")

        self.lb = QTableWidget()
        self.lb.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lb.setColumnCount(2)
        self.lb.setColumnWidth(0, 300)
        self.lb.setSelectionMode(self.lb.SingleSelection)
        self.lb.cellDoubleClicked.connect(self.doubleClicked)
        self.lb.itemClicked.connect(self.getItem)
        self.lb.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lb.horizontalHeader().setStretchLastSection(True)
        self.lb.setAlternatingRowColors(True)
        self.verticalHeader = QHeaderView(Qt.Vertical)
        self.lb.setVerticalHeader(self.verticalHeader)
        self.lb.horizontalHeader().setStretchLastSection(True)
        self.lb.setHorizontalHeaderItem(0, QTableWidgetItem("Имя"))
        self.lb.setHorizontalHeaderItem(1, QTableWidgetItem("Путь"))
        self.verticalHeader.setDefaultSectionSize(24)
        self.lb.verticalHeader().hide()
        self.lb.setToolTip("Дважды щелкните, чтобы открыть файл")
        self.setCentralWidget(self.lb)
        self.findEdit.setFocus()
        self.statusBar().showMessage("Готово к запуску")
        self.setStyleSheet(stylesheet(self))

        self.copyBtn = QPushButton("Скопировать путь")
        self.copyBtn.clicked.connect(self.copyPath)
        self.copyBtn.setFlat(True)
        self.statusBar().addPermanentWidget(self.copyBtn)

        self.dir = self.folderEdit.text()
        self.folderEdit.setText("C:\\Disk")

    def removeDuplicates(self):
        try:
            for row in range(self.lb.rowCount()):
                if self.lb.item(row, 1) == self.lb.item(row + 1, 1):
                    self.lb.removeRow(row)
        except:
            pass

    def selectedRow(self):
        try:
            if self.lb.selectionModel().hasSelection():
                row = self.lb.selectionModel().selectedIndexes()[0].row()
                return int(row)
        except:
            pass

    def selectedColumn(self):
        try:
            column = self.lb.selectionModel().selectedIndexes()[0].column()
            return int(column)
        except:
            pass

    def getItem(self):
        try:
            row = self.selectedRow()
            column = self.selectedColumn()
            item = self.lb.item(row, column)
            if column == 1:
                myfile = item.text()
            else:
                myfile = self.lb.item(row, 1).text() + "/" + self.lb.item(row, 0).text()
            self.msg(myfile, 0)
        except:
            pass

    def copyPath(self):
        try:
            if self.lb.selectionModel().hasSelection():
                row = self.selectedRow()
                myfile = self.lb.item(row, 1).text() + "/" + self.lb.item(row, 0).text()
                clip = QApplication.clipboard()
                clip.setText(myfile)
                self.msg("Путь скопирован!", 0)
            else:
                self.msg("Ничего не выбрано!", 0)
        except:
            pass

    def doubleClicked(self):
        try:
            row = self.selectedRow()
            column = self.selectedColumn()
            item = self.lb.item(row, column)
            if column == 1:
                myfile = item.text()
            else:
                myfile = self.lb.item(row, 1).text() + "/" + self.lb.item(row, 0).text()
            if QFile.exists(myfile) and not os.path.isdir(myfile):
                QDesktopServices.openUrl(QUrl.fromLocalFile(myfile))
        except:
            pass

    def findMyFiles(self):
        try:
            self.folderlist = []
            self.allFolders = []
            self.lb.clearContents()
            self.dir = self.folderEdit.text()
            if not self.findEdit.text() == "*":
                self.lb.setRowCount(0)
                self.findFiles(self.dir)
                self.findFolders(self.dir)
                self.findSufolders()
                self.getFiles()
                self.removeDuplicates()
                if not self.lb.rowCount() == 0:
                    self.msg("Найден(ы) " + str(self.lb.rowCount()) + " файл(ы)", 0)
                else:
                    self.msg("Ничего не найдено", 0)
            else:
                message = "Пожалуйста, введите что-нибудь для поиска"
                self.msg(message, 0)
        except:
            pass

    def findFolders(self, path):
        try:
            fileName = "*"
            currentDir = QDir(path)
            if self.noDot.isChecked():
                files = currentDir.entryList([fileName], QDir.AllDirs)
            else:
                files = currentDir.entryList([fileName], QDir.AllDirs | QDir.NoDotAndDotDot)
            for line in files:
                self.folderlist.append(path + "/" + line)
        except:
            pass

    def findSufolders(self):
        try:
            for folders in self.folderlist:
                self.allFolders.append(folders)
                self.findNewFolders(folders)
        except:
            pass

    def findNewFolders(self, path):
        try:
            fileName = "*"
            currentDir = QDir(path)
            files = currentDir.entryList([fileName], QDir.AllDirs | QDir.NoDotAndDotDot)
            for line in files:
                self.allFolders.append(path + "/" + line)
                self.findNewFolders(path + "/" + line)
        except:
            pass

    def findFiles(self, path):
        try:
            findName = self.findEdit.text()
            currentDir = QDir(path)
            self.msg("Поиск в " + currentDir.path(), 0)
            files = currentDir.entryList([findName], QDir.AllEntries | QDir.System | QDir.Drives)
            for line in files:
                self.lb.insertRow(0)
                self.lb.setItem(0, 0, QTableWidgetItem(line))
                self.lb.setItem(0, 1, QTableWidgetItem(path))
        except:
            pass

    def getFiles(self):
        try:
            for mf in self.allFolders:
                self.findFiles(mf)
        except:
            pass

    def changeFolder(self):
        try:
            newfolder = QFileDialog.getExistingDirectory(self, "Поиск", self.dir)
            if newfolder:
                self.folderEdit.setText(newfolder)
        except:
            pass

    def msg(self, message, timeout):
        try:
            self.statusBar().showMessage(message, timeout)
        except:
            pass


def stylesheet(self):
    return """
QTableWidget
{
    background: #e9e9e9;
    selection-color: white;
    border: 1px solid lightgrey;
    selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #729fcf, stop: 1  #204a87);
    color: #202020;
    outline: 0;
} 
QTableWidget::item::hover
{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #babdb6, stop: 0.5 #d3d7cf, stop: 1 #babdb6);
}
QTableWidget::item::focus
{
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #729fcf, stop: 1  #204a87);
border: 0px;
}
QHeaderView 
{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                         stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                         stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    border: 0px solid grey;
    font-size: 9pt;
    font-weight: bold;
    color: #2e3436;
}
QStatusBar
{
    font-size: 8pt;
    color: #403a3a;
}
QToolBar
{
    border: 0px;
    background-color: transparent;
}
QToolBar::Separator
{
    background-color: transparent;
    width: 20px;
}   
QMainWindow
{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                             stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                             stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QLineEdit
{
    font-size: 9pt;
    background: #eeeeec;
    height: 20px;
}
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ListBox()
    w.show()
    sys.exit(app.exec_())
