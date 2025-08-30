# register.py
# saves habits, tasks and days into csv files

import pandas as pd
import datetime as dt
import obsidian as o
from obsidian import FileFormatError
import os
from config import DATA_DIR


class BaseStatistics:
    template: pd.DataFrame = None
    filename: str = None

    def __init__(self):
        self.path = os.path.join(DATA_DIR, self.filename)
        if not os.path.exists(self.path):
            self.template.to_csv(self.path, sep=';')
            self.data = self.template.copy()
        else:
            self.data = self.load_from_csv()
        self.dates = o.DailyNote.get_daily_notes_list()

    def load_from_csv(self):
        data = pd.read_csv(self.path, sep=';', index_col=0)
        return data.astype(self.template.dtypes.to_dict())

    def push_to_csv(self):
        self.data\
            .sort_values(by='date')\
            .reset_index(drop=True)\
            .to_csv(self.path, sep=';')

    @property
    def dates_loaded(self):
        return self.data['date']

class TaskStatistics(BaseStatistics):
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
    filename = 'tasks.csv'

    def __init__(self):
        super().__init__()

    def load_note(self, date=None):
        if date is None:
            date = max(self.dates)
        note = o.DailyNote(date)
        if pd.to_datetime(date) in self.dates_loaded.values:
            self.data = self.data[self.data['date'] != pd.to_datetime(date)]
        for t in note.tasks_list:
            inserted_index = max(self.data.index) + 1
            self.data.loc[inserted_index] = ({
                'date': dt.datetime.combine(date, dt.time(0, 0, 0)),
                'name': t.name,
                'is_done': t.is_done,
                'reward': t.reward}
            )


class HabitsStatistics(BaseStatistics):
    template = pd.DataFrame(
        columns=(
            'date',
            'name',
            'type',
            'result'
        )
    )
    template = template.astype({
        'date': 'datetime64[s]',
        'name': 'object',
        'type': 'object',
        'result': 'object'
    })
    template['type'] = pd.Categorical(
        template['result'],
        categories=('float', 'bool', 'str', 'datetime')
    )
    filename = 'habits.csv'

    def __init__(self):
        super().__init__()

    def load_note(self, date=None):
        note = o.DailyNote(date if date else max(self.dates))
        for h in note.habits_list:
            inserted_id = len(self.data.index)
            if isinstance(h.value, bool):
                self.data.loc[inserted_id, ['date', 'name', 'type', 'result']]\
                    = [date, h.name, 'bool', str(h.value)]
            elif isinstance(h.value, (float, int)):
                self.data.loc[inserted_id, ['date', 'name', 'type', 'result']]\
                    = [date, h.name, 'float', str(h.value)]
            elif isinstance(h.value, str):
                self.data.loc[inserted_id, ['date', 'name', 'type', 'result']]\
                    = [date, h.name, 'float', str(h.value)]
            elif isinstance(h.value, dt.datetime):
                self.data.loc[inserted_id, ['date', 'name', 'type', 'result']]\
                    = [date, h.name, 'datetime', str(h.value)]
            else:
                continue

if __name__ == '__main__':
    tasks = TaskStatistics()
    for i in tasks.dates:
        tasks.load_note(i)
    tasks.push_to_csv()