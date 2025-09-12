# 1. Достаем зарегестрированные данные
# 2. Достаем правила
# 3. Сравниваем 
# 4. Возвращаем 3 репра: даты и баллы, привычеи и баллы, таски и баллы
import pandas as pd
import register
import dictionaries
import datetime as dt
import config
import os


class TasksRep(register.BaseStatistics):
    filename = 'tasks_report.csv'
    template = pd.DataFrame(
        columns=[
            'date',
            'task',
            'reward',
            'completed',
            'earned_reward'
        ]
    )
    template = template.astype({
        'date': 'datetime64[s]',
        'task': 'object',
        'reward': 'Int16',
        'completed': 'bool',
        'earned_reward': 'Int16'
    })

    def __init__(self):
        super().__init__()

    def get_registered_data(self):
        return register.TaskStatistics().data

    def calc_data(self):
        self.data = self.get_registered_data()
        self.data['earned'] = self.data['reward'] * self.data['is_done']


class DatesRep(register.BaseStatistics):
    template = pd.DataFrame(
        columns=[
            'tasks_reward',
            'habits_reward',
            'reward',
            'max_tasks_reward',
            'max_habits_reward',
            'max_reward'
        ]
    )
    template = template.astype({
        'tasks_reward': 'Int32',
        'habits_reward': 'Int32',
        'reward': 'Int32',
        'max_tasks_reward': 'Int32',
        'max_habits_reward': 'Int32',
        'max_reward': 'Int32'
    })
    filename = 'days.csv'

    def __init__(self):
        super().__init__()

if __name__ == '__main__':
    a = TasksRep()
    a.calc_data()
    print(a.data)
    a.push_to_csv()

    