from GameFinder import *
from RosterTools import *
from StatsPredictor import *

if __name__ == '__main__':
    init_data()
    '''start = time.time()
    rand = get_player_games_vs_team('Lebron James', 'Knicks')
    end = time.time()
    print(rand)
    print(end - start)
    print(get_game_boxscore('0022201038'))
    start = time.time()
    randle = get_player_games("d'angelo russell", 7)
    end = time.time()
    print(randle)
    print(end - start)
    '''
    #print(get_injuries("Los Angeles Lakers"))
    print(get_player_team("Russell Westbrook"))
    #print(get_player_games("Russell Westbrook", 5, "Feb 1, 2021"))
    games = get_team_games("Los Angeles Lakers", 5, "Feb 1, 2021")
    print("Exiting...")