from PyQt5.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QGroupBox, QVBoxLayout,\
    QDialogButtonBox, QPushButton, QHeaderView, QTableWidgetItem, QApplication, QDialog, QFormLayout, QComboBox, \
    QLineEdit, QLabel
from constants import BTC, MAX_SPINBOX_INT
from widgets import QAssetValueSpinBox, AssetLineEdit, ShowTransactionDetails
from .asset_info_view import AssetInfoView

class AssetExchange(QWidget):
    def __init__(self, *args, **kwargs):
        super(AssetExchange, self).__init__(*args, **kwargs)

        glob_vbox_layout = QVBoxLayout()
        place_new_order = QPushButton("Place Order")
        # TODO: present new page with a way to filter all orders, and sort, by stock, by price, etc
        # lookup_orders = QPushButton("Filter Orders")
        do_btc_pay = QPushButton("BTC Pay")
        cancel_order = QPushButton("Cancel Order")
        # asset_lookup = QPushButton("Lookup Asset")
        button_box = QDialogButtonBox()
        button_box.addButton(place_new_order, QDialogButtonBox.NoRole)
        button_box.addButton(do_btc_pay, QDialogButtonBox.NoRole)
        button_box.addButton(cancel_order, QDialogButtonBox.NoRole)
        # button_box.addButton(asset_lookup,QDialogButtonBox.ActionRole)
        # button_box.addButton(lookup_orders, QDialogButtonBox.ActionRole)

        place_new_order.clicked.connect(self.place_order)
        cancel_order.clicked.connect(self.cancel_order)
        do_btc_pay.clicked.connect(self.do_btc_pay)
        # asset_lookup.clicked.connect(self.lookup_asset)

        glob_vbox_layout.addWidget(button_box)
        vbox_layout = QVBoxLayout()
        group_box = QGroupBox('Open Orders (Double click to cancel)')
        self.open_orders = OpenOrdersTableView()
        vbox_layout.addWidget(self.open_orders)
        group_box.setLayout(vbox_layout)
        glob_vbox_layout.addWidget(group_box)
        group_box = QGroupBox('Order Matches')
        vbox_layout = QVBoxLayout()
        self.order_matches = OrderMatchesTableView()
        vbox_layout.addWidget(self.order_matches)
        group_box.setLayout(vbox_layout)
        glob_vbox_layout.addWidget(group_box)
        self.setLayout(glob_vbox_layout)

    def fetch_data(self):
        self.fetch_open_orders()
        self.fetch_matched_orders()

    def place_order(self):
        PickGetAssetOrderDialog().exec_()

    def cancel_order(self):
        cancel_order_ui = CancelOrderDialog()
        cancel_order_ui.exec_()

    def do_btc_pay(self):
        btc_pay_ui = BTCPayDialog()
        btc_pay_ui.exec_()

    def lookup_asset(self, asset=None):
        info_view = AssetInfoView(asset)
        info_view.exec_()

    def fetch_matched_orders(self):
        app = QApplication.instance()
        def callback(matched_orders):
            self.order_matches.setRowCount(len(matched_orders))
            self.order_matches.data = matched_orders
            for i, o in enumerate(matched_orders):
                self.order_matches.setItem(i, 0, QTableWidgetItem('%d' % o['tx0_index']))
                forward_asset = o['forward_asset']
                forward_asset_obj = app.wallet.get_asset(forward_asset)
                forward_amount = str(forward_asset_obj.convert_for_app(o['forward_amount']))
                backward_asset = o['backward_asset']
                backward_asset_obj = app.wallet.get_asset(backward_asset)
                backward_amount = str(backward_asset_obj.convert_for_app(o['backward_amount']))
                self.order_matches.setItem(i, 1, QTableWidgetItem(o['tx0_address']))
                self.order_matches.setItem(i, 2, QTableWidgetItem('%s %s' % (forward_amount, forward_asset)))
                self.order_matches.setItem(i, 3, QTableWidgetItem('%d' % o['tx1_index']))
                self.order_matches.setItem(i, 4, QTableWidgetItem(o['tx1_address']))
                self.order_matches.setItem(i, 5, QTableWidgetItem('%s %s' % (backward_amount, backward_asset)))
                self.order_matches.setItem(i, 6, QTableWidgetItem(o['validity']))
        app.xcp_client.get_order_matches(callback)

    def fetch_open_orders(self):
        app = QApplication.instance()
        addresses = app.wallet.addresses
        def callback(orders):
            self.open_orders.data = orders
            self.open_orders.setRowCount(len(orders))
            btc = QApplication.instance().wallet.get_asset(BTC)
            for i, o in enumerate(orders):
                self.open_orders.setItem(i, 0, QTableWidgetItem('%d' % o['tx_index']))
                get_asset = o['get_asset']
                get_asset_obj = app.wallet.get_asset(get_asset)
                get_amount = str(get_asset_obj.convert_for_app(o['get_amount']))
                give_asset = o['give_asset']
                give_asset_obj = app.wallet.get_asset(give_asset)
                give_amount = str(give_asset_obj.convert_for_app(o['give_amount']))
                self.open_orders.setItem(i, 1, QTableWidgetItem('%s %s' % (get_amount, get_asset)))
                self.open_orders.setItem(i, 2, QTableWidgetItem('%s %s' % (give_amount, give_asset)))
                self.open_orders.setItem(i, 3, QTableWidgetItem('%.2f %s/%s' % (float(give_amount)/float(get_amount), give_asset, get_asset)))
                self.open_orders.setItem(i, 4, QTableWidgetItem('%d' % (o['block_index'] + o['expiration'])))

                self.open_orders.setItem(i, 5, QTableWidgetItem(str(btc.convert_for_app(o['fee_required']))))
                self.open_orders.setItem(i, 6, QTableWidgetItem(str(btc.convert_for_app(o['fee_provided']))))
                self.open_orders.setItem(i, 7, QTableWidgetItem('%s %s' %
                                                    (give_asset_obj.convert_for_app(o['give_remaining']), give_asset)))


        app.xcp_client.get_orders(addresses, callback)


