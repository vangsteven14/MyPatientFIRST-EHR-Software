import mysql.connector
from datetime import datetime

# Import the database connection class
from connect_database import ConnectDatabase

class ConnectDatabaseVisits(ConnectDatabase): 
    # functions for visits_info from SQL database -------------------------------------------------------------------------- #
    # functions for intializing connection
    def __init__(self, db):
        super().__init__()

    def fetch_all_visits(self):
        query = "SELECT * FROM visits_info"
        return self.db.execute_query(query, fetch=True)

    # function to add data to patients_info from SQL database
    def add_info(self, visit_id, patient_id, status, last_name, first_name, birth_date, type, reason):
        # Ensures connection is Active
        self.connect_db()

        if self.con is None:
            return "Database connection failed."
        
        try:
            ## Check if Patient ID Exists
            self.cursor.execute("SELECT COUNT(*) FROM visits_info WHERE visitID = %s", (visit_id,))
            result = self.cursor.fetchone()

            if result and result["COUNT(*)"] > 0:
                return "Error: VisitID already exists. Choose a different ID."

            # Convert birth_date from MM-DD-YYYY to YYYY-MM-DD
            try:
                birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")  # Convert to datetime object
                birth_date = birth_date_obj.strftime("%Y-%m-%d")  # Format to MySQL's YYYY-MM-DD
            except ValueError:
                return "Error: Invalid date format. Use MM-DD-YYYY. Please try again."

            '''
            # Ensure non-null values
            medications = medications if medications else ""
            email_address = email_address if email_address else ""
            '''
            
            # Use Parameterized Query to Prevent SQL Injection
            sql = """ 
                INSERT INTO visits_info (visitID, patientID, status, lastName, firstName, birthDate, type, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (visit_id, patient_id, status, last_name, first_name, birth_date, type, reason)

            self.cursor.execute(sql, values)
            self.con.commit()

            return "Success: Visit added!"

        except mysql.connector.Error as e:
            self.con.rollback()
            print(f"Database error: {e}")  # Log the error
            return "Error: Unable to add new visit. Please try again."

        finally:
            # Closes the database connection
            self.con.close()

    # function to update data to visits_info from SQL database 
    def update_info(self, visit_id=None, status=None, last_name=None, first_name=None, birth_date=None, type=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if status:
            conditions.append(f"status = '{status}'")
        if last_name:
            conditions.append(f"lastName = '{last_name}'")
        if first_name:
            conditions.append(f"firstName = '{first_name}'")
        if birth_date:
            conditions.append(f"birthDate = '{birth_date}'")
        if type:
            conditions.append(f"type = '{type}'")
        if reason:
            conditions.append(f"reason = '{reason}'")
    
        # Update birthDate only if a new value is provided and it's not the default or current date
        if birth_date and birth_date not in ["2000-01-01", current_date]:
            conditions.append(f"birthDate = '{birth_date}'")
        
        # Ensure there are fields to update
        if not conditions:
            return "No fields to update."
        
        # Construct SQL query
        sql = f"""
            UPDATE visits_info
            SET {", ".join(conditions)}
            WHERE visitID = {visit_id}
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

    # function to delete data to vivits_info from SQL database 
    def delete_info(self, visit_id):
        # Connect to the database
        self.connect_db()    

        # Establish SQL query for deleting information
        sql = f"""
            DELETE FROM visits_info
            WHERE visitID = {visit_id}
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
    def search_info(self, visit_id=None, patient_id=None, status=None, last_name=None, first_name=None, birth_date=None, birth_year=None, birth_month=None, birth_day=None, type=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if visit_id:
            conditions.append(f"visitID LIKE '%{visit_id}%'")
        if patient_id:
            conditions.append(f"patientID LIKE '%{patient_id}%'")
        if status:
            conditions.append(f"status LIKE '%{status}%'")
        if last_name:
            conditions.append(f"lastName LIKE '%{last_name}%'")
        if first_name:
            conditions.append(f"firstName LIKE '%{first_name}%'")

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

        if type:
            conditions.append(f"type LIKE '%{type}%'")
        if reason:
            conditions.append(f"reason LIKE '%{reason}%'")

        # Construct SQL query
        sql = "SELECT * FROM visits_info"
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

    '''
    def get_visits_patientID_info(self):
        # Connect to the database
        self.connect_db()

        # Construct SQL query for deleting information
        sql = f"""  
            SELECT patientID FROM visits_info GROUP BY patientID;
        """

        try:
            # Execute the SQL query for searching information
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result

        except Exception as E:
            # Rollback the transaction in case of an error
            self.con.rollback()
            return E

        finally:
            # Close the database connection
            self.con.close()'
    '''