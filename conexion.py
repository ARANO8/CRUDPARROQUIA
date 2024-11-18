import pyodbc

def get_connection():
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=bdParroquia;"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def get_db_connection():
    return pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost\\SQLEXPRESS;DATABASE=BDVENTAS;UID=CRUDBD;PWD=123456")