
import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QCheckBox, \
    QApplication, QDialog, QMainWindow, QComboBox, QSpinBox, QDialogButtonBox, QGridLayout, QGroupBox, QTableWidget, \
    QTableWidgetItem, QAbstractItemView, QHeaderView, QAction, QMenu, QMessageBox
from PyQt5.Qt import QCursor
from constants import MAX_SPINBOX_INT, XCP, BTC_ADDRESSES
from xcp_async_app_client import XCPAsyncAppClient
from models import Wallet, Asset, Portfolio


# stupid hack to get the global RPCClient and some other globals
class APP:
    rpc_client = None
    wallet = Wallet(BTC_ADDRESSES)


class MainWindow(QMainWindow):
    singleton = None

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        MainWindow.singleton = self
        APP.rpc_client = XCPAsyncAppClient(*args, **kwargs)
        self.init_ui()
        # needs to be fetched after to ensure UI is loaded
        self.fetch_initial_data()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Counterparty Exchange')
        central_widget = QWidget(self)
        central_widget.setGeometry(0, 0, self.width(), self.height())  # TODO, this should scale if the window is resized
        grid_layout = QGridLayout()
        tabWidget = QTabWidget()
        tabWidget.addTab(CurrencyExchange(), "BTC/XCP Exchange")
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

    def fetch_initial_data(self):
        wallet = APP.wallet

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
                self.wallet_view.update_data(wallet.addresses)
            APP.rpc_client.get_assets_info(asset_name_list, process_asset_info)

        APP.rpc_client.get_balances(wallet.addresses, process_balances)
        #TODO: here's where we would first get the wallet addresses, but we'll take these for granted


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
        MainWindow.singleton.asset_exchange.update_data(wallet.active_portfolio)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.combo_box.currentText())


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
        line_edit.setPlaceholderText("GOOGL")
        form_layout.addRow("Asset name:", QLineEdit())
        spinbox = QSpinBox()
        spinbox.setMinimumWidth(100)
        spinbox.setMinimum(1)
        spinbox.setMaximum(MAX_SPINBOX_INT)
        form_layout.addRow("Amount: ", spinbox)
        form_layout.addRow("Divisible:", QCheckBox())
        form_layout.addRow("Callable:", QCheckBox())
        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        button_box.addButton("Issue Asset", QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setSizeGripEnabled(False)

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
        self.spinbox = QSpinBox()
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
        if len(assets) > 0:
            current_text = self.combo_box.currentText()
            self.spinbox.setMinimum(0)
            #TODO: bug, spinbox only goes up to 2**31 - 1! is this a problem?
            amount_in_portfolio = portfolio.amount_for_asset(current_text)
            assert amount_in_portfolio is not None
            self.spinbox.setMaximum(min(MAX_SPINBOX_INT, amount_in_portfolio ))
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
        message_box.setInformativeText("About to send %d %s to %s.\n\n"
                                       "This operation cannot be undone." % (self.spinbox.value(),
                                                                            self.combo_box.currentText(),
                                                                            self.line_edit.text()))
        message_box.setIcon(QMessageBox.Warning)
        message_box.addButton("Cancel", QMessageBox.RejectRole)
        message_box.addButton("Confirm", QMessageBox.AcceptRole)
        message_box.exec_()


class TransactionHistory(QWidget):
    #TODO: see http://blockscan.com/address.aspx?q=1FwXZu9j2SZKPHJi3eDpzVrySABJChgJL7
    pass


def main(argv):
    app = QApplication(argv)
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(prog='counterparty-gui', description='the GUI app for the counterparty protocol')
    parser.add_argument('--testnet', action='store_true', help="Whether or not to use the testnet when debugging")
    args = parser.parse_args()
    kwargs = {}
    if args.testnet:
        kwargs['port'] = 14000
    mw = MainWindow(**kwargs)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)