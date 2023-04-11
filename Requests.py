import pandas as pd
import time

# ----- Limited to 20 requests per minute -----

# Get basic box score for a team (ex. "ATL", "2021", "10", "19"), returns home starters, away starters, home bench, away bench
def retrieve_box_score(home_abbrev: str, year: str, month: str, day: str):
    url = f'https://www.basketball-reference.com/boxscores/{year}{month}{day}0{home_abbrev}.html'
    tables = pd.read_html(url)
    home_starters = None
    away_starters = None
    home_bench = None
    away_bench = None
    did_away = False
    is_home = False
    for table in tables:
        name = table.columns.get_level_values(0)[1]
        if name == 'Advanced Box Score Stats':
            is_home = True
        elif name == 'Basic Box Score Stats':
            while table.columns.nlevels >= 2:
                table.columns = table.columns.droplevel(0)
            if is_home:
                home_starters = table.iloc[0: 5]
                home_bench = table.iloc[6:len(table) - 1]
                home_bench.reset_index(drop=True, inplace=True)
                break
            elif not did_away:
                away_starters = table.iloc[0: 5]
                away_bench = table.iloc[6:len(table) - 1]
                away_bench.reset_index(drop=True, inplace=True)
                did_away = True
    time.sleep(3)
    return home_starters, away_starters, home_bench, away_bench

#h_start, a_start, h_bench, a_bench = retrieve_box_score('ATL', 2022, 10, 19)

# Get advanced box score for a team (ex. "ATL", "2021", "10", "19"), returns home starters, away starters, home bench, away bench
def retrieve_adv_box_score(home_abbrev: str, year: str, month: str, day: str):
    url = f'https://www.basketball-reference.com/boxscores/{year}{month}{day}0{home_abbrev}.html'
    tables = pd.read_html(url)
    home_starters = None
    away_starters = None
    home_bench = None
    away_bench = None
    is_home = False
    for table in tables:
        name = table.columns.get_level_values(0)[1]
        if name == 'Advanced Box Score Stats':
            while table.columns.nlevels >= 2:
                table.columns = table.columns.droplevel(0)
            if is_home:
                home_starters = table.iloc[0: 5]
                home_bench = table.iloc[6:len(table) - 1]
                home_bench.reset_index(drop=True, inplace=True)
                break
            else:
                away_starters = table.iloc[0: 5]
                away_bench = table.iloc[6:len(table) - 1]
                away_bench.reset_index(drop=True, inplace=True)
                is_home = True
    time.sleep(3)
    return home_starters, away_starters, home_bench, away_bench


#h_start, a_start, h_bench, a_bench = retrieve_adv_box_score('ATL', 2022, 10, 19)

# Get team schedule for a team (ex. "ATL", "2021"), returns table of games for 2020-2021 season
def retrieve_team_schedule(team_abbrev: str, year: str):
    url = f'https://www.basketball-reference.com/teams/{team_abbrev}/{year}/gamelog-advanced/'
    tables = pd.read_html(url)
    schedule = None
    for table in tables:
        while table.columns.nlevels >= 2:
            table.columns = table.columns.droplevel(0)
        table['Rk'].convert_dtypes(convert_integer=True)
        # Filter out header rows
        schedule = table[table['Rk'].apply(lambda x: str(x).isdigit())]
        schedule.reset_index(drop=True, inplace=True)
        break
    time.sleep(3)
    return schedule