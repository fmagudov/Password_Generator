'''
flet pack main.py -v -D -v -D
pip install --upgrade auto-py-to-exe
auto-py-to-exe
'''

import flet as ft
from sqlite3 import IntegrityError
from modules.config import load_config, save_config
from modules.password_utils import generate_password, is_password_unique
from modules.database import init_db, execute_query, execute_delete_user_and_passwords


def main(page: ft.Page):
    page.title = "Generador Contraseñas"
    page.window.center()
    page.window.width = 400
    page.window.height = 580
    page.window.resizable = False
    page.window.maximizable = False

    conn = init_db()

    # Cargar la configuración previa
    config = load_config()

    # Recuperar usuarios existentes para el desplegable
    users = execute_query('SELECT username FROM users')
    user_options = [ft.dropdown.Option(username) for username, in users]

    # Función para actualizar el valor del config
    def act_config():
        config = {
            "length": length.value,
            "username": username_dropdown.value,
            "include_symbols": include_symbols.value,
            "symbols_at_end": symbols_at_end.value,
            "include_numbers": include_numbers.value,
            "include_uppercase": include_uppercase.value,
        }
        try:
            save_config(config)
        except Exception as e:
            print(f"Error en las configuraciones {e}")

    def on_generate(e):
        outputInfo.value = ""
        try:
            pwd_length = int(length.value) if length.value else 8
            if pwd_length < 3:
                outputInfo.value = "La longitud debe ser al menos 3 para incluir un número, una mayúscula y un símbolo."
                page.update()
                return
        except ValueError:
            outputInfo.value = "Por favor, introduce un número válido para la longitud."
            page.update()
            return

        if username_dropdown.value == "Nuevo Usuario":
            username_value = new_username_input.value
            if not username_value:
                outputInfo.value = "Por favor, introduce un nuevo nombre de usuario."
                page.update()
                return
        else:
            username_value = username_dropdown.value

        inc_symbols = include_symbols.value
        sym_end = symbols_at_end.value
        inc_numbers = include_numbers.value
        inc_uppercase = include_uppercase.value

        password = generate_password(
            pwd_length, inc_symbols, sym_end, inc_numbers, inc_uppercase)

        while not is_password_unique(conn, password):
            password = generate_password(
                pwd_length, inc_symbols, sym_end, inc_numbers, inc_uppercase)

        output.value = password
        outputInfo.value = "Password generado y copiado al portapapeles correctamente!"
        copy_to_clipboard()
        page.update()

    def on_save_to_db(e):
        outputInfo.value = ""
        username_value = username_dropdown.value if username_dropdown.value != "Nuevo Usuario" else new_username_input.value
        if not username_value:
            outputInfo.value = "Por favor, selecciona o introduce un nombre de usuario antes de guardar."
            page.update()
            return

        execute_query(
            'INSERT OR IGNORE INTO users (username) VALUES (?)', (username_value,))

        user_id = execute_query(
            'SELECT id FROM users WHERE username = ?', (username_value,))
        user_id = str(user_id[0][0])

        password = output.value
        try:
            execute_query(
                'INSERT INTO passwords (user_id, password) VALUES (?, ?)', (user_id, password))
            outputInfo.value = "Contraseña guardada en la base de datos."
        except IntegrityError:
            outputInfo.value = "La contraseña ya existe en la base de datos. Por favor, genere una nueva."
        except Exception as e:
            outputInfo.value = f"Error: {e}"
        page.update()

    def on_close(e):
        # if e.data == "close":
            act_config()
            page.window.destroy()

    page.window.prevent_close = True
    page.window.on_event = on_close

    def add_user_drop(e):
        if new_username_input.value != "":
            username_dropdown.options.append(
                ft.dropdown.Option(new_username_input.value))
            username_dropdown.value = new_username_input.value
            new_username_input.value = ""
            page.update()

    def on_delete_user(e):
        print(e)
        username_value = username_dropdown.value
        if not username_value or username_value == "Nuevo Usuario":
            outputInfo.value = "Por favor, selecciona un nombre de usuario válido para borrar."
            page.update()
            return

        if execute_delete_user_and_passwords(username_value):
            outputInfo.value = f"Usuario {
                username_value} y sus contraseñas asociadas han sido eliminados."
        else:
            outputInfo.value = f"Usuario {username_value} no encontrado."

        users = execute_query('SELECT username FROM users')
        user_options = [ft.dropdown.Option(username) for username, in users]
        user_options.append(ft.dropdown.Option("Nuevo Usuario"))
        username_dropdown.options = user_options

        page.update()

    def copy_to_clipboard():
        if output.value:
            page.set_clipboard(output.value)

    titulo = ft.Text(value="Generador de Contraseñas",
                    size=28, weight=ft.FontWeight.BOLD)
    username_dropdown = ft.Dropdown(
        label="Nombre de usuario", options=user_options, value=config.get("username"))
    new_username_input = ft.TextField(label="Nuevo nombre de usuario")
    length = ft.TextField(label="Longitud de la contraseña",
                        value=config.get("length", "8"))
    include_symbols = ft.Checkbox(
        label="Incluir símbolos", value=config.get("include_symbols", True))
    symbols_at_end = ft.Checkbox(
        label="Símbolos al final", value=config.get("symbols_at_end", False))
    include_numbers = ft.Checkbox(
        label="Incluir números", value=config.get("include_numbers", True))
    include_uppercase = ft.Checkbox(
        label="Incluir letras mayúsculas", value=config.get("include_uppercase", True))
    output = ft.Text(size=24, selectable=True)
    outputInfo = ft.Text(size=14, text_align=ft.TextAlign.CENTER)
    generate_button = ft.ElevatedButton(
        text="Generar Contraseña", on_click=on_generate)
    save_button = ft.ElevatedButton(
        text="Guardar en BD", on_click=on_save_to_db)
    save_button2 = ft.ElevatedButton("Guardar y Cerrar", on_click=on_close)
    add_user_button = ft.ElevatedButton("+", on_click=add_user_drop)
    delete_user_button = ft.ElevatedButton("-", on_click=on_delete_user)

    output_container = ft.Container(
        content=output, alignment=ft.alignment.center, expand=True)
    outputInfo_container = ft.Container(
        content=outputInfo, height=80, width=100, padding=10, alignment=ft.alignment.center, expand=True)

    page.add(
        ft.Column([
            ft.Row([titulo]),
            ft.Row([username_dropdown, delete_user_button]),
            ft.Row([new_username_input, add_user_button]),
            ft.Row([length]),
            ft.Row([include_symbols, symbols_at_end]),
            ft.Row([include_numbers, include_uppercase]),
            ft.Row([generate_button]),
            ft.Row([save_button, outputInfo_container]),
            ft.Row([save_button2]),
            ft.Row([output_container])
        ])
    )


ft.app(target=main)
