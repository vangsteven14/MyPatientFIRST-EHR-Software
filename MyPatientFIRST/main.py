# Import neccessary modules
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QFrame, QMessageBox, QTableWidgetItem, QLabel
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QResource

# Import the UI and database connection class
from main_ui import Ui_MainWindow
from connect_database import ConnectDatabase

# Import the resource file
QResource.registerResource("resource.qrc")

# Create a main window class
class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Initialize the UI from a seperate UI file ------------------------------- #
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            # Intitalize Widget Toggles ----------------------------------------------- #
            self.ui.side_widget_1.hide()         
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.home_btn_2.setChecked(True)

            # Load Hide/Show Icons ---------------------------------------------------- #
            self.load_hide_icons()
            self.load_show_icons()

            # Make sure buttons are connected to functions ---------------------------- #
            self.connect_buttons()

        # Load Hide/Show Icons -------------------------------------------------------- #
        def load_hide_icons(self):
            pixmap = QPixmap("icons/MyPatientFirstLogo_Symbol.JPG")
            self.ui.logo_1.setPixmap(pixmap)
            self.ui.home_btn_1.setIcon(QIcon('icons/home.svg'))
            self.ui.patient_btn_1.setIcon(QIcon('icons/patient.svg'))
            self.ui.visit_btn_1.setIcon(QIcon('icons/visit.svg'))
            self.ui.billings_btn_1.setIcon(QIcon('icons/billings.svg'))
            self.ui.exit_btn_1.setIcon(QIcon('icons/exit.svg'))

        def load_show_icons(self):
            pixmap = QPixmap("icons/MyPatientFirstLogo_Symbol.JPG")
            self.ui.logo_2.setPixmap(pixmap)
            self.ui.home_btn_2.setIcon(QIcon('icons/home.svg'))
            self.ui.patient_btn_2.setIcon(QIcon('icons/patient.svg'))
            self.ui.visit_btn_2.setIcon(QIcon('icons/visit.svg'))
            self.ui.billings_btn_2.setIcon(QIcon('icons/billings.svg'))
            self.ui.exit_btn_2.setIcon(QIcon('icons/exit.svg'))

        # Function for changing menu page via side widget buttons --------------------------------- #
        def connect_buttons(self):
            self.ui.home_btn_1.toggled.connect(self.home_btn_toggled)
            self.ui.home_btn_2.toggled.connect(self.home_btn_toggled)

            self.ui.patient_btn_1.toggled.connect(self.patient_btn_toggled)
            self.ui.patient_btn_2.toggled.connect(self.patient_btn_toggled)

            self.ui.visit_btn_1.toggled.connect(self.visit_btn_toggled)
            self.ui.visit_btn_2.toggled.connect(self.visit_btn_toggled)

            self.ui.billings_btn_1.toggled.connect(self.billings_btn_toggled)
            self.ui.billings_btn_2.toggled.connect(self.billings_btn_toggled)

            self.ui.stackedWidget.currentChanged.connect(self.stackedWidget_currentChanged)

            # Ensure buttons are checkable
            self.set_buttons_checkable()

        def set_buttons_checkable(self):
            buttons = [
                self.ui.home_btn_1, self.ui.home_btn_2,
                self.ui.patient_btn_1, self.ui.patient_btn_2,
                self.ui.visit_btn_1, self.ui.visit_btn_2,
                self.ui.billings_btn_1, self.ui.billings_btn_2
            ]
            for btn in buttons:
                btn.setCheckable(True)

        # Function for changing page to user page ----------------------------------------------- #
        def user_btn_clicked(self):
            print(f"Switching to page 3. Total pages: {self.ui.stackedWidget.count()}")
            if self.ui.stackedWidget.count() > 3:
                self.ui.stackedWidget.setCurrentIndex(3)
            else:
                print("Error: Page index 3 does not exist!")
        
        def stackedWidget_currentChanged(self, index):
            btn_list = self.ui.side_widget_1.findChildren(QPushButton) + self.ui.side_widget_2.findChildren(QPushButton)

            for btn in btn_list:
                if index in [2, 3]:
                    btn.setAutoExclusive(False)
                    btn.setChecked(False)
                else:
                    btn.setAutoExclusive(True)

        # Functions for buttons changing pages on side widgets menu page ----------------------- #
        def home_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(0)

        def patient_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(1)

        def visit_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(2)

        def billings_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(3)

# Application entry form
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load style.qss file
    with open("style.qss", "r") as style_file:
        style_qss = style_file.read()
    app.setStyleSheet(style_qss)

    '''
    style_file = QFile("style.qss")
    style_file.open(QFile.ReadOnly | QFile.Text)
    style_stream = QTextStream(style_file)
    app.setStyleSheet(style_stream.readAll())
    '''

    window = MainWindow()
    window.show()

    sys.exit(app.exec())