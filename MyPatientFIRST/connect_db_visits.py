import mysql.connector
from datetime import datetime

# Import the database connection class
from connect_database import ConnectDatabase

class ConnectDatabaseVisits(ConnectDatabase): 
    # functions for visits_info from SQL database -------------------------------------------------------------------------- #
    # functions for intializing connection
    def __init__(self, db):
        super().__init__()
        self.db = db

    def fetch_all_visits(self):
        query = "SELECT * FROM visits_info"
        return self.db.execute_query(query, fetch=True)

    # function to add data to patients_info from SQL database
    def add_info(self, visit_id, patient_id, status, last_name, first_name, visit_date, visit_time, type, reason):
        # Ensures connection is Active
        self.connect_db()

        if self.con is None:
            return "Database connection failed."
        
        try:
            # Check if Patient ID Exists
            self.cursor.execute("SELECT COUNT(*) FROM visits_info WHERE visitID = %s", (visit_id,))
            result = self.cursor.fetchone()

            if result and result["COUNT(*)"] > 0:
                return "Error: VisitID already exists. Choose a different ID."

            try:
                visit_date_obj = datetime.strptime(visit_date, "%Y-%m-%d")  # Convert to datetime object
                visit_date = visit_date_obj.strftime("%Y-%m-%d")  # Format to MySQL's YYYY-MM-DD
            except ValueError:
                return "Error: Invalid date format. Use MM-DD-YYYY. Please try again."
            
            # Use Parameterized Query to Prevent SQL Injection
            sql = """ 
                INSERT INTO visits_info (visitID, patientID, status, lastName, firstName, visitDate, visitTime type, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (visit_id, patient_id, status, last_name, first_name, visit_date, visit_time, type, reason)

            self.cursor.execute(sql, values)
            self.con.commit()

            return "Success: Visit added!"

        except mysql.connector.Error as e:
            self.con.rollback()
            print(f"Database error: {e}")  # Log the error
            return "Error: Unable to add new visit. Please try again."

        finally:
            self.con.close()

    # function to update data to visits_info from SQL database  
    def update_info(self, old_visit_id=None, new_visit_id=None, status=None, last_name=None, first_name=None, visit_date=None, visit_time=None, type=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if new_visit_id and new_visit_id != old_visit_id:
            conditions.append(f"patientID = '{new_visit_id}'")
        if status:
            conditions.append(f"status = '{status}'")
        if last_name:
            conditions.append(f"lastName = '{last_name}'")
        if first_name:
            conditions.append(f"firstName = '{first_name}'")
        if visit_time:
            conditions.append(f"visitTime = '{visit_time}'")
        if type:
            conditions.append(f"type = '{type}'")
        if reason:
            conditions.append(f"reason = '{reason}'")
        
        # Update visitDate only if a new value is provided and it's not the default or current date
        if visit_date and visit_date not in ["2000-01-01", current_date]:
            conditions.append(f"visitDate = '{visit_date}'")
    
        # Ensure there are fields to update
        if not conditions:
            return "No fields to update."
        
        # Construct SQL query
        sql = f"""
            UPDATE visits_info
            SET {", ".join(conditions)}
            WHERE visitID = {old_visit_id}
        """

        print(f"Executing SQL: {sql}")  # Debugging line

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:  # Rollback the transaction in case of an error
            self.con.rollback()
            return e
        finally:  
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

        finally: 
            self.con.close()

    # function to search data to patients_info from SQL database
    def search_info(self, patient_id=None, visit_id=None, status=None, last_name=None, first_name=None, visit_date=None, visit_year=None, visit_month=None, visit_day=None, visit_time=None, type=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if visit_id:
            conditions.append(f"visitID LIKE '%{visit_id}%'")
        if status:
            conditions.append(f"status LIKE '%{status}%'")
        if last_name:
            conditions.append(f"lastName LIKE '%{last_name}%'")
        if first_name:
            conditions.append(f"firstName LIKE '%{first_name}%'")

        # Search by filtering specific birth month, birth day, or birth year
        if visit_year:
            conditions.append(f"YEAR(visitDate) = {visit_year}")
        if visit_month:
            conditions.append(f"MONTH(visitDate) = {visit_month}")
        if visit_day:
            conditions.append(f"DAY(visitDate) = {visit_day}")

        # Ignore visit_date as it's in default "2000-01-01"
        # And current date when selecting clear button
        if visit_date and visit_date not in ["2000-01-01", current_date]:
            if not (visit_year or visit_month or visit_day):
                conditions.append(f"visitDate = '{visit_date}'")

        if visit_time:
            conditions.append(f"visitTime = '{visit_time}'")
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
            self.con.close()  

    # function for View Patient Visit to patients_info from SQL database
    def visits_search_info(self, patient_id=None, visit_id=None, status=None, last_name=None, first_name=None, visit_date=None, visit_year=None, visit_month=None, visit_day=None, visit_time=None, type=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
        current_date = datetime.today().strftime('%Y-%m-%d')

        # Add conditions only if values are provided
        if patient_id:
            conditions.append(f"patientID LIKE '%{patient_id}%'")
        if visit_id:
            conditions.append(f"visitID LIKE '%{visit_id}%'")
        if status:
            conditions.append(f"status LIKE '%{status}%'")
        if last_name:
            conditions.append(f"lastName LIKE '%{last_name}%'")
        if first_name:
            conditions.append(f"firstName LIKE '%{first_name}%'")

        # Search by filtering specific visit month, visit day, or visit year
        if visit_year:
            conditions.append(f"YEAR(visitDate) = {visit_year}")
        if visit_month:
            conditions.append(f"MONTH(visitDate) = {visit_month}")
        if visit_day:
            conditions.append(f"DAY(visitDate) = {visit_day}")

         # Ignore visit_date as it's in default "2000-01-01"
        # And current date when selecting clear button
        if visit_date and visit_date not in ["2000-01-01", current_date]:
            if not (visit_year or visit_month or visit_day):
                conditions.append(f"visitDate = '{visit_date}'")

        if visit_time:
            conditions.append(f"visitTime = '{visit_time}'")
        if type:
            conditions.append(f"type LIKE '%{type}%'")
        if reason:
            conditions.append(f"reason LIKE '%{reason}%'")

        # Construct SQL query
        sql = "SELECT * FROM visits_info"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        print(f"Executing SQL: {sql}")  # Debugging line

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result if result else []  # Return empty list if no results
        except Exception as e:
            print("Database search error:", e)
            return []  # Return empty list instead of crashing

    # function for View Patient Profile to update data to patients_info from SQL database
    def visits_update_info(self, **kwargs):
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
            UPDATE visits_info
            SET {", ".join(conditions)}
            WHERE patientID = '{patient_id}'
        """

        print(f"Executing SQL: {sql}")  

        # Execute SQL query
        try:
            self.cursor.execute(sql)
            self.con.commit()
            return self.cursor.rowcount > 0  
        except Exception as e:
            self.con.rollback()
            return f"Database Error: {e}"
        finally:
            self.con.close()

    # function for View Patient Profile to delete data to patients_info from SQL database 
    def visits_delete_info(self, patient_id):
        self.connect_db()

        try:
            sql = "DELETE FROM visits_info WHERE patientID = %s"
            self.cursor.execute(sql, (patient_id,))
            self.con.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            self.con.rollback()
            print(f"Database Error: {e}")
            return False

        finally:
            self.con.close()