# Import neccessary modules
import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QPushButton,
    QMessageBox, QTableWidgetItem
    )
from PyQt6.QtGui import QIcon, QPixmap, QIntValidator, QFont, QFontDatabase
from PyQt6.QtCore import QResource, QDate, QTime, QTimer, QSize

# Import the UI widgets and functions for the main window
from main_ui_widgets_buttons import MainUIWidgetsButtons

# Import the datetime module for visits tablecl
from datetime import timedelta

# Import the UI and database connection class
from connect_database import ConnectDatabase                               
from connect_db_patients import ConnectDatabasePatients
from connect_db_visits import ConnectDatabaseVisits                        
from connect_db_billings import ConnectDatabaseBillings
from connect_db_userLogin import LoginWindow, LogoutWindow
from connect_fonts import GoogleFonts                     

# Import the Main Window UI, View Patient Profile, View Patient Visit, and View Patient Bill UI files
from main_ui import Ui_MainWindow
from view_patient_profile_ui import Ui_ViewPatientProfile
from view_patient_visit_ui import Ui_ViewPatientVisit
from view_patient_billing_ui import Ui_ViewPatientBilling

# Import the resource file
QResource.registerResource("resource.qrc")

# Utilities to make execute file for the application
from utilities import ResourceLoader

# Class for the main window applicaiton
class MainWindow(QMainWindow):
        def __init__(self, username=None):
            super().__init__() 

            # Set the window icon ------------------------------------------- #
            self.setWindowIcon(QIcon(ResourceLoader.resource_path("icons/MyPatientFirstLogo_Symbol.JPG"))) 

            # Creates a database connection object ------------------------------------ #  
            self.db = ConnectDatabase()                              
            self.db_patients = ConnectDatabasePatients(self.db)
            self.db_visits = ConnectDatabaseVisits(self.db)                 
            self.db_billings = ConnectDatabaseBillings(self.db)         

            # Initialize the UI from a seperate UI file ------------------------------- #
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.main_ui_widgets_buttons = MainUIWidgetsButtons(self.ui)

            # Initialize features for username and home page -------------------------- #
            self.username = username
            self.display_home_page()

            # Initialize features for fonts and UI display ---------------------------- #
            self.display_fonts_ui()

            # Intitalize Widget Toggles ----------------------------------------------- #
            self.ui.side_widget_1.hide()         
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.home_btn_2.setChecked(True)

            # Load Hide/Show Icons ---------------------------------------------------- #
            self.main_ui_widgets_buttons.load_hide_icons()
            self.main_ui_widgets_buttons.load_show_icons()

            # Make sure buttons are connected to functions ---------------------------- #
            self.main_ui_widgets_buttons.connect_buttons()

            # Initialize features for logging out application ------------------------- #
            self.ui.exit_btn_1.clicked.connect(self.logout_to_login)
            self.ui.exit_btn_2.clicked.connect(self.logout_to_login)  

            # Connect UI elements to class varables for patients_info table ----------------------------------------------------- #
            self.patient_id = self.ui.patientlineEdit_1
            self.patient_id.setValidator(QIntValidator(100, 999)) # Allows only 3-digit numbers for PatientID 
                                                                  # Restrict input to integers
            self.last_name = self.ui.patientlineEdit_3
            self.first_name = self.ui.patientlineEdit_4
            self.sex = self.ui.patientlineEdit_2
            self.age = self.ui.patientlineEdit_5
            self.birth_date = self.ui.patient_dateEdit_1
            self.medications = self.ui.patientlineEdit_6
            self.email_address = self.ui.patientlineEdit_7

            self.pat_add_btn = self.ui.add_btn_1
            self.pat_update_btn = self.ui.update_btn_1
            self.pat_select_btn = self.ui.select_btn_1
            self.pat_delete_btn = self.ui.delete_btn_1
            self.pat_clear_btn = self.ui.clear_btn_1
            self.pat_search_btn = self.ui.search_btn_1
            self.view_pat_profile_btn = self.ui.viewPatProfile_btn_1

            self.result_table = self.ui.patient_tableWidget_2
            self.result_table.setSortingEnabled(False)
            self.buttons_list = self.ui.patient_function_frame.findChildren(QPushButton)

            self.pat_refresh_btn = self.ui.patient_refresh_btn

            # Initialize signal and slots connections for patients_info table
            self.init_signal_slots_patients()

            # Connects to patient's birth date autocompleting age from calculate_age()
            self.ui.patient_dateEdit_1.dateChanged.connect(self.calculate_age)

            # Connect UI elements to class varables for visits_info table ----------------------------------------------------- #
            # Create a combo box for patient IDs and Searches for specific patient ID and their last and first names
            self.visits_patientID_comboBox = self.ui.visits_comboBox
            self.visits_patientID_comboBox.currentIndexChanged.connect(self.on_patient_selected)
            self.patient_ids_and_names_dict = {}
            self.populate_patient_ids()

            # Allows only 3-digit numbers for VisitID which restricts input to integers
            self.visit_id = self.ui.visitslineEdit_1
            self.visit_id.setValidator(QIntValidator(100, 999)) 

            self.status = self.ui.visitslineEdit_2
            self.visits_last_name = self.ui.visitslineEdit_3
            self.visits_first_name = self.ui.visitslineEdit_4
            self.visit_date = self.ui.visits_dateEdit_1
            self.visit_time = self.ui.visits_timeEdit_1
            self.visit_type = self.ui.visitslineEdit_5
            self.reason = self.ui.visitslineEdit_6

            self.visits_add_btn = self.ui.add_btn_3
            self.visits_update_btn = self.ui.update_btn_3
            self.visits_select_btn = self.ui.select_btn_3
            self.visits_delete_btn = self.ui.delete_btn_3
            self.visits_clear_btn = self.ui.clear_btn_3
            self.visits_search_btn = self.ui.search_btn_3
            self.view_pat_visits_btn = self.ui.viewVisitsProfile_btn_3

            self.result_table_visits = self.ui.visits_tableWidget
            self.result_table_visits.setSortingEnabled(False)
            self.buttons_list_visits = self.ui.visits_function_frame.findChildren(QPushButton)

            self.visits_refresh_btn = self.ui.visits_refresh_btn

            # Initialize signal and slots connections for vists_info table
            self.init_signal_slots_visits()

            # Connect UI elements to class varables for billings_info table ----------------------------------------------------- #
            # Create a combo box for patient IDs and Searches for specific patient ID and their visitIDs
            self.billings_patientID_comboBox = self.ui.billing_comboBox
            self.billings_patientID_comboBox.currentIndexChanged.connect(self.on_patient_selected_billings)
            self.patient_ids_and_visitIDs_dict = {}
            self.populate_patient_ids_billings()

            # Allows only 3-digit numbers for BillingID and VisitID which restricts input to integers
            self.billing_visit_id = self.ui.billingslineEdit_1
            self.billing_visit_id.setValidator(QIntValidator(100, 999))
            self.billing_id = self.ui.billingslineEdit_2
            self.billing_id.setValidator(QIntValidator(100, 999))

            self.amount = self.ui.billingslineEdit_3
            self.billing_status = self.ui.billingslineEdit_4
            self.doctor = self.ui.billingslineEdit_5
            self.service = self.ui.billingslineEdit_6
            self.billing_reason = self.ui.billingslineEdit_7

            self.billings_add_btn = self.ui.add_btn_4
            self.billings_update_btn = self.ui.update_btn_4
            self.billings_select_btn = self.ui.select_btn_4
            self.billings_delete_btn = self.ui.delete_btn_4
            self.billings_clear_btn = self.ui.clear_btn_4
            self.billings_search_btn = self.ui.search_btn_4
            self.view_pat_billings_btn = self.ui.viewBillingsProfile_btn_4

            self.result_table_billings = self.ui.billings_tableWidget
            self.result_table_billings.setSortingEnabled(False)
            self.buttons_list_billings = self.ui.billings_function_frame.findChildren(QPushButton)

            self.billings_refresh_btn = self.ui.billings_refresh_btn

            # Initialize signal and slots connections for billings_info table
            self.init_signal_slots_billings()

        # Function to display images, fonts, and text adjustments for home page
        def display_home_page(self):
            customFontWelcome = QFontDatabase.addApplicationFont(ResourceLoader.resource_path("fonts/Poppins-ExtraBold.ttf"))
            customFontTitle = QFontDatabase.addApplicationFont(ResourceLoader.resource_path("fonts/Poppins-ExtraBold.ttf"))
            customFont = QFontDatabase.addApplicationFont(ResourceLoader.resource_path("fonts/Poppins-Light.ttf"))
            welcomeLogo = QPixmap(ResourceLoader.resource_path("icons/MyPatientFirstLogo_Symbol.JPG")).scaled(50, 50)
            self.ui.welcome_btn.setIcon(QIcon(welcomeLogo))
            self.ui.welcome_btn.setIconSize(QSize(50, 50))
            self.ui.welcome_label.setText(f"Hello {self.username}, Welcome to MyPatientFirst!")

            if customFontWelcome != -1 and customFontTitle != -1 and customFont != -1:
                font_family_welcome = QFontDatabase.applicationFontFamilies(customFontWelcome)[0]
                customer_font_welcome = QFont(font_family_welcome, 20)
                self.ui.welcome_label.setFont(customer_font_welcome)

                font_family_title = QFontDatabase.applicationFontFamilies(customFontTitle)[0]
                custom_font_title = QFont(font_family_title, 18)
                self.ui.patient_label.setFont(custom_font_title)
                self.ui.visits_label.setFont(custom_font_title)
                self.ui.billing_label.setFont(custom_font_title)

                font_family_info = QFontDatabase.applicationFontFamilies(customFont)[0]
                custom_font_label = QFont(font_family_info, 10) 
                self.ui.patientInfo_label_1.setFont(custom_font_label)
                self.ui.patientInfo_label_2.setFont(custom_font_label)
                self.ui.visitInfo_label_1.setFont(custom_font_label)
                self.ui.visitInfo_label_2.setFont(custom_font_label)
                self.ui.billingInfo_label_1.setFont(custom_font_label)
                self.ui.billingInfo_label_2.setFont(custom_font_label)
            else:
                print("Failed to load font families")

            self.ui.patientInfo_frame.setFixedWidth(600)
            self.ui.pg1_patients_btn.setFixedWidth(500)
            patientPage_image = QPixmap(ResourceLoader.resource_path("images/patient_page_image.jpg")).scaled(200,200)
            self.ui.patientInfo_pic.setPixmap(patientPage_image)
            self.ui.patientInfo_pic.setScaledContents(True)
            self.ui.patientInfo_pic.setFixedSize(200, 200)
            
            self.ui.visitInfo_frame.setFixedWidth(600)
            self.ui.pg1_visits_btn.setFixedWidth(500)
            visitPage_image = QPixmap(ResourceLoader.resource_path("images/visit_page_image.jpg")).scaled(200,200)
            self.ui.visitInfo_pic.setPixmap(visitPage_image)
            self.ui.visitInfo_pic.setScaledContents(True)
            self.ui.visitInfo_pic.setFixedSize(200, 200)
            
            self.ui.billingInfo_frame.setFixedWidth(600)
            self.ui.pg1_billings_btn.setFixedWidth(500)
            billingPage_image = QPixmap(ResourceLoader.resource_path("images/billing_page_image.jpg")).scaled(200,200)
            self.ui.billingInfo_pic.setPixmap(billingPage_image)
            self.ui.billingInfo_pic.setScaledContents(True)
            self.ui.billingInfo_pic.setFixedSize(200, 200)

            # Adjustments for title labels on each pages
            self.ui.title_label_3.setFixedWidth(500)
            self.ui.visits_label_1.setFixedWidth(500)
            self.ui.billings_label_1.setFixedWidth(500)

        # Function to logout and return to login page
        def logout_to_login(self):
            self.logout_window = LogoutWindow()
            self.logout_window.show()
            self.close()

        def display_fonts_ui(self):
            customFont_poppins = QFontDatabase.addApplicationFont(ResourceLoader.resource_path("fonts/Poppins-Light.ttf"))

            if customFont_poppins != -1:
                font_family_info = QFontDatabase.applicationFontFamilies(customFont_poppins)[0]
                custom_font = QFont(font_family_info, 10) 
                self.ui.viewVisitsProfile_btn_3.setFont(custom_font)
            else:
                print("Failed to load font families")

        # Main code functions for patient table ------------------------------------------------------------------------------------------------------------ #
        def init_signal_slots_patients(self):
            self.pat_add_btn.clicked.connect(self.add_info_patients)
            self.pat_update_btn.clicked.connect(self.update_info_patients)
            self.pat_select_btn.clicked.connect(self.select_info_patients)
            self.pat_delete_btn.clicked.connect(self.delete_info_patients) 
            self.pat_clear_btn.clicked.connect(self.clear_info_patients)
            self.pat_search_btn.clicked.connect(self.search_info_patients)
            self.pat_refresh_btn.clicked.connect(self.refresh_patients_table)

            # Connects to View Patient Profile button
            self.view_pat_profile_btn.clicked.connect(self.openViewPatientProfile)

        # Disable all buttons
        def disable_buttons_patients(self):
            for button in self.buttons_list:
                button.setDisabled(True)

        # Enable all buttons
        def enable_buttons_patients(self):
            for button in self.buttons_list:
                button.setDisabled(False)

        # Function to autocomplete age based on patient's birth date
        def calculate_age(self):
            birth_date = self.ui.patient_dateEdit_1.date()
            current_date = QDate.currentDate()
            age_value = current_date.year() - birth_date.year()

            current_month_day = (current_date.month(), current_date.day())
            birth_month_day = (birth_date.month(), birth_date.day())

            if current_month_day < birth_month_day:
                age_value -= 1

            self.ui.patientlineEdit_5.setText(str(age_value))

        # Functions for patient_function_frame
        def add_info_patients(self):
            patient_id = self.patient_id.text()
            first_name = self.first_name.text()
            last_name = self.last_name.text()
            sex = self.sex.text()

            # Autocomplete age based on patient's birth date
            birth_date_qdate = self.birth_date.date()
            today = QDate.currentDate()
            age_value = today.year() - birth_date_qdate.year()
            if (today.month(), today.day()) < (birth_date_qdate.month(), birth_date_qdate.day()):
                age_value -= 1
            self.age.setText(str(age_value))
            age = self.age.text()
            birth_date = self.birth_date.date().toString("yyyy-MM-dd")

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
            
            self.search_info_patients()
            self.enable_buttons_patients()
                
        def update_info_patients(self):
            # Function to update patient information
            new_patient_info = self.get_patient_info()

            selected_row = self.result_table.currentRow()

            if selected_row == -1:
                QMessageBox.information(self, "Warning", "Please select a patient to update.",
                                        QMessageBox.StandardButton.Ok)
                return
            
            # Get the patient ID of the selected row and update the information if needed
            old_patient_id = self.result_table.item(selected_row, 0).text().strip()
            new_patient_id = new_patient_info["patientID"]

            select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to update this patient information?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if select_option == QMessageBox.StandardButton.No:
                return
                    
            if new_patient_info["patientID"]:
                update_result = self.db_patients.update_info(
                    old_patient_id=old_patient_id,
                    new_patient_id=new_patient_id,
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
                    QMessageBox.information(self, "Success", "Patient information updated successfully!",
                                    QMessageBox.StandardButton.Ok)
                    self.search_info_patients()
            
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
                
        def select_info_patients(self):
            # Function to select and populate patient information in the form
            select_row = self.result_table.currentRow()

            if select_row == -1:
                QMessageBox.information(self, "Warning", "Please select a row to update.")
                return

            # Sets the widgets according to their selected row
            patient_id      = self.result_table.item(select_row, 0).text().strip()
            last_name       = self.result_table.item(select_row, 1).text().strip()
            first_name      = self.result_table.item(select_row, 2).text().strip()
            sex             = self.result_table.item(select_row, 3).text().strip()
            age             = self.result_table.item(select_row, 4).text().strip()

            # Convert the birthDate from the table into a QDate correctly
            birth_date_selected = self.result_table.item(select_row, 5).text().strip()
            birth_date = QDate.fromString(birth_date_selected, "MM-dd-yyyy")

            medications     = self.result_table.item(select_row, 6).text().strip()
            email_address   = self.result_table.item(select_row, 7).text().strip()

            # Disables patientID widgets for security and FK relationships
            self.patient_id.setEnabled(False)
            self.patient_id.setText(patient_id)

            self.last_name.setText(last_name)
            self.first_name.setText(first_name)
            self.sex.setText(sex)
            self.age.setText(age)
            self.birth_date.setDate(birth_date)
            self.medications.setText(medications)
            self.email_address.setText(email_address)                

        def delete_info_patients(self):
            # Function to delete patient information
            select_row = self.result_table.currentRow()
            if select_row != -1:
                select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to delete this patient information?\n"
                                                          "This can delete all information related to this patient including in visits and billings table.",
                                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if select_option == QMessageBox.StandardButton.Yes:
                    patient_id = self.result_table.item(select_row, 0).text().strip()

                    delete_result = self.db_patients.delete_info(patient_id=patient_id)
                    if not delete_result:
                        self.search_info_patients()
                    else:
                        QMessageBox.information(self, "Warning", f"Fail to delete the information: {delete_result}, Please try again.",
                                                QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to delete.",
                                        QMessageBox.StandardButton.Ok)
                
        def clear_info_patients(self):
            # Function to clear patient information in the form
            self.patient_id.clear()
            self.patient_id.setEnabled(True)
            self.last_name.clear()
            self.first_name.clear()
            self.sex.clear()
            self.ui.patientlineEdit_5.clear()
            self.ui.patient_dateEdit_1.blockSignals(True)
            self.ui.patient_dateEdit_1.setDate(QDate.currentDate())
            self.ui.patient_dateEdit_1.blockSignals(False)
            self.medications.clear()
            self.email_address.clear()

            # Ensures call search_info displays all records
            self.search_info_patients()

        def search_info_patients(self):
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
                
            self.patients_show_data(patient_result)

        # Function to View Patient Profile via "viewPatProfile_btn_1" button from Patient Page 1
        def openViewPatientProfile(self):
            self.view_patient_window = QMainWindow()
            self.view_patient_ui = Ui_ViewPatientProfile()
            self.view_patient_window.setWindowIcon(QIcon(ResourceLoader.resource_path("icons/MyPatientFirstLogo_Symbol.JPG")))
            self.view_patient_ui.setupUi(self. view_patient_window)

            # Connects to View Patient Profile buttons to function
            self.view_patient_ui.patSearch_btn.clicked.connect(self.viewPatientProfile_patSearch_btn)
            self.view_patient_ui.patSearch_lineEdit.returnPressed.connect(self.viewPatientProfile_patSearch_btn)      # Uses enter/return key for quicker search
            self.view_patient_ui.patSearch_dateEdit.editingFinished.connect(self.update_view_age_from_birthdate)        # Uses enter/return key for quicker search
            self.view_patient_ui.patClear_btn.clicked.connect(self.pat_clear_info)
            self.view_patient_ui.patUpdate_btn.clicked.connect(self.pat_update_info)
            self.view_patient_ui.patDelete_btn.clicked.connect(self.pat_delete_info)

            # Shows the View Patient Profile window/dialog box
            self.view_patient_window.show()

        # Function to searchs specific patientID in the view patient profile window
        def viewPatientProfile_patSearch_btn(self):
            patient_id = self.view_patient_ui.patSearch_lineEdit.text().strip()

            if not patient_id:
                QMessageBox.warning(self.view_patient_window, "Input Error", "Please enter a Patient ID.")
                return

            # Fetch patient info from DB as list of dictionaries
            patSearch_patientData = self.db_patients.pat_search_info(patient_id=patient_id)

            # Debugging: Print the data type and value
            print("Data Retrieved:", patSearch_patientData)

            if not patSearch_patientData or len(patSearch_patientData) == 0:
                QMessageBox.warning(self.view_patient_window, "Not Found", f"PatientID: {patient_id}\nDoes not exist in the Database.\nMust be PatientID only.\nPlease try again.")
                return

            patSearch_patientData = patSearch_patientData[0] 

            # Update View Patient Profile UI with current patient data
            self.view_patient_ui.patSearch_lineEdit_1.setText(str(patSearch_patientData["lastName"])) 
            self.view_patient_ui.patSearch_lineEdit_2.setText(str(patSearch_patientData["firstName"]))  
            self.view_patient_ui.patSearch_lineEdit_3.setText(str(patSearch_patientData["patientID"])) 
            self.view_patient_ui.patSearch_lineEdit_4.setText(str(patSearch_patientData["sex"]))  
            self.view_patient_ui.patSearch_lineEdit_6.setText(str(patSearch_patientData["emailAddress"]))  
            self.view_patient_ui.patSearch_lineEdit_7.setText(str(patSearch_patientData["medications"]))

            # Autocomplete age based on birth date of patient
            birth_date = patSearch_patientData["birthDate"]
            self.view_patient_ui.patSearch_dateEdit.setDate(QDate(birth_date.year, birth_date.month, birth_date.day))
            today = QDate.currentDate()
            age = today.year() - birth_date.year
            if (today.month(), today.day()) < (birth_date.month, birth_date.day):
                age -= 1
            self.view_patient_ui.patSearch_lineEdit_5.setText(str(age))

            # Disables patientID widgets for security and FK relationships
            self.view_patient_ui.patSearch_lineEdit_3.setEnabled(False)

            # Sets a Profile Picture based on sex of PatientID**
            if patSearch_patientData["sex"].lower() == "male":
                profile_pic = ResourceLoader.resource_path("images/default_male_profile_icon.jpg")  # Path to male image
            elif patSearch_patientData["sex"].lower() == "female":
                profile_pic = ResourceLoader.resource_path("images/default_female_profile_icon.jpg")  # Path to female image
            else:
                profile_pic = ResourceLoader.resource_path("images/no_image_found_icon.jpg")  # Default image if sex is unknown

            # Load and display image
            pixmap = QPixmap(profile_pic)
            self.view_patient_ui.profilePic_label.setPixmap(pixmap)
            self.view_patient_ui.profilePic_label.setScaledContents(True)  # Ensure the image fits the label

        # Function which autocompletes patient's age based on their birth date
        def update_view_age_from_birthdate(self):
            birth_date = self.view_patient_ui.patSearch_dateEdit.date()
            today = QDate.currentDate()

            age = today.year() - birth_date.year()
            if (today.month(), today.day()) < (birth_date.month(), birth_date.day()):
                age -= 1

            self.view_patient_ui.patSearch_lineEdit_5.setText(str(age))

        # Callback function to fetch specific patientID for viewPatientProfile_patSearch_btn()
        def pat_search_info(self, patient_id):
            query = "SELECT patientID, firstName, lastName, birthDate, sex, age, emailAddress, medications FROM patients_info WHERE patientID = %s"
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchone()

            if result:
                return result
            else:
                return None

        # Function to clear patient information in the view patient profile window
        def pat_clear_info(self):
            self.view_patient_ui.patSearch_lineEdit.clear()
            self.view_patient_ui.patSearch_lineEdit_1.clear()
            self.view_patient_ui.patSearch_lineEdit_2.clear() 
            self.view_patient_ui.patSearch_lineEdit_3.clear() 
            self.view_patient_ui.patSearch_dateEdit.setDate(QDate.currentDate())
            self.view_patient_ui.patSearch_lineEdit_4.clear() 
            self.view_patient_ui.patSearch_lineEdit_5.clear()  
            self.view_patient_ui.patSearch_lineEdit_6.clear()  
            self.view_patient_ui.patSearch_lineEdit_7.clear()
            self.view_patient_ui.profilePic_label.clear()

        # Function to update patient information in the view patient profile window
        def pat_update_info(self):
            # Retrieve patient data from input fields
            patient_pat_data = {
                "lastName": self.view_patient_ui.patSearch_lineEdit_1.text().strip(),
                "firstName": self.view_patient_ui.patSearch_lineEdit_2.text().strip(),
                "patientID": self.view_patient_ui.patSearch_lineEdit_3.text().strip(),
                "birthDate": self.view_patient_ui.patSearch_dateEdit.date().toString("yyyy-MM-dd"),
                "sex": self.view_patient_ui.patSearch_lineEdit_4.text().strip(),
                "age": self.view_patient_ui.patSearch_lineEdit_5.text().strip(),
                "emailAddress": self.view_patient_ui.patSearch_lineEdit_6.text().strip(),
                "medications": self.view_patient_ui.patSearch_lineEdit_7.text().strip(),
            }

            # Ensure the patient ID is not empty
            if not patient_pat_data["patientID"]:
                QMessageBox.warning(self, "Update Failed", "Patient ID is required for updating.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Call the update function in the database
            update_success = self.db_patients.pat_update_info(**patient_pat_data)

            if update_success:
                QMessageBox.information(self, "Success", "Patient information updated successfully.",
                                        QMessageBox.StandardButton.Ok)
                self.viewPatientProfile_patSearch_btn()  # Refresh the displayed data
            else:
                QMessageBox.warning(self, "Update Failed", "Please try again.")
                self.viewPatientProfile_patSearch_btn()  # Refresh the displayed data

        # Function to delete patient information in the view patient profile window
        def pat_delete_info(self):
            # Retrieve Patient ID from input field
            patient_id = self.view_patient_ui.patSearch_lineEdit.text().strip()

            if not patient_id:
                QMessageBox.warning(self.view_patient_window, "Delete Failed", "Patient ID is required for deleting.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Confirm deletion
            confirm_delete = QMessageBox.warning(
                self.view_patient_window,
                "Confirm Deletion",
                f"Are you sure you want to delete Patient ID: {patient_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm_delete == QMessageBox.StandardButton.Yes:
                # Call delete function in database
                delete_success = self.db_patients.pat_delete_info(patient_id)

                if delete_success:
                    QMessageBox.information(self.view_patient_window, "Success", "Patient record deleted successfully.",
                                            QMessageBox.StandardButton.Ok)
                    self.pat_clear_info()  # Clear the UI fields after deletion
                else:
                    QMessageBox.warning(self.view_patient_window, "Delete Failed", "Error deleting patient record. Please try again.",
                                        QMessageBox.StandardButton.Ok)

        # Function to populate the patient table with patient information
        def patients_show_data(self, result):
            self.result_table.setRowCount(0)

            if not result:
                return
            
            self.result_table.setRowCount(len(result))

            for row, info in enumerate(result):
                if isinstance(info["birthDate"], str):
                    qdate = QDate.fromString(info["birthDate"], "yyyy-MM-dd")
                    date_patient_table = qdate.toString("MM-dd-yyyy")
                else:
                    date_patient_table = info["birthDate"].strftime("%m-%d-%Y")
                info_list = [
                    info["patientID"],
                    info["lastName"],
                    info["firstName"],
                    info["sex"],
                    info["age"],
                    date_patient_table,
                    info["medications"],
                    info["emailAddress"]
                ]

                for column, item in enumerate(info_list):
                    cell_item = QTableWidgetItem(str(item))
                    self.result_table.setItem(row, column, cell_item)
            
        # Function to retrieve patient information from the form
        def get_patient_info(self,):
            patient_id = self.patient_id.text().strip()
            last_name = self.last_name.text().strip()
            first_name = self.first_name.text().strip()
            sex = self.sex.text().strip()
            age = self.age.text().strip()
            birth_date = self.birth_date.date().toString("yyyy-MM-dd")
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
        
        # Function to refresh the patient table with 1 second delay
        def refresh_patients_table(self):
            QTimer.singleShot(1000, self.do_refresh_patients_table)
    
        def do_refresh_patients_table(self):
            try:
                self.patient_id.clear()
                self.last_name.clear()
                self.first_name.clear()
                self.sex.clear()
                self.ui.patientlineEdit_5.clear()
                self.ui.patient_dateEdit_1.blockSignals(True)
                self.ui.patient_dateEdit_1.setDate(QDate.currentDate())
                self.ui.patient_dateEdit_1.blockSignals(False)
                self.medications.clear()
                self.email_address.clear()

                self.search_info_patients()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to refresh patient table: {e}",
                        QMessageBox.StandardButton.Ok)
        
        # Main code functions for visits table ------------------------------------------------------------------------------------------------------------ #
        def init_signal_slots_visits(self):            
            self.visits_add_btn.clicked.connect(self.add_info_visits)
            self.visits_update_btn.clicked.connect(self.update_info_visits)
            self.visits_select_btn.clicked.connect(self.select_info_visits)
            self.visits_delete_btn.clicked.connect(self.delete_info_visits) 
            self.visits_clear_btn.clicked.connect(self.clear_info_visits)
            self.visits_search_btn.clicked.connect(self.search_info_visits)
            self.visits_refresh_btn.clicked.connect(self.refresh_visits_table)

            # Connects to View Patient Visits button
            self.view_pat_visits_btn.clicked.connect(self.openViewPatientVisits)

        # Disable all buttons
        def disable_buttons_visits(self):
            for button in self.buttons_list_visits:
                button.setDisabled(True)

        # Enable all buttons
        def enable_buttons_visits(self):
            for button in self.buttons_list_visits:
                button.setDisabled(False)
        
        # Function to fetch patient IDs from the database and populate into combo box in visits table.
        def populate_patient_ids(self):
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Mypatientfirst",
                    database="db_patients"
                )
                cursor = conn.cursor()

                query = "SELECT patientID, lastName, firstName FROM patients_info"
                cursor.execute(query)
                patient_ids = cursor.fetchall()

                # Clear existing items and add retrieved patient IDs
                self.visits_patientID_comboBox.clear()
                self.patient_ids_and_names_dict.clear()

                # Default empty item
                self.visits_patientID_comboBox.addItem("Select Patient ID")

                for patient in patient_ids:
                    visits_patientID_comboBox, visits_last_name, visits_first_name = patient
                    self.patient_ids_and_names_dict[str(visits_patientID_comboBox)] = (visits_last_name, visits_first_name)
                    self.visits_patientID_comboBox.addItem(str(visits_patientID_comboBox))
                
                print("Selecting Patient IDs and Names for Visits Table:\n", patient_ids)
                cursor.close()
                conn.close()

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Database Error", f"Failed to load Patient IDs: {e}",
                            QMessageBox.StandardButton.Ok)

        def on_patient_selected(self):
            # Get the selected Patient ID
            selected_id = self.visits_patientID_comboBox.currentText()

            #print(f"Selected Patient ID for Visits Table:\n{selected_id}")  # Debugging: See what is selected

            # Check if a valid ID is selected
            if selected_id in self.patient_ids_and_names_dict:
                visits_last_name, visits_first_name = self.patient_ids_and_names_dict[selected_id]
                print(f"Auto-filling: Last Name - {visits_last_name}, First Name - {visits_first_name}")
                
                self.visits_last_name.setText(visits_last_name)
                self.visits_first_name.setText(visits_first_name)
            #else:
                #print("No match found for selected ID")  # Debugging

        # Functions for visits_function_frame
        def add_info_visits(self):
            visits_patientID_comboBox = self.visits_patientID_comboBox.currentText()
            visit_id = self.visit_id.text()
            status = self.status.text()
            visits_last_name = self.visits_last_name.text()
            visits_first_name = self.visits_first_name.text()
            visit_date = self.visit_date.date().toString("yyyy-MM-dd")
            visit_time = self.visit_time.time().toString("hh:mm:ss")
            visit_type = self.visit_type.text()
            reason = self.reason.text()

            # Ensure required fields are filled
            if not visits_patientID_comboBox or not visit_id or not status or not visits_last_name or not visits_first_name or not visit_date or not visit_time or not visit_type or not reason:
                QMessageBox.warning(self, "Warning", "Please fill out all required fields then select add new visit.",
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

                query = """INSERT INTO visits_info 
                        (patientID, visitID, status, lastName, firstName, visitDate, visitTime,type, reason) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                values = (visits_patientID_comboBox, visit_id, status, visits_last_name, visits_first_name, visit_date, visit_time, visit_type, reason)

                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()

                # Resets the visits_patientID_comboBox selection
                self.visits_patientID_comboBox.setCurrentIndex(0)
                
                QMessageBox.information(self, "Success", "Visit record added successfully!",
                                        QMessageBox.StandardButton.Ok)

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Error!", f"Database insertion failed: {e}",
                                    QMessageBox.StandardButton.Ok)
            
            self.search_info_visits()
            self.enable_buttons_visits()

        def update_info_visits(self):
            # Function to update patient information
            new_visits_info = self.get_visits_info()
            selected_row = self.result_table_visits.currentRow()

            if selected_row == -1:
                QMessageBox.information(self, "Warning", "Please select a patient to update.",
                                        QMessageBox.StandardButton.Ok)
                return
            
            # Get the patient ID of the selected row and update the information if needed
            old_visit_id = self.result_table_visits.item(selected_row, 1).text().strip()
            new_visit_id = new_visits_info["visitID"]

            select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to update this patient information?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if select_option == QMessageBox.StandardButton.No:
                return

            if new_visits_info["visitID"]:
                update_result = self.db_visits.update_info(
                    old_visit_id=old_visit_id,
                    new_visit_id=new_visit_id,
                    status=new_visits_info["status"],
                    last_name=new_visits_info["lastName"],
                    first_name=new_visits_info["firstName"],
                    visit_date=new_visits_info["visitDate"],
                    visit_time=new_visits_info["visitTime"],
                    type=new_visits_info["type"],
                    reason=new_visits_info["reason"]
                )

                if update_result:
                    QMessageBox.information(self, "Warning", f"Fail to update the information: {update_result}, Please try again.",
                                            QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.information(self, "Success", f"Visit information updated successfully!",
                                            QMessageBox.StandardButton.Ok)
                    self.search_info_visits()
            
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
        def select_info_visits(self):
            select_row = self.result_table_visits.currentRow()

            if select_row == -1:
                QMessageBox.information(self, "Warning", "Please select a row to update.")
                return
            
            # Sets the widgets according to their selected row
            patient_id_text = self.result_table_visits.item(select_row, 0).text().strip()
            visit_id_text   = self.result_table_visits.item(select_row, 1).text().strip()
            status_text     = self.result_table_visits.item(select_row, 2).text().strip()
            last_name_text  = self.result_table_visits.item(select_row, 3).text().strip()
            first_name_text = self.result_table_visits.item(select_row, 4).text().strip()
            visit_date_text = self.result_table_visits.item(select_row, 5).text().strip()
            visit_time_text = self.result_table_visits.item(select_row, 6).text().strip()
            type_text       = self.result_table_visits.item(select_row, 7).text().strip()
            reason_text     = self.result_table_visits.item(select_row, 8).text().strip()

            # Disables the patientID and visitIDwidgets for security and FK relationships
            self.visits_patientID_comboBox.setEnabled(False)
            self.visits_patientID_comboBox.setCurrentText(patient_id_text)
            self.visit_id.setEnabled(False)
            self.visit_id.setText(visit_id_text)

            self.status.setText(status_text)
            self.visits_last_name.setText(last_name_text)
            self.visits_first_name.setText(first_name_text)

            # Convert the date string back to QDate and convert the time string back to QTime
            qdate = QDate.fromString(visit_date_text, "MM-dd-yyyy")
            self.visit_date.setDate(qdate)
            qtime = QTime.fromString(visit_time_text, "h:mm AP")
            if not qtime.isValid():
                qtime = QTime(0, 0, 0)
            self.visit_time.setTime(qtime)
            #self.visit_time.setTime(qtime)
            self.visit_type.setText(type_text)
            self.reason.setText(reason_text)

        def delete_info_visits(self):
            # Function to delete visit information
            select_row = self.result_table_visits.currentRow()
            if select_row != -1:
                select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to delete this patient information?\n"
                                                          "This can delete all information related to this patient including in patients and billings table.",
                                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if select_option == QMessageBox.StandardButton.Yes:
                    visit_id = self.result_table_visits.item(select_row, 1).text().strip()

                    delete_result = self.db_visits.delete_info(visit_id=visit_id)
                    if not delete_result:
                        self.search_info_visits()
                    else:
                        QMessageBox.information(self, "Wsarning", f"Fail to delete the information: {delete_result}, Please try again.",
                                                QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to delete.",
                                        QMessageBox.StandardButton.Ok)
        def clear_info_visits(self):
            # Function to clear visit information in the form
            self.visits_patientID_comboBox.setCurrentIndex(0)
            self.visits_patientID_comboBox.setEnabled(True)
            self.visit_id.setEnabled(True)

            self.visit_id.clear()
            self.status.clear()
            self.visits_last_name.clear()
            self.visits_first_name.clear()
            self.visit_date.setDate(QDate.currentDate())
            self.visit_time.setTime(QTime(0, 0, 0))
            self.visit_type.clear()
            self.reason.clear()

            # Ensures call search_info_visits displays all records
            self.search_info_visits()
        def search_info_visits(self):
            visits_info = self.get_visits_info()
            # Check if all fields are empty; if so, fetch all records
            # Otherwise, if all values are empty, fetch all records

            if not any(visits_info.values()):
                visits_result = self.db_visits.fetch_all_visits()
            else:
                visits_result = self.db_visits.search_info(
                    patient_id=visits_info["patientID"],
                    visit_id=visits_info["visitID"],
                    status=visits_info["status"],
                    last_name=visits_info["lastName"],
                    first_name=visits_info["firstName"],
                    visit_date=visits_info["visitDate"],
                    visit_time=visits_info["visitTime"],
                    type=visits_info["type"],
                    reason=visits_info["reason"]
                )
            
            self.visits_show_data(visits_result)

        # Function to View Patient Profile via "viewVisitsProfile_btn_3" button from Visit Page 2
        def openViewPatientVisits(self):       
            self.view_visits_window = QMainWindow()
            self.view_visits_ui = Ui_ViewPatientVisit()
            self.view_visits_window.setWindowIcon(QIcon(ResourceLoader.resource_path("icons/MyPatientFirstLogo_Symbol.JPG")))
            #self.view_visits_ui = Ui_ViewPatientVisit()
            self.view_visits_ui.setupUi(self. view_visits_window)

            # Connects to View Patient Visit buttons to function
            self.view_visits_ui.patSearch_btn.clicked.connect(self.viewPatientVisits_patSearch_btn)
            self.view_visits_ui.patSearch_lineEdit.returnPressed.connect(self.viewPatientVisits_patSearch_btn)      # Uses enter/return key for quicker search
            self.view_visits_ui.patClear_btn.clicked.connect(self.visits_clear_info)
            self.view_visits_ui.patUpdate_btn.clicked.connect(self.visits_update_info)
            self.view_visits_ui.patDelete_btn.clicked.connect(self.visits_delete_info)

            # SHows the View Patient Visit window/dialog box
            self.view_visits_window.show()

        # Function to searchs specific patientID in the view patient visit window            
        def viewPatientVisits_patSearch_btn(self):
            patient_id = self.view_visits_ui.patSearch_lineEdit.text().strip()

            if not patient_id:
                QMessageBox.warning(self.view_visits_window, "Input Error", "Please enter a Patient ID.")
                return

            # Fetch patient info from DB as list of dictionaries
            patSearch_patientData_visits = self.db_visits.visits_search_info(patient_id=patient_id)

            if not patSearch_patientData_visits or len(patSearch_patientData_visits) == 0:
                QMessageBox.warning(self.view_visits_window, "Not Found", f"PatientID: {patient_id}\nDoes not exist in the Database.\nMust be PatientID only.\nPlease try again.")
                return

            patSearch_patientData_visits = patSearch_patientData_visits[0] 

            # Update View Patient Profile UI with current patient data
            self.view_visits_ui.visitSearch_lineEdit_1.setText(str(patSearch_patientData_visits["lastName"]))
            self.view_visits_ui.visitSearch_lineEdit_2.setText(str(patSearch_patientData_visits["firstName"]))
            self.view_visits_ui.visitSearch_lineEdit_3.setText(str(patSearch_patientData_visits["patientID"]))
            self.view_visits_ui.visitSearch_lineEdit_4.setText(str(patSearch_patientData_visits["visitID"]))
            self.view_visits_ui.visitSearch_lineEdit_5.setText(str(patSearch_patientData_visits["status"]))
            self.view_visits_ui.visitSearch_lineEdit_6.setText(str(patSearch_patientData_visits["type"]))
            self.view_visits_ui.visitSearch_lineEdit_7.setText(str(patSearch_patientData_visits["reason"]))

            # Converts visitDate properly
            self.view_visits_ui.visitSearch_dateEdit.setDate(QDate(patSearch_patientData_visits["visitDate"].year, 
                                                                   patSearch_patientData_visits["visitDate"].month, 
                                                                   patSearch_patientData_visits["visitDate"].day))

            # Converts visitTime properly
            time_delta = patSearch_patientData_visits["visitTime"]
            seconds_total = time_delta.total_seconds()
            hours = int(seconds_total // 3600)
            minutes = int((seconds_total % 3600) // 60)
            seconds = int(seconds_total % 60)

            qtime = QTime(hours, minutes, seconds)
            self.view_visits_ui.visitSearch_timeEdit.setTime(qtime)

            # Disables patientID and visitID widgets for security and FK relationships
            self.view_visits_ui.visitSearch_lineEdit_3.setEnabled(False)
            self.view_visits_ui.visitSearch_lineEdit_4.setEnabled(False)
            
            # Sets a Profile Picture based on sex of PatientID from patient table
            patient_id = patSearch_patientData_visits["patientID"]
            patient_sex_data = self.db_patients.pat_search_info(patient_id=patient_id)
            if patient_sex_data:
                sex = patient_sex_data[0]["sex"].lower()
                if sex == "male":
                    profile_pic = ResourceLoader.resource_path("images/default_male_profile_icon.jpg")
                elif sex == "female":
                    profile_pic = ResourceLoader.resource_path("images/default_female_profile_icon.jpg")
                else:
                    profile_pic = ResourceLoader.resource_path("images/no_image_found_icon.jpg")
                
                pixmap = QPixmap(profile_pic)
                self.view_visits_ui.profilePic_label.setPixmap(pixmap)
                self.view_visits_ui.profilePic_label.setScaledContents(True)
            else:
                profile_pic = ResourceLoader.resource_path("images/no_image_found_icon.jpg")
                pixmap = QPixmap(profile_pic)
                self.view_visits_ui.profilePic_label.setPixmap(pixmap)
                self.view_visits_ui.profilePic_label.setScaledContents(True)
        
        # Callback function to fetch specific patientID for viewPatientVisits_patSearch_btn()
        def visits_search_info(self, patient_id):
            query = "SELECT patientID, visitID, status, firstName, lastName, visitDate, visitTime, type, reason FROM visit WHERE patientID = %s"
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchone()

            if result:
                return result
            else:
                return None
            
        # Function to clear patient visit information in the view patient profile window
        def visits_clear_info(self):
            self.view_visits_ui.patSearch_lineEdit.clear()
            self.view_visits_ui.visitSearch_lineEdit_1.clear()
            self.view_visits_ui.visitSearch_lineEdit_2.clear()
            self.view_visits_ui.visitSearch_lineEdit_3.clear()
            self.view_visits_ui.visitSearch_lineEdit_4.clear()
            self.view_visits_ui.visitSearch_lineEdit_5.clear()
            self.view_visits_ui.visitSearch_dateEdit.setDate(QDate.currentDate())
            self.view_visits_ui.visitSearch_timeEdit.setTime(QTime.currentTime())
            self.view_visits_ui.visitSearch_lineEdit_6.clear()
            self.view_visits_ui.visitSearch_lineEdit_7.clear()
            self.view_visits_ui.profilePic_label.clear()

         # Function to update patient visit information in the view patient profile window
        def visits_update_info(self):
            # Retrieve patient and visit data from input fields
            patient_visits_data = {
                "lastName": self.view_visits_ui.visitSearch_lineEdit_1.text(),
                "firstName": self.view_visits_ui.visitSearch_lineEdit_2.text(),
                "patientID": self.view_visits_ui.visitSearch_lineEdit_3.text(),
                "visitID": self.view_visits_ui.visitSearch_lineEdit_4.text(),
                "status": self.view_visits_ui.visitSearch_lineEdit_5.text(),
                "visitDate": self.view_visits_ui.visitSearch_dateEdit.date().toString("yyyy-MM-dd"),
                "visitTime": self.view_visits_ui.visitSearch_timeEdit.time().toString("hh:mm:ss"),
                "type": self.view_visits_ui.visitSearch_lineEdit_6.text(),
                "reason": self.view_visits_ui.visitSearch_lineEdit_7.text()
            }

            # Ensure the patient ID is not empty
            if not patient_visits_data["patientID"]:
                QMessageBox.warning(self, "Update Failed", "Patient ID is required for updating.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Call the update function in the database
            update_success = self.db_visits.visits_update_info(**patient_visits_data)

            if update_success:
                QMessageBox.information(self, "Success", "Patient information updated successfully.",
                                        QMessageBox.StandardButton.Ok)
                self.viewPatientVisits_patSearch_btn()  # Refresh the displayed data
            else:
                QMessageBox.warning(self, "Update Failed", "Please try again.")
                self.viewPatientVisits_patSearch_btn()  # Refresh the displayed data

        # Function to delete patient visit information in the view patient profile window
        def visits_delete_info(self):
            # Retrieve Patient ID from input field
            patient_id = self.view_visits_ui.patSearch_lineEdit.text()

            if not patient_id:
                QMessageBox.warning(self.view_visits_window, "Delete Failed", "Patient ID is required for deleting.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Confirm deletion
            confirm_delete = QMessageBox.warning(
                self.view_visits_window,
                "Confirm Deletion",
                f"Are you sure you want to delete Patient ID: {patient_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm_delete == QMessageBox.StandardButton.Yes:
                # Call delete function in database
                delete_success = self.db_patients.pat_delete_info(patient_id)

                if delete_success:
                    QMessageBox.information(self.view_visits_window, "Success", "Patient record deleted successfully.",
                                            QMessageBox.StandardButton.Ok)
                    self.visits_clear_info()  # Clear the UI fields after deletion
                else:
                    QMessageBox.warning(self.view_visits_window, "Delete Failed", "Error deleting patient record. Please try again.",
                                        QMessageBox.StandardButton.Ok)
                    
        # Function to populate the visit table with visit information
        def visits_show_data(self, result):
            self.result_table_visits.setRowCount(0)

            if not result:
                return

            self.result_table_visits.setRowCount(len(result))

            for row, info in enumerate(result):
                    if isinstance(info["visitDate"], str):
                        qdate = QDate.fromString(info["visitDate"], "yyyy-MM-dd")
                        date_visits_table = qdate.toString("MM-dd-yyyy")
                    else:
                        date_visits_table = info["visitDate"].strftime("%m-%d-%Y")

                    # 24hr conversion to 12hr format with AM/PM suffix
                    visit_time_value = info["visitTime"]
                    if isinstance(visit_time_value, timedelta):
                        total_seconds = int(visit_time_value.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        qtime = QTime(hours, minutes, seconds)
                    elif isinstance(visit_time_value, str):
                        qtime = QTime.fromString(visit_time_value, "hh:mm:ss")
                    else:
                        qtime = QTime(0, 0, 0)

                    formatted_time = qtime.toString("hh:mm AP")

                    info_list = [
                        info["patientID"],
                        info["visitID"],
                        info["status"],
                        info["lastName"],
                        info["firstName"],
                        date_visits_table,
                        #info["visitTime"],
                        formatted_time,
                        info["type"],
                        info["reason"]
                    ]

                    for column, item in enumerate(info_list):
                        cell_item = QTableWidgetItem(str(item))
                        self.result_table_visits.setItem(row, column, cell_item)

        # Function to retrieve visit information from the form
        def get_visits_info(self,):
            patient_id = self.visits_patientID_comboBox.currentText().strip()
            visit_id = self.visit_id.text().strip()
            status = self.status.text().strip()
            last_name = self.visits_last_name.text().strip()
            first_name = self.visits_first_name.text().strip()
            visit_date = self.visit_date.date().toString("yyyy-MM-dd")
            raw_time = self.visit_time.time().toString("hh:mm:ss")
            visit_time = "" if raw_time == "00:00:00" else raw_time
            visit_type = self.visit_type.text().strip()
            reason = self.reason.text().strip()
            
            return {
                "patientID": patient_id,
                "visitID": visit_id,
                "status": status,
                "lastName": last_name,
                "firstName": first_name,
                "visitDate": visit_date,
                "visitTime": visit_time,
                "type": visit_type,
                "reason": reason
            }

        def check_visits_id(self, visit_id):
            result = self.db_visits.search_info(visit_id=visit_id)
            return result
        
        def refresh_visits_table(self):
            QTimer.singleShot(1000, self.do_refresh_visits_table)

        def do_refresh_visits_table(self):
            try:
                self.populate_patient_ids()
                self.visits_patientID_comboBox.setCurrentIndex(0)
                self.visits_patientID_comboBox.setEnabled(True)
                self.visit_id.setEnabled(True)
                self.visit_id.clear()
                self.status.clear()
                self.visits_last_name.clear()
                self.visits_first_name.clear()
                self.visit_date.setDate(QDate.currentDate())
                self.visit_time.setTime(QTime(0, 0, 0))
                self.visit_type.clear()
                self.reason.clear()

                self.search_info_visits()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to refresh patient table: {e}",
                        QMessageBox.StandardButton.Ok)

        # Main code functions for visits table ------------------------------------------------------------------------------------------------------------ #
        def init_signal_slots_billings(self):
            self.billings_add_btn.clicked.connect(self.add_info_billings)
            self.billings_update_btn.clicked.connect(self.update_info_billings)
            self.billings_select_btn.clicked.connect(self.select_info_billings)
            self.billings_delete_btn.clicked.connect(self.delete_info_billings)
            self.billings_clear_btn.clicked.connect(self.clear_info_billings)
            self.billings_search_btn.clicked.connect(self.search_info_billings)
            self.billings_refresh_btn.clicked.connect(self.refresh_billings_table)

            # Connects to View Patient Billings button
            self.view_pat_billings_btn.clicked.connect(self.openViewPatientBillings)

        # Disable all buttons
        def disable_buttons_billings(self):
            for button in self.buttons_list_billings:
                button.setDisabled(True)

        # Enable all buttons
        def enable_buttons_billings(self):
            for button in self.buttons_list_billings:
                button.setDisabled(False)

        # Function to fetch patient IDs from the database and populate into combo box in visits table.
        def populate_patient_ids_billings(self):                            
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Mypatientfirst",
                    database="db_patients"
                )
                cursor = conn.cursor()

                query = "SELECT patientID, visitID, reason FROM visits_info"
                cursor.execute(query)
                billings_patient_ids = cursor.fetchall()

                # Clear existing items and add retrieved patient IDs
                self.billings_patientID_comboBox.clear()
                self.patient_ids_and_visitIDs_dict.clear()

                # Default empty item
                self.billings_patientID_comboBox.addItem("Select Patient ID")

                for patient in billings_patient_ids:
                    billings_patientID_comboBox, billing_visit_id, billing_reason = patient
                    self.patient_ids_and_visitIDs_dict[str(billings_patientID_comboBox)] = (billing_visit_id, billing_reason)
                    self.billings_patientID_comboBox.addItem(str(billings_patientID_comboBox))
                
                print("Selecting Patient IDs, Visit IDs, and Reasons for Billings Table:\n", billings_patient_ids)
                cursor.close()
                conn.close()

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Database Error", f"Failed to load Patient IDs: {e}",
                            QMessageBox.StandardButton.Ok)


        def on_patient_selected_billings(self):
            # Get the selected Patient ID
            selected_id = self.billings_patientID_comboBox.currentText()

            # Check if a valid ID is selected
            if selected_id in self.patient_ids_and_visitIDs_dict:
                billing_visit_id, billing_reason = self.patient_ids_and_visitIDs_dict[selected_id]
                print(f"Auto-filling: Visit ID - {billing_visit_id}, Reason - {billing_reason}")
                
                self.billing_visit_id.setText(str(billing_visit_id))
                self.billing_reason.setText(billing_reason)
        
        # Functions for billings_function_frame
        def add_info_billings(self):
            billings_patientID_comboBox = self.billings_patientID_comboBox.currentText()
            billing_id = self.billing_id.text()
            billing_visit_id = self.billing_visit_id.text()
            amount = self.amount.text()
            billing_status = self.billing_status.text()
            doctor = self.doctor.text()
            service = self.service.text()
            billing_reason = self.billing_reason.text()

            # Ensure required fields are filled
            if not billings_patientID_comboBox or not billing_visit_id or not billing_id or not amount or not billing_status or not doctor or not service or not billing_reason:
                QMessageBox.warning(self, "Warning", "Please fill out all required fields then select add new billing.",
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

                query = """INSERT INTO billings_info 
                        (patientID, visitID, billingID, amount, status, doctor, service, reason) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                values = (billings_patientID_comboBox, billing_visit_id, billing_id, amount, billing_status, doctor, service, billing_reason)

                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()

                # Resets the billings_patientID_comboBox selection
                self.billings_patientID_comboBox.setCurrentIndex(0)
                
                QMessageBox.information(self, "Success", "Billing record added successfully!",
                                        QMessageBox.StandardButton.Ok)

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Error!", f"Database insertion failed: {e}",
                                    QMessageBox.StandardButton.Ok)
            
            self.search_info_billings()
            self.enable_buttons_billings()
        
        def update_info_billings(self):
            # Function to update patient information
            new_billing_info = self.get_billings_info()
            selected_row = self.result_table_billings.currentRow()

            if selected_row == -1:
                QMessageBox.information(self, "Warning", "Please select a patient to update.",
                                        QMessageBox.StandardButton.Ok)
                return
            
            # Get the patient ID of the selected row and update the information if needed
            old_billing_id = self.result_table_billings.item(selected_row, 2).text().strip()
            new_billing_id = new_billing_info["billingID"]

            select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to update this patient information?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if select_option == QMessageBox.StandardButton.No:
                return

            if new_billing_info["billingID"]:
                update_result = self.db_billings.update_info(
                    old_billing_id=old_billing_id,
                    new_billing_id=new_billing_id,
                    amount=new_billing_info["amount"],
                    status=new_billing_info["status"],
                    doctor=new_billing_info["doctor"],
                    service=new_billing_info["service"],
                    reason=new_billing_info["reason"]
                    )
                    
                if update_result:
                    QMessageBox.information(self, "Warning", f"Fail to update the information: {update_result}, Please try again.",
                                            QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.information(self, "Success", f"Billing information updated successfully!",
                                            QMessageBox.StandardButton.Ok)
                    self.search_info_billings()
                        
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
                                
        def select_info_billings(self):
            select_row = self.result_table_billings.currentRow()

            if select_row == -1:
                QMessageBox.information(self, "Warning", "Please select a row to update.")
                return

            # Sets the widgets according to their selected row
            patient_id_text = self.result_table_billings.item(select_row, 0).text().strip()
            visit_id_text   = self.result_table_billings.item(select_row, 1).text().strip()
            billing_id_text = self.result_table_billings.item(select_row, 2).text().strip()
            amount_text     = self.result_table_billings.item(select_row, 3).text().strip()
            status_text     = self.result_table_billings.item(select_row, 4).text().strip()
            doctor_text     = self.result_table_billings.item(select_row, 5).text().strip()
            service_text    = self.result_table_billings.item(select_row, 6).text().strip()
            reason_text     = self.result_table_billings.item(select_row, 7).text().strip()

            # Disables the patientID, visitID and billingID widgets for security and FK relationships
            self.billings_patientID_comboBox.setEnabled(False)
            self.billings_patientID_comboBox.setCurrentText(patient_id_text)
            self.billing_visit_id.setEnabled(False)
            self.billing_visit_id.setText(visit_id_text)
            self.billing_id.setEnabled(False)
            self.billing_id.setText(billing_id_text)
            self.amount.setText(amount_text)
            self.billing_status.setText(status_text)
            self.doctor.setText(doctor_text)
            self.service.setText(service_text)
            self.billing_reason.setText(reason_text)
        
        def delete_info_billings(self):
            # Function to delete visit information
            select_row = self.result_table_billings.currentRow()
            if select_row != -1:
                select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to delete this patient information?\n"
                                                          "This can delete all information related to this patient including in patients and visits table.",
                                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if select_option == QMessageBox.StandardButton.Yes:
                    billing_id = self.result_table_billings.item(select_row, 2).text().strip()

                    delete_result = self.db_billings.delete_info(billing_id=billing_id)
                    if not delete_result:
                        self.search_info_billings()
                    else:
                        QMessageBox.information(self, "Wsarning", f"Fail to delete the information: {delete_result}, Please try again.",
                                                QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to delete.",
                                        QMessageBox.StandardButton.Ok)

        def clear_info_billings(self):
            # Function to clear billing information in the form
            self.billings_patientID_comboBox.setCurrentIndex(0)
            self.billings_patientID_comboBox.setEnabled(True)
            self.billing_visit_id.setEnabled(True)
            self.billing_id.setEnabled(True)
            self.billing_reason.setEnabled(True)
            
            self.billing_visit_id.clear()
            self.billing_id.clear()
            self.amount.clear()
            self.billing_status.clear()
            self.doctor.clear()
            self.service.clear()
            self.billing_reason.clear()

            # Ensures call search_info_visits displays all records
            self.search_info_billings()
        
        def search_info_billings(self):
            billings_info = self.get_billings_info()
            # Check if all fields are empty; if so, fetch all records
            # Otherwise, if all values are empty, fetch all records    

            if not any(billings_info.values()):
                billings_result = self.db_billings.fetch_all_billings()
            else:
                billings_result = self.db_billings.search_info(
                    patient_id=billings_info["patientID"],
                    visit_id=billings_info["visitID"],
                    billing_id=billings_info["billingID"],
                    amount=billings_info["amount"],
                    status=billings_info["status"],
                    doctor=billings_info["doctor"],
                    service=billings_info["service"],
                    reason=billings_info["reason"]
                )
            
            self.billings_show_data(billings_result)


        # Function to View Patient Profile via "viewBillingsProfile_btn_4" button from Billing Page 3
        def openViewPatientBillings(self):
            self.view_billings_window = QMainWindow()
            self.view_billings_ui = Ui_ViewPatientBilling()
            self.view_billings_window.setWindowIcon(QIcon(ResourceLoader.resource_path("icons/MyPatientFirstLogo_Symbol.JPG")))
            #self.view_billings_ui = Ui_ViewPatientBilling()
            self.view_billings_ui.setupUi(self.view_billings_window)

            # Connects to View Patient Bill buttons to function
            self.view_billings_ui.patSearch_btn.clicked.connect(self.viewPatientBillings_patSearch_btn)
            self.view_billings_ui.patSearch_lineEdit.returnPressed.connect(self.viewPatientBillings_patSearch_btn)      # Uses enter/return key for quicker search
            self.view_billings_ui.patClear_btn.clicked.connect(self.billings_clear_info)
            self.view_billings_ui.patUpdate_btn.clicked.connect(self.billings_update_info)
            self.view_billings_ui.patDelete_btn.clicked.connect(self.billings_delete_info)
            
            # Shows the View Patient Billing window/dialog box
            self.view_billings_window.show()
            
        # Function to searchs specific patientID in the view patient visit window
        def viewPatientBillings_patSearch_btn(self):
            patient_id = self.view_billings_ui.patSearch_lineEdit.text().strip()

            if not patient_id:
                QMessageBox.warning(self.view_billings_window, "Input Error", "Please enter a Patient ID.")
                return

            # Fetch patient info from DB as list of dictionaries
            patSearch_patientData_billings = self.db_billings.billings_search_info(patient_id=patient_id)

            if not patSearch_patientData_billings or len(patSearch_patientData_billings) == 0:
                QMessageBox.warning(self.view_billings_window, "Not Found", f"PatientID: {patient_id}\nDoes not exist in the Database.\nMust be PatientID only.\nPlease try again.")
                return
            
            patSearch_patientData_billings = patSearch_patientData_billings[0]

            # Fetch patient's first and last name from patient table in DB
            patNames = self.db_patients.pat_search_info(patient_id=patient_id)
            if patNames and len(patNames) > 0:
                patNames = patNames[0]
                last_name = str(patNames["lastName"])
                first_name = str(patNames["firstName"])
            else:
                last_name = ""
                first_name = ""

            # Convert and display amount with US dollar currency
            amount_value = patSearch_patientData_billings["amount"]
            formatted_amount = f"${float(amount_value):.2f}"

            # Update View Patient Billing UI with current patient info
            self.view_billings_ui.billSearch_lineEdit_1.setText(str(patSearch_patientData_billings["patientID"]))
            self.view_billings_ui.billSearch_lineEdit_2.setText(str(patSearch_patientData_billings["visitID"]))
            self.view_billings_ui.billSearch_lineEdit_3.setText(str(patSearch_patientData_billings["billingID"]))
            self.view_billings_ui.billSearch_lineEdit_4.setText(formatted_amount)
            #self.view_billings_ui.billSearch_lineEdit_4.setText(str(patSearch_patientData_billings["amount"]))
            self.view_billings_ui.billSearch_lineEdit_5.setText(str(patSearch_patientData_billings["status"]))
            self.view_billings_ui.billSearch_lineEdit_6.setText(str(patSearch_patientData_billings["doctor"]))
            self.view_billings_ui.billSearch_lineEdit_7.setText(str(patSearch_patientData_billings["service"]))
            self.view_billings_ui.billSearch_lineEdit_8.setText(str(patSearch_patientData_billings["reason"]))
            self.view_billings_ui.billSearchName_lineEdit_1.setText(last_name)
            self.view_billings_ui.billSearchName_lineEdit_2.setText(first_name)

            # Disables patientID, visitID, and billingID widgets for security and FK relationships
            self.view_billings_ui.billSearch_lineEdit_1.setEnabled(False)
            self.view_billings_ui.billSearch_lineEdit_2.setEnabled(False)
            self.view_billings_ui.billSearch_lineEdit_3.setEnabled(False)

            # Sets a Profile Picture based on sex of PatientID from patient table
            patient_id = patSearch_patientData_billings["patientID"]
            patient_sex_data = self.db_patients.pat_search_info(patient_id=patient_id)
            if patient_sex_data:
                sex = patient_sex_data[0]["sex"].lower()
                if sex == "male":
                    profile_pic = ResourceLoader.resource_path("images/default_male_profile_icon.jpg")
                elif sex == "female":
                    profile_pic = ResourceLoader.resource_path("images/default_female_profile_icon.jpg")
                else:
                    profile_pic = ResourceLoader.resource_path("images/no_image_found_icon.jpg")

                pixmap = QPixmap(profile_pic)
                self.view_billings_ui.profilePic_label.setPixmap(pixmap)
                self.view_billings_ui.profilePic_label.setScaledContents(True)
            else:
                profile_pic = ResourceLoader.resource_path("images/no_image_found_icon.jpg")
                pixmap = QPixmap(profile_pic)
                self.view_billings_ui.profilePic_label.setPixmap(pixmap)
                self.view_billings_ui.profilePic_label.setScaledContents(True)

        # Callback function to fetch specific patientID for viewPatientBillings_patSearch_btn()
        def billings_search_info(self, patient_id):
            query = "SELECT * FROM patientID, visitID, billingID, amount, status, doctor, service, reason FROM billing WHERE patientID = %s"
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchone()

            if result:
                return result
            else:
                return None

        # Function to clear patient billing information in the view patient profile window
        def billings_clear_info(self):
            self.view_billings_ui.patSearch_lineEdit.clear()
            self.view_billings_ui.billSearch_lineEdit_1.clear()
            self.view_billings_ui.billSearch_lineEdit_2.clear()
            self.view_billings_ui.billSearch_lineEdit_3.clear()
            self.view_billings_ui.billSearch_lineEdit_4.clear()
            self.view_billings_ui.billSearch_lineEdit_5.clear()
            self.view_billings_ui.billSearch_lineEdit_6.clear()
            self.view_billings_ui.billSearch_lineEdit_7.clear()
            self.view_billings_ui.billSearch_lineEdit_8.clear()
            self.view_billings_ui.profilePic_label.clear()
            self.view_billings_ui.billSearchName_lineEdit_1.clear()
            self.view_billings_ui.billSearchName_lineEdit_2.clear()
        
        # Function to update patient billing information in the view patient profile window
        def billings_update_info(self):
            # Exception handler which ignores amount with dollar sign and comma from user input
            amount_raw = self.view_billings_ui.billSearch_lineEdit_4.text()
            try:
                formatted_amount = f"{float(amount_raw.replace('$', '').replace(',', '')):.2f}"
            except ValueError:
                QMessageBox.warning(self, "Invalid Amount", f"'{amount_raw}' is not a valid amount.",
                                    QMessageBox.StandardButton.Ok)
                return
            
            # Retrieve patient and visit data from input fields
            patient_billings_data = {
                "patientID": self.view_billings_ui.billSearch_lineEdit_1.text(),
                "visitID": self.view_billings_ui.billSearch_lineEdit_2.text(),
                "billingID": self.view_billings_ui.billSearch_lineEdit_3.text(),
                "amount": formatted_amount,
                "status": self.view_billings_ui.billSearch_lineEdit_5.text(),
                "doctor": self.view_billings_ui.billSearch_lineEdit_6.text(),
                "service": self.view_billings_ui.billSearch_lineEdit_7.text(),
                "reason": self.view_billings_ui.billSearch_lineEdit_8.text()
            }

            # Ensure the patient ID is not empty
            if not patient_billings_data["patientID"]:
                QMessageBox.warning(self, "Update Failed", "Patient ID is required for updating.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Call the update function in the database
            update_success = self.db_billings.billings_update_info(**patient_billings_data)

            if update_success:
                QMessageBox.information(self, "Success", "Patient information updated successfully.",
                                        QMessageBox.StandardButton.Ok)
                self.viewPatientBillings_patSearch_btn()  # Refresh the displayed data
            else:
                QMessageBox.warning(self, "Update Failed", "Please try again.")
                self.viewPatientBillings_patSearch_btn()  # Refresh the displayed data

        # Function to delete patient billing information in the view patient profile window
        def billings_delete_info(self):
            # Retrieve Patient ID from input field
            patient_id = self.view_billings_ui.patSearch_lineEdit.text()

            if not patient_id:
                QMessageBox.warning(self.view_billings_window, "Delete Failed", "Patient ID is required for deleting.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Confirm deletion
            confirm_delete = QMessageBox.warning(
                self.view_billings_window,
                "Confirm Deletion",
                f"Are you sure you want to delete Patient ID: {patient_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm_delete == QMessageBox.StandardButton.Yes:
                # Call delete function in database
                delete_success = self.db_patients.pat_delete_info(patient_id)

                if delete_success:
                    QMessageBox.information(self.view_billings_window, "Success", "Patient record deleted successfully.",
                                            QMessageBox.StandardButton.Ok)
                    self.billings_clear_info()  # Clear the UI fields after deletion
                else:
                    QMessageBox.warning(self.view_billings_window, "Delete Failed", "Error deleting patient record. Please try again.",
                                        QMessageBox.StandardButton.Ok)

        # Function to populate the billing table with visit information
        def billings_show_data(self, result):
            self.result_table_billings.setRowCount(0)

            if not result:
                return

            self.result_table_billings.setRowCount(len(result))

            for row, info in enumerate(result):
                    info_list = [
                        info["patientID"],
                        info["visitID"],
                        info["billingID"],
                        info["amount"],
                        info["status"],
                        info["doctor"],
                        info["service"],
                        info["reason"]
                    ]

                    for column, item in enumerate(info_list):
                        # For column amount, add dollar sign and format of each price
                        if column == 3:
                            amount_value = float(item)
                            cell_item = QTableWidgetItem(f"${amount_value:.2f}")
                        else:
                            cell_item = QTableWidgetItem(str(item))
                        self.result_table_billings.setItem(row, column, cell_item)

        # Function to retrieve visit information from the form
        def get_billings_info(self,):
            patient_id = self.billings_patientID_comboBox.currentText().strip()
            billing_visit_id = self.billing_visit_id.text().strip()
            billing_id = self.billing_id.text().strip()

            # Exception handler which ignores amount with dollar sign and comma from user input
            amount_raw = self.amount.text().strip()
            try:
                formatted_amount = f"{float(amount_raw.replace('$', '').replace(',', '')):.2f}"
            except ValueError:
                formatted_amount = ""

            billing_status = self.billing_status.text().strip()
            doctor = self.doctor.text().strip()
            service = self.service.text().strip()
            billing_reason = self.billing_reason.text().strip()
            
            return {
                "patientID": patient_id,
                "visitID": billing_visit_id,
                "billingID": billing_id,
                "amount": formatted_amount,
                "status": billing_status,
                "doctor": doctor,
                "service": service,
                "reason": billing_reason
            }

        def check_billings_id(self, billing_id):
            result = self.db_billings.search_info(billing_id)
            return result

        def refresh_billings_table(self):
            QTimer.singleShot(1000, self.do_refresh_billings_table)

        def do_refresh_billings_table(self):
            try:
                self.populate_patient_ids_billings()
                self.billings_patientID_comboBox.setCurrentIndex(0)
                self.billings_patientID_comboBox.setEnabled(True)
                self.billing_visit_id.setEnabled(True)
                self.billing_id.setEnabled(True)
                self.billing_reason.setEnabled(True)
                self.billing_visit_id.clear()
                self.billing_id.clear()
                self.amount.clear()
                self.billing_status.clear()
                self.doctor.clear()
                self.service.clear()
                self.billing_reason.clear()

                self.search_info_billings()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to refresh patient table: {e}",
                        QMessageBox.StandardButton.Ok)

# Application entry form ----------------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load style.qss file
    with open(ResourceLoader.resource_path("qss/style.qss"), "r") as f:
        style_qss = f.read()
    app.setStyleSheet(style_qss)

    # Load and set global font
    custom_font = GoogleFonts().load_google_fonts(ResourceLoader.resource_path("fonts/Poppins-Light.ttf"))
    app.setFont(custom_font)

    LoginWindow = LoginWindow()
    LoginWindow.show()

    #MainWindow = MainWindow()
    #MainWindow.show()

    app.exec()