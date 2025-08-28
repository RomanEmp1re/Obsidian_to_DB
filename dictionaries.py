# module for managing with data

import pandas as pd
import datetime as dt
import os
from config import DATA_DIR
import re


class BaseClass:
    filename : str = None
    template : pd.DataFrame = None
    default_valid_to : dt.date = dt.date(2222, 12, 31)

    def __init__(self):
        self.path = os.path.join(DATA_DIR, self.filename)
        if not os.path.exists(self.path):
            self.data = self.template
            self.data.to_csv(self.path, sep=';')
        self.data = pd.read_csv(self.path, sep=';', index_col=0).reindex()
        if self.data.empty:
            self.data = self.template

    def push_changes(self):
        self.data = self.data.reindex()
        self.data.to_csv(self.path, sep=';', mode='w')

    def get_actual_data(self, date=None):
        if date == None:
            date = dt.date.today()
        return self.data[
            (self.data['valid_from'] <= date) &
            (self.data['valid_to'] > date)
        ]

class HabitsList(BaseClass):
    filename = 'habits_dict.csv'
    template = pd.DataFrame(
        columns=['unit', 'type']
    )
    template['type'] = pd.Categorical(template['type'], categories=('float', 'str', 'bool'))

    def __init__(self):
        super().__init__()

    def add(self, name, unit=None, type='float'):
        if any(self.data.index == name):
            raise ValueError('The habit ' + name + ' already exists!')
        else:
            self.data.loc[name] = [unit, type]
        return

    def drop(self, name):
        self.data = self.data[self.data.index != name]

    def get_actual_data(self, date=None):
        raise NotImplementedError('This method is not allowed for HabitsList')


class HabitRewards(BaseClass):
    filename = 'habits_rewards.csv'
    template = pd.DataFrame(
        columns=[
            'name', 'type','target', 'reward', 'valid_from', 'valid_to'
            ]
    )
    template = template.astype({
        'name': 'object', 
        'type' : 'datetime64[s]', 
        'target': 'object',
        'reward': 'Int16',
        'valid_from': 'datetime64[s]',
        'valid_to': 'datetime64[s]'
    })
    template['type'] = pd.Categorical(
        template['type'],
        categories=('str', 'bool', 'float')
        )

    def __init__(self):
        super().__init__()

    def add(
            self, 
            habit,
            target,
            reward,
            valid_from=None,
            valid_to=None
    ):
        if valid_from is None:
            valid_from = dt.date.today()
        elif isinstance(valid_from, dt.datetime):
            valid_from = valid_from.date()
        if valid_to is None:
            valid_to = self.default_valid_to
        elif isinstance(valid_to, dt.datetime):
            valid_to = valid_to.date()
        id = len(self.data)
        self.data.loc[id, ('name', 'reward', 'valid_from', 'valid_to')] = (
            habit, reward,
            valid_from, valid_to)
        target = target.strip()
        if target in ('True', 'False'):
            self.data.loc[id, ('type', 'target')] = ['bool', target]
        elif re.search(r'[][[(]([0-9.]*)+[,;-]([0-9.]*)[])]', target.replace(' ', '')):
            # ищем выражение диапазона, типа [1-2], (0,6], [7, 12.2)
            self.data.loc[id, ('type', 'target')] = ['float', target.replace(' ', '')]
        else:
            self.data.loc[id, ('type', 'target')] = ['str', 'target']

    def drop(self, id=None, name=None, valid_from=None,
                    valid_to=None, reward=None):
        if name:
            mask_name = self.data['name'] == name
        else:
            mask_name = True
        if id:
            mask_id = self.data.index == id
        else:
            mask_id = True
        if valid_from:
            mask_valid_from = self.data['valid_from'] == valid_from
        else:
            mask_valid_from = True
        if valid_to:
            mask_valid_to = self.data['valid_to'] == valid_to
        else:
            mask_valid_to = True
        if reward:
            mask_reward = self.data['reward'] == reward
        else:
            mask_reward = True
        mask_for_delete = ~(mask_name & mask_valid_from &
                            mask_id & mask_valid_to & mask_reward)
        self.data = self.data[mask_for_delete]

class SleepReward(BaseClass):
    filename = 'sleep_rewards.csv'
    template = pd.DataFrame(
        columns=['time', 'kind', 'reward', 'valid_from', 'valid_to']
    )
    template = template.astype({
        'time': 'datetime64[ns]', 
        'kind' : 'object', 
        'reward': 'int16',
        'valid_from': 'datetime64[s]',
        'valid_to': 'datetime64[s]'
    })

    def __init__(self):
        super().__init__()
    
    def add(
        self,
        time: dt.time,
        kind: str, 
        reward: int, 
        valid_from=None,
        valid_to=None,
        is_next_day=False
        ):
        if valid_from is None:
            valid_from = dt.date.today()
        if valid_to is None:
            valid_to = self.default_valid_to
        elif isinstance(valid_from, dt.datetime):
            valid_from = valid_from.date()
        elif isinstance(valid_to, dt.datetime):
            valid_to = valid_to.date()
        minutes_since_time = time.hour*60 + time.minute
        if is_next_day:
            minutes_since_time += 1440
        id = len(self.data)
        self.data.loc[id] = [
            minutes_since_time,
            kind,
            reward,
            valid_from,
            valid_to
        ]

    def drop(self, time=None, 
        is_next_day=None, 
        valid_from=None, 
        valid_to=None,
        reward=None):
        default_mask = pd.Series([True for i in self.data.index], index = self.data.index.values)
        if time:
            minutes_since_time = time.hour*60 + time.minute
            if is_next_day:
                minutes_since_time += 1440
            mask_name = self.data['time'] == minutes_since_time
        else:
            mask_name = default_mask
        if valid_from:
            mask_valid_from = self.data['valid_from'] == valid_from
        else:
            mask_valid_from = default_mask
        if valid_to:
            mask_valid_to = self.data['valid_to'] == valid_to
        else:
            mask_valid_to = default_mask
        if reward:
            mask_reward = self.data['reward'] == reward
        else:
            mask_reward = default_mask
        mask_for_delete = ~(mask_name & mask_valid_to & mask_valid_from & mask_reward)
        self.data = self.data[mask_for_delete]


if __name__ == '__main__':
    # test HabitRewards
    # opening and creating empty_dataframe
    '''h = HabitRewards()
    # adding habit float
    h.add('Спорт', '(0;60)', 2, valid_to=dt.date(2001, 11, 1))
    h.add('Спорт', '(;0]', 1)
    h.add('Чтение', '(;0]', 1)
    h.add('Чтение', '(0;10]', 1)
    h.add('Чтение', '(10;)', 1)
    s = SleepReward()
    s.add(dt.time(10, 0, 0), 'begin', 2, valid_from=dt.date(2020, 1, 1))
    s.add(dt.time(10, 30, 0), 'begin', 1, valid_to = dt.date(2029, 2, 1))'''
    h = HabitsList()
    h.add('footbal', 120, 'float')
    print(h.data)
    h.push_changes()

