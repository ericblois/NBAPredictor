import pandas as pd
import json
import time
import os
from Requests import *

team_abbrevs = ["ATL", "BOS", "BRK", "CHO", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]
GAME_LOGS = {}
ADV_BOX_SCORES = {}

def update_game_logs():
    # Check if game logs dir exists
    if not os.path.isdir('game_logs'):
        os.mkdir('game_logs')
    # Get all games from 2022-2023 season
    for abbrev in team_abbrevs:
        print("\033[37m" + f"Retrieving {abbrev} schedule for 2022-2023 season...")
        schedule = retrieve_team_schedule(abbrev, 2023)
        # Save each game to a csv file
        schedule.to_csv(f'game_logs/{abbrev}_2023.csv', index=False)

def load_game_logs():
    # Check if game logs dir exists
    if not os.path.isdir('game_logs'):
        update_game_logs()
    # Get all games from 2022-2023 season
    for abbrev in team_abbrevs:
        print("\033[37m" + f"Loading {abbrev} schedule for 2022-2023 season...")
        try:
            schedule = pd.read_csv(f'game_logs/{abbrev}_2023.csv')
        except:
            print("\033[33m" + f"Could not load {abbrev} schedule for 2022-2023 season, retrieving from web...")
            schedule = retrieve_team_schedule(abbrev, 2023)
            # Save each game to a csv file
            schedule.to_csv(f'game_logs/{abbrev}_2023.csv', index=False)
        GAME_LOGS[abbrev] = schedule

def update_adv_box_scores():
    # Check if game logs dir exists
    if not os.path.isdir('adv_box_scores'):
        os.mkdir('adv_box_scores')
    # Load game logs
    load_game_logs()
    # Get advanced box scores for each game, for each team
    for i, abbrev in enumerate(team_abbrevs):
        # Check if team dir exists
        if not os.path.isdir(f'adv_box_scores/{abbrev}'):
            os.mkdir(f'adv_box_scores/{abbrev}')
        for j, row in GAME_LOGS[abbrev].iterrows():
            #print("\033[37m" + f"Retrieving advanced box scores for {abbrev} {row['Date']}...")
            [year, month, day] = row['Date'].split('-')
            # Check if game has already been retrieved
            if os.path.isfile(f'adv_box_scores/{abbrev}/{year}_{month}_{day}.csv'):
                continue
            is_home = row[[3]][0] != '@'
            home_abbrev = abbrev if is_home else row[[4]][0]
            [year, month, day] = row['Date'].split('-')
            home_starters, away_starters, home_bench, away_bench = retrieve_adv_box_score(home_abbrev, year, month, day)
            home = pd.concat([home_starters, home_bench])
            away = pd.concat([away_starters, away_bench])
            if is_home:
                home.to_csv(f'adv_box_scores/{abbrev}/{year}_{month}_{day}.csv', index=False)
                # Check if away team dir exists
                if not os.path.isdir(f'adv_box_scores/{row[[4]][0]}'):
                    os.mkdir(f'adv_box_scores/{row[[4]][0]}')
                away.to_csv(f'adv_box_scores/{row[[4]][0]}/{year}_{month}_{day}.csv', index=False)
            else:
                away.to_csv(f'adv_box_scores/{abbrev}/{year}_{month}_{day}.csv', index=False)
                # Check if home team dir exists
                if not os.path.isdir(f'adv_box_scores/{row[[4]][0]}'):
                    os.mkdir(f'adv_box_scores/{row[[4]][0]}')
                home.to_csv(f'adv_box_scores/{row[[4]][0]}/{year}_{month}_{day}.csv', index=False)
            print("\033[37m" + f"Saved advanced box scores for {abbrev} and {row[[4]][0]} {row['Date']}, {round(((i*82 + j+1) / 2460)*100, 2)}% complete...")

def load_adv_box_scores():
    # Check if game logs dir exists
    if not os.path.isdir('adv_box_scores'):
        update_adv_box_scores()
    # Get all games from 2022-2023 season
    for abbrev in team_abbrevs:
        print("\033[37m" + f"Loading {abbrev} advanced box scores for 2022-2023 season...")
        # Check if team dir exists
        if not os.path.isdir(f'adv_box_scores/{abbrev}'):
            update_adv_box_scores()
        filenames = os.listdir(f'adv_box_scores/{abbrev}')
        frames = {filename[:10]: pd.read_csv(f'adv_box_scores/{abbrev}/{filename}') for filename in filenames}
        ADV_BOX_SCORES[abbrev] = frames

def update_all():
    update_game_logs()
    update_adv_box_scores()

def load_all():
    load_game_logs()
    load_adv_box_scores()

# Get advanced box score for a team (ex. "ATL", "2021", "10", "19")
def get_advanced_box_score(abbrev: str, year: str, month: str, day: str) -> pd.DataFrame:
    if len(ADV_BOX_SCORES) <= 0:
        load_all()
    try:
        return ADV_BOX_SCORES[abbrev][f'{year}_{month}_{day}']
    except:
        raise Exception(f'No game available for {abbrev} on {year}-{month}-{day}')

# Get team schedule for a team
def get_team_schedule(abbrev: str) -> pd.DataFrame:
    if len(GAME_LOGS) <= 0:
        load_all()
    try:
        return GAME_LOGS[abbrev]
    except:
        raise Exception(f'No schedule available for {abbrev}')