from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import QIcon


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.url = ""
        self.setWindowTitle("WebViewer")
        self.setWindowIcon(QIcon("images/microsoft.png"))
        self.setGeometry(0, 0, 800, 720)

        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.setCentralWidget(self.webView)

        self.webView.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
        self.webView.settings().setFontFamily(QtWebEngineWidgets.QWebEngineSettings.SansSerifFont, "SansSerif")
        self.webView.settings().setFontSize(QtWebEngineWidgets.QWebEngineSettings.DefaultFontSize, 9)
        self.webView.loadFinished.connect(self.url_changed)

    def url_changed(self):
        try:
            self.setWindowTitle(self.webView.title())
        except:
            pass

    def go_back(self):
        try:
            self.webView.back()
        except:
            pass

    def load_url(self, path):
        try:
            self.url = path
            self.webView.load(QtCore.QUrl(self.url))
        except:
            pass
