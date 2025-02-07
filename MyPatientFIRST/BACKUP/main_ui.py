from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
from PyQt6.QtCore import QResource
import sys

QResource.registerResource("resource.qrc")

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

app = QApplication(sys.argv)
window = MainApp()
window.show()

sys.exit(app.exec())