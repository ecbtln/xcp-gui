
import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QCheckBox, \
    QApplication, QDialog, QMainWindow, QComboBox, QDialogButtonBox, QGridLayout, QGroupBox, QTableWidget, \
    QTableWidgetItem, QAbstractItemView, QHeaderView, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QRegExpValidator
from PyQt5.Qt import QCursor
from PyQt5.QtCore import QRegExp
from constants import XCP, BTC
from xcp_async_app_client import XCPAsyncAppClient
from models import Wallet
from widgets import QAssetValueSpinBox
from btc_async_app_client import BTCAsyncAppClient
from utils import display_alert


# stupid hack to get some globals, its a little ugly, but it works
class APP:
    xcp_client = None
    wallet = None
    btc_client = None
    main_window = None

    @classmethod
    def initialize(cls, **kwargs):
        cls.wallet = Wallet()
        cls.main_window = MainWindow()
        # TODO: this has to be called after the pointer is created, so that cls.main_window is not None further down in the init_ui call, there must be a better way
        cls.main_window.init_ui()
        cls.xcp_client = XCPAsyncAppClient(**kwargs[XCP])
        cls.btc_client = BTCAsyncAppClient(**kwargs[BTC])
         # needs to be fetched after to ensure UI is loaded
        cls.fetch_initial_data(lambda addresses: cls.main_window.wallet_view.update_data(addresses))

    @classmethod
    def examine_local_wallet(cls):
        cls.btc_client.get_wallet_addresses(lambda res: cls.wallet.update_addresses(res))

    @classmethod
    def fetch_initial_data(cls, update_addresses_func):
        """
        Fetch the initial data and insert it into our model in the correct format. Because we use callbacks, the
        appearance of this staircase-like method is a bit hideous, but makes the sense if you look at the bottom first.
        Since all callbacks are posted to the main thread, there are no concerns of races.
        """
        wallet = cls.wallet
        cls.examine_local_wallet()  # use the btc rpc to get the addresses in the wallet

        def process_balances(bals):
            portfolios = {}
            assets = set()
            for entry in bals:
                asset = entry['asset']
                assets.add(asset)
                address = entry['address']
                amount = entry['amount']
                if address not in portfolios:
                    portfolios[address] = {}
                p = portfolios[address]
                p[asset] = p.get(asset, 0) + amount
            # don't get_asset_info for XCP, we already know the info and the RCP does not take well with that request
            if XCP in assets:
                assets.remove(XCP)

            asset_name_list = list(assets)

            def process_asset_info(asset_info_results):

                asset_info_list = [{'name': asset_name,
                                    'divisible': res['divisible'],
                                    'callable': res['callable'],
                                    'owner': res['owner']} for asset_name, res in zip(asset_name_list,
                                                                                      asset_info_results)]
                # now massage the portfolios dictionary to be the desired format of the wallet method
                new_portfolios = []
                for address in portfolios:
                    p = portfolios[address]
                    assets = list(p.keys())
                    values = [p[a] for a in assets]
                    new_portfolios.append({'address': address,
                                           'assets': assets,
                                           'values': values})
                wallet.update_portfolios(asset_info_list, new_portfolios)
                update_addresses_func(wallet.addresses)
            cls.xcp_client.get_assets_info(asset_name_list, process_asset_info)

        cls.xcp_client.get_balances(wallet.addresses, process_balances)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Counterparty Exchange')
        central_widget = QWidget(self)
        central_widget.setGeometry(0, 0, self.width(), self.height())  # TODO, this should scale if the window is resized
        grid_layout = QGridLayout()
        tabWidget = QTabWidget()
        tabWidget.addTab(CurrencyExchange(), "Exchange")
        self.asset_exchange = AssetExchange()
        tabWidget.addTab(self.asset_exchange, "My Portfolio")
        tabWidget.addTab(QWidget(), "Asset Info (Lookup)")  # TODO: see http://blockscan.com/assetinfo.aspx?q=ETHEREUM
        tabWidget.addTab(TransactionHistory(), "Transaction History")

        overview = QGroupBox('Overview')
        overview.setFixedWidth(250)
        wallet_view = MyWalletGroupBox()
        self.wallet_view = wallet_view
        grid_layout.addWidget(wallet_view, 0, 1)
        grid_layout.addWidget(overview, 0, 0)
        grid_layout.addWidget(tabWidget, 1, 0, 1, 2)
        central_widget.setLayout(grid_layout)
        self.show()


