import mysql.connector
from datetime import datetime

# Import the database connection class
from connect_database import ConnectDatabase

class ConnectDatabaseBillings(ConnectDatabase): 
    # functions for visits_info from SQL database -------------------------------------------------------------------------- #
    # functions for intializing connection
    def __init__(self, db):
        super().__init__()

    def fetch_all_billings(self):
        query = "SELECT * FROM billings_info"
        return self.db.execute_query(query, fetch=True)

    # function to add data to patients_info from SQL database
    def add_info(self, patient_id, visit_id, billing_id, amount, status, doctor, service, reason):
        # Ensures connection is Active
        self.connect_db()

        if self.con is None:
            return "Database connection failed."
        
        try:
            # Check if Patient ID Exists
            self.cursor.execute("SELECT COUNT(*) FROM billings_info WHERE billingID = %s", (billing_id,))
            result = self.cursor.fetchone()

            if result and result["COUNT(*)"] > 0:
                return "Error: BillingID already exists. Choose a different ID."
            
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
                INSERT INTO billings_info (patientID, visitID, billingID, amount, status, doctor, service, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (patient_id, visit_id, billing_id, amount, status, doctor, service, reason)

            self.cursor.execute(sql, values)
            self.con.commit()

            return "Success: Billing Statment added!"

        except mysql.connector.Error as e:
            self.con.rollback()
            print(f"Database error: {e}")  # Log the error
            return "Error: Unable to add new billing statment. Please try again."

        finally:
            # Closes the database connection
            self.con.close()
    
    # function to update data to patients_info from SQL database 
    def update_info(self, old_billing_id=None, new_billing_id=None, amount=None, status=None, doctor=None, service=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []

        # Add conditions only if values are provided
        if new_billing_id and new_billing_id != old_billing_id:
            conditions.append(f"billingID = '{new_billing_id}'")
        if amount:
            conditions.append(f"amount = '{amount}'")
        if status:
            conditions.append(f"status = '{status}'")
        if doctor:
            conditions.append(f"doctor = '{doctor}'")
        if service:
            conditions.append(f"service = '{service}'")
        if reason:
            conditions.append(f"reason = '{reason}'")
        
        # Ensure there are fields to update
        if not conditions:
            return "No fields to update."
        
        # Construct SQL query
        sql = f"""
            UPDATE billings_info
            SET {", ".join(conditions)}
            WHERE billingID = {old_billing_id}
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
    def delete_info(self, billing_id):
        # Connect to the database
        self.connect_db()    

        # Establish SQL query for deleting information
        sql = f"""
            DELETE FROM billings_info
            WHERE billingID = {billing_id}
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
    def search_info(self, patient_id=None, visit_id=None,  billing_id=None, amount=None, status=None, doctor=None, service=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
    
        # Add conditions only if values are provided
        if visit_id:
            conditions.append(f"visitID LIKE '%{visit_id}%'")
        if billing_id:
            conditions.append(f"billingID LIKE '%{billing_id}%'")
        if amount:
            conditions.append(f"amount LIKE '%{amount}%'")
        if status:
            conditions.append(f"status LIKE '%{status}%'")
        if doctor:
            conditions.append(f"doctor LIKE '%{doctor}%'")
        if service:
            conditions.append(f"service LIKE '%{service}%'")
        if reason:
            conditions.append(f"reason LIKE '%{reason}%'")

        # Construct SQL query
        sql = "SELECT * FROM billings_info"
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

    # function for View Patient Billing to patients_info from SQL database
    def billings_search_info(self, patient_id=None, visit_id=None, billing_id=None, amount=None, status=None, doctor=None, service=None, reason=None):
        # Connect to the database
        self.connect_db()

        conditions = []
    
        # Add conditions only if values are provided
        if patient_id:
            conditions.append(f"patientID LIKE '%{patient_id}%'")
        if visit_id:
            conditions.append(f"visitID LIKE '%{visit_id}%'")
        if billing_id:
            conditions.append(f"billingID LIKE '%{billing_id}%'")
        if amount:
            conditions.append(f"amount LIKE '%{amount}%'")
        if status:
            conditions.append(f"status LIKE '%{status}%'")
        if doctor:
            conditions.append(f"doctor LIKE '%{doctor}%'")
        if service:
            conditions.append(f"service LIKE '%{service}%'")
        if reason:
            conditions.append(f"reason LIKE '%{reason}%'")

        # Construct SQL query
        sql = "SELECT * FROM billings_info"
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

    # function for View Patient Billing to update data to patients_info from SQL database
    def billings_update_info(self, **kwargs):
        # Connect to the database
        self.connect_db()

        patient_id = kwargs.get("patientID")  # Ensure Patient ID exists
        if not patient_id:
            return "Error: Patient ID is required."
        
        conditions = []

        # Dynamically build the update query with only provided fields
        for key, value in kwargs.items():
            if key != "patientID" and value:  
                conditions.append(f"{key} = '{value}'")

        # Ensure there are fields to update
        if not conditions:
            return "No fields to update."
        
        # Construct SQL query
        sql = f"""
            UPDATE billings_info
            SET {', '.join(conditions)}
            WHERE patientID = {patient_id}
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
    
    # function for View Patient Billing to delete data to patients_info from SQL database 
    def billings_delete_info(self, patient_id):
        self.connect_db()

        try:
            sql = "DELETE FROM billings_info WHERE patientID = %s"
            self.cursor.execute(sql, (patient_id,))
            self.con.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            self.con.rollback()
            print(f"Database Error: {e}")
            return False

        finally:
            self.con.close()