class OrderMatchesTableView(QTableWidget):
    def __init__(self, *args):
        super(OrderMatchesTableView, self).__init__(*args)
        self.data = None
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        cols = ["Tx0", "Tx0_address", "Forward Asset", "Tx1", "Tx1_address", "Backward asset", "Validity"]
        self.setColumnCount(len(cols))
        self.setHorizontalHeaderLabels(cols) #
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.data = None
        #self.cellDoubleClicked.connect(self.doubleClickedCell)
        #TODO: figure out the correct api call to get this working

    def doubleClickedCell(self, row, col):
        el = self.data[row]
        app = QApplication.instance()
        if el['forward_asset'] == BTC and el['tx0_address'] in app.wallet.addresses:
            # we request an exchange from BTC to another asset, once matched, we must do a BTCPay
            amt = el['forward_amount']
        elif el['backward_asset'] == BTC and el['tx1_address'] in app.wallet.addresses:
            # we request an exchange from BTC to another asset, but we got matched second
            amt = el['backward_amount']
        else:
            amt = None

        if amt is not None:
            order_match_id = el['tx0_hash'] + el['tx1_hash']
            BTCPayDialog(order_match_id, amt).exec_()


class OpenOrdersTableView(QTableWidget):
    def __init__(self, *args):
        super(OpenOrdersTableView, self).__init__(*args)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        cols = ["Tx", "Buy", "Sell", "Price", "Expiration", "Fee prov", "Fee req", "Remaining"]
        self.setColumnCount(len(cols))
        self.setHorizontalHeaderLabels(cols) #
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.cellDoubleClicked.connect(self.doubleClickedCell)
        self.data = None

    def doubleClickedCell(self, row, col):
        el = self.data[row]
        hash = el['tx_hash']
        CancelOrderDialog(hash).exec_()

