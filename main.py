
import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QCheckBox, \
    QApplication, QDialog, QMainWindow, QComboBox, QSpinBox, QDialogButtonBox, QGridLayout, QGroupBox, QTableWidget, \
    QTableWidgetItem, QAbstractItemView, QHeaderView
from xcp_async_app_client import XCPAsyncAppClient, BTC_ADDRESS


# stupid hack to get the global RPCClient
class RPC:
    client = None


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        RPC.client = XCPAsyncAppClient(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Counterparty Exchange')

        tabWidget = QTabWidget(self)
        tabWidget.setLayout(QVBoxLayout())
        tabWidget.resize(750, 475)
        tabWidget.move(25, 100)
        tabWidget.addTab(CurrencyExchange(), "BTC/XCP Exchange")
        tabWidget.addTab(AssetExchange(), "My Portfolio")
        tabWidget.addTab(TransactionHistory(), "Transaction History")
        #self.menuBar().addMenu('Counterparty')
        self.show()


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
        def process_balances(bals):
            assets = {}
            for entry in bals:
                k = entry.get('asset', False)
                if not k:
                    continue
                v = entry.get('amount', 0)
                assets[k] = assets.get(k, 0) + v
            self.set_assets(assets)
        RPC.client.get_balances(BTC_ADDRESS, process_balances) # TODO: this should be a dynamic address

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

    def update_data(self, assets):
        self.clearContents()
        self.setRowCount(len(assets))
        for i, k in enumerate(assets.keys()):
            self.setItem(i, 0, QTableWidgetItem(k))
            self.setItem(i, 1, QTableWidgetItem(str(assets[k])))



class AssetIssueDialog(QDialog):
    def __init__(self):
        super(AssetIssueDialog, self).__init__()
        self.setWindowTitle("Issue Asset for 5 XCP?")
        self.resize(300, 160)
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("GOOGL")
        form_layout.addRow("Asset name:", QLineEdit())
        spinbox = QSpinBox()
        spinbox.setMinimumWidth(100)
        spinbox.setMinimum(1)
        spinbox.setMaximum(99999999999999999)
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
        self.line_edit.setPlaceholderText("Destination address")
        self.line_edit.setFixedWidth(150)
        form_layout.addRow("Pay To: ", self.line_edit)
        self.combo_box = QComboBox()

        form_layout.addRow("Asset: ", self.combo_box)
        self.spinbox = QSpinBox()
        self.spinbox.setMinimumWidth(100)
        self.combo_box.currentIndexChanged.connect(self.update_spinbox_range)
        self.update_assets(self.assets)
        form_layout.addRow("Amount: ", self.spinbox)
        button_box = QDialogButtonBox()
        button_box.addButton("Reset", QDialogButtonBox.RejectRole)
        button_box.addButton("Send", QDialogButtonBox.AcceptRole)
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
            self.spinbox.setRange(0, self.assets[self.combo_box.currentText()])
            self.spinbox.setEnabled(True)
        else:
            self.spinbox.setRange(0, 0)
            self.spinbox.setEnabled(False)

    def submit(self):
        # asset_name, amount, address
        print("We should be making a http call to send the $$")


class TransactionHistory(QWidget):
    pass


def main(argv):
    app = QApplication(argv)
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(prog='counterparty-gui', description='the GUI app for the counterparty protocol')
    parser.add_argument('--debug', action='store_true', help="Whether or not to use the testnet when debugging")
    args = parser.parse_args()
    kwargs = {}
    if args.debug:
        kwargs['port'] = 14000
    mw = MainWindow(**kwargs)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)