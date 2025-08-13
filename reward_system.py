import pandas as pd
import datetime as dt
import os
from config import DATA_DIR


class HabitsList:
    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_list')

class HabitRewards:

    def __init__(self):
        self.path = os.path.join(DATA_DIR, 'habits_rewards.csv')
        self.rewards = pd.read_csv(DATA_DIR)

    def add_reward(
            self, 
            habit,
            min_value,
            max_value,
            valid_from = dt.date.today()
    ):
        self.rewards.concat({
            'habit' : habit,
            'min_value' : min_value,
            'max_value' : max_value,
            'valid_from' : valid_from
        })