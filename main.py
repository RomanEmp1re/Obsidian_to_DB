# BUG: два раза устанавливается соединение
# TODO все-таки пусть будут ежеденвные логи ссохранением логов за последние 7 дней
# TODO: добавить отчистку логов
# TODO: обновление информации, если таковая уже загружена
# TODO: получение информации через консоль
# TODO: массовая загрузка ранее не загруженных дат


import datetime as dt
import re
import logging
import pandas as pd


# НАСТРОЙКИ

# Настройки логирования
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(levelname)s | %(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

# чистим логи, которые существуют более 3 месяцев
def cleanup_old_logs(log_dir, max_months=3):
    now = dt.datetime.now()
    for fname in os.listdir(log_dir):
        match = re.match(r"log_(\d{4})-(\d{2})\.log", fname)
        if match:
            year, month = int(match[1]), int(match[2])
            file_date = dt.datetime(year, month, 1)
            if (now - file_date).days > (max_months * 30):
                try:
                    os.remove(os.path.join(log_dir, fname))
                    logging.info(f"Удалён старый лог: {fname}")
                except Exception as e:
                    logging.warning(f"Не удалось удалить лог {fname}: {e}")


# Классы
class FileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.ERROR(f'Ошибка формата файла')


# === ОСНОВНАЯ ЛОГИКА ===
if __name__ == '__main__':
    input_date = input('Введите дату, которую хотите загрузить (если не'\
        + 'ввести ничего, то загружена будет вчерашняя дата): ')
    if input_date.strip() == '.':
        connection = DataBase(**DB_CONFIG)
        connection.connect()
        date = DailyNote(dt.date.today())
        print(date.get_daily_notes_list())
        print(connection.scan_day_statistics)
        quit()
    if input_date.strip() == '':
        DATE = dt.date.today() - dt.timedelta(days=1)
    else:
        try:
            DATE = dt.date.fromisoformat(input_date) # надо определеить способ как выбрать дату
        except ValueError:
            logging.error(f'Введен некорректный формат даты {input_date}')
            raise ValueError('Введите корректный формат даты, например 2025-06-10')
        
    d1 = DailyNote(DATE)

    connection = DataBase(**DB_CONFIG)
    connection.connect()
    connection.dump_daily_note(d1)