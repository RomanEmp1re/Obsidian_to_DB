# module for managing with data

import datetime as dt
import os
from config import DATA_DIR
import json
import re

class Habit:
    def __init__(
            self, 
            name:str, 
            target,
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

    def to_dict(self):
        return {
            self.name: {
                    self.valid_from: {
                        'target': self.target,
                        'reward': self.reward,
                        'is_negative': self.is_negative
                    }
                }
            }

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
            unit:str,
            reward:int=1, 
            is_negative:bool=False,
            valid_from:dt.date=None):
        if not isinstance(target, (int, float)):
            raise TypeError('"target" argument must be a number')
        super().__init__(name, target, reward, is_negative, valid_from)
        self.unit = unit

    def to_dict(self):
        result = super().to_dict()
        result[self.name][self.valid_from]['unit'] = self.unit
        return result

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
        reward:int=1,
        is_negative:bool=False,
        valid_from:dt.date=None
        ):
        if not isinstance(target, bool):
            raise TypeError('"target" argument must be bool type')
        super().__init__(name, target, reward, is_negative, valid_from)

    def __str__(self):
        return (
            f'{self.name}\ntarget : {'not' if self.is_negative else ''} '
            f'{'completed' if self.target else 'missed'}'
            f'\nreward : {self.reward}'
        )

class StrListHabit(Habit):
    def __init__(
        self,
        name:str,
        target:list,
        reward:list,
        is_negative:bool=False,
        valid_from:dt.date=None
    ):
        if (
            not isinstance(target, (list, tuple)) 
            or any([not isinstance(i, str) for i in target])
        ):
            raise TypeError('"target" argument must be list/tuple of str')
        if (
            not isinstance(reward, (list, tuple)) 
            or any([not isinstance(i, (int, float)) for i in reward])
        ):
            raise TypeError('"reward" argument must be list/tuple of int')
        if len(target) != len(reward):
            raise ValueError('"reward" and "target" arguments must be list or\
                              tuple with same length')
        if not isinstance(name, str):
            raise TypeError('"name" argument must be str type')
        if not isinstance(is_negative, bool):
            raise TypeError('"is_negative" argument must be boolean type')
        self.name = name
        self.reward = reward
        self.is_negative = is_negative
        self.target = target
        self.valid_from = super().validate_date(valid_from, dt.date.today())
        self.rewards_dict = dict(zip(self.target, self.reward))

    def __str__(self):
        return f'{self.name}\ntargets : \n{'\n'.join(
            '  ' + k + ' - ' + str(i)
            for k, i in self.rewards_dict.items())}'


class TimeHabit(Habit):
    def __init__(
        self,
        name:str,
        target:dt.time,
        reward:int,
        is_negative:bool=False,
        valid_from:dt.date=None
    ):
        super().__init__(name, target, reward, is_negative, valid_from)
        self.target = super().validate_time(target)
        self.time_str = self.target.isoformat()
        self.target = self.target.hour*60 + self.target.minute

    def to_dict(self):
        result = super().to_dict()
        result[self.name][self.valid_from]['unit'] =\
            'minutes from the beggining of the day'
        return result

    def __str__(self):
        return (
            f'{self.name}\ntarget : '
            f'{'earlier than' if self.is_negative else 'later than'} '
            f'{self.time_str}\nreward : {self.reward}'
        )

class ManageJson:
    def __init__(self):
        self.path=os.path.join(DATA_DIR, 'habits.json')
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
        with open (self.path, 'r') as f:
            self.data = json.load(f, object_hook=self.parse_date)

    @staticmethod
    def parse_date(data):
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                try:
                    result[k] = dt.date.fromisoformat(v)
                except ValueError:
                    result[k] = v
            elif isinstance (k, str):
                try:
                    result[dt.date.fromisoformat(k)] = v
                except ValueError:
                    result[k] = v
            else:
                result[k] = v
        return result

    def update(self, habit:Habit):
        self.data.update(habit.to_dict())

    def remove(self, habit, valid_from=None):
        if valid_from is None:
            del self.data[habit]
        if valid_from is not None:
            del self.data[habit][valid_from.isoformat()]

    def dump(self):
        for habit, targets in self.data.items():
            converted_habit = {}
            for valid_from, val in targets.items():
                if isinstance(val['target'], str):
                    if re.match(
                        r'^([0-1][0-9]|2[0-3]):[0-5][0-9].*', 
                        val['target']):
                        val['target'] = val['target'].isoformat()
                converted_habit.update({valid_from.isoformat(): val})
            self.data[habit] = converted_habit
        f = open(self.path, 'w')
        json.dump(self.data, f)
        f.close()

    def get_actual_rules(self, date=dt.date(2025, 9, 2)):
        Habit.validate_date(date, dt.date.today())
        actual_date = dt.date.today()
        result = {}
        for habit, rules in self.data.items():
            if len(rules) > 1:
                for d, r in rules:
                    actual_rules = {k : v for k, v in rules.items() if k >= actual_date}
                    latest_rule = max(actual_rules.keys())
                    result.update({habit:rules[latest_rule]})
            else:
                result.update({habit:rules})
        return result


if __name__ == '__main__':
    new_habit1 = NumericHabit(
        name='reading',
        target=30, 
        unit='minutes',
        valid_from=dt.date(2025, 9, 10))
    new_habit2 = NumericHabit(
        name='self-education', 
        target=60, 
        unit='minutes',
        is_negative=False, 
        valid_from=dt.date(2025, 9, 10))
    new_habit3 = BooleanHabit(
        name='Morning exercises',
        valid_from=dt.date(2025, 9, 10))
    new_habit4 = TimeHabit(
        name='Wake up',
        target=dt.time(5, 30),
        reward=1,
        valid_from=dt.date(2021, 1, 1)
    )
    a = ManageJson()
    print(a.data)
    a.update(new_habit1)
    a.update(new_habit2)
    a.update(new_habit3)
    a.update(new_habit4)
    a.dump()
    print(a.get_actual_rules())