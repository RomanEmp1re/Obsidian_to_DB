# 1. Достаем зарегестрированные данные
# 2. Достаем правила
# 3. Сравниваем 
# 4. Возвращаем 3 репра: даты и баллы, привычеи и баллы, таски и баллы
import pandas as pd
import register
import dictionaries
import datetime as dt


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


class HabitsRep:
    filename = 'habits_repost.csv'
    template = pd.DataFrame(
        columns=[
            'date',
            'habit',
            'type',
            'value',
            'target',
            'repr_value',
            'completed',
            'reward',
            'earned',
            'is_negative'
        ]
    )
    template = template.astype(
        {
            'date':'datetime64[D]',
            'name':'object',
            'type':'object',
            'result':'object',
            'target':'object',
            'str_value':'object',
            'completed':'bool',
            'reward':'Int16',
            'earned':'Int16',
            'is_negative':'bool'
        }
    )
    template['type'] = pd.Categorical(
        template['type'], 
        categories=('float', 'bool', 'str', 'datetime')
    )

    def __init__(self):
        super().__init__()

    def get_registered_data(self):
        return register.HabitsStatistics().data

    def eval_habit(self, habit, result, date=None):
        date = dictionaries.Habit.validate_date(date)
        actual_rules = dictionaries.ManageJson.get_actual_rules(date=date)
        needed_habit = actual_rules[habit]
        return

    def calc_data(self):
        self.results = self.get_registered_data()
        registered_data = register.HabitsStatistics()
        self.raw_data = registered_data.data
        self.data = self\
            .data\
            .apply(
                lambda x: x['result_float'] = x['result'] if x['type'] == 'float' else pd.NA,
                )


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


if __name__ == '__main__':
    a = TasksRep()
    a.calc_data()
    print(a.data)
    a.push_to_csv()

    