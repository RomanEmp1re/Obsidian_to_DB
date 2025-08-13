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
                pd.to_datetime(note.day_begin, utc=True),
                pd.to_datetime(note.day_end, utc=True),
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA
            ]
        self.data['prev_end'] = self.data['end'].shift(1)
        mask = self.data['begin'].notna() & self.data['prev_end'].notna() 
        self.data.loc[mask, 'slept'] = self.data.loc[mask, 'begin'] -\
            self.data.loc[mask, 'prev_end']
        

if __name__ == '__main__':
    d = Daysstatistics()
    print(d.data)