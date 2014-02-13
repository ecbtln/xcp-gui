

from PyQt5.QtWidgets import QSplashScreen, QProgressBar
from PyQt5.QtGui import QPixmap, QColor



class XCPSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(480, 320)
        pixmap.fill(QColor(255, 255, 255))
        super(XCPSplashScreen, self).__init__(pixmap)
        self.bar = QProgressBar(self)
        self.bar.setFixedWidth(200)
        self.bar.setRange(0, 100)
        self.bar.move(175, 175)