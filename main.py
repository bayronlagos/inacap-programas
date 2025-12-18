import bcrypt
import requests
import oracledb
import os
from dotenv import load_dotenv
from typing import Optional
import datetime

load_dotenv()

class Database:
    def __init__(self, username, dsn, password):
        self.username = username
        self.dsn = dsn
        self.password = password
    def get_connection(self):
        return oracledb.connect(user=self.username, password=self.password, dsn=self.dsn)
    def create_all_tables(self):
        tables = [
            (
                "CREATE TABLE USERS("
                "id INTEGER PRIMARY KEY,"
                "username VARCHAR(32) UNIQUE,"
                "password VARCHAR(128)"
                ")"
            )
        ]

        for table in tables:
            self.query(table)
            
    def insert_finance_query(
        self,
        indicator_name: str,
        indicator_date: datetime.date,
        query_date: datetime.datetime,
        username: str,
        provider_site: str,
        value: float | None,
    ):
        sql = (
            "INSERT INTO FINANCE_QUERIES("
            "  indicator_name, indicator_date, query_date, username, provider_site, value"
            ") VALUES ("
            "  :indicator_name, :indicator_date, :query_date, :username, :provider_site, :value"
            ")"
        )
        params = {
            "indicator_name": indicator_name,
            "indicator_date": indicator_date,
            "query_date": query_date,
            "username": username,
            "provider_site": provider_site,
            "value": value,
        }
        self.query(sql, params)


    def query(self, sql: str, parameters: Optional[dict] = None):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    ejecucion = cur.execute(sql, parameters)
                    if sql.startswith("SELECT"):
                        resultado = []
                        for fila in ejecucion:
                            resultado.append(fila)
                        return resultado
                conn.commit()
        except oracledb.DatabaseError as error:
            print(error)

class Auth:
    @staticmethod
    def login(db: Database, username: str, password: str):
        password = password.encode("UTF-8")

        resultado = db.query(
            sql= "SELECT * FROM USERS WHERE username = :username",
            parameters={"username":username}
        )

        if len(resultado) == 0:
            return print("No hay coincidencias")
        
        hashed_password = bytes.fromhex(resultado[0][2])

        if bcrypt.checkpw(password, hashed_password):
            return print("Logeado correctamente")
        else:
            return print("Contraseña incorrecta")

    @staticmethod
    def register(db: Database, id: int, username: str, password: str):
        print("registrando usuario")
        password = password.encode("UTF-8")
        salt = bcrypt.gensalt(12)
        hash_password = bcrypt.hashpw(password,salt)

        usuario = {
            "id": id,
            "username": username,
            "password": hash_password
        }

        db.query(
            sql= "INSERT INTO USERS(id,username,password) VALUES (:id, :username, :password)",
            parameters=usuario
        )
        print("usuario registrado con exito")


