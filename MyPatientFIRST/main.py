# Import neccessary modules
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QFrame, QMessageBox, QTableWidgetItem, QLabel
from PyQt6.QtGui import QIcon, QPixmap, QIntValidator
from PyQt6.QtCore import QResource, QDate

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

            # Creates a database connection object ------------------------------------ #
            self.db = ConnectDatabase()

            # Connect UI elements to class varables for patient table ----------------- #
            self.patient_id = self.ui.lineEdit_5
            # Restrict input to integers
            self.patient_id.setValidator(QIntValidator)

            self.last_name = self.ui.lineEdit
            self.first_name = self.ui.lineEdit_2
            self.age = self.ui.lineEdit_6
            self.birthDate = self.ui.dateEdit_4
            self.medications = self.ui.lineEdit_7
            self.email_address = self.ui.lineEdit_8

            self.add_btn = self.ui.add_btn_1
            self.update_btn = self.ui.update_btn_1
            self.select_btn = self.ui.select_btn_1
            self.search_btn = self.ui.search_btn_1
            self.clear_btn = self.ui.clear_btn_1
            self.delete_btn = self.ui.delete_btn_1

            self.result_table = self.ui.patient_tableWidget_2
            self.result_table.setSortingEnabled(False)
            self.buttons_list = self.ui.patient_function_frame.findChildren(QPushButton)

            # Initialize signal and slots connections -------------------------------- #
            self.init_signal_slots()
    
            # Populate birth date in the birth date QDateEdit ------------------------ #
            self.birth_date()

        def init_signal_slots(self):
            self.add_btn.clicked.connect(self.add_info)
            self.update_btn.clicked.connect(self.update_info)
            self.select_btn.clicked.connect(self.select_info)
            self.search_btn.clicked.connect(self.search_info)
            self.clear_btn.clicked.connect(self.clear_info)
            self.delete_btn.clicked.connect(self.delete_info)
        def birth_date(self):                                  # function may not work; just a demo/test for now
            try:
                sql = "SELECT birthDate FROM patients_info"  # Adjust query if needed
                self.db.cursor.execute(sql)
                result = self.db.cursor.fetchone()  # Get one birthDate value
        
                if result and result["birthDate"]:
                    birth_date = result["birthDate"]  # Extract date from DB
                    qdate = QDate.fromString(str(birth_date), "MM-dd-yyyy")  # Convert to QDate
                    self.birthDate.setDate(qdate)  # Set in QDateEdit

            except Exception as e:
                print(f"Error fetching birth date: {e}")

        # Functions for patient_function_frame
        def add_info(self):            
            pass
        def update_info(self):
            pass
        def select_info(self):
            pass
        def search_info(self):
            pass
        def clear_info(self):
            pass
        def delete_info(self):
            pass
        

        # Load Hide/Show Side Widgets Icons ------------------------------------------------------- #
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