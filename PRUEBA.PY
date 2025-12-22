import oracledb

conn = oracledb.connect(
    user="C##BAYRON_CID",
    password="Inacap#2025",
    dsn="localhost:1521/XEPDB1"
)

print("Conexión exitosa")
conn.close()