class Finance:
    def __init__(self, base_url: str = "https://mindicador.cl/api"):
        self.base_url = base_url

    def get_indicator(
        self,
        indicator: str,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        """
        Obtiene el valor del indicador para 'fecha' (formato 'dd-mm-yyyy').
        Si log=True y se pasan db y username, registra la consulta en FINANCE_QUERIES.
        """
        try:
            # Fecha por defecto: hoy (formato correcto con ceros a la izquierda)
            if not fecha:
                fecha = datetime.date.today().strftime("%d-%m-%Y")

            # Consumir API
            url = f"{self.base_url}/{indicator}/{fecha}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            valor = float(data["serie"][0]["valor"])

            # Preparar fechas para el registro
            indicator_date = datetime.datetime.strptime(fecha, "%d-%m-%Y").date()
            query_date = datetime.datetime.now()

            # Registrar en BD si corresponde
            if log and db is not None and username is not None:
                db.insert_finance_query(
                    indicator_name=indicator,
                    indicator_date=indicator_date,
                    query_date=query_date,
                    username=username,
                    provider_site=self.base_url,
                    value=valor,
                )

            return valor

        except Exception as e:
            print(f"Hubo un error con la solicitud: {e}")
            return None

    def get_usd(
        self,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        valor = self.get_indicator("dolar", fecha, db=db, username=username, log=log)
        if valor is not None:
            print(f"El valor del dólar en CLP es: {valor}")
        return valor

    def get_eur(
        self,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        return self.get_indicator("euro", fecha, db=db, username=username, log=log)

    def get_uf(
        self,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        return self.get_indicator("uf", fecha, db=db, username=username, log=log)

    def get_ivp(
        self,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        return self.get_indicator("ivp", fecha, db=db, username=username, log=log)

    def get_ipc(
        self,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        return self.get_indicator("ipc", fecha, db=db, username=username, log=log)

    def get_utm(
        self,
        fecha: Optional[str] = None,
        db: Optional["Database"] = None,
        username: Optional[str] = None,
        log: bool = False,
    ) -> Optional[float]:
        return self.get_indicator("utm", fecha, db=db, username=username, log=log)





def print_menu_principal():
    print("========================================")
    print("|           Menu: Finanzas             |")
    print("|--------------------------------------|")
    print("| 1. Registrarme                       |")
    print("| 2. Iniciar sesión                    |")
    print("| 3. Consultar indicador               |")
    print("| 4. Consultar y registrar             |")
    print("| 0. Salir                             |")
    print("========================================")

def print_menu_indicadores():
    print("========================================")
    print("|         Menu: Indicadores            |")
    print("|--------------------------------------|")
    print("| 1. Dólar (CLP)                       |")
    print("| 2. Euro (CLP)                        |")
    print("| 3. UF                                |")
    print("| 4. IVP                               |")
    print("| 5. IPC                               |")
    print("| 6. UTM                               |")
    print("| 0. Volver                            |")
    print("========================================")

# ---- Helpers muy simples ----
def leer_opcion(msg: str, opciones_validas: set[str]) -> str:
    op = input(msg).strip()
    while op not in opciones_validas:
        op = input(f"Opción inválida. {msg}").strip()
    return op

def leer_entero(msg: str) -> int:
    while True:
        s = input(msg).strip()
        try:
            v = int(s)
            if v <= 0:
                print("Debe ser un entero positivo.")
                continue
            return v
        except ValueError:
            print("Ingrese un número entero válido.")

def leer_texto(msg: str, min_len: int = 1, max_len: int = 128) -> str:
    while True:
        s = input(msg).strip()
        if len(s) < min_len:
            print(f"Debe tener al menos {min_len} caracteres.")
            continue
        if len(s) > max_len:
            print(f"No puede superar {max_len} caracteres.")
            continue
        return s

def leer_fecha(msg: str) -> str:
    s = input(msg + " (dd-mm-yyyy, vacío para hoy): ").strip()
    if not s:
        return datetime.date.today().strftime("%d-%m-%Y")
    try:
        datetime.datetime.strptime(s, "%d-%m-%Y")
        return s
    except ValueError:
        print("Fecha inválida. Se usará hoy.")
        return datetime.date.today().strftime("%d-%m-%Y")

# ---- Helper de login (simple y funcional) ----
def try_login(db: "Database", username: str, password: str) -> Optional[str]:
    """
    Valida credenciales consultando USERS.
    Retorna el username si son válidas; si no, None.
    """
    filas = db.query(
        "SELECT username, password FROM USERS WHERE username = :u",
        {"u": username}
    )
    if not filas:
        print("Credenciales inválidas.")
        return None

    stored = filas[0][1]
    # Intentar interpretar el hash como texto (recomendado)
    try:
        stored_hash_bytes = stored.encode("utf-8")
    except AttributeError:
        # Si por error está guardado como hex/bytes
        try:
            stored_hash_bytes = bytes.fromhex(stored)
        except Exception:
            print("Formato de hash inválido en BD.")
            return None

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash_bytes):
        print("Logeado correctamente")
        return username
    else:
        print("Credenciales inválidas.")
        return None

# ---- Bucle principal del menú ----
def run_cli():
    # Usa las variables de entorno ya cargadas por load_dotenv() al inicio del archivo
    db = Database(
        username=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN"),
    )
    finance = Finance()

    logged_username: Optional[str] = None

    while True:
        print_menu_principal()
        op = leer_opcion("Elige una opción: ", {"0", "1", "2", "3", "4"})

        if op == "0":
            print("¡Hasta luego!")
            break

        elif op == "1":
            # Registrarme
            user_id = leer_entero("Id (entero positivo): ")
            username = leer_texto("Usuario (3-32, letras/números/._-): ", 3, 32)
            password = leer_texto("Contraseña (≥8 caracteres): ", 8, 128)
            try:
                Auth.register(db, user_id, username, password)
            except Exception:
                print("No se pudo registrar el usuario.")

        elif op == "2":
            # Iniciar sesión
            username = leer_texto("Usuario: ", 3, 32)
            password = leer_texto("Contraseña: ", 1, 128)
            logged = try_login(db, username, password)
            logged_username = logged if logged else None

        elif op in {"3", "4"}:
            # Submenú: consultar (3) o consultar y registrar (4)
            while True:
                print_menu_indicadores()
                op_ind = leer_opcion("Elige un indicador: ", {"0", "1", "2", "3", "4", "5", "6"})
                if op_ind == "0":
                    break

                mapa = {
                    "1": "dolar",
                    "2": "euro",
                    "3": "uf",
                    "4": "ivp",
                    "5": "ipc",
                    "6": "utm",
                }
                indicador = mapa[op_ind]
                fecha = leer_fecha("Fecha")

                try:
                    # Consultar valor
                    valor = finance.get_indicator(indicador, fecha)
                    if valor is not None:
                        print(f"\n[{indicador.upper()}] {fecha} → valor: {valor}")

                        # Registrar solo si la opción es 4
                        if op == "4":
                            if logged_username:
                                indicator_date = datetime.datetime.strptime(fecha, "%d-%m-%Y").date()
                                query_date = datetime.datetime.now()
                                try:
                                    db.insert_finance_query(
                                        indicator_name=indicador,
                                        indicator_date=indicator_date,
                                        query_date=query_date,
                                        username=logged_username,
                                        provider_site="https://mindicador.cl/api",
                                        value=float(valor),
                                    )
                                    print("Consulta registrada en FINANCE_QUERIES.")
                                except Exception:
                                    print("No se pudo registrar la consulta.")
                            else:
                                print("Debes iniciar sesión para registrar.")
                    else:
                        print("\nNo se pudo obtener el valor.")
                except Exception:
                    print("Error al consultar el indicador.")

        # Pausa entre iteraciones
        input("\nPresiona ENTER para continuar...")

# ---- Ejecutar interfaz como programa principal ----
if __name__ == "__main__":





















    if __name__ == "__main__":
        db = Database(
            username=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )   

    db.create_all_tables()

    Auth.login(db, "C##Bayron", "220605")

