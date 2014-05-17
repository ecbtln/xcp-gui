from . import PyQtGui, PyQt, PY_QT5
from .widgets import QAssetValueSpinBox, ShowTransactionDetails, AssetLineEdit
from constants import MAX_BYTES_ASSET_DESCRIPTION, MAX_SPINBOX_INT, MIN_LENGTH_ASSET_NAME, XCP
from models import Asset


class MyPortfolio(PyQtGui.QWidget):
    def __init__(self):
        super(MyPortfolio, self).__init__()
        grid_layout = PyQtGui.QGridLayout()
        send_asset_box = PyQtGui.QGroupBox("Send Asset")
        send_asset_box.setFixedHeight(200)
        vertical_layout = PyQtGui.QVBoxLayout()
        self.send_asset_widget = SendAssetWidget()
        vertical_layout.addWidget(self.send_asset_widget)
        send_asset_box.setLayout(vertical_layout)
        grid_layout.addWidget(send_asset_box, 0, 0)
        asset_ownership_box = PyQtGui.QGroupBox("Asset Admin Panel")
        vertical_layout = PyQtGui.QVBoxLayout()
        self.ownership_panel = AssetOwnershipPanel()
        vertical_layout.addWidget(self.ownership_panel)
        asset_ownership_box.setLayout(vertical_layout)
        grid_layout.addWidget(asset_ownership_box, 1, 0)
        self.asset_table = MyAssetTable()
        grid_layout.addWidget(self.asset_table, 0, 1, 2, 1)
        grid_layout.setColumnStretch(1, 6)
        self.setLayout(grid_layout)

    def update_data(self, portfolio):
        self.asset_table.update_data(portfolio)
        self.send_asset_widget.update_data(portfolio)
        self.ownership_panel.update_data(portfolio)


