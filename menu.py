
import os
import datetime
import bcrypt
from typing import Optional
from dotenv import load_dotenv

# IMPORTA tus clases desde el archivo donde están definidas:
from main import Database, Auth, Finance
# ^^^ Cambia 'core_app' por el nombre real de tu archivo (sin .py).
#    Si están en un paquete/carpeta, usa 'from carpeta.core_app import ...'

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

def leer_opcion(msg, opciones_validas):
    op = input(msg).strip()
    while op not in opciones_validas:
        op = input(f"Opción inválida. {msg}").strip()
    return op

def leer_entero(msg):
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

def leer_texto(msg, min_len=1, max_len=128):
    while True:
        s = input(msg).strip()
        if len(s) < min_len:
            print(f"Debe tener al menos {min_len} caracteres.")
            continue
        if len(s) > max_len:
            print(f"No puede superar {max_len} caracteres.")
            continue
        return s

def leer_fecha(msg):
    s = input(msg + " (dd-mm-yyyy, vacío para hoy): ").strip()
    if not s:
        return datetime.date.today().strftime("%d-%m-%Y")
    try:
        datetime.datetime.strptime(s, "%d-%m-%Y")
        return s
    except ValueError:
        print("Fecha inválida. Se usará hoy.")
        return datetime.date.today().strftime("%d-%m-%Y")

def try_login(db, username, password) -> Optional[str]:
    filas = db.query(
        "SELECT username, password FROM USERS WHERE username = :u",
        {"u": username}
    )
    if not filas:
        print("Credenciales inválidas.")
        return None

    stored = filas[0][1]
    try:
        stored_hash_bytes = stored.encode("utf-8")
    except AttributeError:
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

def main():
    load_dotenv()

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
            user_id = leer_entero("Id (entero positivo): ")
            username = leer_texto("Usuario (3-32, letras/números/._-): ", 3, 32)
            password = leer_texto("Contraseña (≥8 caracteres): ", 8, 128)
            try:
                Auth.register(db, user_id, username, password)
            except Exception:
                print("No se pudo registrar el usuario.")

        elif op == "2":
            username = leer_texto("Usuario: ", 3, 32)
            password = leer_texto("Contraseña: ", 1, 128)
            logged = try_login(db, username, password)
            logged_username = logged if logged else None

        elif op in {"3", "4"}:
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
                    valor = finance.get_indicator(indicador, fecha)
                    if valor is not None:
                        print(f"\n[{indicador.upper()}] {fecha} → valor: {valor}")

                        if op == "4":  # registrar también
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

        print("\nPresiona ENTER para continuar...")
        input()

if __name__ == "__main__"