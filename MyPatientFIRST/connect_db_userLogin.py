import time
import mysql.connector
import bcrypt
from PyQt6.QtWidgets import (
    QPushButton, QMessageBox, QWidget,
    QLineEdit, QLabel, QGridLayout
    )
from PyQt6.QtGui import QIcon, QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, QTimer

# Classes for password encryption using hashing
def hash_password(curr_password: str) -> str:
    # .gensalt() generates a random string added to a password before hashing
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(curr_password.encode('utf-8'), salt)
    # Debugging and testing
    print("-----------------------------------")
    print("Current Password: ", curr_password)
    print("Salt: ", salt)
    print("Hashed: ", hashed_password)
    return hashed_password.decode('utf-8')

def check_password(curr_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(curr_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
# Class for the user login applicaiton
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyPatientFirst User Login")
        self.setWindowIcon(QIcon("icons/MyPatientFirstLogo_Symbol.JPG"))
        self.window_width, self.window_height = 400, 300
        self.setFixedSize(self.window_width, self.window_height)

        layout = QGridLayout()
        self.setLayout(layout)

        self.login_status_correct = QLabel("")
        self.login_status = QLabel("")
        self.login_status_correct.setText("Hello, welcome to MyPatientFirst!\nPlease login below or create a new account.")
        self.login_status_correct.setStyleSheet("font-family: Verdana; font-size: 2em; color: black;")
        self.login_status.setStyleSheet("font-family: Verdana; font-size: 1.5em; color: red;")

        # Create widgets for username and password and arrange widgets in layout
        self.username_label = QLabel("Username:")
        self.password_label = QLabel("Password:")

        self.username_edit = QLineEdit()
        tenChar_username = QRegularExpression("^[A-Za-z0-9]{1,10}$")
        validator_username = QRegularExpressionValidator(tenChar_username, self.username_edit) # Allows only 10 characters or less for Username
        self.username_edit.setValidator(validator_username)

        self.password_edit = QLineEdit()
        tenChar_password =  QRegularExpression(r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\'":\\|,.<>/?]{1,10}$')
        validator_password = QRegularExpressionValidator(tenChar_password, self.password_edit) # Allows only 10 characters/special characters or less for Password
        self.password_edit.setValidator(validator_password)

        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        button_login = QPushButton("Login", clicked=self.checkCredentials)
        self.create_account_button = QPushButton("Create New Account", clicked=self.openCreateAccountWindow)

        layout.addWidget(self.login_status_correct,     0, 0, 1, 3)
        layout.addWidget(self.username_label,           1, 0, 1, 1)
        layout.addWidget(self.username_edit,            1, 1, 1, 3)
        layout.addWidget(self.password_label,           2, 0, 1, 1)
        layout.addWidget(self.password_edit,            2, 1, 1, 3)
        layout.addWidget(button_login,                  3, 3, 1, 1)
        layout.addWidget(self.create_account_button,    4, 2, 1, 2)
        layout.addWidget(self.login_status,             5, 0, 1, 3)

        # Connect to the MySQL database using mysql.connector
        self.connectToUserLoginDatabase()
    
    # Function to connect User Login Creditials to MySQL Database
    def connectToUserLoginDatabase(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Mypatientfirst",
                database="db_patients"
            )
            if not self.db.is_connected():
                self.login_status.setText("Connection failed")
        except mysql.connector.Error as err:
            self.login_status.setText(f"Connection failed: {err}")

    # Function to check user login credentials
    def checkCredentials(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        # Debugging and testing hashing and encryption from hash_password()
        debug_hashed = hash_password(password)
        print("Encrypted Password:", debug_hashed)
        print("----------------------------------------------")

        try:
            cursor = self.db.cursor(dictionary=True)
            query = ("SELECT * FROM userLogin_info WHERE MPFUserName = %s")
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result:
                if result.get("MPFPassword") == password:
                    self.login_status.setStyleSheet("font-family: Verdana; font-size: 1.5em; color: green;")
                    self.login_status.setText(f"Login successful!\n{username} your password has been encrypted\nand stored successfully!\nPlease wait...")

                    QTimer.singleShot(5000, lambda: (
                        __import__("main").MainWindow(),
                        setattr(self, 'main_window',
                        __import__("main").MainWindow(username=username)),
                        self.main_window.show(),
                        self.close()
                        )
                    )
                else:
                    self.login_status.setText("Password is incorrect.\nPlease try again.")
            else:
                self.login_status.setText("Username or Password is incorrect.\nPlease try again.")
                cursor.close()
        except mysql.connector.Error as e:
            self.login_status.setText(f"Database error: {e}")

    def openCreateAccountWindow(self):
        self.create_account_window = CreateAccountWindow(db_connection=self.db)
        self.create_account_window.show()

# Class for the create new account applicaiton
class CreateAccountWindow(QWidget):
    def __init__(self, db_connection=None):
        super().__init__()
        self.setWindowTitle("Create New Account")
        self.setWindowIcon(QIcon("icons/MyPatientFirstLogo_Symbol.JPG"))
        self.window_width, self.window_height = 600, 250
        self.setFixedSize(self.window_width, self.window_height)

        layout = QGridLayout()
        self.setLayout(layout)
        
        self.new_userId_info = QLabel("Please enter a new User ID, Username, and Password to create a new account."
                                      "\n1). User ID must be unique and 5 digits ONLY."
                                      "\n2). Username must be unique, letters and numbers ONLY, and\n     10 characters or less."
                                      "\n3). Password must be 10 characters or less. Special characters are allowed.\n     (e.g. !, @, #, etc.).")
        self.new_userId_info.setStyleSheet("font-family: Verdana; font-size: 1.5em; color: red;")
        self.new_userId_label = QLabel("New User ID:")
        self.new_username_label = QLabel("New Username:")
        self.new_password_label = QLabel("New Password:")
        self.new_userId_edit = QLineEdit()
        self.new_userId_edit.setValidator(QIntValidator(10000, 99999, self)) # Allows only 5-digit numbers for User ID 

        self.new_username_edit = QLineEdit()
        tenChar_new_username = QRegularExpression("^[A-Za-z0-9]{1,10}$")
        validator_new_username = QRegularExpressionValidator(tenChar_new_username, self.new_username_edit) # Allows only 10 characters or less for Username
        self.new_username_edit.setValidator(validator_new_username)

        self.new_password_edit = QLineEdit()
        tenChar_new_password =  QRegularExpression(r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\'":\\|,.<>/?]{1,10}$')
        validator_new_password = QRegularExpressionValidator(tenChar_new_password, self.new_password_edit) # Allows only 10 characters/special characters or less for Password
        self.new_password_edit.setValidator(validator_new_password)

        self.submit_button = QPushButton("Create Account", clicked=self.createAccount)

        layout.addWidget(self.new_userId_info,      0, 0, 1, 4)
        layout.addWidget(self.new_userId_label,     1, 0, 1, 1)
        layout.addWidget(self.new_userId_edit,      1, 1, 1, 3)
        layout.addWidget(self.new_username_label,   2, 0, 1, 1)
        layout.addWidget(self.new_username_edit,    2, 1, 1, 3)
        layout.addWidget(self.new_password_label,   3, 0, 1, 1)
        layout.addWidget(self.new_password_edit,    3, 1, 1, 3)
        layout.addWidget(self.submit_button,        4, 3, 1, 1)
        
        if db_connection:
            self.db = db_connection
        else:
            try:
                self.db = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Mypatientfirst",
                    database="db_patients"
                )
            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Database Error", f"Error connecting to database: {e}")

    # Function to create a new account if creditionals are not already in database using a new account window
    def createAccount(self):
        new_id = self.new_userId_edit.text().strip()
        new_username = self.new_username_edit.text().strip()
        new_password = self.new_password_edit.text().strip()
        
        if not new_id or not new_username or not new_password:
            QMessageBox.warning(self, "Input Error", "User ID, username,and password are required for account creation.")
            return
        
        try:
            cursor = self.db.cursor(dictionary=True)
            check_query = "SELECT * FROM userLogin_info WHERE MPFUserName = %s"
            cursor.execute(check_query, (new_username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "User ID already exists. Please choose a different User ID.")
                cursor.close()
                return
            
            insert_query = "INSERT INTO userLogin_info (userID, MPFUserName, MPFPassword) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (new_id, new_username, new_password))
            self.db.commit()
            QMessageBox.information(self, "Success", "Account created successfully!")
            cursor.close()
            self.close()
        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"Error creating account: {e}")