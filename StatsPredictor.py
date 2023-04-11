import pandas as pd
import time
from Calculations import *
from DataNBA import *

ABBREV = 'MIL'
# 20 seems to be a good number
N = 20

def get_weighted_rtgs(abbrev: str, date: str = None, n: int = N):
    schedule = get_team_schedule(abbrev).iloc[::-1]
    schedule = schedule.reset_index(drop=True, inplace=False)
    idx = 0
    if date is not None:
        try:
            idx = int(schedule[schedule['Date'] == date].index[0])
        except:
            raise Exception(f'No game available on date {date}')
    # Get weighted off/def rtgs of last n games
    num = schedule.shape[0] - idx - 1
    num = n if num > n else num
    if num == 0:
        return 0, 0
    weights = [(num - i) / num for i in range(num)]
    off_rtgs = [float(row['ORtg']) for _, row in schedule.iloc[idx+1:idx+num+1].iterrows()]
    def_rtgs = [float(row['DRtg']) for _, row in schedule.iloc[idx+1:idx+num+1].iterrows()]
    weight_sum = sum(weights)
    weighted_off_rtg = sum([weights[i] * off_rtgs[i] for i in range(num)]) / weight_sum
    weighted_def_rtg = sum([weights[i] * def_rtgs[i] for i in range(num)]) / weight_sum
    return weighted_off_rtg, weighted_def_rtg

def predict_rtgs(abbrev: str, date: str = None, is_opp: bool = False):
    schedule = get_team_schedule(abbrev).iloc[::-1]
    schedule = schedule.reset_index(drop=True, inplace=False)
    idx = 0
    if date is not None:
        try:
            idx = int(schedule[schedule['Date'] == date].index[0])
        except:
            raise Exception(f'No game available on date {date}')
    # Get abbreviations, date, and home/away status of first game
    target = schedule.iloc[idx]
    is_home = target[[3]][0] != '@'
    opp_abbrev = target[[4]][0]
    [year, month, day] = date.split('-')
    # Get roster of target game
    target_roster = get_advanced_box_score(abbrev, year, month, day)
    target_roster = convert_roster(target_roster)
    # Get weighted off/def rtgs of last n games
    n = schedule.shape[0] - idx - 1
    n = N if n > N else n
    count = 0
    # Adjust influence of games based on opponent's recent performance
    opp_weights = []
    # Increase influence of games with similar rosters
    diff_weights = []
    # Increase influence of games closer to target game
    time_weights = []
    # Increase influence of games with same home/away status
    home_weights = []
    # Increase influence of games against target opponent
    bonus_weights = []
    ortgs = []
    drtgs = []
    for _, row in schedule.iloc[idx+1:].iterrows():
        curr_is_home = row[[3]][0] != '@'
        [year, month, day] = row['Date'].split('-')
        t_roster = get_advanced_box_score(abbrev, year, month, day)
        t_roster = convert_roster(t_roster)
        off_rtg = float(row['ORtg'])
        def_rtg = float(row['DRtg'])
        o_off_rtg, o_def_rtg = get_weighted_rtgs(row[[4]][0], row['Date'])
        if o_off_rtg == 0 or o_def_rtg == 0:
            opp_weight = 0.5
        else:
            opp_weight = (100 - abs(off_rtg - o_def_rtg) - abs(def_rtg - o_off_rtg))/100
        diff_weight = 60/roster_diff(target_roster, t_roster)
        time_weight = (n - count)/n
        opp_weights.append(opp_weight)
        diff_weights.append(diff_weight)
        time_weights.append(time_weight)
        home_weights.append(1 if (curr_is_home and is_home) or (not curr_is_home and not is_home) else 0)
        bonus_weights.append(1 if row[[4]][0] == opp_abbrev else 0)
        ortgs.append(off_rtg)
        drtgs.append(def_rtg)
        count += 1
        if count == n:
            break
        pass
    # Calculate weighted average
    opp_total = sum(opp_weights)
    opp_ortg = sum([opp_weights[i] * ortgs[i] for i in range(len(opp_weights))]) / opp_total
    opp_dtrg = sum([opp_weights[i] * drtgs[i] for i in range(len(opp_weights))]) / opp_total
    diff_total = sum(diff_weights)
    diff_ortg = sum([diff_weights[i]/diff_total * ortgs[i] for i in range(len(diff_weights))])
    diff_dtrg = sum([diff_weights[i]/diff_total * drtgs[i] for i in range(len(diff_weights))])
    time_total = sum(time_weights)
    time_ortg = sum([time_weights[i]/time_total * ortgs[i] for i in range(len(time_weights))])
    time_dtrg = sum([time_weights[i]/time_total * drtgs[i] for i in range(len(time_weights))])
    home_total = sum(home_weights)
    home_ortg = sum([home_weights[i]/home_total * ortgs[i] for i in range(len(home_weights))]) if home_total > 0 else 0
    home_dtrg = sum([home_weights[i]/home_total * drtgs[i] for i in range(len(home_weights))]) if home_total > 0 else 0
    bonus_total = sum(bonus_weights)
    bonus_ortg = sum([bonus_weights[i]/bonus_total * ortgs[i] for i in range(len(bonus_weights))]) if bonus_total > 0 else 0
    bonus_dtrg = sum([bonus_weights[i]/bonus_total * drtgs[i] for i in range(len(bonus_weights))]) if bonus_total > 0 else 0
    div = 5
    if home_total == 0:
        div -= 1
    if bonus_total == 0:
        div -= 1
    weighted_ortg = (opp_ortg + diff_ortg + time_ortg + home_ortg + bonus_ortg)/div
    weighted_dtrg = (opp_dtrg + diff_dtrg + time_dtrg + home_dtrg + bonus_dtrg)/div
    # Get opponent's weighted off/def rtgs
    if not is_opp:
        opp_ortg, opp_dtrg = predict_rtgs(opp_abbrev, date=date, is_opp=True)
        return weighted_ortg, weighted_dtrg, opp_ortg, opp_dtrg
    else:
        return weighted_ortg, weighted_dtrg


