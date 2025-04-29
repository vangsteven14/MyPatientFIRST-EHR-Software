import mysql.connector

# functions for intializing connection from SQL database -------------------------------------------------------------------------- #
class ConnectDatabase:
    def __init__(self):
        self._host = "localhost"
        self._port = 3306
        self._user = "root"
        self._password = "Mypatientfirst"
        self._database = "db_patients"
        self.con = None
        self.cursor = None

    # Establish a database connection    
    def connect_db(self):
        try:
            # Establish a database connection
            self.con = mysql.connector.connect(
                host=self._host,
                port=self._port,
                database=self._database,
                user=self._user,
                password=self._password
            )

            # Create a cursor for executing SQL queries
            self.cursor = self.con.cursor(dictionary=True)
            print("Database connected successful!")

        except mysql.connector.Error as e:
            self.con.rollback()
            print(f"Database error: {e}")  # Login the error
            return "Error: Unable to add patient. Please try again."
    
    # Ensures connection is active
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
     
    # Fetch all patients from SQL database  
    def fetch_all_patients(self):
        query = "SELECT * FROM patients_info"
        return self.execute_query(query, fetch=True)