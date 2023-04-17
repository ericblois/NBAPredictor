import pandas as pd
import time
from Requests import *

# Converts a string of minutes and seconds to seconds
def mp_to_sec(mp: str) -> int:
    mp = mp.split(':')
    try:
        return int(mp[0]) * 60 + int(mp[1])
    except:
        return 0

def convert_roster(roster: pd.DataFrame):
    return {row[0]: row[1] for row in roster.values if len(row[1]) < 6}

# Compares seconds of difference between two rosters (dict of player: time, ex. "Lebron James": "36:00")
def roster_diff(roster1: dict[str: str], roster2: dict[str: str]):
    r1 = roster1.copy()
    r2 = roster2.copy()
    sec_diff = 0
    for player, time in r1.items():
        try:
            time2 = r2[player]
            sec_diff += abs(mp_to_sec(time) - mp_to_sec(time2))
            del r2[player]
        except:
            sec_diff += mp_to_sec(time)
    for time in r2.values():
        sec_diff += mp_to_sec(time)
    return sec_diff
