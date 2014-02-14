

from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QColor



class XCPSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(480, 320)
        pixmap.fill(QColor(255, 255, 255))
        super(XCPSplashScreen, self).__init__(pixmap)


    def mousePressEvent(self, QMouseEvent):
        #Don't call super, we don't want this dismissing
        pass