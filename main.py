__author__ = 'elubin'

import sys
import argparse
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QCheckBox, \
    QApplication, QDialog, QMainWindow, QComboBox, QSpinBox
from PyQt5.QtCore import Qt
from xcp_async_app_client import XCPAsyncAppClient, BTC_ADDRESS


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.addresses = [BTC_ADDRESS]
        self.client = XCPAsyncAppClient(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Counterparty (XCP)')

        tabWidget = QTabWidget(self)
        tabWidget.setLayout(QVBoxLayout())
        tabWidget.resize(750, 475)
        tabWidget.move(25, 100)
        #tabWidget.addTab(Send
        tabWidget.addTab(SendDialog(assets={'XCP': 1000, 'FUCK':100990012}), "Send")
        tabWidget.addTab(CurrencyExchange(), "BTC/XCP Exchange")
        tabWidget.addTab(AssetExchange(), "Assets")
        tabWidget.addTab(TransactionHistory(), "Transaction History")
        #self.menuBar().addMenu('Counterparty')
        self.show()


class CurrencyExchange(QWidget):
    pass


class AssetExchange(QWidget):
    def __init__(self):
        super(AssetExchange, self).__init__()
        button = QPushButton('Issue an Asset', self)
        button.clicked.connect(self.present_dialog)

    def present_dialog(self):
        dialog = AssetIssueDialog()
        dialog.exec_()


class AssetIssueDialog(QDialog):
    def __init__(self):
        super(AssetIssueDialog, self).__init__()
        self.setWindowTitle("Issue Asset for 5 XCP?")
        self.resize(300, 160)
        form_layout = QFormLayout(self)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("GOOGL")
        form_layout.addRow("Asset name:", QLineEdit())
        form_layout.addRow("Divisible:", QCheckBox())
        form_layout.addRow("Callable:", QCheckBox())
        cancel = QPushButton('Cancel', self)
        cancel.move(25, 110)
        issue = QPushButton('Issue Asset', self)
        issue.move(175, 110)
        cancel.clicked.connect(self.close)
        issue.clicked.connect(self.submit)
        #self.overrideWindowFlags(Qt.WindowCloseButtonHint)
        self.setSizeGripEnabled(False)

    def submit(self):
        print("We should be making a http call!")
        self.close()


class SendDialog(QDialog):
    def __init__(self, assets):
        """
        :param assets: a mapping of all your assets and the amount you have of each
        """
        super(SendDialog, self).__init__()
        self.assets = assets
        self.setWindowTitle("Send XCP/Asset")
        form_layout = QFormLayout(self)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Destination address")
        form_layout.addRow("Pay To: ", line_edit)
        self.combo_box = QComboBox()
        self.combo_box.addItems(list(assets.keys()))
        if len(assets) <= 1:
            self.combo_box.setDisabled(True)
        form_layout.addRow("Asset: ", self.combo_box)
        self.spinbox = QSpinBox()
        self.combo_box.currentIndexChanged.connect(self.update_spinbox_range)
        self.update_spinbox_range()
        form_layout.addRow("Amount: ", self.spinbox)

    def update_spinbox_range(self):
        self.spinbox.setRange(0, self.assets[self.combo_box.currentText()])


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