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

    def drop(
        self,
        id:int=None,
        name:str=None,
        date:dt.date=None,
        intersect=True
    ):
        if id is None and name is None and date is None:
            self.data = self.template
            return
        if id is not None:
            if not isinstance(id, int):
                raise TypeError('id argument must be int type')
            else:
                mask_id = self.data.index != id
        else:
            mask_id = True
        if name is not None:
            if not isinstance(name, str):
                raise TypeError('name argument must be str type')
            else:
                mask_name = self.data['name'] != name
        else:
            mask_name = True
        if date is not None:
            if not isinstance(name, dt.date):
                raise TypeError('name argument must be date type')
            else:
                mask_date = self.data['name'] != pd.to_datetime(date)
        else:
            mask_date = True
        if intersect:
            self.data = self.data[(mask_id & mask_date & mask_name)]
        else:
            self.data = self.data[(mask_id | mask_date | mask_name)]

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
            if len(self.data.index) != 0:
                inserted_index = max(self.data.index) + 1
            else:
                inserted_index = 0
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
        note = o.DailyNote(date)
        if pd.to_datetime(date) in self.dates_loaded.values:
            self.data = self.data[self.data['date'] != pd.to_datetime(date)]
        note = o.DailyNote(date if date else max(self.dates))
        for h in note.habits_list:
            inserted_id = max(self.data.index) + 1
            if isinstance(h.value, bool):
                inserted_type = 'bool'
            elif isinstance(h.value, (float, int)):
                inserted_type = 'float'
            elif isinstance(h.value, str):
                inserted_type = 'str'
            elif isinstance(h.value, dt.datetime):
                inserted_type = 'datetime'
            else:
                continue
            self.data.loc[inserted_id, ['date', 'name', 'type', 'result']] =\
                [date, h.name, inserted_type, str(h.value)]

if __name__ == '__main__':
    t = TaskStatistics()
    for i in range(1, 10):
        t.load_note(dt.date(2025, 8, i))
    t.push_to_csv()