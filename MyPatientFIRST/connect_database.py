import mysql.connector
from datetime import datetime
#from mysql.connector import Error

class ConnectDatabase:
    def __init__(self):
        self.con = None
        self.cursor = None
        self.connect_db() 

    # Establish a database connection    
    def connect_db(self):
        try:
            self.con = mysql.connector.connect(
                host="localhost",
                port="3306",
                user="root",
                password="Mypatientfirst",
                database="db_patients"
            )
            self.cursor = self.con.cursor(dictionary=True)
            print("Database connected successful!")

        except mysql.connector.Error as e:
            self.con.rollback()
            print(f"Database error: {e}")  # Log the error
            return "Error: Unable to add patient. Please try again."

    def check_connection(self):
        if self.con is None or not self.con.is_connected():
            print("Reconnecting to database...")
            self.connect_db()

    # Execute queries safely
    def execute_query(self, query, params=None, fetch=False):
        self.check_connection()  # Ensure connection is active
        if self.con is None:
            print("No active database connection.")
            return None
        try:
            self.check_connection()
            self.cursor.execute(query, params)
            if fetch:
                return self.cursor.fetchall()  # Fetch results for SELECT queries
            self.con.commit()
            return True
        
        except mysql.connector.Error as e:
            self.con.rollback()
            return f"Error: {e}"
    """
    def execute_query(self, query, params=None):
        self.check_connection()  # Ensure connection is active
        try:
            self.cursor.execute(query, params)
            self.con.commit()
            return self.cursor.fetchall()  # Return results if applicable
        except mysql.connector.Error as e:
            print(f"Query failed: {e}")
            return None
    """

    # Fetch all patients from SQL database  
    def fetch_all_patients(self):
        query = "SELECT * FROM patients_info"
        return self.execute_query(query, fetch=True)
        
    # functions for patients_info from SQL database -------------------------------------------------------------------------- #
    # function to add data to patients_info from SQL database
    def add_info(self, patient_id, last_name, first_name, sex, age, birth_date, medications, email_address):
        # Ensures connection is Active
        self.connect_db()

        if self.con is None:
            return "Database connection failed."
        
        try:
            # Check if Patient ID Exists
            self.cursor.execute("SELECT COUNT(*) FROM patients_info WHERE patientID = %s", (patient_id,))
            result = self.cursor.fetchone()

            if result and result["COUNT(*)"] > 0:
                return "Error: PatientID already exists. Choose a different ID."

            # Convert birth_date from MM-DD-YYYY to YYYY-MM-DD
            try:
                birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")  # Convert to datetime object
                birth_date = birth_date_obj.strftime("%Y-%m-%d")  # Format to MySQL's YYYY-MM-DD
            except ValueError:
                return "Error: Invalid date format. Use MM-DD-YYYY. Please try again."
            
            # Ensure non-null values
            medications = medications if medications else ""
            email_address = email_address if email_address else ""
            
            # Use Parameterized Query to Prevent SQL Injection
            sql = """ 
                INSERT INTO patients_info (patientID, lastName, firstName, sex, age, birthDate, medications, emailAddress)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (patient_id, last_name, first_name, sex, age, birth_date, medications, email_address)

            self.cursor.execute(sql, values)
            self.con.commit()

            return "Success: Patient added!"

        except mysql.connector.Error as e:
            self.con.rollback()
            print(f"Database error: {e}")  # Log the error
            return "Error: Unable to add patient. Please try again."

    # function to update data to patients_info from SQL database 
    def update_info(self, patient_id, last_name, first_name, sex, age, birth_date, medications, email_address):
        # Connect to the database
        self.connect_db()

        # Establish SQL query for updating information
        sql = f""" 
            UPDATE patients_info
            SET lastName = '{last_name}', firstName = '{first_name}', sex = '{sex}', age = {age}, birthDate = '{birth_date}', medications = '{medications}', emailAddress = '{email_address}'
            WHERE patientID = {patient_id}
        """
        
        # Execute SQL query for updating information
        try:
            self.cursor.execute(sql)
            self.con.commit()
        
        except Exception as E: # Rollback the transaction in case of an error
            self.con.rollback()
            return E

        finally: # Close the database connection
            self.con.close()

    # function to delete data to patients_info from SQL database 
    def delete_info(self, patient_id):
        # Connect to the database
        self.connect_db()    

        # Establish SQL query for deleting information
        sql = f"""
            DELETE FROM patients_info
            WHERE patientID = {patient_id}
        """

        # Execute SQL query for deleting information
        try:
            self.cursor.execute(sql)
            self.con.commit()    
        
        except Exception as E: # Rollback the transaction in case of an error
            self.con.rollback()
            return E

        finally: # Close the database connection
            self.con.close()

    # function to search data to patients_info from SQL database
    def search_info(self, patient_id=None, last_name=None, first_name=None, sex=None, age=None, birth_date=None, medications=None, email_address=None):
        # Connect to the database
        self.connect_db()

        condition = ""
        if patient_id:
            condition += f"patientID = {patient_id}"
        else:
            if last_name:
                if condition:
                    condition += f" and lastName LIKE '%{last_name}%'"
                else:
                    condition += f"lastName LIKE '%{last_name}%'"

            if first_name:
                if condition:
                    condition += f" and firstName LIKE '%{first_name}%'"
                else:
                    condition += f"firstName LIKE '%{first_name}%'"

            if sex:
                if condition:
                    condition += f" and sex LIKE '%{sex}%'"
                else:
                    condition += f"sex LIKE '%{sex}%'"

            if age:
                if condition:
                    condition += f" and age = {age}"
                else:
                    condition += f"age = {age}"

            if birth_date:
                if condition:
                    condition += f" and birthDate LIKE '%{birth_date}%'"
                else:
                    condition += f"birthDate LIKE '%{birth_date}%'"

            if medications:
                if condition:
                    condition += f" and medications LIKE '%{medications}%'"
                else:
                    condition += f"medications LIKE '%{medications}%'"

            if email_address:
                if condition:
                    condition += f" and emailAddress LIKE '%{email_address}%'"
                else:
                    condition += f"emailAddress LIKE '%{email_address}%'"
        
        # Establish SQL query for searching information with conditions
        if condition:   
            sql = f"""
                SELECT *
                FROM patients_info
                WHERE {condition}
            """
        # Establish SQL query for searching all information
        else:
            sql = f"""
                SELECT *
                FROM patients_info
            """
        # Execute SQL query for searching information
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        
        except Exception as E: # Rollback the transaction in case of an error
            return E
        
        finally: # Close the database connection
            self.con.close()        
       
    # functions for visits_info from SQL database -------------------------------------------------------------------------- #
