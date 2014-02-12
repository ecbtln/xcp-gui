
import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QPushButton, QFormLayout, QApplication, QMainWindow, \
    QComboBox, QDialogButtonBox, QGridLayout, QGroupBox
from constants import XCP, BTC
from utils import display_alert
from application import XCPApplication
from gui.portfolio_view import MyPortfolio
from gui.asset_exchange_view import AssetExchange

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

        #central_widget.setGeometry(0, 0, self.width(), self.height())  # TODO, this should scale if the window is resized
        grid_layout = QGridLayout()
        tabWidget = QTabWidget()
        tabWidget.addTab(AssetExchange(), "Exchange")
        self.my_portfolio = MyPortfolio()
        tabWidget.addTab(self.my_portfolio, "My Portfolio")
        tabWidget.addTab(QWidget(), "Asset Info (Lookup)")  # TODO: see http://blockscan.com/assetinfo.aspx?q=ETHEREUM
        tabWidget.addTab(QWidget(), "Broadcast/Bet")
        tabWidget.addTab(TransactionHistory(), "Transaction History")

        overview = QGroupBox('Overview')
        refresh = QPushButton("Refresh", overview)
        refresh.clicked.connect(QApplication.instance().fetch_initial_data)
        overview.setFixedWidth(250)
        wallet_view = MyWalletGroupBox(self)
        self.wallet_view = wallet_view
        grid_layout.addWidget(wallet_view, 0, 1)
        grid_layout.addWidget(overview, 0, 0)
        grid_layout.addWidget(tabWidget, 1, 0, 1, 2)
        central_widget.setLayout(grid_layout)
        self.show()


class MyWalletGroupBox(QGroupBox):
    def __init__(self, parent):
        super(QGroupBox, self).__init__('Wallet')
        self.setFixedHeight(110)
        self.mw = parent
        self.combo_box = QComboBox()
        self.combo_box.setMinimumWidth(330)
        self.combo_box.currentIndexChanged.connect(self.selected_address_changed)
        self.update_data(QApplication.instance().wallet.addresses)
        form_layout = QFormLayout()
        form_layout.addRow("Select an Address: ", self.combo_box)
        button_box = QDialogButtonBox()
        export = QPushButton("Export")
        button_box.addButton(export, QDialogButtonBox.NoRole)
        copy_address = QPushButton("Copy Address")
        copy_address.clicked.connect(self.copy_to_clipboard)
        button_box.addButton(copy_address, QDialogButtonBox.NoRole)
        new_address = QPushButton("New Address")
        new_address.clicked.connect(self.new_address)
        button_box.addButton(new_address, QDialogButtonBox.ResetRole)
        form_layout.addRow(button_box)
        #TODO: fix vertical alignment
        #form_layout.setAlignment(Qt.)
        self.setLayout(form_layout)

    def update_data(self, addresses):
        old = self.combo_box.currentText()
        self.combo_box.clear()
        if len(addresses) > 0:
            self.combo_box.addItems(addresses)
            self.combo_box.setCurrentIndex(0)
            if old in addresses:
                self.combo_box.setCurrentText(old)
        self.selected_address_changed()

    def selected_address_changed(self):
        wallet = QApplication.instance().wallet
        if self.combo_box.count() == 0:
            wallet.active_address_index = None
        else:
            wallet.active_address_index = self.combo_box.currentIndex()

        self.mw.my_portfolio.update_data(wallet.active_portfolio)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.combo_box.currentText())

    def new_address(self):
        def process_address(address):
            print("Generated new address: ", address)
            wallet = QApplication.instance().wallet
            old = wallet.addresses
            old.append(address)
            wallet.update_addresses(old)
            self.update_data(old)
            display_alert("Added new address (%s) to wallet" % address)
        QApplication.instance().btc_client.get_new_address(process_address)


class TransactionHistory(QWidget):
    #TODO: see http://blockscan.com/address.aspx?q=1FwXZu9j2SZKPHJi3eDpzVrySABJChgJL7
    pass


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
    mw = MainWindow()
    app.fetch_initial_data(lambda x: mw.wallet_view.update_data(x))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)