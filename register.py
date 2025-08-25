# register.py

import pandas as pd
import datetime as dt
import obsidian as o
import os
from config import DATA_DIR
from reward_system import HabitRewards


class Daysstatistics:
    '''class for working with daystatistics
'''
    template = pd.DataFrame(
        columns=[
            'begin', 
            'end', 
            'slept', 
            'reward', 
            'fine', 
            'total', 
            'balance', 
            'spent'
        ]
    )
    template = template.astype({
        'begin': 'datetime64[s]', 
        'end' : 'datetime64[s]', 
        'slept': 'timedelta64[s]',
        'reward': 'Int8',
        'fine': 'Int8',
        'total': 'Int8',
        'balance': 'Int16',
        'spent': 'Int8'
    })

    def __init__(self):
        self.dates = o.DailyNote.get_daily_notes_list()
        self.path = os.path.join(DATA_DIR, 'days.csv')
        self.data = self.template.copy()
        if not os.path.exists(self.path):
            self.data.to_csv(self.path, sep=';')

    def load_from_csv(self):
        self.data = pd.read_csv(self.path, sep=';')

    def push_to_csv(self):
        self.data.sort_index(axis=0, inplace=True)
        self.data.to_csv(self.path, sep=';')

    def load_note(self, date=None):
        # loads note to current DataFrame by means of DailyNote
        # if date argument is None, loads note for current_date
        if date is None:
            date = max(self.dates)
        note = o.DailyNote(date)
        self.data.loc[date] = (
            pd.to_datetime(note.day_begin, utc=True),
            pd.to_datetime(note.day_end, utc=True),
            pd.to_timedelta(note.slept),
            pd.NA,
            pd.NA,
            pd.NA,
            pd.NA,
            pd.NA
        )

class TaskStatistics(Daysstatistics):
    template = pd.DataFrame(
        columns=(
            'date',
            'name',
            'is_done',
            'reward'
        )
    )
    template = template.astype({
        'date': 'datetime64[s]',
        'name': 'object',
        'is_done': 'bool',
        'reward': 'Int32'
    })
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'tasks.csv')
        self.data = self.template.copy()
        self.dates = o.DailyNote.get_daily_notes_list()
        if not os.path.exists(self.path):
            self.data.to_csv(self.path, sep=';')

    def load_note(self, date=None):
        if date is None:
            date = dt.date.today()
        note = o.DailyNote(date)
        for t in note.tasks_list:
            id = len(self.data)
            self.data.loc[id] = ({
                'date': date,
                'name': t.name,
                'is_done': t.is_done,
                'reward': t.reward}
            )

class HabitsStatistics(Daysstatistics):
    template = pd.DataFrame(
        columns=(
            'date',
            'name',
            'reward',
            'result_float',
            'result_str',
            'result_bool'
        )
    )
    template = template.astype({
        'date': 'datetime64[s]',
        'name': 'object',
        'reward': 'Int32',
        'result_float': 'float64',
        'result_str': 'object',
        'result_bool': 'bool'
    })
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits.csv')
        self.data = self.template.copy()
        self.dates = o.DailyNote.get_daily_notes_list()
        if not os.path.exists(self.path):
            self.data.to_csv(self.path, sep=';')

    def load_note(self, date=None):
        if date is None:
            date = max(self.dates)
        self.dates = o.DailyNote.get_daily_notes_list()
        note = o.DailyNote(date)
        rewards = HabitRewards().data
        habits_from_rewards = set(rewards['name'])
        print([[note.name, note.value] for note in note.habits_list])
        print(habits_from_rewards)
        for h in note.habits_list:
            if h.name in (habits_from_rewards):
                if isinstance(h.value, bool):
                    reward = rewards[
                        (rewards['type'] == 'bool') &
                        (rewards['target_bool'] == h.value) &
                        (rewards['name'] == h.name)
                    ]
                elif isinstance(h.value, float) or isinstance(h.value, int):
                    reward = rewards[
                        (rewards['type'] == 'float') &
                        (rewards['target_float'] <= h.value) &
                        (rewards['name'] == h.name)
                    ]
                elif isinstance(h.value, str):
                    reward = rewards[
                        (rewards['type'] == 'str') &
                        (rewards['target_str'] <= h.value) &
                        (rewards['name'] == h.name)
                    ]
                else:
                    continue
                if len(reward) > 0:
                    id = len(self.data)
                    max_reward = max(reward['reward'])
                    print(reward)
                    self.data.loc[id, [
                        'date', 
                        'name', 
                        'reward', 
                        'result_float',
                        'result_str',
                        'result_bool'
                        ]
                    ] = [
                        date,
                        h.name,
                        max_reward,
                        max(reward[reward['reward']==max_reward]['target_float']),
                        max(reward[reward['reward']==max_reward]['target_str']),
                        max(reward[reward['reward']==max_reward]['target_bool']),
                    ]
                    print(reward)

                    

if __name__ == '__main__':
    d = HabitsStatistics()
    d.load_note()
    print(d.data)
    # d.push_to_csv()