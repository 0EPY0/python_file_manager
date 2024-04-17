from PyQt5.QtCore import pyqtSignal, QAbstractItemModel, QFileInfo, \
    QModelIndex, Qt, QTime, QUrl, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaMetaData, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, \
    QListView, QMessageBox, QPushButton, \
    QSlider, QStyle, QToolButton, QVBoxLayout, QWidget, QStatusBar


class PlaylistModel(QAbstractItemModel):
    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.m_playlist = None

    def rowCount(self, parent=QModelIndex()):
        try:
            return self.m_playlist.mediaCount() if self.m_playlist is not None \
                                               and not parent.isValid() \
                                            else 0
        except:
            pass

    def columnCount(self, parent=QModelIndex()):
        try:
            return self.ColumnCount if not parent.isValid() else 0
        except:
            pass

    def index(self, row, column, parent=QModelIndex()):
        try:
            return self.createIndex(row, column) if self.m_playlist is not None \
                                                    and not parent.isValid() \
                                                    and 0 <= row < self.m_playlist.mediaCount() \
                                                    and 0 <= column < self.ColumnCount \
                                                 else QModelIndex()
        except:
            pass

    def parent(self, child):
        try:
            return QModelIndex()
        except:
            pass

    def data(self, index, role=Qt.DisplayRole):
        try:
            if index.isValid() and role == Qt.DisplayRole:
                if index.column() == self.Title:
                    location = self.m_playlist.media(index.row()).canonicalUrl()
                    return QFileInfo(location.path()).fileName()
                return self.m_data[index]
            return None
        except:
            pass

    def playlist(self):
        try:
            return self.m_playlist
        except:
            pass

    def setPlaylist(self, playlist):
        try:
            if self.m_playlist is not None:
                self.m_playlist.mediaAboutToBeInserted.disconnect(self.beginInsertItems)
                self.m_playlist.mediaInserted.disconnect(self.endInsertItems)
                self.m_playlist.mediaAboutToBeRemoved.disconnect(self.beginRemoveItems)
                self.m_playlist.mediaRemoved.disconnect(self.endRemoveItems)
                self.m_playlist.mediaChanged.disconnect(self.changeItems)

            self.beginResetModel()
            self.m_playlist = playlist

            if self.m_playlist is not None:
                self.m_playlist.mediaAboutToBeInserted.connect(self.beginInsertItems)
                self.m_playlist.mediaInserted.connect(self.endInsertItems)
                self.m_playlist.mediaAboutToBeRemoved.connect(self.beginRemoveItems)
                self.m_playlist.mediaRemoved.connect(self.endRemoveItems)
                self.m_playlist.mediaChanged.connect(self.changeItems)

            self.endResetModel()
        except:
            pass
    def beginInsertItems(self, start, end):
        try:
            self.beginInsertRows(QModelIndex(), start, end)
        except:
            pass

    def endInsertItems(self):
        try:
            self.endInsertRows()
        except:
            pass

    def beginRemoveItems(self, start, end):
        try:
            self.beginRemoveRows(QModelIndex(), start, end)
        except:
            pass

    def endRemoveItems(self):
        try:
            self.endRemoveRows()
        except:
            pass

    def changeItems(self, start, end):
        try:
            self.dataChanged.emit(self.index(start, 0), self.index(end, self.ColumnCount))
        except:
            pass


class PlayerControls(QWidget):
    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()
    next = pyqtSignal()
    previous = pyqtSignal()
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    changeRate = pyqtSignal(float)

    def __init__(self, parent=None):
        super(PlayerControls, self).__init__(parent)

        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False

        self.playButton = QToolButton(clicked=self.playClicked)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        self.nextButton = QToolButton(clicked=self.next)
        self.nextButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.previousButton = QToolButton(clicked=self.previous)
        self.previousButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))

        self.muteButton = QToolButton(clicked=self.muteClicked)
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

        self.volumeSlider = QSlider(Qt.Horizontal, sliderMoved=self.changeVolume)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setStyleSheet(stylesheet(self))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        self.setLayout(layout)

    def state(self):
        try:
            return self.playerState
        except:
            pass

    def setState(self, state):
        try:
            if state != self.playerState:
                self.playerState = state

                if state == QMediaPlayer.StoppedState:
                    self.stopButton.setEnabled(False)
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                elif state == QMediaPlayer.PlayingState:
                    self.stopButton.setEnabled(True)
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                elif state == QMediaPlayer.PausedState:
                    self.stopButton.setEnabled(True)
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        except:
            pass

    def volume(self):
        try:
            return self.volumeSlider.value()
        except:
            pass

    def setVolume(self, volume):
        try:
            self.volumeSlider.setValue(volume)
        except:
            pass

    def isMuted(self):
        try:
            return self.playerMuted
        except:
            pass

    def setMuted(self, muted):
        try:
            if muted != self.playerMuted:
                self.playerMuted = muted
                self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted
                                                                  if muted else QStyle.SP_MediaVolume))
        except:
            pass

    def playClicked(self):
        try:
            if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
                self.play.emit()
            elif self.playerState == QMediaPlayer.PlayingState:
                self.pause.emit()
        except:
            pass

    def muteClicked(self):
        try:
            self.changeMuting.emit(not self.playerMuted)
        except:
            pass


