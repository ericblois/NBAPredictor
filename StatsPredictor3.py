import math
import pandas as pd
import time

from sklearn.model_selection import train_test_split
from Calculations import *
from DataNBA import *
from sklearn.linear_model import LinearRegression
import numpy as np


def find_important_stats(team: str, date: str, n = 8):
    ''' Get n stats that are most correlated with the final score of the game, for a certain team before a date '''
    # Get schedule for specific team
    sched = get_team_schedule(team).copy()

    try:
        idx = int(sched[sched['Date'] == date].index[0])
        sched = sched.iloc[:idx]
    except:
        # Use entire schedule if date is not found
        print(f'No game available on date {date} for team {team}')
        pass
    # Format columns
    sched.iloc[:, [3]] = sched.iloc[:, [3]].apply(lambda x: x != '@')
    sched.iloc[:, [5]] = sched.iloc[:, [5]].apply(lambda x: x == 'W')
    sched.drop(['Date', 'Opp'], axis=1, inplace=True)
    # Get correlations between all stats
    corrs = sched.corr().abs().values.flatten()
    labels = []
    last = ()
    for i in range(len(corrs)):
        index = np.argmax(corrs)
        val = corrs[index]
        # Check if value is 1.0 or nan
        if val == 1.0 or math.isnan(val):
            corrs[index] = 0
            continue
        label1 = sched.columns[math.floor(index / sched.shape[1])]
        label2 = sched.columns[index % sched.shape[1]]
        # Check if labels are the same as a previous pair
        if label1 in last or label2 in last:
            corrs[index] = 0
            continue
        labels.append((label1, label2, val))
        last = (label1, label2)
        corrs[index] = 0

    # Find top 10 stats that are correlated with Tm or Opp.1
    stat_labels = ['Pace']
    i = 0
    while len(stat_labels) < n:
        label = labels[i]
        if label[0] in ['Tm', 'Opp.1'] and label[1] not in ['Tm', 'Opp.1'] and label[1] not in stat_labels:
            stat_labels.append(label[1])
        i += 1
    return stat_labels


def predict_stats_from_adv(team: str, date: str = None, n = 5):
    sched = get_team_schedule(team).copy()
    opp = sched.iloc[-1]['Opp']
    try:
        idx = int(sched[sched['Date'] == date].index[0])
        sched = sched.iloc[:idx]
    except:
        # Use entire sched if date is not found
        print(f'No game available on date {date} for team {team}')
        pass

    # Get important stats
    stat_labels = find_important_stats(team, date)
    # Add a new column for each stat, which is the stat divided by the average of the last 10 games
    for label in stat_labels:
        # Get column
        col = sched[label].values
        new_col = [np.mean(col[max(i-(n + 1), 0):max(i-1, 1)]) for i in range(len(col))]
        sched[f"{label}_1"] = new_col
    # Do the same for each opponent in the schedule
    new_cols = {f"{label}_2": [] for label in stat_labels}
    for i, opp in enumerate(sched['Opp']):
        o_sched = get_team_schedule(opp).copy()
        o_date = sched.iloc[i]['Date']
        #row = o_sched.iloc[-1]
        try:
            idx = int(o_sched[o_sched['Date'] == o_date].index[0])
            #row = o_sched.iloc[idx]
            o_sched = o_sched.iloc[:idx]
        except:
            # Use entire sched if date is not found
            print(f'No game available on date {date} for team {team}')
            pass
        for label in stat_labels:
            # Get value
            #x = row[label]
            col = o_sched[label].values
            aver = np.mean(col[max(i-(n+1), 0):max(i-1, 1)])
            #if math.isnan(aver):
                #aver = x
            val = aver
            new_cols[f"{label}_2"].append(val)
    for key, val in new_cols.items():
        sched[key] = val
    # Prepare data for model (ignore first 5 games, not enough previous data)
    x = sched.iloc[:, -20:].values[5:]
    y = sched.loc[:, ['Tm', 'Opp.1']].values[5:]
    # Split train and test data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0, shuffle=True)
    # Train model
    model = LinearRegression()
    model.fit(x_train, y_train)
    # Predict
    y_out = model.predict(x_test)
    # Print results
    corr_wl = 0
    total = 0
    acc = 0
    for i in range(len(y_out)):
        # Check if team won or lost
        if y_out[i][0] > y_out[i][1] and y_test[i][0] > y_test[i][1]:
            corr_wl += 1
        elif y_out[i][0] < y_out[i][1] and y_test[i][0] < y_test[i][1]:
            corr_wl += 1
        total += 1
        acc += abs(y_out[i][0] - y_test[i][0]) + abs(y_out[i][1] - y_test[i][1])
        print(f'Predicted: {np.round(y_out[i])}, Actual: {y_test[i]}')
    print(f'Accuracy: {corr_wl / total}')
    print(f'Average difference (individual team): {acc / (total*2)}')
    return x, y

    

predict_stats_from_adv('MIN')