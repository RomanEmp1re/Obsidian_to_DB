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


class HabitsRep(register.BaseStatistics):
    filename = 'habits_repost.csv'
    template = pd.DataFrame(
        columns=[
            'date',
            'name',
            'type',
            'result',
            'target',
            'str_value',
            'completed',
            'reward',
            'earned',
            'is_negative'
        ]
    )
    types_dict = {
            'date':'datetime64[s]',
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

    def __init__(self):
        super().__init__()
        self.data['type'] = pd.Categorical(
            self.data['type'], 
            categories=('float', 'bool', 'str', 'datetime')
        )

    def get_registered_data(self):
        return register.HabitsStatistics().data

    def eval_habit(self, habit:str, result:str, date=None):
        date = dictionaries.Habit.validate_date(date)
        actual_rules = dictionaries.RegisterRules().get_actual_rules(as_of_date=date)
        needed_habit = actual_rules.query("name == @habit")
        earned = 0
        completed_flag = False
        result = float(result)
        match needed_habit.iat[0, 4]:
            case 'float' | 'time':
                if needed_habit.iat[0, 2]:
                    earned = needed_habit['reward'].iat[0] \
                        if result < float(needed_habit['target'].iat[0]) else 0
                    completed_flag = False \
                        if result < float(needed_habit['target'].iat[0]) \
                        else True
                else:
                    earned = needed_habit['reward'].iat[0] \
                        if result >= float(needed_habit['target'].iat[0]) else 0
                    completed_flag = True \
                        if result < float(needed_habit['target'].iat[0]) \
                        else True
            case 'bool':
                if needed_habit.iat[0, 2]:
                    earned = needed_habit['reward'].iat[0] if not result else 0
                    completed_flag = not result
                else:
                    earned = needed_habit['reward'].iat[0] if result else 0
                    completed_flag =  result
        return earned, \
            needed_habit['target'].iat[0], \
            completed_flag, \
            (str(result) + ' ' + needed_habit['unit'].iat[0]).strip()


    def fill_table(self):
        mask = self.data[self.data['earned'].isna()]
        self.data.loc[mask, ['earned', 'reward', 'str_value', 'completed']] = (
            self.data.loc[mask, ['name', 'result', 'date']]
            .apply(lambda row : self.eval_habit(
                row['name'], row['result'], row['date']), axis=1)
            .apply(pd.Series)
        )


    '''
    def calc_data(self):
        self.results = self.get_registered_data()
        registered_data = register.HabitsStatistics()
        self.raw_data = registered_data.data
        self.data = self\
            .data\
            .apply(
                lambda x: x['result_float'] = x['result'] if x['type'] == 'float' else pd.NA,
                )'''


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
    a = HabitsRep()
    print(a.eval_habit('hobby', 22))
    print(a.eval_habit('hobby', 34, dt.date(2024, 1, 1)))
    print(a.eval_habit('meditation', False))