class Player(QWidget):
    fullScreenChanged = pyqtSignal(bool)

    def __init__(self, playlist, parent=None):
        super(Player, self).__init__(parent)
        self.setStyleSheet(stylesheet(self))
        self.colorDialog = None
        self.trackInfo = ""
        self.statusInfo = ""
        self.duration = 0

        self.url = ""
        self.settings = QSettings("QAudioPlayer", "QAudioPlayer")

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)
        self.player.mediaStatusChanged.connect(self.statusChanged)
        self.player.bufferStatusChanged.connect(self.bufferingProgress)
        self.player.error.connect(self.displayErrorMessage)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setStyleSheet(stylesheet(self))
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(self.playlistModel.index(self.playlist.currentIndex(), 0))

        self.playlistView.activated.connect(self.jump)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.player.duration() / 1000)
        self.slider.setStyleSheet(stylesheet(self))

        self.labelDuration = QLabel()
        self.slider.sliderMoved.connect(self.seek)

        openButton = QPushButton(clicked=self.open)
        openButton.setIcon(QIcon("images/import.png"))
        openButton.setToolTip("Открыть файл(ы)")

        clearButton = QPushButton(clicked=self.clearList)
        clearButton.setIcon(QIcon("images/trash.png"))
        clearButton.setToolTip("Очистить плейлист")

        controls = PlayerControls()
        controls.setState(self.player.state())
        controls.setVolume(self.player.volume())
        controls.setMuted(controls.isMuted())

        controls.play.connect(self.player.play)
        controls.pause.connect(self.player.pause)
        controls.stop.connect(self.player.stop)
        controls.next.connect(self.playlist.next)
        controls.previous.connect(self.previousClicked)
        controls.changeVolume.connect(self.player.setVolume)
        controls.changeMuting.connect(self.player.setMuted)
        controls.changeRate.connect(self.player.setPlaybackRate)

        self.player.stateChanged.connect(controls.setState)
        self.player.volumeChanged.connect(controls.setVolume)
        self.player.mutedChanged.connect(controls.setMuted)

        displayLayout = QHBoxLayout()
        displayLayout.addWidget(self.playlistView)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(clearButton)
        controlLayout.addWidget(controls)

        layout = QVBoxLayout()
        layout.addLayout(displayLayout)
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.slider)
        hLayout.addWidget(self.labelDuration)
        layout.addLayout(hLayout)
        layout.addLayout(controlLayout)

        self.statusBar = QStatusBar()
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.statusBar)
        layout.addLayout(vlayout)
        self.setWindowTitle("AudioPlayer")
        self.setWindowIcon(QIcon("images/spotify.png"))
        self.setMinimumSize(300, 200)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.readSettings()

        if not self.player.isAvailable():
            QMessageBox.warning(self, "Сервис недоступен",
                                "AudioPlayer не может подобрать подходящий сервис\n"
                                "Пожалуйста, проверьте установлены ли необходимые плагины.")

            controls.setEnabled(False)
            self.playlistView.setEnabled(False)
            openButton.setEnabled(False)
            self.colorButton.setEnabled(False)
            self.fullScreenButton.setEnabled(False)

        self.metaDataChanged()

        self.addToPlaylist(playlist)

    def readSettings(self):
        try:
            if self.settings.contains("url"):
                self.url = self.settings.value("url")
                self.addToPlaylist(self.url)
        except:
            pass

    def writeSettings(self):
        try:
            self.settings.setValue("url", self.url)
        except:
            pass

    def closeEvent(self, event):
        try:
            self.writeSettings()
            self.player.stop()
            event.accept()
        except:
            pass

    def open(self):
        try:
            fileNames, _ = QFileDialog.getOpenFileNames(self, "Открыть аудио",
                                                    "/home", "Audio Files *.mp3 *.m4a *.ogg *.wav *.m3u")
            if fileNames:
                self.url = fileNames
                self.addToPlaylist(fileNames)
        except:
            pass

    def openOnStart(self, name):
        try:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                if fileInfo.suffix().lower() == 'm3u':
                    self.playlist.load(url)
                else:
                    self.playlist.addMedia(QMediaContent(url))
            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))
        except:
            pass

    def clearList(self):
        try:
            self.playlist.clear()
            self.statusBar.clearMessage()
        except:
            pass

    def addToPlaylist(self, fileNames):
        try:
            for name in fileNames:
                fileInfo = QFileInfo(name)
                if fileInfo.exists():
                    url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                    if fileInfo.suffix().lower() == 'm3u':
                        self.playlist.load(url)
                    else:
                        self.playlist.addMedia(QMediaContent(url))
                else:
                    url = QUrl(name)
                    if url.isValid():
                        self.playlist.addMedia(QMediaContent(url))
        except:
            pass

    def durationChanged(self, duration):
        try:
            duration /= 1000

            self.duration = duration
            self.slider.setMaximum(duration)
        except:
            pass

    def positionChanged(self, progress):
        try:
            progress /= 1000

            if not self.slider.isSliderDown():
                self.slider.setValue(progress)

            self.updateDurationInfo(progress)
        except:
            pass

    def metaDataChanged(self):
        try:
            if self.player.isMetaDataAvailable():
                self.setTrackInfo("%s - %s" % (
                    self.player.metaData(QMediaMetaData.AlbumArtist),
                    self.player.metaData(QMediaMetaData.Title)))
        except:
            pass

    def previousClicked(self):
        try:
            if self.player.position() <= 5000:
                self.playlist.previous()
            else:
                self.player.setPosition(0)
        except:
            pass

    def jump(self, index):
        try:
            if index.isValid():
                self.playlist.setCurrentIndex(index.row())
                self.player.play()
        except:
            pass

    def playlistPositionChanged(self, position):
        try:
            self.playlistView.setCurrentIndex(
                self.playlistModel.index(position, 0))
        except:
            pass

    def seek(self, seconds):
        try:
            self.player.setPosition(seconds * 1000)
        except:
            pass

    def statusChanged(self, status):
        try:
            self.handleCursor(status)

            if status == QMediaPlayer.LoadingMedia:
                self.setStatusInfo("Загрузка...")
            elif status == QMediaPlayer.StalledMedia:
                self.setStatusInfo("Пауза")
            elif status == QMediaPlayer.EndOfMedia:
                QApplication.alert(self)
            elif status == QMediaPlayer.InvalidMedia:
                self.displayErrorMessage()
            else:
                self.setStatusInfo("")
        except:
            pass

    def handleCursor(self, status):
        try:
            if status in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.StalledMedia):
                self.setCursor(Qt.BusyCursor)
            else:
                self.unsetCursor()
        except:
            pass

    def bufferingProgress(self, progress):
        try:
            self.setStatusInfo("Буферизация %d%" % progress)
        except:
            pass

    def setTrackInfo(self, info):
        try:
            self.trackInfo = info

            if self.statusInfo != "":
                self.statusBar.showMessage("%s | %s" % (self.trackInfo, self.statusInfo))
            else:
                self.statusBar.showMessage(self.trackInfo)
        except:
            pass

    def setStatusInfo(self, info):
        try:
            self.statusInfo = info

            if self.statusInfo != "":
                self.statusBar.showMessage("%s | %s" % (self.trackInfo, self.statusInfo))
            else:
                self.statusBar.showMessage(self.trackInfo)
        except:
            pass

    def displayErrorMessage(self):
        try:
            self.setStatusInfo(self.player.errorString())
        except:
            pass

    def updateDurationInfo(self, currentInfo):
        try:
            duration = self.duration
            if currentInfo or duration:
                currentTime = QTime((currentInfo / 3600) % 60, (currentInfo / 60) % 60,
                                    currentInfo % 60, (currentInfo * 1000) % 1000)
                totalTime = QTime((duration / 3600) % 60, (duration / 60) % 60,
                                  duration % 60, (duration * 1000) % 1000)
                format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
                tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
            else:
                tStr = ""

            self.labelDuration.setText(tStr)
        except:
            pass


