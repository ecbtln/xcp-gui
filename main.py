
import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QCheckBox, \
    QApplication, QDialog, QMainWindow, QComboBox, QSpinBox, QDialogButtonBox, QGridLayout, QGroupBox, QTableWidget, \
    QTableWidgetItem, QAbstractItemView, QHeaderView, QAction, QMenu, QMessageBox
from PyQt5.Qt import QCursor
from constants import MAX_SPINBOX_INT
from xcp_async_app_client import XCPAsyncAppClient, BTC_ADDRESSES

#TODO: use list instead of dictionary so that keys are always ordered consistently

# stupid hack to get the global RPCClient and some other globals
class RPC:
    active_address_index = None
    client = None
    all_addresses = BTC_ADDRESSES

    @classmethod
    def active_address(cls):
        if len(cls.all_addresses) and cls.active_address_index is not None:
            return cls.all_addresses[cls.active_address_index]


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        RPC.client = XCPAsyncAppClient(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Counterparty Exchange')
        central_widget = QWidget(self)
        central_widget.setGeometry(0, 0, self.width(), self.height())  # TODO, this should scale if the window is resized
        grid_layout = QGridLayout()
        tabWidget = QTabWidget()
        # tabWidget.resize(750, 475)
        # tabWidget.move(25, 100)
        tabWidget.addTab(CurrencyExchange(), "BTC/XCP Exchange")
        self.asset_exchange = AssetExchange()
        tabWidget.addTab(self.asset_exchange, "My Portfolio")
        tabWidget.addTab(QWidget(), "Asset Info") # TODO: see http://blockscan.com/assetinfo.aspx?q=ETHEREUM
        tabWidget.addTab(TransactionHistory(), "Transaction History")

        overview = QGroupBox('Overview')
        overview.setFixedWidth(250)
        wallet = MyWalletGroupBox()
        self.wallet = wallet
        wallet.combo_box.currentIndexChanged.connect(self.change_selected_address)
        self.change_selected_address()
        grid_layout.addWidget(wallet, 0, 1)
        grid_layout.addWidget(overview, 0, 0)
        grid_layout.addWidget(tabWidget, 1, 0, 1, 2)
        central_widget.setLayout(grid_layout)
        self.show()

    def change_selected_address(self):
        RPC.active_address_index = self.wallet.combo_box.currentIndex()
        self.asset_exchange.fetch_assets()


class MyWalletGroupBox(QGroupBox):
    def __init__(self):
        super(QGroupBox, self).__init__('Wallet')
        self.setFixedHeight(130)
        self.combo_box = QComboBox()
        self.combo_box.addItems(RPC.all_addresses)
        self.combo_box.setCurrentIndex(0)
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
        issue_asset_button.move(25, 25) # TODO: fix this
        issue_asset_button.clicked.connect(self.present_dialog)
        grid_layout.addWidget(misc_box, 1, 0)
        self.asset_table = MyAssetTable()
        grid_layout.addWidget(self.asset_table, 0, 1, 2, 1)
        self.setLayout(grid_layout)
        self.fetch_assets()

    def fetch_assets(self):
        if RPC.active_address() is None:
            return
        def process_balances(bals):
            assets = {}
            for entry in bals:
                k = entry.get('asset', False)
                if not k:
                    continue
                v = entry.get('amount', 0)
                assets[k] = assets.get(k, 0) + v
            self.set_assets(assets)
        RPC.client.get_balances(RPC.active_address(), process_balances) # TODO: this should be a dynamic address

    def present_dialog(self):
        dialog = AssetIssueDialog()
        dialog.exec_()

    def set_assets(self, assets):
        self.asset_table.update_data(assets)
        self.send_asset_widget.update_assets(assets)


class MyAssetTable(QTableWidget):
    def __init__(self, *args):
        super(MyAssetTable, self).__init__(*args)
        self.setColumnCount(2)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Asset", "Amount"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cellDoubleClicked.connect(self.contextMenuEvent)

    def update_data(self, assets):
        self.clearContents()
        self.setRowCount(len(assets))
        for i, k in enumerate(assets.keys()):
            self.setItem(i, 0, QTableWidgetItem(k))
            self.setItem(i, 1, QTableWidgetItem(str(assets[k])))

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
        self.assets = {}
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
        self.combo_box.currentIndexChanged.connect(self.update_spinbox_range)
        self.update_assets(self.assets)
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

    def update_assets(self, assets):
        self.combo_box.clear()
        all_keys = list(assets.keys())
        num_assets = len(assets)
        self.combo_box.addItems(all_keys)
        self.combo_box.setEnabled(num_assets > 0)
        if num_assets > 0:
            self.combo_box.setCurrentText(all_keys[0])
        self.assets = assets
        self.update_spinbox_range()

    def update_spinbox_range(self):
        if len(self.assets) > 0:
            current_text = self.combo_box.currentText()
            self.spinbox.setMinimum(0)
            #TODO: bug, spinbox only goes up to 2**31 - 1! is this a problem?
            self.spinbox.setMaximum(min(MAX_SPINBOX_INT, self.assets[current_text]))
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
        message_box.setInformativeText("About to send %d %s to %s.\n\nThis operation cannot be undone." % (self.spinbox.value(),
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