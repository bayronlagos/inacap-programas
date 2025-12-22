from ecotech import auth, Database, Finance
from dotenv import load_dotenv
import flet as ft
import os

load_dotenv()

class App:
    def __init__(self, page: ft.page):
        self.page = page
        self.page.tittle = "Ecotech solutions"
        self.db = Database(
            username=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )
        try:
            self.db.create_all_tables()
        except Exception as error:
            print(f"{error}")

    def page_register(self):
        self.page.controls.clear()
        
        self.input_id = ft.TextField(
            label= "ID del usuario", 
            hint_text= "ingresa un numero para el ID del usuario"
        )
        self.input_username = ft.TextField(
            label= "Nombre de usuario", 
            hint_text= "ingresa un nombre de  usuario"
        )
        self.input_password = ft.TextField(
            label= "contraseña", 
            hint_text= "ingrese una contraseña",
            password=True,
            can_reveal_password=True
        )
        self.button_register = ft.Button(
            text= "REGISTRARSE",
            on_click=self.handle_register
        )
        self.text_status =ft.text(
            value=""
        )
        self.text_login =ft.button(
            text="iniciar sesion",
            on_click= lambda e: self.page_login()
        )
        self.page.add(
            self.input_id,
            self.input_username,
            self.input_password,
            self.button_register,
            self.text_status,
            self.text_login,
            self.button_login
        )
        self.page.update()


    def handle_register(self,e):
        try:
            id_user = int((self.input_id.value or"").strip())
            username = (self.input_username.value or "").strip()
            password = (self.input_password.value or "").strip()

            status = auth.register(db=self.db,
                                   id=id_user,
                                   username=username,
                                   password=password)
        except:
    def page_login(self):
        self.page.controls.clear()
        
        self.input_username = ft.TextField(
            label="nombre de usuario",
            hint_text="ingresa tu nombre de usuario"
        )
        self.input_password = ft.TextField(
            label="contraseña",
            hint_text="ingrese su contraseña",
            password=True,
            can_reveal_password=True
        )
        self.button_login= ft.button(
            text="iniciar sesion"
        )
        self.text_status= ft.text(
            value=""
        )
        self.text_register =ft.Text(
            values = "¿aun no tienes cuenta?"
        )
        self.button_register =ft.Text(
            text="registrate",
            on_click=lambda e: self.page_register()
        )
        self.page.update()

    def handle_login(self, e):
        username = (self.input_username.value or "").strip()
        password = (self.input_password.value or "").strip()

        status= auth.login(db=self.db,
                           username=username,
                           password=password)
        self.text_status.value = status["message"]
        self.page.update()
        if status["succes"]:
            self.logged_user = username
            self.page_main_menu()

    def page_main_menu(self):
        self.page.controls.clear()
        
        self.text_tittle_main_menu = ft.Text(
            value= "Main Menu",
            color= "#cc0000",
            size=32,
            weight=ft.FontWeight("bold")
        )
        self.button_indicators = ft.Button(
            text= "consultar indicadores",
            on_click = lambda e: self.page_indicator_menu()
        )
        self.button_logout = ft.Button(
            text= " cerrar sesion",
            on_click= lambda e: self.page_login()
        )
        self.page_add(
            self.text_tittle_main_menu,
            self.button_indicators,
            self.button_

        )

        self.page.update()

    def page_indicator_menu(self):
        self.page.controls.clear()
        #CODIGO
        self.page.update()

    def page_history_menu(self):
        self.page.controls.clear()
        #CODIGO
        self.page.update()

if __name__ == "__main__":
    ft.app(target=App)