# config.py
import os
import datetime as dt


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # путь до скрипта
# пусть до папки с заметками, папка с заметками должна лежать параллелоьно с папкой со скриптом
VAULT_PATH = os.path.join(SCRIPT_DIR, "..", "My Notes", "Daily Notes") 
LOG_DIR = os.path.join('logs')
CURRENT_LOG_NAME = dt.date.today().strftime('log_%Y-%m.log')
LOG_PATH = os.path.join(LOG_DIR, CURRENT_LOG_NAME)
DB_CONFIG = { # данные для подключения к БД
    "host": "localhost",
    "port": 5432,
    "dbname": "myStatistics",
    "user": "postgres",  # замени при необходимости
    "password": "1"  # замени на свой пароль
}
DATA_DIR = os.path.join('data')