
# here some trash i deleted from code to use it bin future probably
class DaysStatistics(BaseStatistics):
    # class for working with daystatistics
    template = pd.DataFrame(
        columns = []
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
    filename = 'days.csv'

    def __init__(self):
        super().__init__()

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
    
    def calc_reward_for_date(self, date=None):
        self.sleep_rewards = SleepReward()
        if date is None:
            date = max(self.dates)
        note = o.DailyNote(date)
        actual_rewards = self.sleep_rewards.data[
            self.sleep_rewards.data['valid_from'] >= date
            ]
        print(actual_rewards)
