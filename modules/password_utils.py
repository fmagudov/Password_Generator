from sqlite3 import Error
import random
import string
from .database import execute_query

def generate_password(length, include_symbols, symbols_at_end, include_numbers, include_uppercase):
    letters = string.ascii_lowercase
    if include_uppercase:
        letters += string.ascii_uppercase
    digits = string.digits if include_numbers else ''
    symbols = string.punctuation if include_symbols else ''

    # Asegurar que al menos haya un número, una mayúscula y un símbolo si se incluyen
    password = ''
    if include_numbers:
        password += random.choice(digits)
        length -= 1
    if include_uppercase:
        password += random.choice(string.ascii_uppercase)
        length -= 1
    if include_symbols:
        if not symbols_at_end:
            password += random.choice(symbols)
            length -= 1
        else:
            length -= 1

    # Generar el resto de la contraseña
    if not symbols_at_end:
        all_chars = letters + digits + symbols
    else:
        all_chars = letters + digits

    password += ''.join(random.choice(all_chars) for i in range(length))

    # Mezclar la contraseña
    password = ''.join(random.sample(password, len(password)))
    
    # Agregar símbolos al final
    if symbols_at_end:
        password += ''.join(random.sample(symbols,1))

    return password

def is_password_unique(conn, password): 
    cursor = conn.cursor() 
    try: 
        cursor.execute('SELECT 1 FROM passwords WHERE password = ?', (password,)) 
        result = cursor.fetchone() 
        return result is None 
    except Error as e: 
        print(f"Error checking password uniqueness: {e}") 
        return False