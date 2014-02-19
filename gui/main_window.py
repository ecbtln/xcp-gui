from .portfolio_view import MyPortfolio
from .asset_exchange_view import AssetExchange
from .transaction_history_view import TransactionHistory
from .my_wallet_view import MyWalletGroupBox
from . import PyQtGui


class MainWindow(PyQtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowTitle('Counterparty Exchange')
        central_widget = PyQtGui.QWidget()
        self.setCentralWidget(central_widget)
        grid_layout = PyQtGui.QGridLayout()
        tabWidget = PyQtGui.QTabWidget()
        self.asset_exchange = AssetExchange()
        tabWidget.addTab(self.asset_exchange, "Exchange")
        self.my_portfolio = MyPortfolio()
        tabWidget.addTab(self.my_portfolio, "My Portfolio")
        # tabWidget.addTab(QWidget(), "Broadcast/Bet")
        # tabWidget.addTab(TransactionHistory(), "Transaction History")

        overview = PyQtGui.QGroupBox('Overview')
        self.block_chain_label = PyQtGui.QLabel()
        layout = PyQtGui.QHBoxLayout()
        layout.addWidget(self.block_chain_label)
        overview.setLayout(layout)

        overview.setFixedWidth(250)
        wallet_view = MyWalletGroupBox(self)
        self.wallet_view = wallet_view
        grid_layout.addWidget(wallet_view, 0, 1)
        grid_layout.addWidget(overview, 0, 0)
        grid_layout.addWidget(tabWidget, 1, 0, 1, 2)
        central_widget.setLayout(grid_layout)
        self.show()

    def fetch_initial_data_lambda(self):
        return lambda results: self.wallet_view.update_data(results)

    def fetch_initial_data(self):
        PyQtGui.QApplication.instance().fetch_initial_data(self.fetch_initial_data_lambda())

    def initialize_data_in_tabs(self):
        """
        Called after the initial request is done populating addresses into the wallet
        """
        self.asset_exchange.fetch_data()

    def setActiveBlockNumber(self, block_num):
        self.block_chain_label.setText('Block #: %d' % block_num)
