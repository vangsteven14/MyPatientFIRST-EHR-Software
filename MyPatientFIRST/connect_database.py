#class ConnectDatabase:
    #pass

import mysql.connector

class ConnectDatabase:
    def __init__(self):
        self._host = "localhost"
        self._port = "3306"
        self._user = "root"
        self._password = "Mypatientfirst"
        self._database = "db_patients"
        self.con = None
        self.cursor = None

    def connect_db(self):
        # Establish a database connection
        self.con = mysql.connector.connect(
            host=self._host,
            port=self._port,
            database=self._database,
            user=self._user,
            password=self._password,
        )

        # Establish a cursor for executing SQL queries
        self.cursor = self.con.cursor(dictionary=True)
    
    # function to add data to patients_info from SQL database ---------------------------------------------------- #
    def add_info(self, patient_id, last_name, first_name, age, birth_date, medications, email_address):
        # Connect to the database
        self.connect_db()

        # Establish SQL query for adding information
        sql = f""" 
            INSERT INTO patients_info (patientID, lastName, firstName, age, birthDate, medications, emailAddress)
            VALUES ({patient_id}, '{last_name}', '{first_name}', {age}, '{birth_date}', '{medications}', '{email_address}')
        """
        
        # Execute SQL query for adding information
        try:
            self.cursor.execute(sql)
            self.con.commit()
        
        except Exception as E: # Rollback the transaction in case of an error
            self.con.rollback()
            return E

        finally: # Close the database connection
            self.con.close() 

    # function to update data to patients_info from SQL database ------------------------------------------------ #
    def update_info(self, patient_id, last_name, first_name, age, birth_date, medications, email_address):
        # Connect to the database
        self.connect_db()

        # Establish SQL query for updating information
        sql = f""" 
            UPDATE patients_info
            SET lastName = '{last_name}', firstName = '{first_name}', age = {age}, birthDate = '{birth_date}', medications = '{medications}', emailAddress = '{email_address}'
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

    # function to delete data to patients_info from SQL database --------------------------------------------- #
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

    # function to search data to patients_info from SQL database ------------------------------------------- #
    def search_info(self, patient_id=None, last_name=None, first_name=None, age=None, birth_date=None, medications=None, email_address=None):
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

    # function to get birthDates to patients_info from SQL database ------------------------------------- #
    def get_birthDates(self, birth_date): 
        # Connect to the database
        self.connect_db()

        # Retrieve all patients born on a specific date
        sql = f"""
                SELECT *
                FROM patients_info
                WHERE birthDate = %s
        """
        # Execute SQL query for searching information
        try:
            self.cursor.execute(sql, (birth_date))
            result = self.cursor.fetchall()
            return result
        
        except Exception as E: # Rollback the transaction in case of an error
            self.con.rollback()
            return E
        
        finally: # Close the database connection
            self.con.close()
       