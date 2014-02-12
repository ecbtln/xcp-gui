from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QCheckBox, \
    QDialog,  QComboBox, QDialogButtonBox, QGridLayout, QGroupBox, QTableWidget, \
    QTableWidgetItem, QAbstractItemView, QHeaderView, QAction, QMenu, QMessageBox, QLabel, QApplication
from PyQt5.QtGui import QRegExpValidator
from PyQt5.Qt import QCursor
from PyQt5.QtCore import QRegExp
from widgets import QAssetValueSpinBox, ShowTransactionDetails


class AssetOwnershipPanel(QGroupBox):
    def __init__(self):
        super(AssetOwnershipPanel, self).__init__("Asset Admin Panel")
        form_layout = QFormLayout()
        issue_asset_button = QPushButton('Issue New Asset')
        issue_asset_button.clicked.connect(self.issue_asset)
        form_layout.addRow(issue_asset_button)
        self.owned_assets = []
        self.no_assets = QLabel('The current address does not own the rights to any assets. You may issue an asset above to get started.')
        self.no_assets.setWordWrap(True)
        form_layout.addRow(self.no_assets)
        self.setLayout(form_layout)
        self.combo_box = QComboBox()
        button_box = QDialogButtonBox()
        button_box.addButton("Send Dividends", QDialogButtonBox.ActionRole)
        button_box.addButton("Callback", QDialogButtonBox.ActionRole)
        button_box2 = QDialogButtonBox()
        button_box2.addButton("Transfer", QDialogButtonBox.ActionRole)
        button_box2.addButton("Issue More", QDialogButtonBox.ActionRole)
        self.button_box = [button_box, button_box2]
        self.update_data()

    def issue_asset(self):
        dialog = AssetIssueDialog()
        dialog.exec_()

    def update_data(self, portfolio=None):
        if portfolio is None:
            assets = []
        else:
            assets = portfolio._assets
        if len(self.owned_assets) > 0 and len(assets) > 0:
            # keep track of which was highlighted
            old = self.combo_box.currentText()
            self.combo_box.clear()
            self.combo_box.addItems(assets)
            if old in assets:
                self.combo_box.setCurrentText(old)
        else:
            self.layout().removeWidget(self.combo_box)
            self.layout().removeWidget(self.no_assets)
            self.layout().removeWidget(self.button_box[0])
            self.layout().removeWidget(self.button_box[1])

            if len(assets) > 0:
                self.combo_box.clear()
                self.combo_box.addItems(assets)
                self.layout().addRow(self.combo_box)
                self.layout().addRow(self.button_box[0])
                self.layout().addRow(self.button_box[1])
            else:
                self.layout().addRow(self.no_assets)

        self.owned_assets = assets
            # reinitialize the form layout


class MyPortfolio(QWidget):
    def __init__(self):
        super(MyPortfolio, self).__init__()
        grid_layout = QGridLayout()
        send_asset_box = QGroupBox("Send Asset")
        send_asset_box.setFixedHeight(200)
        vertical_layout = QVBoxLayout()
        self.send_asset_widget = SendAssetWidget()
        vertical_layout.addWidget(self.send_asset_widget)
        send_asset_box.setLayout(vertical_layout)
        grid_layout.addWidget(send_asset_box, 0, 0)
        self.ownership_panel = AssetOwnershipPanel()
        grid_layout.addWidget(AssetOwnershipPanel(), 1, 0)
        self.asset_table = MyAssetTable()
        grid_layout.addWidget(self.asset_table, 0, 1, 2, 1)
        grid_layout.setColumnStretch(1, 6)
        self.setLayout(grid_layout)

    def update_data(self, portfolio):
        self.asset_table.update_data(portfolio)
        self.send_asset_widget.update_data(portfolio)
        self.ownership_panel.update_data(portfolio)


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
        self.combo_box.setFixedWidth(150)

        form_layout.addRow("Asset: ", self.combo_box)
        self.spinbox = QAssetValueSpinBox()
        self.spinbox.valueChanged.connect(self.enable_disable_send)
        self.spinbox.setFixedWidth(150)
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
        self.update_spinbox_range(QApplication.instance().wallet.active_portfolio)

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
        sender = QApplication.instance().wallet.active_address
        amount = QApplication.instance().wallet.get_asset(asset).format_for_api(amount)

        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()

        QApplication.instance().xcp_client.do_send(sender, recipient, amount, asset, success_callback)