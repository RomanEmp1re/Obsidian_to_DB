# BUG to_csv connects row added to header and then moves to another row

import pandas as pd
import datetime as dt
import os
from config import DATA_DIR


class HabitsList:
    'class for managing habits rewards and habits_list'
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_list')
        self.habits = pd.read_csv(self.path, sep=';', index_col=0)
        self.habits['measure_kind'] = pd.Categorical(self.habits['measure_kind'], categories=('float', 'str', 'bool'))

    def add_habit(self, name, unit, measure_kind):
        if any(self.habits.index == name):
            raise ValueError('The habit ' + name + ' already exists!')
        else:
            self.habits.loc[name] = [unit, measure_kind]
        return

    def drop_habit(self, name):
        self.habits = self.habits[self.habits['name'] != name]

class HabitRewards:

    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_rewards.csv')
        self.rewards = pd.read_csv(self.path, sep=';')
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
            valid_from = dt.date.today()
    ):
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
        h.rewards.reset_index()
        h.rewards.to_csv(self.path, sep=';', mode='w')


if __name__ == '__main__':
    h = HabitRewards()
    h.push_changes()