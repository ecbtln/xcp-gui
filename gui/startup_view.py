
from . import PyQtGui, PyQt

class XCPSplashScreen(PyQtGui.QSplashScreen):
    def __init__(self):
        pixmap = PyQt.QtGui.QPixmap(480, 320)
        pixmap.fill(PyQt.QtGui.QColor(255, 255, 255))
        super(XCPSplashScreen, self).__init__(pixmap)


    def mousePressEvent(self, QMouseEvent):
        #Don't call super, we don't want this dismissing
        pass
