import flet as ft
from config import load_config, save_config
from password_utils import generate_password, is_password_unique
from database import init_db, execute_query
import sqlite3

def main(page: ft.Page):
    page.window_width = 800
    page.window_height = 600

    conn = init_db()

    # Cargar la configuración previa
    config = load_config()

    # Recuperar usuarios existentes para el desplegable
    future_users = execute_query('SELECT username FROM users')
    users = future_users.result()
    user_options = [ft.dropdown.Option(username) for username, in users]
    user_options.append(ft.dropdown.Option("Nuevo Usuario"))

    length = ft.TextField(label="Longitud de la contraseña", value=config.get("length", "12"))
    username_dropdown = ft.Dropdown(label="Nombre de usuario", options=user_options, value=config.get("username"))
    include_symbols = ft.Checkbox(label="Incluir símbolos", value=config.get("include_symbols", True))
    symbols_at_end = ft.Checkbox(label="Símbolos al final", value=config.get("symbols_at_end", False))
    include_numbers = ft.Checkbox(label="Incluir números", value=config.get("include_numbers", True))
    include_uppercase = ft.Checkbox(label="Incluir letras mayúsculas", value=config.get("include_uppercase", True))
    output = ft.Text()

    save_to_db = ft.Checkbox(label="Guardar en base de datos", value=config.get("save_to_db", True))

    def on_generate(e):
        try:
            pwd_length = int(length.value)
            if pwd_length < 3:
                output.value = "La longitud debe ser al menos 3 para incluir un número, una mayúscula y un símbolo."
                page.update()
                return
        except ValueError:
            output.value = "Por favor, introduce un número válido para la longitud."
            page.update()
            return

        if username_dropdown.value == "Nuevo Usuario":
            output.value = "Por favor, escribe el nuevo nombre de usuario en el desplegable."
            page.update()
            return
        else:
            username_value = username_dropdown.value

        inc_symbols = include_symbols.value
        sym_end = symbols_at_end.value
        inc_numbers = include_numbers.value
        inc_uppercase = include_uppercase.value

        password = generate_password(pwd_length, inc_symbols, sym_end, inc_numbers, inc_uppercase)
        
        while not is_password_unique(conn, password):  # Pasar la conexión en lugar del cursor
            password = generate_password(pwd_length, inc_symbols, sym_end, inc_numbers, inc_uppercase)

        output.value = password

        # Guardar la configuración actual
        config.update({
            "length": length.value,
            "username": username_value if username_dropdown.value != "Nuevo Usuario" else None,
            "include_symbols": include_symbols.value,
            "symbols_at_end": symbols_at_end.value,
            "include_numbers": include_numbers.value,
            "include_uppercase": include_uppercase.value,
            "save_to_db": save_to_db.value
        })
        save_config(config)
        page.update()

    def on_save_to_db(e):
        username_value = username_dropdown.value
        if not username_value or username_value == "Nuevo Usuario":
            output.value = "Por favor, selecciona o escribe un nombre de usuario antes de guardar."
            page.update()
            return

        future_insert_user = execute_query('INSERT OR IGNORE INTO users (username) VALUES (?)', [username_value])  # Cambiar a lista
        future_insert_user.result()

        future_user_id = execute_query('SELECT id FROM users WHERE username = ?', [username_value])  # Cambiar a lista
        user_id = future_user_id.result()[0]
        
        password = output.value
        try:
            future_insert_password = execute_query('INSERT INTO passwords (user_id, password) VALUES (?, ?)', [user_id, password])  # Cambiar a lista
            future_insert_password.result()
            output.value = "Contraseña guardada en la base de datos."
        except sqlite3.IntegrityError as e:
            output.value = "La contraseña ya existe en la base de datos. Por favor, genera una nueva."
        
        page.update()

    def on_user_select(e):
        if username_dropdown.value == "Nuevo Usuario":
            username_dropdown.options[-1] = ft.dropdown.Option(label="Nuevo Usuario (escriba aquí)", value="")
        page.update()

    username_dropdown.on_change = on_user_select

    generate_button = ft.ElevatedButton(text="Generar Contraseña", on_click=on_generate)
    save_button = ft.ElevatedButton(text="Guardar en BD", on_click=on_save_to_db)
    
    # Agregar un contenedor centrado para el output
    output_container = ft.Container(
        content=output,
        alignment=ft.alignment.center,
        expand=True
    )
    
    page.add(ft.Column([
        ft.Row([username_dropdown]),
        ft.Row([length]),
        ft.Row([include_symbols, symbols_at_end]),
        ft.Row([include_numbers, include_uppercase]),
        ft.Row([save_to_db]),
        ft.Row([generate_button]),
        ft.Row([save_button]),
        ft.Row([output_container])  # Usar el contenedor centrado
    ]))

    # Función para guardar la configuración al cerrar la ventana
    def on_close(e):
        save_config(config)
    
    page.on_event("close", on_close)

ft.app(target=main)
