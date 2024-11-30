import sqlite3
from os import getcwd
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)  # Ajusta el número de hilos según sea necesario
db = getcwd()+"\\db\\passwords.db"
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
    with sqlite3.connect(db, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
    return result

def execute_query(query, params=()):
    return executor.submit(run_query, query, params)
