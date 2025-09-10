# 1. Достаем зарегестрированные данные
# 2. Достаем правила
# 3. Сравниваем 
# 4. Возвращаем 3 репра: даты и баллы, привычеи и баллы, таски и баллы
import pandas as pd
import register
import dictionaries
import config
import os


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
        rules = dictionaries.ManageJson
        print(rules.get_actual_rules())
    