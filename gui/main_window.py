from PyQt5.Qt import QMainWindow, QWidget, QGridLayout, QTabWidget, QGroupBox, QPushButton, QApplication
from gui.portfolio_view import MyPortfolio
from gui.asset_exchange_view import AssetExchange
from gui.transaction_history_view import TransactionHistory
from gui.my_wallet_view import MyWalletGroupBox


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowTitle('Counterparty Exchange')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout()
        tabWidget = QTabWidget()
        self.asset_exchange = AssetExchange()
        tabWidget.addTab(self.asset_exchange, "Exchange")
        self.my_portfolio = MyPortfolio()
        tabWidget.addTab(self.my_portfolio, "My Portfolio")
        tabWidget.addTab(QWidget(), "Broadcast/Bet")
        tabWidget.addTab(TransactionHistory(), "Transaction History")

        overview = QGroupBox('Overview')
        refresh = QPushButton("Refresh", overview)
        refresh.move(50, 50)
        refresh.clicked.connect(self.fetch_initial_data)
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
        QApplication.instance().fetch_initial_data(self.fetch_initial_data_lambda())

    def initialize_data_in_tabs(self):
        """
        Called after the initial request is done populating addresses into the wallet
        """
        self.asset_exchange.fetch_data()
