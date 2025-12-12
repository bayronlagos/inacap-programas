
#conectar a base de datos
import oracledb
import os
from dotenv import load_dotenv
#implementar hasheo de contraseñas
import bcrypt
#importar el tipo de dato opcional
from typing import Optional 
#cargar las variables desde archivo .env

load_dotenv()
import requests
import datetime
#rescatar las credenciales de conexion a oracle
username = os.getenv("ORACLE_USER")
dsn = os.getenv("ORACLE_DSN")
password = os.getenv("ORACLE_PASSWORD")


class Database:
    def __init__(self, username,password,dsn):
        self.username = username
        self.password = password
        self.dsn = dsn
    def get_connection(self):
        return oracledb.connect(user=self.username, password=self.password, dsn=self.dsn)
    def create_all_table(self):
        pass
    def query(self, sentence: str, parameters: Optional [dict] = None):
        print(f"Ejecutando query:\n{sentence}\nParametros:n{parameters}")
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sentence, parameters)
                    for fila in resultado:
        except oracledb.databaseError as error:
            print(f"no se pudo crear la tabla; {error}")
    












class auth:
    @staticmethod
    def register(db: Database, username: str, password: str):
        salt= bcrypt.gensalt(12)
        hashed_password = bcrypt.hashpw(password,salt)
        usuario = {
            "id": 1,
            "username": username,
            "password": hashed_password
        }
        db.query(
            "INSERT INTO USERS(id,username,password) VALUES (:id,:username:password)",
            usuario
        )
    @staticmethod
    def login(db: Database, username: str, password: str):
        resultado = db.query(
            "SELECT * FROM USERS WHERE username = :username",
            {"username" : username}
        )

        for usuario in resultado:
            password_user = usuario[2]
            return bcrypt.checkpw(password, password_user)





class finance:
    def __init__(self,base_url: str = "https://mindicador.cl/api"):
        self.base_url = base_url
    def get_uf(self,fecha: str = None):
        if not fecha:
            year = datetime.datetime.now().year()
            month = datetime.datetime.now().month()
            day = datetime.datetime.now().day()
            fecha = f"{day}-{month}-{year}"
        url = f"{self.base_url}/uf/{fecha}"
        data = requests.get(url=url).json()
        print(data)
    def get_ipv(self,fecha: str = None):
        if not fecha:
            year = datetime.datetime.now().year()
            month = datetime.datetime.now().month()
            day = datetime.datetime.now().day()
            fecha = f"{day}-{month}-{year}"
        url = f"{self.base_url}/ipv/{fecha}"
        data = requests.get(url=url).json()
        print(data)
    def get_ipc(self,fecha: str = None):
        if not fecha:
            year = datetime.datetime.now().year()
            month = datetime.datetime.now().month()
            day = datetime.datetime.now().day()
            fecha = f"{day}-{month}-{year}"
        url = f"{self.base_url}/ipc/{fecha}"
        data = requests.get(url=url).json()
        print(data)
    def get_utm(self,fecha: str = None):
        if not fecha:
            year = datetime.datetime.now().year()
            month = datetime.datetime.now().month()
            day = datetime.datetime.now().day()
            fecha = f"{day}-{month}-{year}"
        url = f"{self.base_url}/utm/{fecha}"
        data = requests.get(url=url).json()
        print(data)
    def get_usd(self,fecha: str = None):
        if not fecha:
            year = datetime.datetime.now().year()
            month = datetime.datetime.now().month()
            day = datetime.datetime.now().day()
            fecha = f"{day}-{month}-{year}"
        url = f"{self.base_url}/usd/{fecha}"
        data = requests.get(url=url).json()
        print(data)
    def get_eur(self,fecha: str = None):
        if not fecha:
            year = datetime.datetime.now().year()
            month = datetime.datetime.now().month()
            day = datetime.datetime.now().day()
            fecha = f"{day}-{month}-{year}"
        url = f"{self.base_url}/eur/{fecha}"
        data = requests.get(url=url).json()
        print(data)
        

if __name__ == "__main__":
    indicadores = finance()
    db = Database(username=username,password=password,dsn=dsn)
    db.query("SELECT sysdate FROM dual")