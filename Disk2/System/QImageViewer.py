from PyQt5.QtGui import QImage, QPalette, QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QMainWindow, QMessageBox, QSizePolicy
import os


class ImageViewer(QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.myimage = QImage()
        self.filename = ""
        self.scaleFactor = 1.778

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        mp = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setSizePolicy(mp)
        self.imageLabel.setScaledContents(True)
        self.setCentralWidget(self.imageLabel)

        self.setWindowTitle("ImageViewer")
        self.setWindowIcon(QIcon("images/photoshop.png"))
        w = 400
        h = int(400 / self.scaleFactor)
        self.resize(w, h)
        self.move(0, 0)

    def resizeEvent(self, event):
        try:
            if not self.myimage.isNull():
                self.updateView()
        except:
            pass

    def updateView(self):
        try:
            if self.scaleFactor < 1:
                self.imageLabel.resize(self.height() * self.scaleFactor, self.height())
            else:
                self.imageLabel.resize(self.width(), (self.width() / self.scaleFactor))
            w = self.imageLabel.width()
            h = self.imageLabel.height()
            self.resize(w, h)
        except:
            pass

    def loadFile(self, fileName):
        try:
            if self.filename:
                self.myimage = QImage(self.filename)
            if self.myimage.isNull():
                QMessageBox.information(self, "Image Viewer", "Не удалось загрузить %s." % self.filename)
                return
            self.imageLabel.setPixmap(QPixmap.fromImage(self.myimage))
            self.scaleFactor = int(self.myimage.width()) / int(self.myimage.height())
            f = round(self.scaleFactor, 3)
            if self.scaleFactor < 1:
                self.resize(600 * self.scaleFactor, 600)
            else:
                self.resize(600, 600 / self.scaleFactor)
            self.setWindowTitle(os.path.splitext(str(self.filename))[0].split("/")[-1])
        except:
            pass
