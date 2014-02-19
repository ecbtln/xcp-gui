from .widgets import AssetLineEdit
from . import PyQtGui

class AssetInfoView(PyQtGui.QDialog):
    def __init__(self, asset_name, *args, **kwargs):
        super(AssetInfoView, self).__init__(*args, **kwargs)
        self.setGeometry(300, 300, 500, 400)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setWindowTitle('Asset Lookup')

        vbox_layout = PyQtGui.QVBoxLayout()
        tabWidget = PyQtGui.QTabWidget()
        tabWidget.addTab(PyQtGui.QWidget(), "Overview")
        tabWidget.addTab(PyQtGui.QWidget(), "Shareholders")
        tabWidget.addTab(PyQtGui.QWidget(), "Dividends")
        tabWidget.addTab(PyQtGui.QWidget(), "Updates")
        tabWidget.addTab(PyQtGui.QWidget(), "Contacts")


        hbox_layout = PyQtGui.QHBoxLayout()
        top_container = PyQtGui.QWidget()
        top_container.setFixedHeight(50)
        self.search_field = AssetLineEdit()
        self.search_field.setPlaceholderText("ASSET_NAME")
        hbox_layout.addWidget(self.search_field)
        search_button = PyQtGui.QPushButton('Search')
        hbox_layout.addWidget(search_button)
        top_container.setLayout(hbox_layout)
        vbox_layout.addWidget(top_container)
        vbox_layout.addWidget(tabWidget)
        self.setLayout(vbox_layout)
        self.asset_name = asset_name


