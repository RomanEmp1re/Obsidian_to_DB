'''
Модуль для работы с базой данных
'''
import os
import yaml
import datetime as dt
import re
from config import VAULT_PATH, LOG_DIR, CURRENT_LOG_NAME, LOG_PATH
import logging

class DataBase:
    '''Класс для соединения и работой с БД'''
    def __init__(self, host, port, dbname, user, password):
        self.user = user
        self.host = host
        self.port = port
        self.dbname = dbname
        self.password = password
        self.cursor = self.connect().cursor()

    # устанавливает соединение с БД по переданным параметрам
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                password=self.password,
                user=self.user
            )
            logging.info('Успешное соединение с БД')
            return self.connection
        except Exception as ex:
            logging.error(f'Ошибка соединения с БД: {ex}')
            raise

    # Возвращает даты, которых нет в daysstatistics
    def scan_day_statistics(self):
        self.cursor.execute('''
select * from dates_not_in_statistics
        ''')
        return self.cursor.fetchall()

    

    # вставляет указанную дату в daysstatistics
    def insert_day_statistics(self, date, day_begin, day_end):
        if not isinstance(day_begin, dt.datetime) \
            or not(isinstance(day_end, dt.datetime)):
            logging.error(
                'Неправильный формат даты в файле obsidian'
                )
            raise TypeError(\
                'Не введена дата начала дня или дата конца дня'\
                ', или неправильный формат даты'
                )
        try:
            self.cursor.execute("""
                INSERT INTO daysstatistics (date, day_b, day_e)
                VALUES (%s, %s, %s)
            """, (date, day_begin, day_end)
            )
            logging.info(
                f'В daysstatistics загружена информация: {date.isoformat()}'
                f' подъем был {day_begin.isoformat()}, сон {day_end.isoformat()}')
        except Exception as e:
            logging.info(
                'В базу данных не удалось загрузить информацию по началу и'
                 f' концу дня за {date.isoformat()}'
            )
            raise
        
    # Вставляет ежедневные привычки
    def insert_daily_habits(self, date, habits_list):
        cnt_inserted = 0
        cnt_input = 0
        for h in habits_list:
            try:
                if h.name in ('Day begin', 'Day end'):
                    continue
                cnt_input += 1
                self.cursor.execute('''
                    insert into dailyhabits(day, habit_id, value)
                    select %s, 
                        h.id,
                        %s
                    from habits as h
                    where h.name = %s
                ''', (date, h.value_int, h.name)
                )
                cnt_inserted += 1
            except Exception as ex:
                logging.error(f'Привычку {h.name} загрузить не удалось: {ex}')
                raise
        return cnt_input, cnt_inserted
    
    def insert_task(self, date, tasks_list):
        cnt_inserted = 0
        cnt_input = len(tasks_list)
        for t in tasks_list:
            self.cursor.execute('''
                insert into purposes(name, day, reward, is_done, info)
                values (%s, %s, %s, %s, %s)
            ''', (t.name, date, t.reward, t.is_done, t.comment)
            )
            cnt_inserted += 1
        return cnt_input, cnt_inserted
        
    def dump_daily_note(self, day):
        connect = self.connect()
        try:
            self.insert_day_statistics(day.date, day.day_begin, day.day_end)
            habit_cnt_all, habit_cnt_loaded = self.insert_daily_habits(
                day.date, day.habits_list
                )
            task_cnt_all, task_cnt_loaded = self.insert_task(
                day.date, day.tasks_list
                )
            if task_cnt_all == task_cnt_loaded \
                and habit_cnt_all == habit_cnt_loaded:
                connect.commit()
                logging.info(
                    f'Транзакция завершена, все данные загружены'
                    )
            else:
                logging.error(
                    'Не удалось загрузить все данные, транзакция отменена. '\
                    'До отмены транзакции удалось загрузить '\
                    f'{task_cnt_loaded} из {task_cnt_all} задач и '\
                    f'{habit_cnt_loaded} из {habit_cnt_all} привычек.'
                )
                connect.rollback()
            logging.info(f'Заметки за {day.date.isoformat()} сохранены')
        except Exception as ex:
            logging.error(
                f'Заметки за {day.date.isoformat()} не были сохранены: {ex}'
                )
            raise