class AssetOwnershipPanel(PyQtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(AssetOwnershipPanel, self).__init__(*args, **kwargs)
        layout = PyQtGui.QFormLayout()
        issue_asset_button = PyQtGui.QPushButton('Issue New Asset')
        issue_asset_button.clicked.connect(self.issue_asset)
        layout.addRow(issue_asset_button)
        self.owned_assets = []
        self.combo_box = PyQtGui.QComboBox()
        layout.addRow(self.combo_box)
        button_box = PyQtGui.QDialogButtonBox()
        send_dividends_button = PyQtGui.QPushButton("Send Dividends")
        send_dividends_button.clicked.connect(self.do_dividends)
        button_box.addButton(send_dividends_button, PyQtGui.QDialogButtonBox.ActionRole)
        button_box.addButton("Callback", PyQtGui.QDialogButtonBox.ActionRole)
        button_box2 = PyQtGui.QDialogButtonBox()
        transfer_asset_button = PyQtGui.QPushButton("Transfer")
        button_box2.addButton(transfer_asset_button, PyQtGui.QDialogButtonBox.ActionRole)
        transfer_asset_button.clicked.connect(self.transfer_asset)
        button_box2.addButton("Issue More", PyQtGui.QDialogButtonBox.ActionRole)
        self.button_box = [button_box, button_box2]
        layout.addRow(self.button_box[0])
        layout.addRow(self.button_box[1])

        self.setLayout(layout)
        self.update_data()

    def current_asset(self):
        return self.combo_box.currentText()

    def do_dividends(self):
        DoDividendDialog(self.current_asset()).exec_()

    def transfer_asset(self):
        TransferAssetDialog(self.current_asset()).exec_()

    def issue_asset(self):
        dialog = AssetIssueDialog()
        dialog.exec_()

    def update_data(self, portfolio=None):
        self.combo_box.clear()
        if portfolio is None:
            assets = []
            num_assets = 0
        else:
            assets = [a.name for a in portfolio.assets if portfolio.owns_asset(a.name)]
            num_assets = len(assets)

        self.combo_box.setEnabled(num_assets > 0)
        self.button_box[0].setEnabled(num_assets > 0)
        self.button_box[1].setEnabled(num_assets > 0)

        if num_assets > 0:
            self.combo_box.addItems(assets)




class MyAssetTable(PyQtGui.QTableWidget):
    def __init__(self, *args):
        super(MyAssetTable, self).__init__(*args)
        self.setColumnCount(2)
        self.setEditTriggers(PyQtGui.QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Asset", "Amount"])
        if PY_QT5:
            self.horizontalHeader().setSectionResizeMode(PyQtGui.QHeaderView.Stretch)
        else:
            self.horizontalHeader().setResizeMode(PyQtGui.QHeaderView.Stretch)
        self.setSelectionBehavior(PyQtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(PyQtGui.QAbstractItemView.SingleSelection)

    def update_data(self, portfolio):
        self.clearContents()
        assets = portfolio.assets if portfolio is not None else []
        self.setRowCount(len(assets))
        for i, a in enumerate(assets):
            self.setItem(i, 0, PyQtGui.QTableWidgetItem(a.name))
            self.setItem(i, 1, PyQtGui.QTableWidgetItem(a.format_quantity(portfolio.amount_for_asset(a.name))))


class AssetIssueDialog(PyQtGui.QDialog):
    def __init__(self):
        super(AssetIssueDialog, self).__init__()
        self.setWindowTitle("Issue Asset?")
        self.resize(300, 160)

        self.line_edit = AssetLineEdit()
        self.line_edit.textChanged.connect(self.processAssetNameChange)
        self.setToolTip("Issue a new asset")

        self.line_edit.setFixedWidth(150)

        self.spinbox = QAssetValueSpinBox()
        self.spinbox.setFixedWidth(150)
        self.spinbox.setMinimum(1)
        self.line_edit.setToolTip("The asset to issue")
        self.spinbox.setToolTip("The amount of the asset to issue")


        self.asset_description = PyQtGui.QPlainTextEdit()
        self.asset_description.textChanged.connect(self.processChangedText)
        self.asset_description.setToolTip("A textual description for the asset")

        self.divisible_toggle = PyQtGui.QCheckBox()
        self.divisible_toggle.setToolTip("Whether this asset is divisible or not")
        self.divisible_toggle.stateChanged.connect(self.divisible_toggled)

        self.callable_toggle = PyQtGui.QCheckBox()
        #self.callable_toggle.stateChanged.connect(self.regenerate_form)

        self.callable_toggle.setToolTip("Whether the asset is callable or not.")
        button_box = PyQtGui.QDialogButtonBox()
        button_box.addButton("Cancel", PyQtGui.QDialogButtonBox.RejectRole)
        self.issue_button = PyQtGui.QPushButton("Issue Asset")
        button_box.addButton(self.issue_button, PyQtGui.QDialogButtonBox.AcceptRole)
        self.issue_button.setEnabled(False)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.button_box = button_box
        self.setSizeGripEnabled(False)
        self.call_date = PyQtGui.QCalendarWidget()
        self.call_date.setSelectionMode(PyQtGui.QCalendarWidget.SingleSelection)
        self.call_date.setHorizontalHeaderFormat(PyQtGui.QCalendarWidget.SingleLetterDayNames)
        self.call_date.setToolTip("The timestamp at which the asset may be called back, in Unix time. Only valid for callable assets.")
        self.call_price = PyQtGui.QDoubleSpinBox()
        self.call_price.setMinimum(0)
        self.call_price.setMaximum(MAX_SPINBOX_INT)
        self.call_price.setToolTip("The price at which the asset may be called back, on the specified call_date.")
        self.regenerate_form()

    def regenerate_form(self):

        form_layout = PyQtGui.QFormLayout()
        form_layout.addRow("Asset name:", self.line_edit)
        form_layout.addRow("Amount: ", self.spinbox)
        form_layout.addRow("Description: ", self.asset_description)
        form_layout.addRow("Divisible:", self.divisible_toggle)
        form_layout.addRow("Callable:", self.callable_toggle)
        # TODO: add support for these to be toggled on the callable toggle
        #if self.callable_toggle.isChecked():
        form_layout.addRow("Call Date: ", self.call_date)
        form_layout.addRow("Call Price: ", self.call_price)
        form_layout.addRow(self.button_box)
        self.setLayout(form_layout)

    def divisible_toggled(self):
        self.spinbox.set_asset_divisible(self.divisible_toggle.isChecked())

    def submit(self):
        source = PyQtGui.QApplication.instance().wallet.active_address
        divisible = bool(self.divisible_toggle.isChecked())
        callable = bool(self.callable_toggle.isChecked())
        asset = self.line_edit.text()
        description = self.asset_description.toPlainText()
        a = Asset(asset, divisible, callable, source)
        quantity = a.convert_for_api(self.spinbox.value())
        if callable:
            call_price = int(self.call_price.value())
            call_date = self.call_date.selectedDate()
            datetime = PyQt.QtCore.QDateTime(call_date)
            datetime = int(datetime.toMSecsSinceEpoch() / 1000)
        else:
            call_price = 0
            datetime = 0

        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()

        PyQtGui.QApplication.instance().xcp_client.do_issuance(source, quantity, asset, divisible, description, callable, datetime, call_price, success_callback)
        self.close()

    def processChangedText(self):
        string = self.asset_description.toPlainText()
        if len(string) > MAX_BYTES_ASSET_DESCRIPTION:
            self.asset_description.setPlainText(string[:MAX_BYTES_ASSET_DESCRIPTION])
            self.asset_description.moveCursor(PyQtGui.QTextCursor.End)

    def processAssetNameChange(self):
        self.issue_button.setEnabled(len(self.line_edit.text()) >= MIN_LENGTH_ASSET_NAME)


class SendAssetWidget(PyQtGui.QWidget):
    def __init__(self, *args, **kwargs):
        """
        :param assets: a mapping of all your assets and the amount you have of each
        """
        super(SendAssetWidget, self).__init__(*args, **kwargs)
        form_layout = PyQtGui.QFormLayout()
        self.setLayout(form_layout)
        self.line_edit = PyQtGui.QLineEdit()
        self.setToolTip("Send XCP or a user defined asset.")
        self.send_button = PyQtGui.QPushButton("Send")
        self.line_edit.textChanged.connect(self.enable_disable_send)
        self.line_edit.setPlaceholderText("Destination address")
        self.line_edit.setFixedWidth(150)
        form_layout.addRow("Pay To: ", self.line_edit)
        self.line_edit.setToolTip("The address to receive the asset")
        self.combo_box = PyQtGui.QComboBox()
        self.combo_box.setFixedWidth(150)
        self.combo_box.setToolTip("The asset to send")

        form_layout.addRow("Asset: ", self.combo_box)
        self.spinbox = QAssetValueSpinBox()
        self.spinbox.valueChanged.connect(self.enable_disable_send)
        self.spinbox.setFixedWidth(150)
        self.combo_box.currentIndexChanged.connect(self.combo_box_index_changed)
        self.update_data(None)
        form_layout.addRow("Amount: ", self.spinbox)
        self.spinbox.setToolTip("The amount of the asset to send.")
        button_box = PyQtGui.QDialogButtonBox()
        button_box.addButton("Reset", PyQtGui.QDialogButtonBox.RejectRole)

        button_box.addButton(self.send_button, PyQtGui.QDialogButtonBox.AcceptRole)
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
        self.update_spinbox_range(PyQtGui.QApplication.instance().wallet.active_portfolio)

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
        message_box = PyQtGui.QMessageBox()
        message_box.setText("Are you sure?")
        message_box.setInformativeText("About to send %s %s to %s.\n\n"
                                       "This operation cannot be undone." % (self.spinbox.text(),
                                                                             self.combo_box.currentText(),
                                                                             self.line_edit.text()))
        message_box.setIcon(PyQtGui.QMessageBox.Warning)
        message_box.addButton("Cancel", PyQtGui.QMessageBox.RejectRole)
        message_box.addButton("Confirm", PyQtGui.QMessageBox.AcceptRole)
        message_box.accepted.connect(self.confirm_send)
        message_box.exec_()

    def confirm_send(self):
        amount = self.spinbox.text()
        asset = self.combo_box.currentText()
        recipient = self.line_edit.text()
        sender = PyQtGui.QApplication.instance().wallet.active_address
        amount = PyQtGui.QApplication.instance().wallet.get_asset(asset).convert_for_api(amount)

        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()

        PyQtGui.QApplication.instance().xcp_client.do_send(sender, recipient, amount, asset, success_callback)


class DoDividendDialog(PyQtGui.QDialog):
    def __init__(self, asset, *args, **kwargs):
        super(DoDividendDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Issue Dividends for %s" % asset)
        self.asset = asset
        form_layout = PyQtGui.QFormLayout()
        self.spinbox = QAssetValueSpinBox()
        self.spinbox.set_asset_divisible(True)
        form_layout.addRow("Quantity Per Unit: ", self.spinbox)
        self.spinbox.setToolTip("The amount of XCP rewarded per whole unit of the asset.")
        button_box = PyQtGui.QDialogButtonBox()
        button_box.addButton("Cancel", PyQtGui.QDialogButtonBox.RejectRole)
        self.send_button = PyQtGui.QPushButton("Send")
        button_box.addButton(self.send_button, PyQtGui.QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setLayout(form_layout)

    def submit(self):
        app = PyQtGui.QApplication.instance()
        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()
        wallet = app.wallet
        a = wallet.get_asset(XCP)

        app.xcp_client.do_dividend(wallet.active_address,
                                   a.convert_for_api(self.spinbox.value()),
                                   self.asset,
                                   success_callback)
        self.close()


class TransferAssetDialog(PyQtGui.QDialog):
    def __init__(self, asset, *args, **kwargs):
        super(TransferAssetDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Transfer %s to..." % asset)
        self.asset = asset
        form_layout = PyQtGui.QFormLayout()
        self.to_address = PyQtGui.QLineEdit()
        self.to_address.setToolTip("The address to receive the asset")
        form_layout.addRow("Transfer to: ", self.to_address)
        self.setToolTip("Transfer the ownership of an asset.")
        button_box = PyQtGui.QDialogButtonBox()
        button_box.addButton("Cancel", PyQtGui.QDialogButtonBox.RejectRole)
        self.send_button = PyQtGui.QPushButton("Transfer")
        button_box.addButton(self.send_button, PyQtGui.QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setLayout(form_layout)
        self.to_address.textChanged.connect(self.to_changed)
        self.to_changed()

    def to_changed(self):
        self.send_button.setEnabled(len(self.to_address.text()) > 0)

    def submit(self):
        app = PyQtGui.QApplication.instance()
        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()
        wallet = app.wallet
        a = wallet.get_asset(self.asset)
        #TODO: it doesn't look like this API is set up in the backend yet
        app.xcp_client.do_transfer(app.wallet.active_address, self.asset, a.divisible, self.to_address.text()
             ,success_callback)
        self.close()




