__author__ = 'elubin'


import sys
from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Counterparty Exchange')

        tabBar = QtWidgets.QTabBar()
        self.show()

def main(argv):
    app = QtWidgets.QApplication(argv)
    mw = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)