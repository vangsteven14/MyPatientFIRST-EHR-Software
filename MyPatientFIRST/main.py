# Import neccessary modules
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QFrame, QMessageBox, QTableWidgetItem, QTableWidget, QLabel
from PyQt6.QtGui import QIcon, QPixmap, QIntValidator
from PyQt6.QtCore import QResource, QDate
import mysql.connector

# Import the UI and database connection class
from connect_database import ConnectDatabase                               
from connect_db_patients import ConnectDatabasePatients
from connect_db_visits import ConnectDatabaseVisits                        # Still in progress
from connect_db_billings import ConnectDatabaseBillings                    # Still in progress
from main_ui import Ui_MainWindow

# Import the resource file
QResource.registerResource("resource.qrc")

# Create a main window class
class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Creates a database connection object ------------------------------------ #  
            self.db = ConnectDatabase()                              
            self.db_patients = ConnectDatabasePatients(self.db)
            #self.db_visits = ConnectDatabaseVisits(self.db)                 # Still in progress
            #self.db_billings = ConnectDatabaseBillings(self.db)             # Still in progress

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

            # Connect UI elements to class varables for patients_info table ----------- #
            self.patient_id = self.ui.patientlineEdit_1
            # Restrict input to integers
            self.patient_id.setValidator(QIntValidator(100, 999)) # Allows only 3-digit numbers for PatientID

            self.last_name = self.ui.patientlineEdit_3
            self.first_name = self.ui.patientlineEdit_4
            self.sex = self.ui.patientlineEdit_2
            self.age = self.ui.patientlineEdit_5
            self.birthDate = self.ui.patient_dateEdit_1
            self.medications = self.ui.patientlineEdit_6
            self.email_address = self.ui.patientlineEdit_7

            self.add_btn = self.ui.add_btn_1
            self.update_btn = self.ui.update_btn_1
            self.select_btn = self.ui.select_btn_1
            self.search_btn = self.ui.search_btn_1
            self.clear_btn = self.ui.clear_btn_1
            self.delete_btn = self.ui.delete_btn_1

            self.result_table = self.ui.patient_tableWidget_2
            #self.result_table.setVisible(True)  # Ensure it's visible
            #self.result_table.show()            # Force show in UI
            #self.result_table.update()
            self.result_table.setSortingEnabled(False)
            self.buttons_list = self.ui.patient_function_frame.findChildren(QPushButton)

            # Initialize signal and slots connections -------------------------------- #
            self.init_signal_slots()
    
        # Main code functions for patient table -------------------------------------------------------------------------------- #
        def init_signal_slots(self):
            self.add_btn.clicked.connect(self.add_info)
            self.update_btn.clicked.connect(self.update_info)
            self.select_btn.clicked.connect(self.select_info)
            self.search_btn.clicked.connect(self.search_info)
            self.clear_btn.clicked.connect(self.clear_info)
            self.delete_btn.clicked.connect(self.delete_info) 

        # Disable all buttons
        def disable_buttons(self):
            for button in self.buttons_list:
                button.setDisabled(True)

        # Enable all buttons
        def enable_buttons(self):
            for button in self.buttons_list:
                button.setDisabled(False)
        
        # Functions for patient_function_frame
        def add_info(self):
            #select_row = self.result_table.currentRow()

            patient_id = self.patient_id.text()
            first_name = self.first_name.text()
            last_name = self.last_name.text()
            sex = self.sex.text()
            age = self.age.text()
            birth_date = self.birthDate.date().toString("yyyy-MM-dd")
            medications = self.medications.text()
            email_address = self.email_address.text()

            # Ensure required fields are filled
            if not patient_id or not first_name or not last_name or not sex or not age or not birth_date or not medications or not email_address:
                QMessageBox.warning(self, "Warning", "Please fill out all required fields then select add new patient.",
                                    QMessageBox.StandardButton.Ok)
                return

            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Mypatientfirst",
                    database="db_patients"
                )
                cursor = conn.cursor()

                query = """INSERT INTO patients_info 
                        (patientID, firstName, LastName, sex, age, birthDate, medications, emailAddress) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (patient_id, first_name, last_name, sex, age, birth_date, medications, email_address)

                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()
                
                QMessageBox.information(self, "Success", "Patient record added successfully!",
                                        QMessageBox.StandardButton.Ok)

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Error!", f"Database insertion failed: {e}",
                                    QMessageBox.StandardButton.Ok)
            
            self.search_info()
            self.enable_buttons()
                
        def update_info(self):
            # Function to update patient information
            new_patient_info = self.get_patient_info()

            if new_patient_info["patientID"]:
                update_result = self.db_patients.update_info(
                    patient_id=new_patient_info["patientID"],
                    last_name=new_patient_info["lastName"],
                    first_name=new_patient_info["firstName"],
                    sex=new_patient_info["sex"],
                    age=new_patient_info["age"],
                    birth_date=new_patient_info["birthDate"],
                    medications=new_patient_info["medications"],
                    email_address=new_patient_info["emailAddress"]
                )

                if update_result:
                    QMessageBox.information(self, "Warning", f"Fail to update the information: {update_result}, Please try again.",
                                            QMessageBox.StandardButton.Ok)
                else:
                    self.search_info()
            
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
                
        def select_info(self):
            # Function to select and populate patient information in the form
            select_row = self.result_table.currentRow()

            if select_row != -1:
                # Convert the birthDate from the table into a QDate correctly
                birth_date_text = self.result_table.item(select_row, 5).text().strip()
                birth_date = QDate.fromString(birth_date_text, "MM-dd-yyyy")

                self.patient_id.setEnabled(False)
                patient_id = self.result_table.item(select_row, 0).text().strip()
                last_name = self.result_table.item(select_row, 1).text().strip()
                first_name = self.result_table.item(select_row, 2).text().strip()
                sex = self.result_table.item(select_row, 3).text().strip()
                age = self.result_table.item(select_row, 4).text().strip()
                birth_date = self.birthDate.date().toString("yyyy-MM-dd")
                medications = self.result_table.item(select_row, 6).text().strip()
                email_address = self.result_table.item(select_row, 7).text().strip()

                self.patient_id.setText(patient_id)
                self.last_name.setText(last_name)
                self.first_name.setText(first_name)
                self.sex.setText(sex)
                self.age.setText(age)
                self.birthDate.setDate(QDate.fromString(birth_date, "MM-dd-yyyy"))
                self.medications.setText(medications)
                self.email_address.setText(email_address)

            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
        def search_info(self):
            patient_info = self.get_patient_info()
            # Check if all fields are empty; if so, fetch all records
            # Otherwise, if all values are empty, fetch all records
            if not any(patient_info.values()):
                patient_result = self.db_patients.fetch_all_patients()
            else:
                patient_result = self.db_patients.search_info(
                    patient_id=patient_info["patientID"],
                    last_name=patient_info["lastName"],
                    first_name=patient_info["firstName"],
                    sex=patient_info["sex"],
                    age=patient_info["age"],
                    birth_date=patient_info["birthDate"],
                    medications=patient_info["medications"],
                    email_address=patient_info["emailAddress"]
                )
                
            #print("Search Result:", patient_result)
            self.show_data(patient_result)

        def clear_info(self):
            # Function to clear patient information in the form
            self.patient_id.clear()
            self.patient_id.setEnabled(True)
            self.last_name.clear()
            self.first_name.clear()
            self.sex.clear()
            self.age.clear()
            self.birthDate.setDate(QDate.currentDate())
            self.medications.clear()
            self.email_address.clear()

            # Ensures call search_info displays all records
            self.search_info()

        def delete_info(self):
            # Function to delete patient information
            select_row = self.result_table.currentRow()
            if select_row != -1:
                select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to delete this patient information?",
                                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if select_option == QMessageBox.StandardButton.Yes:
                    patient_id = self.result_table.item(select_row, 0).text().strip()

                    delete_result = self.db_patients.delete_info(patient_id=patient_id)
                    if not delete_result:
                        self.search_info()
                    else:
                        QMessageBox.information(self, "Warning", f"Fail to delete the information: {delete_result}, Please try again.",
                                                QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to delete.",
                                        QMessageBox.StandardButton.Ok)
        """
        def disable_buttons(self):
            for button in self.buttons_list:
                button.setEnabled(True)
        def enable_buttons(self):
            for button in self.buttons_list:
                button.setEnabled(False)
        """
        
        # Function to populate the patient table with patient information
        def show_data(self, result):
            
            if result:
                self.result_table.setRowCount(0)
                self.result_table.setRowCount(len(result))

                for row, info in enumerate(result):
                    info_list = [
                        info["patientID"],
                        info["lastName"],
                        info["firstName"],
                        info["sex"],
                        info["age"],
                        info["birthDate"],
                        info["medications"],
                        info["emailAddress"]
                    ]

                    for column, item in enumerate(info_list):
                        cell_item = QTableWidgetItem(str(item))
                        self.result_table.setItem(row, column, cell_item)

                #print("Table Updated Sucessfully!")
            else:
                #print("No Data Found. Please try again.")
                self.result_table.setRowCount(0)
                return
            
        # Function to retrieve patient information from the form
        def get_patient_info(self):
            patient_id = self.patient_id.text().strip()
            last_name = self.last_name.text().strip()
            first_name = self.first_name.text().strip()
            sex = self.sex.text().strip()
            age = self.age.text().strip()
            birth_date = self.birthDate.date().toString("yyyy-MM-dd")
            medications = self.medications.text().strip()
            email_address = self.email_address.text().strip()

            patient_info = {
                "patientID": patient_id,
                "lastName": last_name,
                "firstName": first_name,
                "sex": sex,
                "age": age,
                "birthDate": birth_date,
                "medications": medications,
                "emailAddress": email_address
            }

            return patient_info
        
        # Function to check if the patient ID already exists in the database
        def check_patient_id(self, patient_id):
            result = self.db_patients.search_info(patient_id=patient_id)
            return result
            
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
            # Functions for side widgets menu page
            self.ui.home_btn_1.toggled.connect(self.home_btn_toggled)
            self.ui.home_btn_2.toggled.connect(self.home_btn_toggled)

            self.ui.patient_btn_1.toggled.connect(self.patient_btn_toggled)
            self.ui.patient_btn_2.toggled.connect(self.patient_btn_toggled)

            self.ui.visit_btn_1.toggled.connect(self.visit_btn_toggled)
            self.ui.visit_btn_2.toggled.connect(self.visit_btn_toggled)

            self.ui.billings_btn_1.toggled.connect(self.billings_btn_toggled)
            self.ui.billings_btn_2.toggled.connect(self.billings_btn_toggled)

            # Functions for page 1 widgets page
            self.ui.pg1_patients_btn.toggled.connect(self.pg1_patients_btn_toggled)
            self.ui.pg1_visits_btn.toggled.connect(self.pg1_visits_btn_toggled)
            self.ui.pg1_billings_btn.toggled.connect(self.pg1_billings_btn_toggled)
    
            # Ensures stacked widget pages is changed
            self.ui.stackedWidget.currentChanged.connect(self.stackedWidget_currentChanged)

            # Ensure buttons are checkable
            self.set_buttons_checkable()

        def set_buttons_checkable(self):
            buttons = [
                self.ui.home_btn_1, self.ui.home_btn_2,
                self.ui.patient_btn_1, self.ui.patient_btn_2,
                self.ui.visit_btn_1, self.ui.visit_btn_2,
                self.ui.billings_btn_1, self.ui.billings_btn_2,
                self.ui.pg1_patients_btn,
                self.ui.pg1_visits_btn,
                self.ui.pg1_billings_btn
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

        # Functions for buttons changing pages on page 1 widgets page ----------------------- #
        def pg1_patients_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(1)
            
        def pg1_visits_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(2)

        def pg1_billings_btn_toggled(self):
            self.ui.stackedWidget.setCurrentIndex(3)

# Application entry form ----------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load style.qss file
    with open("style.qss", "r") as style_file:
        style_qss = style_file.read()
    app.setStyleSheet(style_qss)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())