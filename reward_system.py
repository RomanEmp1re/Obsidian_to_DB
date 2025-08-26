# BUG to_csv connects row added to header and then moves to another row

import pandas as pd
import datetime as dt
import os
from config import DATA_DIR


class HabitsList:
    'class for managing habits rewards and habits_list'
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_list.csv')
        self.data = pd.read_csv(self.path, sep=';', index_col=0)
        if self.data.empty:
            self.data = pd.DataFrame(columns=['unit', 'measure_kind'])
        self.data['measure_kind'] = pd.Categorical(self.data['measure_kind'], categories=('float', 'str', 'bool'))

    def add_habit(self, name, unit=None, type='float'):
        if any(self.data.index == name):
            raise ValueError('The habit ' + name + ' already exists!')
        else:
            self.data.loc[name] = [unit, type]
        return

    def drop_habit(self, name):
        self.data = self.data[self.data.index != name]

    def push_changes(self):
        self.data = self.data.reindex()
        self.data.to_csv(self.path, sep=';', mode='w')

class BaseRewards:
    filename : str = None
    template : pd.DataFrame = None

    def __init__(self):
        self.path = os.path.join(DATA_DIR, self.filename)
        self.data = pd.read_csv(self.path, sep=';', index_col=0)
        if self.data.empty:
            self.data = self.template

    def push_changes(self):
        self.data = self.data.reindex()
        self.data.to_csv(self.path, sep=';', mode='w')

    def get_actual_data(self, date=None):
        if date == None:
            date = dt.date.today()
        return self.data[
            (self.data['valid_from'] >= date) &
            (self.data['valid_to'] < date)
        ]

class HabitRewards(BaseRewards):
    filename = 'habits_rewards.csv'
    template = pd.DataFrame(
        columns=[
            'name', 'type', 'target_float', 'target_str', 
            'target_bool', 'reward', 'valid_from', 'valid_to'
            ]
    )
    template = template.astype({
        'name': 'object', 
        'type' : 'datetime64[s]', 
        'float_start': 'timedelta64[s]',
        'float_end': 'Int8',
        'target_str': 'Int8',
        'target_bool': 'Int8',
        'reward': 'Int16',
        'valid_from': 'timestamp64[ns]',
        'valid_to': 'timestamp64[ns]'
    })
    template['type'] = pd.Categorical(
        template['type'],
        categories=('str', 'bool', 'float')
        )

    def __init__(self):
        super().__init__()

    def add_reward(
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
            valid_from = valid_from.replace(hour=0, minute=0, second=0, microsecond=0)
        if valid_to is None:
            valid_to = dt.date(2222, 12, 31)
        elif isinstance(valid_to, dt.datetime):
            valid_to = valid_to.replace(hour=0, minute=0, second=0, microsecond=0)
        id = len(self.data)
        self.data.loc[id, ('name', 'reward', 'valid_from', 'valid_to')] = (
            habit, reward,
            pd.to_datetime(valid_from), pd.to_datetime(valid_to))
        match target:
            case bool():
                self.data.loc[id, ('type', 'target_bool')] = \
                    ['bool', target]
            case int():
                self.data.loc[id, ('type', 'target_float')] = \
                    ['float', target]
            case float():
                self.data.loc[id, ('type', 'target_float')] = \
                    ['float', target]
            case str():
                self.data.loc[id, ('type', 'target_str')] = \
                    ['str', target]

    def drop_reward(self, name=None, valid_from=None, valid_to=None, reward=None):
        if name:
            mask_name = self.data['name'] == name
        else:
            mask_name = True
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
        mask_for_delete = ~(mask_name & mask_valid_from & mask_valid_to & mask_reward)
        self.data = self.data[mask_for_delete]

class SleepReward(BaseRewards):
    filename = 'sleep_rewards.csv'
    template = pd.DataFrame(
        columns=['time', 'kind', 'reward', 'valid_from']
    )
    template = template.astype({
        'time': 'object', 
        'kind' : 'datetime64[s]', 
        'reward': 'int16',
        'valid_from': 'timestamp64[ns]',
        'valid_to': 'timestamp64[ns]'
    })

    def __init__(self):
        super().__init__(self)
    
    def add_reward(
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
            valid_to = dt.date(2222, 12, 31)
        elif isinstance(valid_from, dt.datetime):
            valid_from = valid_from.replace(hour=0, minute=0, second=0, microsecond=0)
        elif isinstance(valid_to, dt.datetime):
            valid_to = valid_to.replace(hour=0, minute=0, second=0, microsecond=0)
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

    def drop_reward(self, time=None, 
        is_next_day=False, 
        valid_from=None, 
        valid_to=None,
        reward=None):
        if time:
            minutes_since_time = time.hour*60 + time.minute
            if is_next_day:
                minutes_since_time += 1440
            mask_name = self.data['time'] == minutes_since_time
        else:
            mask_name = True
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
        mask_for_delete = ~(mask_name & mask_valid_to & mask_valid_from & mask_reward)
        print(mask_for_delete)
        self.data = self.data[mask_for_delete]


if __name__ == '__main__':
    s = HabitRewards()
    print(s.data)
    s.add_reward('Подходы', 1, 1, dt.date(2025, 6, 1))
    s.add_reward('Общение', True, 1, dt.date(2025, 6, 1))
    s.add_reward('Подходы', 3, 3, dt.date(2025, 6, 1))
    s.push_changes()