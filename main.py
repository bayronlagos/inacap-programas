import bcrypt
import requests
import oracledb
import os
from dotenv import load_dotenv
from typing import Optional
import datetime

load_dotenv()
print(os.getenv("ORACLE_USER"))
print(os.getenv("ORACLE_PASSWORD"))
print(os.getenv("ORACLE_DSN"))
class Database:
    def __init__(self, username, dsn, password):
        self.username = username
        self.dsn = dsn
        self.password = password

    def get_connection(self):
        return oracledb.connect(
            user=self.username,
            password=self.password,
            dsn=self.dsn
        )

    def query(self, sql: str, parameters: Optional[dict] = None):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, parameters or {})

                if sql.strip().upper().startswith("SELECT"):
                    rows = cur.fetchall()
                    fixed_rows = []

                    for row in rows:
                        fixed_row = []
                        for col in row:
                            if isinstance(col, oracledb.LOB):
                                fixed_row.append(col.read())
                            else:
                                fixed_row.append(col)
                        fixed_rows.append(tuple(fixed_row))

                    return fixed_rows
            conn.commit()

    def create_tables(self):
        sql_users = """
        CREATE TABLE USERS (
            id NUMBER PRIMARY KEY,
            username VARCHAR2(32) UNIQUE,
            password VARCHAR2(255)
        )
        """

        sql_consulta = """
        CREATE TABLE CONSULTA_INDICADOR (
            id_consulta NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre_indicador VARCHAR2(20),
            valor NUMBER(15,4),
            fecha_indicador DATE,
            fecha_consulta DATE,
            usuario VARCHAR2(32),
            fuente VARCHAR2(100)
        )
        """

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(sql_users)
                except oracledb.DatabaseError:
                    pass

                try:
                    cur.execute(sql_consulta)
                except oracledb.DatabaseError:
                    pass
            conn.commit()

    def registrar_consulta(self, nombre_indicador, valor, fecha_indicador, usuario, fuente):
        sql = """
        INSERT INTO CONSULTA_INDICADOR
        (nombre_indicador, valor, fecha_indicador, fecha_consulta, usuario, fuente)
        VALUES
        (:nombre_indicador, :valor, :fecha_indicador, :fecha_consulta, :usuario, :fuente)
        """

        parametros = {
            "nombre_indicador": nombre_indicador,
            "valor": valor,
            "fecha_indicador": fecha_indicador,
            "fecha_consulta": datetime.datetime.now(),
            "usuario": usuario,
            "fuente": fuente
        }

        self.query(sql, parametros)

class Auth:
    @staticmethod
    def login(db: Database, username: str, password: str):
        password_bytes = password.encode("UTF-8")

        resultado = db.query(
            "SELECT password FROM USERS WHERE username = :username",
            {"username": username}
        )

        if not resultado:
            print("Usuario no encontrado")
            return False

        hashed_password = resultado[0][0].encode("UTF-8")

        if bcrypt.checkpw(password_bytes, hashed_password):
            print("Logeado correctamente")
            return True
        else:
            print("Contraseña incorrecta")
            return False

    @staticmethod
    def register(db: Database, id: int, username: str, password: str):
        password_bytes = password.encode("UTF-8")
        salt = bcrypt.gensalt(12)
        hash_password = bcrypt.hashpw(password_bytes, salt).decode("UTF-8")

        usuario = {
            "id": id,
            "username": username,
            "password": hash_password
        }

        db.query(
            "INSERT INTO USERS(id, username, password) VALUES (:id, :username, :password)",
            usuario
        )
        print("Usuario registrado con éxito")

class Finance:
    def _init_(self, base_url: str = "https://mindicador.cl/api"):
        self.base_url = base_url

    def get_indicator(self, indicator: str):
        respuesta = requests.get(f"{self.base_url}/{indicator}").json()
        serie = respuesta["serie"][0]
        valor = serie["valor"]
        fecha = datetime.datetime.strptime(serie["fecha"][:10], "%Y-%m-%d")
        return valor, fecha

    def consultar_y_guardar(self, indicator: str, db, usuario: str):
        valor, fecha_indicador = self.get_indicator(indicator)

        print(f"{indicator.upper()} = {valor}")

        guardar = input("¿Desea guardar la consulta? (s/n): ").lower()

        if guardar == "s":
            db.registrar_consulta(
                nombre_indicador=indicator.upper(),
                valor=valor,
                fecha_indicador=fecha_indicador,
                usuario=usuario,
                fuente="https://mindicador.cl"
            )
            print("Consulta registrada en Oracle")

# ===== MENÚ DEFINITIVO (DIFERENTE Y GUIADO) =====
def menu_indicadores(finance, db, usuario):
    opciones = {
        "1": ("UF (Unidad de Fomento)", "uf"),
        "2": ("IVP (Índice de Valor Promedio)", "ivp"),
        "3": ("IPC (Índice de Precios al Consumidor)", "ipc"),
        "4": ("UTM (Unidad Tributaria Mensual)", "utm"),
        "5": ("Dólar Observado", "dolar"),
        "6": ("Euro", "euro"),
        "0": ("Salir del sistema", None)
    }

    while True:
        os.system("cls")
        print("=== CONSULTA DE INDICADORES ECONÓMICOS ===\n")

        for key, value in opciones.items():
            print(f"{key}. {value[0]}")

        print("\n-----------------------------------------")
        opcion = input("Seleccione el número del indicador: ").strip()

        if opcion == "0":
            print("\nSesión finalizada.")
            break

        if opcion in opciones:
            indicador = opciones[opcion][1]
            finance.consultar_y_guardar(indicador, db, usuario)
        else:
            print("\nOpción no reconocida.")

        input("\nPresione ENTER para continuar...")

if  __name__ == "__main__":
    db = Database(
        username=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

    db.create_tables()
    Auth.register(db, 1, "C##BAYRON_CID", "INACAP#2025")

    if Auth.login(db, "C##BAYRON_CID", "INACAP#2025"):
        finance = Finance()
        menu_indicadores(finance, db, "C##BAYRON_CID")