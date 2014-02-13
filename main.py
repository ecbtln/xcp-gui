import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QPushButton, QApplication, QMainWindow, \
    QGridLayout, QGroupBox
from constants import XCP, BTC
from application import XCPApplication
from gui.portfolio_view import MyPortfolio
from gui.asset_exchange_view import AssetExchange
from gui.startup_view import XCPSplashScreen
from gui.my_wallet_view import MyWalletGroupBox


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowTitle('Counterparty Exchange')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout()
        tabWidget = QTabWidget()
        self.asset_exchange = AssetExchange()
        tabWidget.addTab(self.asset_exchange, "Exchange")
        self.my_portfolio = MyPortfolio()
        tabWidget.addTab(self.my_portfolio, "My Portfolio")
        tabWidget.addTab(QWidget(), "Broadcast/Bet")
        tabWidget.addTab(TransactionHistory(), "Transaction History")

        overview = QGroupBox('Overview')
        refresh = QPushButton("Refresh", overview)
        refresh.move(50, 50)
        refresh.clicked.connect(self.fetch_initial_data)
        overview.setFixedWidth(250)
        wallet_view = MyWalletGroupBox(self)
        self.wallet_view = wallet_view
        grid_layout.addWidget(wallet_view, 0, 1)
        grid_layout.addWidget(overview, 0, 0)
        grid_layout.addWidget(tabWidget, 1, 0, 1, 2)
        central_widget.setLayout(grid_layout)
        self.show()

    def fetch_initial_data_lambda(self):
        return lambda results: self.wallet_view.update_data(results)

    def fetch_initial_data(self):
        QApplication.instance().fetch_initial_data(self.fetch_initial_data_lambda())

    def initialize_data_in_tabs(self):
        """
        Called after the initial request is done populating addresses into the wallet
        """
        self.asset_exchange.fetch_data()

class TransactionHistory(QWidget):
    #TODO: see http://blockscan.com/address.aspx?q=1FwXZu9j2SZKPHJi3eDpzVrySABJChgJL7
    pass
    # self.setSelectionBehavior(QAbstractItemView.SelectRows)


def main(argv):
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(prog='counterparty-gui', description='the GUI app for the counterparty protocol')
    parser.add_argument('--testnet', action='store_true', help="Whether or not to use the testnet when debugging")
    args = parser.parse_args()
    options = {}
    if args.testnet:
        options[XCP] = {'port': 14000}
        options[BTC] = {'port': 18332}

    app = XCPApplication(argv, options=options)
    splashScreen = XCPSplashScreen()
    splashScreen.show()
    splashScreen.showMessage("Doing some other stuff")

    app.processEvents()
    # TODO: block main thread as we do stuff
    mw = MainWindow()
    def callback(results):
        mw.fetch_initial_data_lambda()(results)
        mw.initialize_data_in_tabs()

    app.fetch_initial_data(callback)

    splashScreen.finish(mw)
    sys.exit(app.exec())


if __name__ == '__main__':
    main(sys.argv)