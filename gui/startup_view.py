# TODO: this is where the view with the loading bar will go

from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QColor


class XCPSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(480, 320)
        pixmap.fill(QColor(255, 255, 255))
        super(XCPSplashScreen, self).__init__(pixmap)
        self.showMessage("Establishing connections... (PROOF OF CONCEPT)")