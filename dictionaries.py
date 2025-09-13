# module for managing with data

import datetime as dt
import os
from config import DATA_DIR
import pandas as pd
from register import BaseStatistics

class Habit:
    def __init__(
            self, 
            name:str, 
            target,
            unit:str='',
            reward:int=1, 
            is_negative=False,
            valid_from:dt.date=None
            ):
        if not isinstance(name, str):
            raise TypeError('"name" argument must be str type')
        if not isinstance(reward, (int, float)):
            raise TypeError('"reward argument must be int or float type')
        if not isinstance(is_negative, bool):
            raise TypeError('"is_negative" argument must be boolean type')
        self.name = name
        self.reward = reward
        self.is_negative = is_negative
        self.target = target
        self.valid_from = self.validate_date(valid_from, dt.date.today())
        self.unit = unit
        self.pd_row = pd.DataFrame({
            'name': [self.name],
            'reward': [self.reward],
            'is_negative': [self.is_negative],
            'target': [self.target],
            'valid_from': [self.valid_from],
            'unit': [self.unit]
        })
        self.pd_row['unit'] = self.pd_row['unit'].astype('object')


    @staticmethod
    def validate_date(date, if_none=None):
        if date is None:
            return if_none
        if isinstance(date, dt.datetime):
            return date.date()
        elif isinstance(date, str):
            try:
                return dt.date.fromisoformat(date)
            except:
                raise ValueError('str date must be isoformat')
        elif isinstance(date, (int, float)):
            try:
                return dt.date.fromtimestamp(date)
            except:
                raise ValueError('int date must be timestamp with correct value')
        elif isinstance(date, dt.date):
            return date
        else:
            raise TypeError(
                'date must be datetime.date, datetime.datetime, representi'
                'ng str with isoformat or representing timestamp')
                
    @staticmethod
    def validate_time(time, if_none=None):
        if time is None:
            return if_none
        if isinstance(time, dt.time):
            return time
        elif isinstance(time, dt.datetime):
            return time.time()
        elif isinstance(time, (float, int)):
            return dt.datetime.fromtimestamp(time).time()
        elif isinstance(time, str):
            try:
                return dt.time.fromisoformat(str)
            except:
                raise ValueError('Time str must be isoformat')
        else:
            raise TypeError(
                'time must be datetime.time, datetime.datetie representing'
                    'timestamp int/float or str (isoformat)')

class NumericHabit(Habit):
    def __init__(
            self, 
            name:str, 
            target:float,
            unit:str='minutes',
            reward:int=1, 
            is_negative:bool=False,
            valid_from:dt.date=None):
        if not isinstance(target, (int, float)):
            raise TypeError('"target" argument must be a number')
        target = str(target)
        super().__init__(name, target, unit, reward, is_negative, valid_from)

    def __str__(self):
        return (
            f'{self.name}\ntarget : '
            f'{'less than ' if self.is_negative else 'greater than '}'
            f'{self.target} {self.unit}\nreward : {self.reward}'
        )

class BooleanHabit(Habit):
    def __init__(
        self,
        name:str,
        target:bool=True,
        unit:str='',
        reward:int=1,
        is_negative:bool=False,
        valid_from:dt.date=None
        ):
        if not isinstance(target, bool):
            raise TypeError('"target" argument must be bool type')
        target = str(target)
        super().__init__(name, target, unit, reward, is_negative, valid_from)

    def __str__(self):
        return (
            f'{self.name}\ntarget : {'not' if self.is_negative else ''} '
            f'{'completed' if self.target else 'missed'}'
            f'\nreward : {self.reward}'
        )


class TimeHabit(Habit):
    def __init__(
        self,
        name:str,
        target:int,
        unit:str='minutes from the beginning of the day',
        reward:int=1,
        is_negative:bool=False,
        valid_from:dt.date=None
    ):
        if not isinstance(target, int):
            raise TypeError('"target" argument must be a number')
        self.time_str = dt.time(target//60, target%60)
        target = str(target)
        super().__init__(name, target, unit, reward, is_negative, valid_from)

    def __str__(self):
        return (
            f'{self.name}\ntarget : '
            f'{'earlier than' if self.is_negative else 'later than'} '
            f'{self.time_str}\nreward : {self.reward}'
        )


class RegisterRules(BaseStatistics):
    filename = 'habits_rules.csv'
    template = pd.DataFrame(
        columns = [
            'name',
            'reward',
            'is_negative',
            'target',
            'valid_from',
            'unit'
        ]
    )
    def __init__(self):
        self.path = os.path.join(DATA_DIR, self.filename)
        if not os.path.exists(self.path):
            self.template.to_csv(self.path, sep=';')
            self.data = self.template.copy()
        else:
            self.data = self.load_from_csv()
        
    def update(self, habit:Habit):
        # inserts new habit row into datafrane. Replaces old if valid_from and name already in it
        self.data = self.data[~(
            (self.data['name'] == habit.name)&
            (self.data['valid_from'] == habit.valid_from))]
        self.data = pd.concat((self.data, habit.pd_row), ignore_index=True)

    def get_actual_rules(self, as_of_date:dt.date=None):
        as_of_date = Habit.validate_date(as_of_date, if_none=dt.date.today())
        indexes = self.data[self.data['valid_from'] <= as_of_date]\
            .groupby('name')['valid_from']\
            .idxmax()
        return self.data.loc[indexes]

    def push_to_csv(self):
        self.data\
            .sort_values(by='valid_from')\
            .reset_index(drop=True)\
            .to_csv(self.path, sep=';')


if __name__ == '__main__':
    hs = (
        NumericHabit('self education', 60, unit='minutes'),
        TimeHabit('wake up', 330, valid_from=dt.date(2026, 1, 1)),
        BooleanHabit('meditation'),
        NumericHabit('hobby', 30, valid_from=dt.date(2021, 12, 11)),
        NumericHabit('hobby', 40),
        NumericHabit('hobby', 40, valid_from=dt.date(2011, 7, 3))
    )
    stat = RegisterRules()
    for h in hs:
        stat.update(h)
    print(stat.data)
    stat.push_to_csv()