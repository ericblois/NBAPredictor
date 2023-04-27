import pandas as pd
import time

from sklearn.model_selection import train_test_split
from Calculations import *
from DataNBA import *
from sklearn.linear_model import LinearRegression
import numpy as np

'''
Steps:
1. Get weighted stats based on roster similarity, time, and opponent for team and opponent
2. Get most important stats that determine outcome of game
3. Use stat weightings with team weightings to predict outcome of game

'''

STATS_N = 10

def train_score_model():
    load_game_logs()
    # Get all game logs (only include relevant stats)
    all_game_logs = pd.concat(GAME_LOGS.values()).iloc[:, [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27]]
    # Get all scores
    all_scores = pd.concat(GAME_LOGS.values()).iloc[:, [6, 7]]
    # Convert dataframes to numpy arrays
    all_game_logs = all_game_logs.values
    all_scores = all_scores.values
    # Split data 
    x_train, x_test, y_train, y_test = train_test_split(all_game_logs, all_scores, test_size=0.2, random_state=0, shuffle=True)
    # Train model
    model = LinearRegression()
    model.fit(x_train, y_train)
    '''
    # Predict
    y_out = model.predict(x_test)
    # Print results
    for i in range(len(y_out)):
        print(f'Predicted: {y_out[i]} Actual: {y_test[i]}')
    team_acc = sum([y_out[i][0] - y_test[i][0] for i in range(len(y_out))])/len(y_out)
    opp_acc = sum([y_out[i][1] - y_test[i][1] for i in range(len(y_out))])/len(y_out)
    print(f'Team accuracy: {team_acc} Opponent accuracy: {opp_acc}')
    '''
    return model


def train_stats_model(n: int):
    load_adv_box_scores()
    # Get all game logs (only include relevant stats)
    all_game_logs = pd.concat(GAME_LOGS.values())
    x, y = [], []
    teams = list(GAME_LOGS.keys())
    team_count = 0
    curr_team = None
    for i, row in all_game_logs.iterrows():
        # Keep track of team
        if i == 0:
            curr_team = teams[team_count]
            team_count += 1
            continue
        elif i < n:
            continue
        # Get roster
        date = row['Date']
        [year, month, day] = date.split('-')
        roster = get_advanced_box_score(curr_team, year, month, day)
        roster = convert_roster(roster)
        all_stats = []
        # Get previous 10 games
        for j in range(n):
            prev_game = all_game_logs.iloc[(82*(team_count-1)) + i-j-1]
            prev_date = prev_game['Date']
            [prev_y, prev_m, prev_d] = prev_date.split('-')
            prev_roster = get_advanced_box_score(curr_team, prev_y, prev_m, prev_d)
            prev_roster = convert_roster(prev_roster)
            # Get roster difference
            r_diff = 20400 - roster_diff(roster, prev_roster)
            stats = prev_game.iloc[[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27]].values
            # Append r_diff to stats
            stats = np.append(stats, r_diff)
            '''# Append num of games back to stats
            stats = np.append(stats, j+1)'''
            # Append to all stats
            all_stats.extend(stats)
        x.append(all_stats)
        y.append(row.iloc[[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27]].values)
        pass
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0, shuffle=True)
    # Train model
    model = LinearRegression()
    model.fit(x_train, y_train)
    # Predict
    y_out = model.predict(x_test)
    # Print results
    for i in range(len(y_out)):
        print(f'Predicted: {y_out[i]}\nActual: {y_test[i]}')
    return model

def get_stats_model_input(team: str, date: str, n: int):
    schedule = get_team_schedule(team)
    try:
        idx = int(schedule[schedule['Date'] == date].index[0])
    except:
        raise Exception(f'No game available on date {date}')
    # Get roster
    [year, month, day] = date.split('-')
    roster = get_advanced_box_score(team, year, month, day)
    roster = convert_roster(roster)
    all_stats = []
    # Get previous 10 games
    for j in range(n):
        prev_game = schedule.iloc[idx-j-1]
        prev_date = prev_game['Date']
        [prev_y, prev_m, prev_d] = prev_date.split('-')
        prev_roster = get_advanced_box_score(team, prev_y, prev_m, prev_d)
        prev_roster = convert_roster(prev_roster)
        # Get roster difference
        r_diff = 20400 - roster_diff(roster, prev_roster)
        stats = prev_game.iloc[[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27]].values
        # Append r_diff to stats
        stats = np.append(stats, r_diff)
        '''# Append num of games back to stats
        stats = np.append(stats, j+1)'''
        # Append to all stats
        all_stats.extend(stats)
    return all_stats


#train_score_model()

def predict_stats_from_roster(team: str, date: str):
    schedule = get_team_schedule(team)
    try:
        idx = int(schedule[schedule['Date'] == date].index[0])
    except:
        raise Exception(f'No game available on date {date}')
    [year, month, day] = date.split('-')
    target_roster = get_advanced_box_score(team, year, month, day)
    target_roster = convert_roster(target_roster)
    schedule = schedule.iloc[:idx]
    roster_diff_total = 0
    w_stats = None
    for i, row in schedule.iterrows():
        # Get advanced box score
        [year, month, day] = row['Date'].split('-')
        roster = get_advanced_box_score(team, year, month, day)
        roster = convert_roster(roster)
        # Get roster difference
        r_diff = 20400 - roster_diff(target_roster, roster)
        stats = row.iloc[[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27]]
        if w_stats is None:
            w_stats = r_diff * stats
        else:
            w_stats += r_diff * stats
        roster_diff_total += r_diff
    w_stats /= roster_diff_total
    # Add roster differences to schedule
    return w_stats

#predict_stats_from_roster('TOR', '2023-03-02')

score_model = train_score_model()
stats_model = train_stats_model(STATS_N)
#get_stats_model_input('TOR', '2023-03-02', STATS_N)

def predict_score(team: str, date: str):
    # Get weighted stats based on roster similarity
    #team_stats = predict_stats_from_roster(team, date)
    stats_input = get_stats_model_input(team, date, STATS_N)
    team_stats = stats_model.predict([stats_input])[0]
    pred = score_model.predict([team_stats])
    # Get actual score
    schedule = get_team_schedule(team)
    game_stats = schedule[schedule['Date'] == date]
    actual = game_stats.iloc[:, [6, 7]].values.tolist()
    print(f'Predicted: {pred} Actual: {actual}')
    pass

# --- NEED TO TAKE INTO ACCOUNT OTHER TEAM'S STATS --- #

predict_score('TOR', '2023-03-02')
predict_score('TOR', '2023-03-04')
predict_score('TOR', '2023-03-06')
predict_score('TOR', '2023-03-08')
predict_score('TOR', '2023-03-10')