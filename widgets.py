from PyQt5.QtWidgets import QDoubleSpinBox, QDialog, QTextEdit, QDialogButtonBox, QVBoxLayout
from constants import Satoshi, MAX_SPINBOX_INT

class QAssetValueSpinBox(QDoubleSpinBox):
    """
    Automatically toggles between satoshi-decimal and whole-number precision with a simple method call
    """
    def __init__(self, *args, **kwargs):
        super(QAssetValueSpinBox, self).__init__(*args, **kwargs)
        self.setMaximum(MAX_SPINBOX_INT)  # overrides the default value of 100
        self.set_asset_divisible(False)

    def set_asset_divisible(self, divisible):
        if divisible:
            self.setSingleStep(float(Satoshi.INVERSE))
            self.setDecimals(Satoshi.NUM_DECIMALS)
        else:
            self.setSingleStep(1.0)
            self.setDecimals(0)

    def setMaximum(self, p_float):
        #TODO: bug, spinbox only goes up to 2**31 - 1 for integers! is this a problem?
        super(QAssetValueSpinBox, self).setMaximum(min(MAX_SPINBOX_INT, p_float))


class ShowTransactionDetails(QDialog):
    def __init__(self, text):
        text_edit = QTextEdit()
        text_edit.setText(text)
        self.setWindowTitle("Details")
        button_box = QDialogButtonBox()
        button_box.addButton("Close", QDialogButtonBox.AcceptRole)
        layout = QVBoxLayout()
        layout.addItem(text_edit)
        layout.addItem(button_box)
        self.setMinimumHeight(180)
        self.setLayout(layout)
        button_box.clicked.connect(self.close)