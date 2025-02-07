# Import neccessary modules
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QFrame, QMessageBox, QTableWidgetItem
from PyQt6.QtGui import QIntValidator

# Import the UI and database connection class
from main_ui import Ui_MainWindow
from connect_database import ConnectDatabase

# Create a main window class
class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Initialize the UI from a seperate UI file
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            # Intitalize Widget Toggles
            #self.ui.icon_only_widget.hide()            # Hide the icon only widget not working 
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.home_btn_2.setChecked(True)

# Application entry form
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())