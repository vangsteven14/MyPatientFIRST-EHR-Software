# Import neccessary modules
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QMessageBox, QTableWidgetItem, QComboBox
from PyQt6.QtGui import QIcon, QPixmap, QIntValidator
from PyQt6.QtCore import QResource, QDate
import mysql.connector

# Import the UI widgets and functions for the main window
from main_ui_widgets_buttons import MainUIWidgetsButtons

# Import the UI and database connection class
from connect_database import ConnectDatabase                               
from connect_db_patients import ConnectDatabasePatients
from connect_db_visits import ConnectDatabaseVisits                        
#from connect_db_billings import ConnectDatabaseBillings                    # Still in progress

# Import the Main Window UI and View Patient Profile UI files
from main_ui import Ui_MainWindow
from view_patient_profile_ui import Ui_ViewPatientProfile

# Import the resource file
QResource.registerResource("resource.qrc")

# Create a main window class
class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Set the window icon ------------------------------------------- #
            self.setWindowIcon(QIcon("icons/MyPatientFirstLogo_Symbol.JPG")) 

            # Creates a database connection object ------------------------------------ #  
            self.db = ConnectDatabase()                              
            self.db_patients = ConnectDatabasePatients(self.db)
            self.db_visits = ConnectDatabaseVisits(self.db)                 
            #self.db_billings = ConnectDatabaseBillings(self.db)             # Still in progress

            # Initialize the UI from a seperate UI file ------------------------------- #
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.main_ui_widgets_buttons = MainUIWidgetsButtons(self.ui)

            # Intitalize Widget Toggles ----------------------------------------------- #
            self.ui.side_widget_1.hide()         
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.home_btn_2.setChecked(True)

            # Load Hide/Show Icons ---------------------------------------------------- #
            self.main_ui_widgets_buttons.load_hide_icons()
            self.main_ui_widgets_buttons.load_show_icons()

            # Make sure buttons are connected to functions ---------------------------- #
            self.main_ui_widgets_buttons.connect_buttons()  

            # Connect UI elements to class varables for patients_info table ----------------------------------------------------- #
            self.patient_id = self.ui.patientlineEdit_1
            self.patient_id.setValidator(QIntValidator(100, 999)) # Allows only 3-digit numbers for PatientID 
                                                                  # Restrict input to integers
            self.last_name = self.ui.patientlineEdit_3
            self.first_name = self.ui.patientlineEdit_4
            self.sex = self.ui.patientlineEdit_2
            self.age = self.ui.patientlineEdit_5
            self.birthDate = self.ui.patient_dateEdit_1
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

            # Initialize signal and slots connections for patients_info table
            self.init_signal_slots_patients()

            # Connect UI elements to class varables for visits_info table ----------------------------------------------------- #
            # Create a combo box for patient IDs
            '''
            self.visits_patient_id = self.ui.visits_comboBox
            self.visit_id = self.ui.visitslineEdit_1
            '''
            # Searches for specific patient ID and their last and first names
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
            self.visits_birthDate = self.ui.patient_dateEdit_1
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

            # Initialize signal and slots connections for vists_info table # Down on lines 516-7
            self.init_signal_slots_visits()

            # Populate initial data from patients_info table to patient_id combobox
            #self.update_patient_id()

        # Main code functions for patient table ------------------------------------------------------------------------------------------------------------ #
        def init_signal_slots_patients(self):
            self.pat_add_btn.clicked.connect(self.add_info)
            self.pat_update_btn.clicked.connect(self.update_info)
            self.pat_select_btn.clicked.connect(self.select_info)
            self.pat_delete_btn.clicked.connect(self.delete_info) 
            self.pat_clear_btn.clicked.connect(self.clear_info)
            self.pat_search_btn.clicked.connect(self.search_info)

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

        # Functions for patient_function_frame
        def add_info(self):
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
            self.enable_buttons_patients()
                
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
                
            self.show_data(patient_result)

        # Function to View Patient Profile via "viewPatProfile_btn_1" button from Patient Page 1
        def openViewPatientProfile(self):
            self.view_patient_window = QMainWindow()
            self.view_patient_ui = Ui_ViewPatientProfile()
            self.view_patient_window.setWindowIcon(QIcon("icons/MyPatientFirstLogo_Symbol.JPG"))
            self.view_patient_ui = Ui_ViewPatientProfile()
            self.view_patient_ui.setupUi(self. view_patient_window)

            # Connects to View Patient Profile buttons to function
            self.view_patient_ui.patSearch_btn.clicked.connect(self.viewPatientProfile_patSearch_btn)
            self.view_patient_ui.patClear_btn.clicked.connect(self.pat_clear_info)
            self.view_patient_ui.patUpdate_btn.clicked.connect(self.pat_update_info)
            self.view_patient_ui.patDelete_btn.clicked.connect(self.pat_delete_info)

            # SHows the View Patient Profile window/dialog box
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
                QMessageBox.warning(self.view_patient_window, "Not Found", f"PatientID: {patient_id}\nDoes not exist in the Database.\nPlease try again.")
                return

            patSearch_patientData = patSearch_patientData[0] 

            # Update View Patient Profile UI with current patient data
            self.view_patient_ui.patSearch_lineEdit_1.setText(str(patSearch_patientData["lastName"])) 
            self.view_patient_ui.patSearch_lineEdit_2.setText(str(patSearch_patientData["firstName"]))  
            self.view_patient_ui.patSearch_lineEdit_3.setText(str(patSearch_patientData["patientID"])) 
            self.view_patient_ui.patSearch_lineEdit_4.setText(str(patSearch_patientData["sex"]))  
            self.view_patient_ui.patSearch_lineEdit_5.setText(str(patSearch_patientData["age"]))
            self.view_patient_ui.patSearch_lineEdit_6.setText(str(patSearch_patientData["emailAddress"]))  
            self.view_patient_ui.patSearch_lineEdit_7.setText(str(patSearch_patientData["medications"]))

            # Convert birthDate properly
            self.view_patient_ui.patSearch_dateEdit.setDate(QDate(patSearch_patientData["birthDate"].year, 
                                                patSearch_patientData["birthDate"].month, 
                                                patSearch_patientData["birthDate"].day))
            
            # Sets a Profile Picture based on sex of PatientID**
            if patSearch_patientData["sex"].lower() == "male":
                profile_pic = "images/default_male_profile_icon.jpg"  # Path to male image
            elif patSearch_patientData["sex"].lower() == "female":
                profile_pic = "images/default_female_profile_icon.jpg"  # Path to female image
            else:
                profile_pic = "images/no_image_found_icon.jpg"  # Default image if sex is unknown

            # Load and display image
            pixmap = QPixmap(profile_pic)
            self.view_patient_ui.profilePic_label.setPixmap(pixmap)
            self.view_patient_ui.profilePic_label.setScaledContents(True)  # Ensure the image fits the label

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
            # Function to clear all patient information in the view patient profile window
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
            patient_data = {
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
            if not patient_data["patientID"]:
                QMessageBox.warning(self, "Update Failed", "Patient ID is required for updating.",
                                    QMessageBox.StandardButton.Ok)
                return

            # Include image data if available
            if hasattr(self, "image_path") and self.image_path:
                with open(self.image_path, "rb") as file:
                    patient_data["profileImage"] = file.read()

            # Call the update function in the database
            update_success = self.db_patients.pat_update_info(**patient_data)

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
        def get_patient_info(self,):
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
        
        # Main code functions for visits table ------------------------------------------------------------------------------------------------------------ #
        def init_signal_slots_visits(self):
            self.visits_add_btn.clicked.connect(self.add_info_visits)
            self.visits_update_btn.clicked.connect(self.update_info_visits)
            self.visits_select_btn.clicked.connect(self.select_info_visits)
            self.visits_delete_btn.clicked.connect(self.delete_info_visits) 
            self.visits_clear_btn.clicked.connect(self.clear_info_visits)
            self.visits_search_btn.clicked.connect(self.search_info_visits)

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
        
        '''
        def update_patient_id(self):
            patient_id_result = self.db_visits.get_visits_patientID_info()

            self.visits_patientID_comboBox.clear()

            patient_list = [""]
            for item in patient_id_result:
                for key, value in item.items():
                    if value != "":
                        patient_list.append((value))
            
            if len(patient_list) > 1:
                self.visits_patientID_comboBox.addItems(patient_list)

            self.visits_patientID_comboBox.setCurrentIndex(0)
        '''
        # Function to fetch patient IDs from the database and populate into combo box.
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
                
                print("Patient IDs:", patient_ids)
                cursor.close()
                conn.close()

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Database Error", f"Failed to load Patient IDs: {e}",
                            QMessageBox.StandardButton.Ok)

        def on_patient_selected(self):
            # Get the selected Patient ID
            selected_id = self.visits_patientID_comboBox.currentText()

            print(f"Selected Patient ID: {selected_id}")  # Debugging: See what is selected

            # Check if a valid ID is selected
            if selected_id in self.patient_ids_and_names_dict:
                visits_last_name, visits_first_name = self.patient_ids_and_names_dict[selected_id]
                print(f"Auto-filling: Last Name - {visits_last_name}, First Name - {visits_first_name}")
                
                self.visits_last_name.setText(visits_last_name)
                self.visits_first_name.setText(visits_first_name)
            else:
                print("No match found for selected ID")  # Debugging
                #self.visits_last_name.clear()
                #self.visits_first_name.clear()

        # Functions for visits_function_frame
        def add_info_visits(self):
            visits_patientID_comboBox = self.visits_patientID_comboBox.currentText()
            visit_id = self.visit_id.text()
            status = self.status.text()
            visits_last_name = self.visits_last_name.text()
            visits_first_name = self.visits_first_name.text()
            visits_birthDate = self.visits_birthDate.date().toString("yyyy-MM-dd")
            visit_type = self.visit_type.text()
            reason = self.reason.text()

            # Ensure required fields are filled
            if not visits_patientID_comboBox or not visit_id or not status or not visits_last_name or not visits_first_name or not visits_birthDate or not visit_type or not reason:
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

                query = """INSERT INTO visits_info 
                        (visitID, patientID, status, lastName, firstName, birthDate, type, reason) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (visit_id, visits_patientID_comboBox, status, visits_last_name, visits_first_name, visits_birthDate, visit_type, reason)

                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()
                
                QMessageBox.information(self, "Success", "Patient record added successfully!",
                                        QMessageBox.StandardButton.Ok)

            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Error!", f"Database insertion failed: {e}",
                                    QMessageBox.StandardButton.Ok)
            
            self.search_info_visits()
            self.enable_buttons_visits()

        def update_info_visits(self):
            # Function to update patient information
            new_visits_info = self.get_visits_info()

            if new_visits_info["visitID"]:
                update_result = self.db_visits.update_info(
                    visit_id=new_visits_info["visitID"],
                    status=new_visits_info["status"],
                    last_name=new_visits_info["lastName"],
                    first_name=new_visits_info["firstName"],
                    birth_date=new_visits_info["birthDate"],
                    type=new_visits_info["type"],
                    reason=new_visits_info["reason"]
                )

                if update_result:
                    QMessageBox.information(self, "Warning", f"Fail to update the information: {update_result}, Please try again.",
                                            QMessageBox.StandardButton.Ok)
                else:
                    self.search_info_visits()
            
            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
        def select_info_visits(self):
            # Function to select and populate visit information in the form
            select_row = self.result_table_visits.currentRow()

            if select_row != -1:
                # Convert the birthDate from the table into a QDate correctly
                birth_date_text = self.result_table_visits.item(select_row, 5).text().strip()
                visits_birth_date = QDate.fromString(birth_date_text, "MM-dd-yyyy")

                self.visit_id.setEnabled(False)
                visits_patientID_comboBox = self.result_table_visits.item(select_row, 0).text().strip()
                visit_id = self.result_table_visits.item(select_row, 0).text().strip()
                visits_last_name = self.result_table_visits.item(select_row, 1).text().strip()
                visits_first_name = self.result_table_visits.item(select_row, 2).text().strip()
                visits_birth_date = self.birthDate.date().toString("yyyy-MM-dd")
                visit_type = self.result_table_visits.item(select_row, 6).text().strip()
                reason = self.result_table_visits.item(select_row, 7).text().strip()

                self.patient_id.setText(visits_patientID_comboBox)
                self.visit_id.setText(visit_id)
                self.visits_last_name.setText(visits_last_name)
                self.visits_first_name.setText(visits_first_name)
                self.birthDate.setDate(QDate.fromString(visits_birth_date, "MM-dd-yyyy"))
                self.visit_type.setText(visit_type)
                self.reason.setText(reason)

            else:
                QMessageBox.information(self, "Warning", "Please select one patient information to update.",
                                        QMessageBox.StandardButton.Ok)
        def delete_info_visits(self):
            # Function to delete visit information
            select_row = self.result_table_visits.currentRow()
            if select_row != -1:
                select_option = QMessageBox.warning(self, "Warning", "Are you sure you want to delete this patient information?",
                                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if select_option == QMessageBox.StandardButton.Yes:
                    visit_id = self.result_table_visits.item(select_row, 0).text().strip()

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
            self.visits_patientID_comboBox.clear()
            #self.populate_patient_ids(self).clear()
            self.visit_id.setEnabled(True)
            self.visits_last_name.clear()
            self.visits_first_name.clear()
            self.visits_birthDate.setDate(QDate.currentDate())
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
                    birth_date=visits_info["birthDate"],
                    type=visits_info["type"],
                    reason=visits_info["reason"]
                )
            
            self.visits_show_data(visits_result)

        def openViewPatientVisits(self):                    # Functions still in progress
            pass
        def viewPatientVisits_patSearch_btn(self):
            pass
        def visits_search_info(self):
            pass
        def visits_clear_info(self):
            pass
        def visits_update_info(self):
            pass
        def visits_delete_info(self):
            pass

        # Function to populate the visit table with visit information
        def visits_show_data(self, result):
            if result:
                self.result_table_visits.setRowCount(0)
                self.result_table_visits.setRowCount(len(result))

                for row, info in enumerate(result):
                    info_list = [
                        info["patientID"],
                        info["visitID"],
                        info["status"],
                        info["lastName"],
                        info["firstName"],
                        info["birthDate"],
                        info["type"],
                        info["reason"]
                    ]

                    for column, item in enumerate(info_list):
                        cell_item = QTableWidgetItem(str(item))
                        self.result_table_visits.setItem(row, column, cell_item)

            else:
                self.result_table_visits.setRowCount(0)
                return

        # Function to retrieve visit information from the form
        def get_visits_info(self,):
            visits_patientID_comboBox = self.visits_patientID_comboBox.currentText().strip()
            visit_id = self.visit_id.text().strip()
            status = self.status.text().strip()
            visits_last_name = self.visits_last_name.text().strip()
            visits_first_name = self.visits_last_name.text().strip()
            visits_birth_date = self.birthDate.date().toString("yyyy-MM-dd")
            visit_type = self.visit_type.text().strip()
            reason = self.reason.text().strip()

            visits_info = {
                "patientID": visits_patientID_comboBox,
                "visitID": visit_id,
                "status": status,
                "lastName": visits_last_name,
                "firstName": visits_first_name,
                "birthDate": visits_birth_date,
                "type": visit_type,
                "reason": reason
            }

            return visits_info

        def check_visits_id(self, visit_id):
            result = self.db_visits.search_info(visit_id=visit_id)
            return result
        
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