# class CancelledOrdersTableView(QTableWidget):
#     def __init__(self, *args):
#         super(CancelledOrdersTableView, self).__init__(*args)
#         self.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.verticalHeader().setVisible(False)
#
#
# class CompletedOrdersTableView(QTableWidget):
#     def __init__(self, *args):
#         super(CompletedOrdersTableView, self).__init__(*args)
#         self.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.verticalHeader().setVisible(False)


class PlaceOrderDialog(QDialog):
    def __init__(self, asset, *args, **kwargs):
        super(PlaceOrderDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Place Order for Asset")
        self.setToolTip("Issue an order request.")
        form_layout = QFormLayout()
        self.get_asset = asset
        self.give_combo_box = QComboBox()
        self.give_combo_box.setToolTip("The asset to give")
        self.wallet = QApplication.instance().wallet
        active_portfolio = self.wallet.active_portfolio
        assets = active_portfolio.assets if active_portfolio is not None else []
        asset_names = [a.name for a in assets] # don't allow trading for the asset you're getting
        asset_names.append(BTC)
        asset_names = [a for a in asset_names if a != self.get_asset]
        self.give_combo_box.addItems(asset_names)
        self.give_value_box = QAssetValueSpinBox()
        self.give_value_box.setToolTip("The amount of the asset to give")
        form_layout.addRow("Give Asset: ", self.give_combo_box)
        form_layout.addRow("Give Quantity: ", self.give_value_box)
        self.give_combo_box.currentIndexChanged.connect(self.give_combo_box_value_changed)
        self.give_combo_box_value_changed()

        self.get_combo_box = QAssetValueSpinBox()
        self.get_combo_box.setToolTip("The quantity of the asset request in return")
        self.get_combo_box.set_asset_divisible(self.wallet.get_asset(self.get_asset).divisible)
        self.get_combo_box.setRange(0, MAX_SPINBOX_INT)
        form_layout.addRow("Get Asset: ", QLabel(self.get_asset))
        form_layout.addRow("Get Quantity: ", self.get_combo_box)


        self.expiration = QAssetValueSpinBox()
        self.expiration.setToolTip("The number of blocks for which the order should be valid.")
        self.expiration.set_asset_divisible(False)
        self.expiration.setRange(1, MAX_SPINBOX_INT)
        self.expiration.setValue(50)
        form_layout.addRow("Expiration: ", self.expiration)


        self.fee_required = QAssetValueSpinBox()
        self.fee_required.setToolTip("The miners' fee required to be paid by orders for "
                                     "them to match this one; in BTC; required only if "
                                     "buying BTC (may be zero, though).")

        self.fee_required.set_asset_divisible(True)
        self.fee_required.setRange(0, MAX_SPINBOX_INT)
        form_layout.addRow("Fee Required: ", self.fee_required)

        self.fee_provided = QAssetValueSpinBox()
        self.fee_provided.setToolTip("The miners' fee provided; in BTC; required only if selling BTC "
                                     "(should not be lower than is required for acceptance in a block)")
        self.fee_provided.set_asset_divisible(True)
        self.fee_provided.setRange(0, MAX_SPINBOX_INT)
        form_layout.addRow("Fee Provided: ", self.fee_provided)

        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)

        button_box.addButton("Order", QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setLayout(form_layout)

    def submit(self):
        give_asset = self.give_combo_box.currentText()
        wallet = QApplication.instance().wallet
        give_quantity =  wallet.get_asset(give_asset).convert_for_api(self.give_value_box.value())
        get_asset = self.get_asset
        get_quantity = wallet.get_asset(get_asset).convert_for_api(self.get_combo_box.value())
        expiration = int(self.expiration.value())
        btc = wallet.get_asset(BTC)
        fee_required = btc.convert_for_api(self.fee_required.value())
        fee_provided = btc.convert_for_api(self.fee_provided.value())

        source = QApplication.instance().wallet.active_address

        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()
        QApplication.instance().xcp_client.do_order(source, give_quantity, give_asset, get_quantity, get_asset,
                                                    expiration, fee_required, fee_provided, success_callback)
        self.close()

    def give_combo_box_value_changed(self):
        a = self.give_combo_box.currentText()
        if a == BTC:
            max = MAX_SPINBOX_INT
        else:
            max = self.wallet.active_portfolio.amount_for_asset(a)
        asset_obj = self.wallet.get_asset(a)
        divisible = asset_obj and asset_obj.divisible
        self.give_value_box.set_asset_divisible(divisible)
        self.give_value_box.setRange(0, max)


class PickGetAssetOrderDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(PickGetAssetOrderDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Pick Asset to Order")
        form_layout = QFormLayout()
        self.get_asset = AssetLineEdit()
        form_layout.addRow("Get Asset: ", self.get_asset)
        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)

        self.submit_button = QPushButton("Select")
        button_box.addButton(self.submit_button, QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setLayout(form_layout)
        self.get_asset.textChanged.connect(self.textChanged)
        self.wallet = QApplication.instance().wallet
        self.textChanged()

    def textChanged(self):
        self.submit_button.setEnabled(self.wallet.get_asset(self.get_asset.text()) is not None)

    def submit(self):
        asset = self.get_asset.text()
        if self.wallet.get_asset(asset) is not None:
            self.close()
            PlaceOrderDialog(asset).exec_()

class CancelOrderDialog(QDialog):
    def __init__(self, tx_hash=None, *args, **kwargs):
        super(CancelOrderDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Cancel Order for Asset")

        form_layout = QFormLayout()

        self.offer_hash = QLineEdit()
        if tx_hash:
            self.offer_hash.setText(tx_hash)
        self.offer_hash.textChanged.connect(self.textChanged)
        self.offer_hash.setToolTip("The transaction hash of the order or bet.")
        self.setToolTip("Cancel an open order or bet you created.")
        form_layout.addRow("Offer Hash: ", self.offer_hash)

        button_box = QDialogButtonBox()
        button_box.addButton("Undo", QDialogButtonBox.RejectRole)

        self.submit_button = QPushButton("Submit Request")
        button_box.addButton(self.submit_button, QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setLayout(form_layout)
        self.textChanged()

    def submit(self):
        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()
        self.close()
        QApplication.instance().xcp_client.do_cancel(self.offer_hash.text(), success_callback)

    def textChanged(self):
        self.submit_button.setEnabled(len(self.offer_hash.text()) > 0)


class BTCPayDialog(QDialog):
    def __init__(self, order_match_id=None, amt=None, *args, **kwargs):
        super(BTCPayDialog, self).__init__(*args, **kwargs)
        if amt is None:
            self.setWindowTitle("BTCpay")
        else:
            a = QApplication.instance().wallet.get_asset(BTC)
            self.setWindowTitle("Send %s %s" % (a.convert_for_app(amt), BTC))

        form_layout = QFormLayout()

        self.order_match_id = QLineEdit()
        if order_match_id:
            self.order_match_id.setText(order_match_id)
        self.order_match_id.textChanged.connect(self.textChanged)
        self.order_match_id.setToolTip("The concatenation of the hashes of the two transactions which compose the order match.")
        self.setToolTip("Create and broadcast a BTCpay message, to settle an Order Match for which you owe BTC.")
        form_layout.addRow("Order Match ID: ", self.order_match_id)

        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.submit_button = QPushButton("Pay")
        button_box.addButton(self.submit_button, QDialogButtonBox.AcceptRole)
        form_layout.addRow(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.submit)
        self.setLayout(form_layout)
        self.textChanged()

    def textChanged(self):
        self.submit_button.setEnabled(len(self.order_match_id.text()) > 0)

    def submit(self):
        def success_callback(response):
            print(response)
            ShowTransactionDetails(response).exec_()

        QApplication.instance().xcp_client.do_btcpay(self.order_match_id.text(), success_callback)
        self.close()


