from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import QDir, Qt, QUrl, QPoint, QTime, QProcess
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLineEdit,\
                            QPushButton, QSlider, QMessageBox,\
                            QStyle, QVBoxLayout, QWidget, QShortcut, QMenu


class VideoPlayer(QWidget):
    def __init__(self, aPath, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAcceptDrops(True)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVolume(80)
        videoWidget = QVideoWidget()

        self.lbl = QLineEdit("00:00:00")
        self.lbl.setReadOnly(True)
        self.lbl.setFixedWidth(70)
        self.lbl.setUpdatesEnabled(True)
        self.lbl.setStyleSheet(stylesheet(self))

        self.elbl = QLineEdit("00:00:00")
        self.elbl.setReadOnly(True)
        self.elbl.setFixedWidth(70)
        self.elbl.setUpdatesEnabled(True)
        self.elbl.setStyleSheet(stylesheet(self))

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedWidth(32)
        self.playButton.setStyleSheet("background-color: black")
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setStyleSheet(stylesheet(self))
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderMoved.connect(self.handleLabel)
        self.positionSlider.setSingleStep(2)
        self.positionSlider.setPageStep(20)
        self.positionSlider.setAttribute(Qt.WA_TranslucentBackground, True)

        self.Volume = QLineEdit()
        self.Volume.setFixedWidth(80)
        self.Volume.setReadOnly(True)
        self.Volume.setText("Volume: " + str(self.mediaPlayer.volume()))
        self.Volume.setStyleSheet(stylesheet(self))

        self.clip = QApplication.clipboard()
        self.process = QProcess(self)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(5, 0, 5, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.lbl)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.elbl)
        controlLayout.addWidget(self.Volume)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        self.setLayout(layout)

        self.myinfo = "\nMouse Wheel = Zoom\nUP = Прибавить громкость\nDOWN = Убавить громкость\n" + \
                      "LEFT = < 1 минута\nRIGHT = > 1 минута\n" + \
                      "SHIFT + LEFT = < 10 минут\nSHIFT + RIGHT = > 10 минут\n"
        self.widescreen = True

        self.shortcut = QShortcut(QKeySequence("Q"), self)
        self.shortcut.activated.connect(self.handleQuit)
        self.shortcut = QShortcut(QKeySequence("O"), self)
        self.shortcut.activated.connect(self.openFile)
        self.shortcut = QShortcut(QKeySequence(" "), self)
        self.shortcut.activated.connect(self.play)
        self.shortcut = QShortcut(QKeySequence("F"), self)
        self.shortcut.activated.connect(self.handleFullscreen)
        self.shortcut = QShortcut(QKeySequence("I"), self)
        self.shortcut.activated.connect(self.handleInfo)
        self.shortcut = QShortcut(QKeySequence("S"), self)
        self.shortcut.activated.connect(self.toggleSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut.activated.connect(self.forwardSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut.activated.connect(self.backSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut.activated.connect(self.volumeUp)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut.activated.connect(self.volumeDown)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier + Qt.Key_Right), self)
        self.shortcut.activated.connect(self.forwardSlider10)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier + Qt.Key_Left), self)
        self.shortcut.activated.connect(self.backSlider10)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.positionChanged.connect(self.handleLabel)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.setAcceptDrops(True)
        self.setWindowTitle("VideoPlayer")
        self.setWindowIcon(QIcon("images/youtube.png"))
        self.setGeometry(100, 300, 600, 380)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)
        self.widescreen = True

    def openFile(self):
        try:
            fileName, _ = QFileDialog.getOpenFileName(self, "Открыть видео",
                                                      QDir.homePath() + "/Videos", "Media"
                                                      "(*.webm *.mp4 *.ts *.avi *.mpeg *.mpg *.mkv *.VOB *.m4v"
                                                      "*.3gp *.mp3 *.m4a *.wav *.ogg *.flac *.m3u *.m3u8)")
            if fileName != "":
                self.loadFilm(fileName)
        except:
            pass

    def play(self):
        try:
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
        except:
            pass

    def mediaStateChanged(self):
        try:
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.playButton.setIcon(QIcon("images/play.png"))
            else:
                self.playButton.setIcon(QIcon("images/pause-button.png"))
        except:
            pass

    def positionChanged(self, position):
        try:
            self.positionSlider.setValue(position)
        except:
            pass

    def durationChanged(self, duration):
        try:
            self.positionSlider.setRange(0, duration)
            mtime = QTime(0, 0, 0, 0)
            mtime = mtime.addMSecs(self.mediaPlayer.duration())
            self.elbl.setText(mtime.toString())
        except:
            pass

    def setPosition(self, position):
        try:
            self.mediaPlayer.setPosition(position)
        except:
            pass

    def handleError(self):
        try:
            self.playButton.setEnabled(False)
        except:
            pass

    def handleQuit(self):
        try:
            self.mediaPlayer.stop()
            self.close()
        except:
            pass

    def closeEvent(self, event):
        try:
            event.accept()
            self.mediaPlayer.stop()
            self.close()
        except:
            pass

    def contextMenuRequested(self, point):
        try:
            menu = QMenu()
            actionFile = menu.addAction("Открыть файл (O)")
            actionToggle = menu.addAction("Показать / Скрыть слайдер (S)")
            actionFull = menu.addAction("Полноэкранный режим (F)")
            action169 = menu.addAction("16 : 9")
            action43 = menu.addAction("4 : 3")
            actionInfo = menu.addAction("Info (I)")
            actionQuit = menu.addAction("Выход (Q)")
    
            actionFile.triggered.connect(self.openFile)
            actionQuit.triggered.connect(self.handleQuit)
            actionFull.triggered.connect(self.handleFullscreen)
            actionInfo.triggered.connect(self.handleInfo)
            actionToggle.triggered.connect(self.toggleSlider)
            action169.triggered.connect(self.screen169)
            action43.triggered.connect(self.screen43)
            menu.exec_(self.mapToGlobal(point))
        except:
            pass

    def wheelEvent(self, event):
        try:
            mwidth = self.frameGeometry().width()
            mleft = self.frameGeometry().left()
            mtop = self.frameGeometry().top()
            mscale = event.angleDelta().y() / 5
            if self.widescreen:
                self.setGeometry(mleft, mtop, mwidth + mscale, int((mwidth + mscale) / 1.778))
            else:
                self.setGeometry(mleft, mtop, mwidth + mscale, int((mwidth + mscale) / 1.33))
        except:
            pass

    def screen169(self):
        try:
            self.widescreen = True
            mwidth = self.frameGeometry().width()
            mleft = self.frameGeometry().left()
            mtop = self.frameGeometry().top()
            mratio = 1.778
            self.setGeometry(mleft, mtop, mwidth, int(mwidth / mratio))
        except:
            pass

    def screen43(self):
        try:
            self.widescreen = False
            mwidth = self.frameGeometry().width()
            mleft = self.frameGeometry().left()
            mtop = self.frameGeometry().top()
            mratio = 1.33
            self.setGeometry(mleft, mtop, mwidth, int(mwidth / mratio))
        except:
            pass

    def handleFullscreen(self):
        try:
            if self.windowState() & Qt.WindowFullScreen:
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.showNormal()
            else:
                self.showFullScreen()
                QApplication.setOverrideCursor(Qt.BlankCursor)
        except:
            pass

    def handleInfo(self):
        try:
            msg = QMessageBox.about(self, "VideoPlayer", self.myinfo)
        except:
            pass

    def toggleSlider(self):
        try:
            if self.positionSlider.isVisible():
                self.hideSlider()
            else:
                self.showSlider()
        except:
            pass

    def hideSlider(self):
        try:
            self.widescreen = True
            self.playButton.hide()
            self.lbl.hide()
            self.positionSlider.hide()
            self.elbl.hide()
            mwidth = self.frameGeometry().width()
            mleft = self.frameGeometry().left()
            mtop = self.frameGeometry().top()
            if self.widescreen:
                self.setGeometry(mleft, mtop, mwidth, int(mwidth / 1.778))
            else:
                self.setGeometry(mleft, mtop, mwidth, int(mwidth / 1.33))
        except:
            pass

    def showSlider(self):
        try:
            self.playButton.show()
            self.lbl.show()
            self.positionSlider.show()
            self.elbl.show()
            mwidth = self.frameGeometry().width()
            mleft = self.frameGeometry().left()
            mtop = self.frameGeometry().top()
            if self.widescreen:
                self.setGeometry(mleft, mtop, mwidth, int(mwidth / 1.55))
            else:
                self.setGeometry(mleft, mtop, mwidth, int(mwidth / 1.33))
        except:
            pass

    def forwardSlider(self):
        try:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1000 * 60)
        except:
            pass

    def forwardSlider10(self):
        try:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 10000 * 60)
        except:
            pass

    def backSlider(self):
        try:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1000 * 60)
        except:
            pass

    def backSlider10(self):
        try:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() - 10000 * 60)
        except:
            pass

    def volumeUp(self):
        try:
            self.mediaPlayer.setVolume(self.mediaPlayer.volume() + 10)
            self.Volume.setText("Volume: " + str(self.mediaPlayer.volume()))
        except:
            pass

    def volumeDown(self):
        try:
            self.mediaPlayer.setVolume(self.mediaPlayer.volume() - 10)
            self.Volume.setText("Volume: " + str(self.mediaPlayer.volume()))
        except:
            pass

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() == Qt.LeftButton:
                self.move(int(event.globalPos() - QPoint(self.frameGeometry().width() / 2,
                                                         self.frameGeometry().height() / 2)))
                event.accept()
        except:
            pass

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                event.accept()
            elif event.mimeData().hasText():
                event.accept()
            else:
                event.ignore()
        except:
            pass

    def loadFilm(self, f):
        try:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(f)))
            self.playButton.setEnabled(True)
            self.mediaPlayer.play()
        except:
            pass

    def openFileAtStart(self, filelist):
        try:
            matching = [s for s in filelist if ".myformat" in s]
            if len(matching) > 0:
                self.loadFilm(matching)
        except:
            pass

    def handleLabel(self):
        try:
            self.lbl.clear()
            mtime = QTime(0, 0, 0, 0)
            self.time = mtime.addMSecs(self.mediaPlayer.position())
            self.lbl.setText(self.time.toString())
        except:
            pass


def stylesheet(self):
    return"""
QSlider::handle:horizontal 
    {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333, stop:1 #bc0000);
        width: 14px;
        border-radius: 0px;
    }
QSlider::groove:horizontal
    {
        border: 1px solid #444;
        height: 10px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #000, stop:1 #222222);
    }
QLineEdit
    {
        background: black;
        color: #791212;
        border: 0px solid #076100;
        font-size: 8pt;
        font-weight: bold;
    }
    """
