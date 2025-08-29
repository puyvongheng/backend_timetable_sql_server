import pyodbc

# Database configuration
db_config = {
    'server': r'DESKTOP-GDQPL4A\PUYVONGHENG',  # Your SQL Server instance
    'database': 'timetable',                   # Your database name
    'username': 'PUYVONGHENG',                 # Your SQL login username
    'password': 'PUYVONGHENG'                  # Your SQL login password
}

def get_db_connection():
    try:
        # Connection string
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
            "TrustServerCertificate=Yes;"   # Avoid SSL issues
        )
        
        # Connect
        conn = pyodbc.connect(conn_str)
        print("✅ Connected to SQL Server successfully!")
        return conn

    except pyodbc.Error as e:
        print("❌ Database connection failed!")
        print("Error:", e)
        return None


# Example usage
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases;")
        for row in cursor.fetchall():
            print(row[0])
        conn.close()