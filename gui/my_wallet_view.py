from PyQt5.QtWidgets import QGroupBox, QComboBox, QApplication, QFormLayout, QDialogButtonBox, QPushButton, QCheckBox
from utils import display_alert


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
        # TODO: add checkbox for toggle between showing all accounts and showing only accounts that have BTC in them
        self.check_box = QCheckBox()
        button_box = QDialogButtonBox()
        copy_address = QPushButton("Copy Address")
        copy_address.clicked.connect(self.copy_to_clipboard)
        button_box.addButton(copy_address, QDialogButtonBox.NoRole)
        new_address = QPushButton("New Address")
        new_address.clicked.connect(self.new_address)
        button_box.addButton(new_address, QDialogButtonBox.ResetRole)
        form_layout.addRow(button_box)
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

