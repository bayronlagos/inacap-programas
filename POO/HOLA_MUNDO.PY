# 1. Paso: Importar flet
import flet as ft

# 2. Paso: Clase principal de la aplicación
class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Hola mundo"
        # Siempre cómo última linea de __init__
        self.build()
    # Metodo principal para agregar elementos
    # En mi página/aplicación
    def build(self):
        self.page.add(
            ft.Text(value="Hola mundo")
        )
# 3. Inicializamos la app
if __name__ == "__main__":
    ft.app(target=App)