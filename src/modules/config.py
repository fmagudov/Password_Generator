import json
from os import getcwd, path

# ruta_actual = os.getcwd() 
# print("Ruta actual:", ruta_actual) # Moverse un nivel atrás en la estructura de rutas 
# ruta_anterior = os.path.dirname(ruta_actual) 
# os.chdir(ruta_anterior) 
# print("Nueva ruta:", os.getcwd())

# CONFIG_FILE = os.path.dirname(__file__)+"\\db\\config.json"
CONFIG_FILE = getcwd()+"\\db\\config.json"

def load_config():
  if path.exists(CONFIG_FILE):
      with open(CONFIG_FILE, 'r') as f:
        return json.load(f)
  return {}

def save_config(config):
  with open(CONFIG_FILE, 'w') as f:
    json.dump(config, f)
