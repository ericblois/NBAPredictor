from nba_api.stats.endpoints import *
import nba_api.stats.library.parameters as params
from nba_api.stats.static import players
from nba_api.stats.static import teams
import pandas as pd
import time
import datetime
import re

HEADERS={
    "Host": "stats.nba.com", 
    "User-Agent": "Firefox/55.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://stats.nba.com/events",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "DNT": "1"
}

CURR_YEAR = 2022

PLAYER_IDS = {}
TEAM_IDS = {}
TEAM_ABBREVS = {}

months = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
months_keys = list(months.keys())

def init_data():
    global PLAYER_IDS
    PLAYER_IDS = {player['full_name'].lower(): player['id'] for player in players.get_players() if player['is_active']}
    global TEAM_IDS
    for team in teams.get_teams():
        TEAM_IDS[team['full_name'].lower()] = team['id']
        TEAM_IDS[team['abbreviation'].lower()] = team['id']
        TEAM_IDS[team['nickname'].lower()] = team['id']
        TEAM_IDS[team['city'].lower()] = team['id']
        TEAM_ABBREVS[str(team['id'])] = team['abbreviation']
    pass

def get_player_id(player_name: str):
    try:
        return str(PLAYER_IDS[player_name.lower()])
    except:
        raise Exception('Could not find player with name: ' + player_name)

def get_team_id(team: str):
    try:
        return str(TEAM_IDS[team.lower()])
    except:
        raise Exception('Could not find team with name: ' + team)

def get_team_abbrev(team: str):
    try:
        return TEAM_ABBREVS[get_team_id(team)]
    except:
        raise Exception('Could not find team with name: ' + team)

def date_to_timestamp(date: str):
    month, day, year = re.split(' |, ', date)
    month = months[month.lower()]
    return time.mktime(datetime.datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y").timetuple())

def timestamp_to_date(timestamp: int):
    dt = datetime.datetime.fromtimestamp(timestamp)
    day = dt.day
    month = dt.month
    month = months_keys[month - 1].upper()
    year = dt.year
    return f"{month} {day}, {year}"

# Get the last num_games games the player has played (date is in format MON Day, year ex. Feb 1, 2021)
def get_player_games(player_name: str, num_games: int = 1, before_date: str = None):
    player_id = get_player_id(player_name)
    # Get all the games the player has played
    games = playergamelog.PlayerGameLog(player_id=player_id, season="all", season_type_all_star='Regular Season', league_id_nullable='00', headers=HEADERS).get_data_frames()[0]
    # Add a column for timestamp of the game date
    games['TIMESTAMP'] = games['GAME_DATE'].map(date_to_timestamp)
    if before_date is not None:
        try:
            before_time = date_to_timestamp(before_date)
        except:
            raise Exception('Date must be in format Mon Day, year ex. Feb 1, 2021')
        # Filter the games to only include the games before the date
        games = games.loc[games['TIMESTAMP'] < before_time]
        games.reset_index(drop=True, inplace=True)
    # Return the first num_games games
    return games.iloc[0: num_games]

def get_player_games_vs_team(player_name: str, team: str):
    team_abbrev = get_team_abbrev(team)
    player_id = get_player_id(player_name)
    # Get all the games the player has played
    games = playergamelog.PlayerGameLog(player_id=player_id, season="all").get_data_frames()[0]
    # Filter the games to only include the games that involve the team
    games = games.loc[games['MATCHUP'].str.endswith(team_abbrev)]
    # Add a column for timestamp of the game date
    games['TIMESTAMP'] = games['GAME_DATE'].map(date_to_timestamp)
    games.reset_index(drop=True, inplace=True)
    return games

# Get the last num_games games the player has played (date is in format MON Day, year ex. Feb 1, 2021)
def get_team_games(team_name: str, num_games: int = 1, before_date: str = None):
    team_id = get_team_id(team_name)
    # Get all the games the player has played
    #games = teamgamelog.TeamGameLog(team_id=team_id, season="all", season_type_all_star='Regular Season', league_id_nullable='00', date_to_nullable='2023-04-10', headers=HEADERS)
    games = teamgamelogs.TeamGameLogs(team_id_nullable=team_id, date_to_nullable='2023-04-10')
    games = games.get_data_frames()[0]
    # Add a column for timestamp of the game date
    games['TIMESTAMP'] = games['GAME_DATE'].map(date_to_timestamp)
    if before_date is not None:
        try:
            before_time = date_to_timestamp(before_date)
        except:
            raise Exception('Date must be in format Mon Day, year ex. Feb 1, 2021')
        # Filter the games to only include the games before the date
        games = games.loc[games['TIMESTAMP'] < before_time]
        games.reset_index(drop=True, inplace=True)
    # Return the first num_games games
    return games.iloc[0: num_games]

def get_game_boxscore(game_id: str):
    return boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]