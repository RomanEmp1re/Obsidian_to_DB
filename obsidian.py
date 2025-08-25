'''obsidian.py
Интерфейсы для работы с markdown файламии из obsidian, для извлечения и обработки
этих данных
'''
import os
import yaml
import datetime as dt
import re
from config import VAULT_PATH, LOG_DIR, CURRENT_LOG_NAME, LOG_PATH
import logging


class FileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)


class DailyNote:
    # Class for daily note
    vault_path = VAULT_PATH
    def __init__(self, date):
        self.date = date
        self.note_name = dt.date.isoformat(date) + '.md'
        self._note_content = ''

    def __str__(self) -> str:
        return dt.date.isoformat(self.date)

    @classmethod
    def get_daily_notes_list(cls):
        filepath = os.path.join(cls.vault_path)
        file_list = os.listdir(filepath)
        return [dt.date.fromisoformat(d.replace('.md', '')) for d in file_list]

    @classmethod
    def get_first_date(cls):
        return min(cls.get_daily_notes_list())

    @classmethod
    def get_last_date(cls):
        return max(cls.get_daily_notes_list())

    @property
    def note_content(self) -> str:
        if hasattr(self, '_note_content'):
            filepath = os.path.join(self.vault_path, self.note_name)
            try:
                with open (filepath, 'r', encoding='utf-8') as f:
                    self._note_content = f.read()
            except FileNotFoundError as ex:
                logging.error(
                    f'Файл {self.note_name} не найден в {self.vault_path}'
                    )
                raise
        return self._note_content

    def describe(self) -> str:
        return f'''Дата - {self.__str__()}

Задачи:

{'\n'.join([i.__str__() for i in self.tasks_list]) or "нет задач"}

Привычки:

{'\n'.join([i.__str__() for i in self.habits_list]) or "нет привычек"}'''

    @property
    def tasks_list(self) -> list:
        tasks_block = re.search(r'# Tasks\s*(.*)', self.note_content, re.DOTALL)
        if not tasks_block:
            logging.error("Block with tasks wasn't found")
            raise FileFormatError("Block with tasks wasn't found")
        task_lines = tasks_block.group(1).splitlines()
        task_pattern = re.compile(r"- \[( |x)\] (.+?) \((\d+)\)")
        tasks = []
        for line in task_lines:
            match = task_pattern.match(line.strip())
            if match:
                is_done = match.group(1) != " "
                name = match.group(2).strip()
                reward = int(match.group(3))
                comment = None
                tasks.append(Task(is_done, name, reward, comment))
        if len(tasks) == 0:
            logging.warning("There's no tasks in note")
        return tasks

    @property
    def habits_list(self) -> list:
        match = re.search(r"---\s*\n(.*?)\n---", self.note_content, re.DOTALL)
        if not match:
            return []
        try:
            habits_list = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            logging.error(f"YAML wasn't read {e}")
            raise
        return [Habit(k, v) for k, v in habits_list.items()]

    @property
    def day_begin(self):
        for h in self.habits_list:
            if h.name == 'Day begin':
                return h.value
        return
        
    @property
    def day_end(self):
        for h in self.habits_list:
            if h.name == 'Day end':
                return h.value
        return

    @property
    def slept(self):
        prev_note = DailyNote(self.date - dt.timedelta(days=1))
        prev_day_end = prev_note.day_end
        if prev_day_end:
            return self.day_begin - prev_note.day_end
        else:
            return

class Task:
    '''Класс для задачи'''
    def __init__(self, is_done, name, reward, comment):
        self.is_done = is_done
        self.name = name
        self.reward = reward
        self.comment = comment

    def __str__(self):
        get_reward = 'выполнена ' + '(+' + str(self.reward) + ')' \
            if self.is_done else 'не выполнена' 
        return f'Задача "{self.name}" {get_reward}'


class Habit:
    '''Класс для привычек'''
    def __init__(self, name, value):
        if not isinstance(name, str):
            raise TypeError('Атрибут name должен быть типа str')
        self.name = name
        self.value = value
    
    def __str__(self):
        return self.name + ' - ' + str(self.value)


if __name__ == '__main__':
    my_date = dt.date(2025, 8, 16)
    d = DailyNote(my_date)
    print(d.slept)