class MyWalletGroupBox(QGroupBox):
    def __init__(self):
        super(QGroupBox, self).__init__('Wallet')
        self.setFixedHeight(130)
        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.selected_address_changed)
        self.update_data(APP.wallet.addresses)
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
        self.combo_box.clear()
        if len(addresses) > 0:
            self.combo_box.addItems(addresses)
            self.combo_box.setCurrentIndex(0)
        self.selected_address_changed()

    def selected_address_changed(self):
        wallet = APP.wallet
        if self.combo_box.count() == 0:
            wallet.active_address_index = None
        else:
            wallet.active_address_index = self.combo_box.currentIndex()
        APP.main_window.asset_exchange.update_data(wallet.active_portfolio)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.combo_box.currentText())

    def new_address(self):
        def process_address(address):
            print("Generated new address: ", address)
            wallet = APP.wallet
            old = wallet.addresses
            old.append(address)
            wallet.update_addresses(old)
            self.update_data(old)
            display_alert("Added new address (%s) to wallet" % address)
        APP.btc_client.get_new_address(process_address)



class CurrencyExchange(QWidget):
    pass


class AssetExchange(QWidget):
    def __init__(self):
        super(AssetExchange, self).__init__()

        grid_layout = QGridLayout()
        send_asset_box = QGroupBox("Send XCP/Asset")
        vertical_layout = QVBoxLayout()
        self.send_asset_widget = SendAssetWidget()
        vertical_layout.addWidget(self.send_asset_widget)
        send_asset_box.setLayout(vertical_layout)
        grid_layout.addWidget(send_asset_box, 0, 0)
        misc_box = QGroupBox("Other Actions")
        issue_asset_button = QPushButton('Issue an Asset', misc_box)
        do_bet_button = QPushButton('Make Bet', misc_box)
        do_bet_button.move(25, 75)
        issue_asset_button.move(25, 25) # TODO: fix this
        issue_asset_button.clicked.connect(self.present_dialog)
        grid_layout.addWidget(misc_box, 1, 0)
        self.asset_table = MyAssetTable()
        grid_layout.addWidget(self.asset_table, 0, 1, 2, 1)
        self.setLayout(grid_layout)

    def present_dialog(self):
        dialog = AssetIssueDialog()
        dialog.exec_()

    def update_data(self, portfolio):
        self.asset_table.update_data(portfolio)
        self.send_asset_widget.update_data(portfolio)


class MyAssetTable(QTableWidget):
    def __init__(self, *args):
        super(MyAssetTable, self).__init__(*args)
        self.setColumnCount(2)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Asset", "Amount"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cellDoubleClicked.connect(self.contextMenuEvent)

    def update_data(self, portfolio):
        self.clearContents()
        assets = portfolio.assets if portfolio is not None else []
        self.setRowCount(len(assets))
        for i, a in enumerate(assets):
            self.setItem(i, 0, QTableWidgetItem(a.name))
            self.setItem(i, 1, QTableWidgetItem(str(portfolio.amount_for_asset(a.name))))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        infoAction = QAction('Get Info', self)
        infoAction.triggered.connect(self.show_asset_info)
        menu.addAction(infoAction)
        dividends = QAction('Dividends...', self)
        dividends.triggered.connect(self.do_dividends)
        menu.addAction(dividends)
        callback = QAction('Callback...', self)
        callback.triggered.connect(self.do_callback)
        menu.addAction(callback)
        # add other required actions
        menu.popup(QCursor.pos())

    def show_asset_info(self):
        pass

    def do_dividends(self):
        pass

    def do_callback(self):
        pass


