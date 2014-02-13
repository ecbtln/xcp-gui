from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QPushButton, QDialog
from widgets import AssetLineEdit

class AssetInfoView(QDialog):
    def __init__(self, asset_name, *args, **kwargs):
        super(AssetInfoView, self).__init__(*args, **kwargs)
        self.setGeometry(300, 300, 500, 400)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setWindowTitle('Asset Lookup')

        vbox_layout = QVBoxLayout()
        tabWidget = QTabWidget()
        tabWidget.addTab(QWidget(), "Overview")
        tabWidget.addTab(QWidget(), "Shareholders")
        tabWidget.addTab(QWidget(), "Dividends")
        tabWidget.addTab(QWidget(), "Updates")
        tabWidget.addTab(QWidget(), "Contacts")


        hbox_layout = QHBoxLayout()
        top_container = QWidget()
        top_container.setFixedHeight(50)
        self.search_field = AssetLineEdit()
        self.search_field.setPlaceholderText("ASSET_NAME")
        hbox_layout.addWidget(self.search_field)
        search_button = QPushButton('Search')
        hbox_layout.addWidget(search_button)
        top_container.setLayout(hbox_layout)
        vbox_layout.addWidget(top_container)
        vbox_layout.addWidget(tabWidget)
        self.setLayout(vbox_layout)
        self.asset_name = asset_name