def stylesheet(self):
    return """
Player
        {
            border: 1px solid #d5d5d5;
            background: #000000;
        }
QSlider::handle:horizontal 
        {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
            width: 6px;
            border: 1px solid #353535;
            border-radius: 0px;
        }
QSlider::groove:horizontal 
        {
            border: 1px solid #353535;
            height: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
        }
QListView
    {
        border: 1px solid #000000;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #000000);
        font-family: Arial;
        font-weight: bold;
        font-size: 8pt;
        color: #eeeeec; 
    }
QListView::item 
    {
        height: 17px;
    }
QListView::item:selected 
    {
        color: #DCDCDC;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
    }
QListView::item:hover
    {   
        border: 0.5px solid #f4f4f4;
        color: black;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #2d9400, stop:1 #39bc00);
        font-weight: bold;       
    }
QPushButton
    {
        height: 22px;
        font-family: Droid Sans;
        font-size: 8pt;
        border: 1px inset #353535;
        border-radius: 0px;
        width: 70px;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
    }
QPushButton::hover
    {
        border: 1px inset #353535;
        border-radius: 0px;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #DCDCDC, stop:1 #808080);
    } 
QPushButton::action
    {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
    } 
QToolButton
    {
        height: 20px;
        font-family: Arial;
        font-size: 8pt;
        border: 1px inset #353535;
        border-radius: 0px;
        width: 32px;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
    } 
QToolButton::hover
    {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #DCDCDC, stop:1 #808080);
    } 
QToolButton::action
    {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C0C0C0, stop:1 #696969);
    } 
QApplication
    {
        background: #000000;
        border: 1px inset #000000;
    }
QStatusBar
    {
        font-family: Arial;
        font-weight: bold;
        font-size: 8pt;
        background: #808080;
        color: #000000;
     }
QLabel
    {
        font-family: Arial;
        font-weight: bold;
        font-size: 8pt;
        color: #eeeeec;
     }
    """
