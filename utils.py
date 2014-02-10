from threading import Lock
from PyQt5.QtWidgets import QMessageBox


class AtomicInteger:
    """
    A helper class used in at least one place in the web request client for atomic integers. Based off of java's
    AtomicInteger class
    """

    def __init__(self, value):
        self.value = value
        self.lock = Lock()

    def intValue(self):
        with self.lock:
            return self.value

    def addAndGet(self, delta):
        with self.lock:
            self.value += delta
            return self.value

    def decrementAndGet(self):
        return self.addAndGet(-1)

    def incrementAndGet(self):
        return self.addAndGet(1)

    def getAndAdd(self, delta):
        with self.lock:
            old = self.value
            self.value += delta
            return old

    def getAndIncrement(self):
        return self.getAndAdd(1)

    def getAndDecrement(self):
        return self.getAndAdd(-1)


def display_alert(text, detailed_text=None):
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Information)
    message_box.setText(text)
    if detailed_text:
        message_box.setDetailedText(detailed_text)
    message_box.exec_()