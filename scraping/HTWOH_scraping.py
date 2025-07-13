from datetime import datetime
import os
import random
from csv import reader

from selenium.webdriver.support.wait import WebDriverWait

import utils
from database.database_interface import PlayersSqlDatabase, COURT_TYPE, HTWOHSqlDatabase
import undetected_chromedriver as uc
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from utils import custom_fuzzy_strategy, compare_strings


current_year = datetime.now().year
#The head to head scraping should be based on the matches we have

#Currently we have two matches datasets 2024 and 2025

def scrape_htwoh_of_two_players(name1: str, name2: str) -> list:
    pass

#load the list of elements we need to populate the database (namely names)
list_of_tuples_players_names_from_matches = []

#first 2024

with open("../database/github_dataset/atp_matches_2024.csv") as matches_2024:
    r = reader(matches_2024)
    for row in r:
        list_of_tuples_players_names_from_matches.append((row[10].upper(), row[18].upper()))

#number of matches
print("Number of matches: ", len(list_of_tuples_players_names_from_matches))

#Now we need to see if we have those names in the database and scrape them from the website Ultimate Tennis Statistics
#we will need to do some kind of fuzzy matching

#it does not matter which year we take for the database we just need the names
players_database = PlayersSqlDatabase(court_type=COURT_TYPE.HARD, year=2025)

players = [player[0] for player in players_database.get_all_players_from_database()]
players = list(map(utils.keep_only_letters_and_spaces, players))
sum = 0

matched_players_tuples = []
for tuple_of_players in list_of_tuples_players_names_from_matches:
    player_1 = utils.keep_only_letters_and_spaces(tuple_of_players[0])
    player_2 = utils.keep_only_letters_and_spaces(tuple_of_players[1])

    player_1_string_from_database = None
    player_2_string_from_database = None
    for player in players:
        if custom_fuzzy_strategy(player_1, player):
            player_1_string_from_database = player
        if custom_fuzzy_strategy(player_2, player):
            player_2_string_from_database = player

    if player_1_string_from_database is not None and player_2_string_from_database is not None:
        sum += 1
        matched_players_tuples.append((player_1_string_from_database, player_2_string_from_database))
    else:
        if player_1_string_from_database is None:
            print("PLAYER 1 NOT FOUND: ", player_1)

        if player_2_string_from_database is None:
            print("PLAYER 2 NOT FOUND: ", player_2)

print("Number of matched tuples: ",sum)

#
"""
adblock_path = os.path.abspath("adblock.crx")

# Setup Chrome options
options = Options()
options.browser_version = "139"
options.add_argument("--no-sandbox")
options.add_extension(adblock_path)  # Load the .crx extension

# Initialize regular ChromeDriver
driver = webdriver.Chrome(service=Service(), options=options)

# Test it
driver.get("https://www.ultimatetennisstatistics.com/headToHead")

time.sleep(10)
"""
#random.shuffle(matched_players_tuples)


"""driver.get("https://www.ultimatetennisstatistics.com/headToHead")"""

"""
for i, player_tuple in enumerate(matched_players_tuples):
    print("Percentage finished: ", i/len(matched_players_tuples))

    try:
        player1 = player_tuple[0]
        player2 = player_tuple[1]
        exists_in_database = False
        for j in range(2016, 2026):
            htwoh_database = HTWOHSqlDatabase(year=j)
            if htwoh_database.check_if_names_are_on_the_database(player1, player2):
                exists_in_database = True
                break
        if exists_in_database: continue

        player1_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "player1"))
        )
        player1_input.clear()
        player1_input.send_keys(player_tuple[0])

        # Wait for the suggestion dropdown to appear (li inside the autocomplete ul)
        options = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#ui-id-1 li div.ui-menu-item-wrapper"))
        )

        # Now safely click the first one
        first_option = options[0]

        # Optional: Scroll and use JS click for reliability
        driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
        driver.execute_script("arguments[0].click();", first_option)

        # Wait for player2 input and enter text
        player2_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "player2"))
        )
        player2_input.clear()
        player2_input.send_keys(player_tuple[1])
        time.sleep(1)

        # Wait for the second autocomplete suggestion
        options = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#ui-id-2 li div.ui-menu-item-wrapper"))
        )

        # Now safely click the first one
        first_option = options[0]

        # Optional: Scroll and use JS click for reliability
        driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
        driver.execute_script("arguments[0].click();", first_option)

        # go to the matches tab

        matches_button = driver.find_element(By.ID, "matchesPill")
        matches_button.click()

        time.sleep(2)
        matches = (WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "matchesTable")))
                   .find_element(By.TAG_NAME, "tbody")).find_elements(By.TAG_NAME, "tr")

        if len(matches) == 0 or len(matches) == 1 and matches[0].find_element(By.TAG_NAME,
                                                                              "td").text == "No matches found":
            print("No matches")
            continue

        for match in matches:
            try:
                row_elements = match.find_elements(By.TAG_NAME, "td")
                match_date = row_elements[0].text
                match_date_stripped = match_date.split("-")  # DD/MM/YYYY
                htwoh = row_elements[6].text.split("-")
                htwoh_database = HTWOHSqlDatabase(year=int(match_date_stripped[2]))
                # put the htwoh data in the database
                tuple_for_database = (
                    player1,
                    player2,
                    int(htwoh[0]),
                    int(htwoh[1]),
                    match_date
                )

                htwoh_database.write_htwoh_entry_to_database(tuple_for_database)
            except Exception as e:
                print("Exception", e)
                import traceback

                traceback.print_exc()
                time.sleep(10)
                continue

        time.sleep(10)
    except:
        print("There was an error")
        continue
"""

