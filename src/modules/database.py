import sqlite3
from os import getcwd

db = getcwd() + "\\db\\passwords.db"

def init_db():
    conn = sqlite3.connect(db, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        password TEXT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    conn.commit()
    return conn

def run_query(query, params=()):
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
    return result

def execute_query(query, params=()):
    return run_query(query, params)

def delete_user_and_passwords(username):
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        # Obtener el id del usuario
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()
        if user_id:
            user_id = user_id[0]
            # Eliminar las contraseñas asociadas
            cursor.execute('DELETE FROM passwords WHERE user_id = ?', (user_id,))
            # Eliminar el usuario
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return True
        return False

def execute_delete_user_and_passwords(username):
    return delete_user_and_passwords(username)