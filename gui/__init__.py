try:
    import PyQt5 as PyQt
    import PyQt5.QtWidgets as PyQtGui

    PY_QT5 = True

except ImportError:
    # PyQt 5 is not installed, use PyQt 4 instead
    PY_QT5 = False
    import PyQt4 as PyQt
    import PyQt4.QtGui as PyQtGui