class AssetIssueDialog(QDialog):
    def __init__(self):
        super(AssetIssueDialog, self).__init__()
        self.setWindowTitle("Issue Asset?")
        self.resize(300, 160)
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        line_edit = QLineEdit()
        line_edit.setValidator(QRegExpValidator(QRegExp('[a-zA-Z]')))
        line_edit.setPlaceholderText("GOOGL")
        line_edit.setFixedWidth(150)
        form_layout.addRow("Asset name:", line_edit)
        self.spinbox = QAssetValueSpinBox()
        self.spinbox.setFixedWidth(150)
        self.spinbox.setMinimum(1)

        form_layout.addRow("Amount: ", self.spinbox)
        self.divisible_toggle = QCheckBox()
        self.divisible_toggle.stateChanged.connect(self.divisible_toggled)
        form_layout.addRow("Divisible:", self.divisible_toggle)
        form_layout.addRow("Callable:", QCheckBox())
        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        button_box.addButton("Issue Asset", QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setSizeGripEnabled(False)

    def divisible_toggled(self):
        self.spinbox.set_asset_divisible(self.divisible_toggle.isChecked())

    def submit(self):
        # , asset_name, callable, divisible, amount
        print("We should be making a http call!")
        self.close()


class SendAssetWidget(QWidget):
    def __init__(self, *args, **kwargs):
        """
        :param assets: a mapping of all your assets and the amount you have of each
        """
        super(SendAssetWidget, self).__init__(*args, **kwargs)
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        self.line_edit = QLineEdit()
        self.send_button = QPushButton("Send")
        self.line_edit.textChanged.connect(self.enable_disable_send)
        self.line_edit.setPlaceholderText("Destination address")
        self.line_edit.setFixedWidth(150)
        form_layout.addRow("Pay To: ", self.line_edit)
        self.combo_box = QComboBox()

        form_layout.addRow("Asset: ", self.combo_box)
        self.spinbox = QAssetValueSpinBox()
        self.spinbox.valueChanged.connect(self.enable_disable_send)
        self.spinbox.setMinimumWidth(100)
        self.combo_box.currentIndexChanged.connect(self.combo_box_index_changed)
        self.update_data(None)
        form_layout.addRow("Amount: ", self.spinbox)
        button_box = QDialogButtonBox()
        button_box.addButton("Reset", QDialogButtonBox.RejectRole)

        button_box.addButton(self.send_button, QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.reset_form)
        button_box.accepted.connect(self.submit)

    def reset_form(self):
        self.line_edit.setText("")
        self.spinbox.setValue(0)

    def update_data(self, portfolio):
        self.combo_box.clear()
        if portfolio is None:
            num_assets = 0
        else:
            num_assets = len(portfolio.assets)
            self.combo_box.addItems([a.name for a in portfolio.assets])

        self.combo_box.setEnabled(num_assets > 0)
        if num_assets > 0:
            self.combo_box.setCurrentIndex(0)
        self.update_spinbox_range(portfolio)

    def combo_box_index_changed(self):
        self.update_spinbox_range(APP.wallet.active_portfolio)

    def update_spinbox_range(self, portfolio):
        assets = portfolio.assets if portfolio is not None else []
        if len(assets) > 0 and self.combo_box.currentText() != '':
            current_text = self.combo_box.currentText()
            self.spinbox.setMinimum(0)
            amount_in_portfolio = portfolio.amount_for_asset(current_text)
            assert amount_in_portfolio is not None
            asset = portfolio.get_asset(current_text)
            self.spinbox.set_asset_divisible(asset.divisible)
            self.spinbox.setMaximum(amount_in_portfolio)
            self.spinbox.setEnabled(True)
        else:
            self.spinbox.setRange(0, 0)
            self.spinbox.setEnabled(False)

        self.enable_disable_send()

    def enable_disable_send(self):
        self.send_button.setEnabled(len(self.line_edit.text()) > 0 and self.spinbox.value() > 0)

    def submit(self):
        message_box = QMessageBox()
        message_box.setText("Are you sure?")
        message_box.setInformativeText("About to send %s %s to %s.\n\n"
                                       "This operation cannot be undone." % (self.spinbox.text(),
                                                                             self.combo_box.currentText(),
                                                                             self.line_edit.text()))
        message_box.setIcon(QMessageBox.Warning)
        message_box.addButton("Cancel", QMessageBox.RejectRole)
        message_box.addButton("Confirm", QMessageBox.AcceptRole)
        message_box.accepted.connect(self.confirm_send)
        message_box.exec_()

    def confirm_send(self):
        amount = self.spinbox.text()
        asset = self.combo_box.currentText()
        recipient = self.line_edit.text()
        sender = APP.wallet.active_address
        amount = APP.wallet.get_asset(asset).format_for_api(amount)

        def success_callback(response):
            print(response)
            #display_alert("Transaction completed!", str(response))

        APP.xcp_client.do_send(sender, recipient, amount, asset, success_callback)


class TransactionHistory(QWidget):
    #TODO: see http://blockscan.com/address.aspx?q=1FwXZu9j2SZKPHJi3eDpzVrySABJChgJL7
    pass


def main(argv):

    # Parse command-line arguments.
    parser = argparse.ArgumentParser(prog='counterparty-gui', description='the GUI app for the counterparty protocol')
    parser.add_argument('--testnet', action='store_true', help="Whether or not to use the testnet when debugging")
    args = parser.parse_args()
    kwargs = {}
    if args.testnet:
        kwargs[XCP] = {'port': 14000}
        kwargs[BTC] = {'port': 18332}

    app = QApplication(argv)
    APP.initialize(**kwargs)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)