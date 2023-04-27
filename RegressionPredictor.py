from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from DataNBA import *
''' Get weighted stats of last n games before date '''
def get_weighted_stats(team: str, date: str, n = 100):
    schedule = get_team_schedule(team)
    schedule = schedule.reset_index(drop=True, inplace=False)
    try:
        idx = int(schedule[schedule['Date'] == date].index[0])
    except:
        raise Exception(f'No game available on date {date}')
    num_prev_games = min(idx, n)
    if num_prev_games == 0:
        raise Exception(f'No games available before date: {date}')
    # Get sum of weights (weights are 1, 2, ..., num_prev_games)
    weight_sum = (num_prev_games * (num_prev_games + 1)) / 2
    w_stats = []
    # Get weighted stats of last n games
    for i in [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27]:
        stats = schedule.iloc[idx - num_prev_games:idx, [i]].values
        w_stat = (sum([stats[i - 1] * i for i in range(1, num_prev_games + 1)])/weight_sum)[0]
        w_stats.append(w_stat)
    '''ortgs = schedule.iloc[idx - num_prev_games:idx]['ORtg'].values
    w_ortg = sum([ortgs[i - 1] * i for i in range(1, num_prev_games + 1)])/weight_sum
    drtgs = schedule.iloc[idx - num_prev_games:idx]['DRtg'].values
    w_dtrg = sum([drtgs[i - 1] * i for i in range(1, num_prev_games + 1)])/weight_sum
    '''
    return w_stats

def train_historical():
    x, y = [], []
    load_game_logs()
    for team in GAME_LOGS.keys():
        # Prepare data
        sched = GAME_LOGS[team]
        for i, row in sched.iterrows():
            if i == 0:
                continue
            stats = get_weighted_stats(team, row['Date'])
            try:
                opp_stats = get_weighted_stats(row['Opp'], row['Date'])
            except:
                continue
            stats.extend(opp_stats)
            # Add home field advantage
            stats.append(int(row.values[3] != '@'))
            # Add result
            did_win = int(row.values[5] == 'W')
            #point_ratio = float(row.values[6]) / float(row.values[7])
            #points_scored = int(row.values[6])
            x.append(stats)
            y.append(did_win)
            #y.append(point_ratio)
            #y.append(points_scored)
            pass
    # Split data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0, shuffle=True)
    model = LogisticRegression()
    model.fit(x_train, y_train)
    y_out = model.predict(x_test)
    accuracies = [y_test[i] - y_out[i] for i in range(len(y_test))]
    print(y_out[:20].tolist())
    print(y_test[:20])
    print(f'Average prediction diff: {sum(map(abs, accuracies))/len(accuracies)}')
    pass

train_historical()