list_of_tuples_players_names_from_matches = []

#then 2025 matches
with open("../database/github_dataset/atp_tennis.csv") as matches_2025:
    r = reader(matches_2025)
    for row in r:
        if "2025" in row[1]:
            list_of_tuples_players_names_from_matches.append((row[7], row[8]))
matched_players_tuples = []
for tuple_of_players in list_of_tuples_players_names_from_matches:
    player_1 = utils.keep_only_letters_and_spaces(tuple_of_players[0])
    player_2 = utils.keep_only_letters_and_spaces(tuple_of_players[1])

    player_1_string_from_database = None
    player_2_string_from_database = None
    for player in players:
        if custom_fuzzy_strategy(player_1, player):
            player_1_string_from_database = player
        if custom_fuzzy_strategy(player_2, player):
            player_2_string_from_database = player

    if player_1_string_from_database is not None and player_2_string_from_database is not None:
        sum += 1
        matched_players_tuples.append((player_1_string_from_database, player_2_string_from_database))
    else:
        if player_1_string_from_database is None:
            print("PLAYER 1 NOT FOUND: ", player_1)

        if player_2_string_from_database is None:
            print("PLAYER 2 NOT FOUND: ", player_2)

#then scrape HTWOH 2025
#driver.close()
#driver.quit()
options = uc.ChromeOptions()

options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)

driver.get("https://www.atptour.com/en/players/atp-head-2-head")
time.sleep(10)

htwoh_current_year_database = HTWOHSqlDatabase(year=current_year)
print(current_year)
length_of_database = len(htwoh_current_year_database.find_all_from_database())
matched_players_tuples.reverse()
for i, player_tuple in enumerate(matched_players_tuples):
    print("Percentage finished: ", i/len(matched_players_tuples) * 100)
    if i / len(matched_players_tuples) >= length_of_database / len(matched_players_tuples):
        try:
            player1 = player_tuple[0]
            player2 = player_tuple[1]

            if not htwoh_current_year_database.check_if_names_are_on_the_database(player1, player2):
                driver.refresh()
                time.sleep(2)
                search_wrapper = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-wrapper")))

                player_div = search_wrapper.find_element(By.CLASS_NAME, "player")

                opponent_div = search_wrapper.find_element(By.CLASS_NAME, "opponent")

                button_player_search = player_div.find_element(By.CLASS_NAME, "player-search")
                button_player_search.click()

                player_search_input = player_div.find_element(By.CLASS_NAME, "search-input")
                player_search_input.send_keys(player1)

                players_list_first_option = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "player-list"))).find_elements(By.TAG_NAME, "li")[0]
                players_list_first_option.click()

                button_opponent_search = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "opponent-search")))
                button_opponent_search.click()

                search_wrapper = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-wrapper")))

                opponent_div = search_wrapper.find_element(By.CLASS_NAME, "opponent")

                opponent_search_input = WebDriverWait(opponent_div, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-input")))
                opponent_search_input.send_keys(player2)

                opponents_list_first_option = \
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                    ".player-list.player-list--opponent"))).find_elements(
                        By.TAG_NAME, "li")[0]
                opponents_list_first_option.click()

                time.sleep(2)
                match_stats_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "match-stats")))
                win_stats = match_stats_div.find_element(By.CLASS_NAME, "win-stats")

                player_wins = win_stats.find_element(By.CLASS_NAME, "player").text
                opponent_wins = win_stats.find_element(By.CLASS_NAME, "opponent").text

                if int(player_wins) == 0 and int(opponent_wins) == 0:
                    continue

                # put the results in the 2025 database
                tuple_for_database = (
                    player1,
                    player2,
                    int(player_wins),
                    int(opponent_wins),
                    f"01/01/{current_year}"
                )

                htwoh_current_year_database.write_htwoh_entry_to_database(tuple_for_database)


        except Exception as e:
            print("Exception", e)
            import traceback

            traceback.print_exc()
            time.sleep(10)
            continue




















