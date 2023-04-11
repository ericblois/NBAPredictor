from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from nba_api.stats.endpoints import *
import nba_api.stats.library.parameters as params
from nba_api.stats.static import players
from nba_api.stats.static import teams
from GameFinder import *

#Set options for driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

#Start driver using preset options
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#driver = webdriver.Chrome("/Applications/chromedriver", options=chrome_options)
driver.implicitly_wait(10)

def get_player_team(player_name: str):
    player_id = get_player_id(player_name)
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
    #player_info = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
    city = player_info.iloc[0]["TEAM_CITY"] if player_info.iloc[0]["TEAM_CITY"] != "LA" else "Los Angeles"
    return city + ' ' + player_info.iloc[0]["TEAM_NAME"]

# Team name should be the full name of the team (ex. "Los Angeles Lakers")
def get_injuries(team: str):
    #Get injuries
    driver.get("https://www.espn.com/nba/injuries")
    card = driver.find_element(By.CLASS_NAME, "Card")
    section = card.find_element(By.TAG_NAME, "section")
    teams = section.find_elements(By.CLASS_NAME, "ResponsiveTable")
    injuries = []
    for team_div in teams:
        team_name = team_div.find_element(By.TAG_NAME, "span").text
        if team_name != team:
            continue
        trows = team_div.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
        for row in trows:
            tds = row.find_elements(By.TAG_NAME, "td")
            player_name = tds[0].text
            player_status = tds[3].text
            if player_status != "Day-To-Day":
                injuries.append(player_name)
        break
    return injuries