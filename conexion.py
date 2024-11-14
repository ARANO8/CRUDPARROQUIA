import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"  # Cambia el servidor a localhost\SQLEXPRESS
    "DATABASE=BDVENTAS;"
    "UID=CRUDBD;"
    "PWD=123;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Conexión exitosa")
except Exception as e:
    print("Error al conectar:", e)



