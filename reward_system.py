# BUG to_csv connects row added to header and then moves to another row

import pandas as pd
import datetime as dt
import os
from config import DATA_DIR


class HabitsList:
    'class for managing habits rewards and habits_list'
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_list.csv')
        self.habits = pd.read_csv(self.path, sep=';', index_col=0)
        if self.habits.empty:
            self.habits = pd.DataFrame(columns=['unit', 'measure_kind'])
        self.habits['measure_kind'] = pd.Categorical(self.habits['measure_kind'], categories=('float', 'str', 'bool'))

    def add_habit(self, name, unit=None, measure_kind='float'):
        if any(self.habits.index == name):
            raise ValueError('The habit ' + name + ' already exists!')
        else:
            self.habits.loc[name] = [unit, measure_kind]
        return

    def drop_habit(self, name):
        self.habits = self.habits[self.habits.index != name]

    def push_changes(self):
        self.habits = self.habits.reindex()
        self.habits.to_csv(self.path, sep=';', mode='w')

class HabitRewards:

    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_rewards.csv')
        self.rewards = pd.read_csv(self.path, sep=';')
        if self.rewards.empty:
            self.rewards = pd.DataFrame(
                columns=[
                    'name', 'type', 'target_float', 'target_str', 
                    'target_bool', 'reward', 'valid_from'
                    ]
                )
        self.rewards['type'] = pd.Categorical(
            self.rewards['type'],
            categories=('str', 'bool', 'float')
            )
        self.rewards['target_bool'] = self.rewards['target_bool'].astype('boolean')
        self.rewards['valid_from'] = self.rewards['valid_from'].astype('datetime64[ns]')
        self.rewards['target_float'] = self.rewards['target_float'].astype('float64')
        self.rewards['reward'] = self.rewards['reward'].astype('int')

    def add_reward(
            self, 
            habit,
            target,
            reward,
            valid_from=None
    ):
        if valid_from is None:
            valid_from = dt.date.today()
        else:
            valid_from = valid_from.replace(hour=0, minute=0, second=0, microsecond=0)
        id = len(self.rewards)
        self.rewards.loc[id, ('name', 'reward', 'valid_from')] = (habit, pd.to_datetime(valid_from))
        match target:
            case bool():
                self.reward.loc[id, ('type', 'target_bool')] = \
                    ['bool', target]
            case int():
                self.reward.loc[id, ('type', 'target_float')] = \
                    ['float', target]
            case float():
                self.reward.loc[id, ('type', 'target_float')] = \
                    ['float', target]
            case str():
                self.reward.loc[id, ('type', 'target_str')] = \
                    ['str', target]

    def drop_reward(self, name=None, valid_from=None, reward=None):
        if name:
            mask_name = self.rewards['name'] == name
        else:
            mask_name = True
        if valid_from:
            mask_valid_from = self.rewards['valid_from'] == valid_from
        else:
            mask_valid_from = True
        if reward:
            mask_reward = self.rewards['reward'] == reward
        else:
            mask_reward = True
        mask_for_delete = ~(mask_name & mask_valid_from & mask_reward)
        print(mask_for_delete)
        self.rewards = self.rewards[mask_for_delete]

    def push_changes(self):
        self.rewards = self.rewards.reindex()
        self.rewards.to_csv(self.path, sep=';', mode='w')

class SleepReward:
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'sleep_rewards.csv')
        self.sleep_rewards = pd.read_csv(self.path, sep=';')
        if self.sleep_rewards.empty:
            self.sleep_rewards = pd.DataFrame(columns=['time', 'kind', 'reward', 'valid_from'])
        self.sleep_rewards['time'] = self.sleep_rewards['time']\
            .astype('Int32')
        self.sleep_rewards['kind'] = pd.Categorical(
            self.sleep_rewards['kind'], 
            categories=('begin', 'end')
        )
        self.sleep_rewards['reward'] = self.sleep_rewards['reward']\
            .astype('Int32')
        self.sleep_rewards['valid_from'] = self.sleep_rewards['valid_from']\
            .astype('datetime64[ns]')
    
    def add_reward(
        self,
        time: dt.time,
        kind: str, 
        reward: int, 
        valid_from=None,
        is_next_day=False
        ):
        if valid_from is None:
            valid_from = dt.date.today()
        elif isinstance(valid_from, dt.datetime):
            valid_from = valid_from.replace(hour=0, minute=0, second=0, microsecond=0)
        minutes_since_time = time.hour*60 + time.minute
        if is_next_day:
            minutes_since_time += 1440
        id = len(self.sleep_rewards)
        self.sleep_rewards.loc[id, :] = [
            minutes_since_time,
            kind,
            reward,
            valid_from
        ]

    def drop_reward(self, time=None, is_next_day=False, valid_from=None, reward=None):
        if time:
            minutes_since_time = time.hour*60 + time.minute
            if is_next_day:
                minutes_since_time += 1440
            mask_name = self.sleep_rewards['time'] == minutes_since_time
        else:
            mask_name = True
        if valid_from:
            mask_valid_from = self.sleep_rewards['valid_from'] == valid_from
        else:
            mask_valid_from = True
        if reward:
            mask_reward = self.sleep_rewards['reward'] == reward
        else:
            mask_reward = True
        mask_for_delete = ~(mask_name & mask_valid_from & mask_reward)
        print(mask_for_delete)
        self.sleep_rewards = self.sleep_rewards[mask_for_delete]

    def push_changes(self):
        self.sleep_rewards.reindex().to_csv(self.path)

if __name__ == '__main__':
    s = SleepReward()
    s.add_reward(dt.time(7, 0, 0), kind='begin', reward=2)
    s.add_reward(dt.time(7, 30, 0), kind='begin', reward=1)
    s.add_reward(dt.time(8, 0, 0), kind='begin', reward=0, valid_from=dt.date(2025, 8, 15))
    print(s.sleep_rewards)
    s.push_changes()