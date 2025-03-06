import mysql.connector
from datetime import datetime

# Import the database connection class
from connect_database import ConnectDatabase

class ConnectDatabasePatients(ConnectDatabase): 
    # functions for patients_info from SQL database -------------------------------------------------------------------------- #
    # functions for intializing connection
    def __init__(self, db):
        super().__init__()

    def fetch_all_patients(self):
        query = "SELECT * FROM patients_info"
        return self.db.execute_query(query, fetch=True)

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

        finally:
            # Closes the database connection
            self.con.close()

    # function to update data to patients_info from SQL database 
    def update_info(self, patient_id=None, last_name=None, first_name=None, sex=None, age=None, birth_date=None, medications=None, email_address=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if last_name:
            conditions.append(f"lastName = '{last_name}'")
        if first_name:
            conditions.append(f"firstName = '{first_name}'")
        if sex:
            conditions.append(f"sex = '{sex}'")
        if age:
            conditions.append(f"age = {age}")
        if medications:
            conditions.append(f"medications = '{medications}'")
        if email_address:
            conditions.append(f"emailAddress = '{email_address}'")
    
        # Update birthDate only if a new value is provided and it's not the default or current date
        if birth_date and birth_date not in ["2000-01-01", current_date]:
            conditions.append(f"birthDate = '{birth_date}'")
        
        # Ensure there are fields to update
        if not conditions:
            return "No fields to update."
        
        # Construct SQL query
        sql = f"""
            UPDATE patients_info
            SET {", ".join(conditions)}
            WHERE patientID = {patient_id}
        """

        print(f"Executing SQL: {sql}")  # Debugging line

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:  # Rollback the transaction in case of an error
            self.con.rollback()
            return e
        finally:  # Close the database connection
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
    def search_info(self, patient_id=None, last_name=None, first_name=None, sex=None, age=None, birth_date=None, birth_year=None, birth_month=None, birth_day=None, medications=None, email_address=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if patient_id:
            conditions.append(f"patientID LIKE '%{patient_id}%'")
        if last_name:
            conditions.append(f"lastName LIKE '%{last_name}%'")
        if first_name:
            conditions.append(f"firstName LIKE '%{first_name}%'")
        if sex:
            conditions.append(f"sex LIKE '{sex}'")
        if age:
            conditions.append(f"age LIKE '%{age}%'")

        # Search by filtering specific birth month, birth day, or birth year
        if birth_year:
            conditions.append(f"YEAR(birthDate) = {birth_year}")
        if birth_month:
            conditions.append(f"MONTH(birthDate) = {birth_month}")
        if birth_day:
            conditions.append(f"DAY(birthDate) = {birth_day}")

        # Ignore birth_date as it's in default "2000-01-01"
        # And current date when selecting clear button
        if birth_date and birth_date not in ["2000-01-01", current_date]:
            if not (birth_year or birth_month or birth_day):
                conditions.append(f"birthDate = '{birth_date}'")

        if medications:
            conditions.append(f"medications LIKE '%{medications}%'")
        if email_address:
            conditions.append(f"emailAddress LIKE '%{email_address}%'")

        # Construct SQL query
        sql = "SELECT * FROM patients_info"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)  # Add WHERE only if conditions exist

        print(f"Executing SQL: {sql}")  # Debugging line

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result if result else []  # Return empty list if no results
        except Exception as e:
            print("Database search error:", e)
            return []  # Return empty list instead of crashing
        finally:
            self.con.close()  # Close the database connection

    # function for View Patient Profile to patients_info from SQL database
    def pat_search_info(self, patient_id=None, last_name=None, first_name=None, sex=None, age=None, birth_date=None, birth_year=None, birth_month=None, birth_day=None, medications=None, email_address=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if patient_id:
            conditions.append(f"patientID LIKE '%{patient_id}%'")
        if last_name:
            conditions.append(f"lastName LIKE '%{last_name}%'")
        if first_name:
            conditions.append(f"firstName LIKE '%{first_name}%'")
        if sex:
            conditions.append(f"sex LIKE '{sex}'")
        if age:
            conditions.append(f"age LIKE '%{age}%'")

        # Search by filtering specific birth month, birth day, or birth year
        if birth_year:
            conditions.append(f"YEAR(birthDate) = {birth_year}")
        if birth_month:
            conditions.append(f"MONTH(birthDate) = {birth_month}")
        if birth_day:
            conditions.append(f"DAY(birthDate) = {birth_day}")

        # Ignore birth_date as it's in default "2000-01-01"
        # And current date when selecting clear button
        if birth_date and birth_date not in ["2000-01-01", current_date]:
            if not (birth_year or birth_month or birth_day):
                conditions.append(f"birthDate = '{birth_date}'")

        if medications:
            conditions.append(f"medications LIKE '%{medications}%'")
        if email_address:
            conditions.append(f"emailAddress LIKE '%{email_address}%'")

        # Construct SQL query
        sql = "SELECT * FROM patients_info"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)  # Add WHERE only if conditions exist

        print(f"Executing SQL: {sql}")  # Debugging line

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result if result else []  # Return empty list if no results
        except Exception as e:
            print("Database search error:", e)
            return []  # Return empty list instead of crashing
        finally:
            self.con.close()  # Close the database connection

    # function for View Patient Profile to update data to patients_info from SQL database
    def pat_update_info(self, **kwargs):
        # Connect to the database
        self.connect_db()

        patient_id = kwargs.get("patientID")  # Ensure Patient ID exists
        if not patient_id:
            return "Error: Patient ID is required."

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Dynamically build the update query with only provided fields
        for key, value in kwargs.items():
            if key != "patientID" and value:  # Skip Patient ID in the SET clause
                conditions.append(f"{key} = '{value}'")

        # Ensure there are fields to update
        if not conditions:
            return "No fields to update."

        # Construct SQL query
        sql = f"""
            UPDATE patients_info
            SET {", ".join(conditions)}
            WHERE patientID = '{patient_id}'
        """

        print(f"Executing SQL: {sql}")  # Debugging line

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            self.con.commit()
            return self.cursor.rowcount > 0  # Return True if update was successful
        except Exception as e:
            self.con.rollback()
            return f"Database Error: {e}"
        finally:
            self.con.close()

    # function for View Patient Profile to delete data to patients_info from SQL database 
    def pat_delete_info(self, patient_id):
        # Connect to the database
        self.connect_db()    

        try:
            sql = "DELETE FROM patients_info WHERE patientID = %s"
            self.cursor.execute(sql, (patient_id,))
            self.con.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            self.con.rollback()
            print(f"Database Error: {e}")
            return False  

        finally:
            self.con.close()