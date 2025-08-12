import pandas as pd
import datetime as dt
import obsidian


class Daysstatistics:
    def __init__(self):
        self.dates = obsidian.DailyNote.get_daily_notes_list()
        self.data = pd.DataFrame(
            columns=[
                'begin', 
                'end', 
                'slept', 
                'reward', 
                'fine', 
                'total', 
                'balance', 
                'spent'
            ],
            index = self.dates
        )
        self.data = self.data.astype({
            'begin': 'datetime64[s]', 
            'end' : 'datetime64[s]', 
            'slept': 'timedelta64[s]',
            'reward': 'Int8',
            'fine': 'Int8',
            'total': 'Int8',
            'balance': 'Int16',
            'spent': 'Int8'
        })
        for date in self.dates:
            note = obsidian.DailyNote(date)
            self.data.loc[date] = [
                pd.to_datetime(note.day_begin),
                pd.to_datetime(note.day_end),
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA
            ]
        # self.data.slept = self.data['begin'] - self.data['end'].shift(1)

if __name__ == '__main__':
    d = Daysstatistics()
    print(d.data)