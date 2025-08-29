# import mysql.connector

# # Database configuration
# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '',
#     'database': 'timetable'
# }

# # Connect to the database
# def get_db_connection():
#     return mysql.connector.connect(
#         host=db_config['host'],
#         user=db_config['user'],
#         password=db_config['password'],
#         database=db_config['database']
#     )





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
