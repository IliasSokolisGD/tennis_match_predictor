import time
from enum import EnumType

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import undetected_chromedriver as uc
import utils
from database.database_interface import COURT_TYPE
from training_set_preparation import predict_winner
from utils import keep_only_numbers

YEAR = 2025

def try_to_convert_to_int(string_to_convert_to_int: str):
    try:
        return int(string_to_convert_to_int)
    except:
        raise Exception()

def get_players_and_output_probabilities(url1: str, url2: str, wins_player_1: int, wins_player_2: int, odds1: float, odds2: float, surface: str):
    SURFACE = surface
    urls = [(url1, odds1), (url2, odds2)]

    player_tuples = []

    options = uc.ChromeOptions()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    for url, odds in urls:
        driver.get(url)
        time.sleep(7)


        player_stats = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "player-stats-details")))
        player_stats_ytd = player_stats[0]
        player_stats_career = player_stats[1]

        name = driver.find_element(By.CLASS_NAME, "player_name").find_element(By.TAG_NAME, "span").text

        rank = utils.keep_only_numbers(player_stats_ytd.find_element(By.CLASS_NAME, "stat").text)
        wins_loses_ytd = player_stats_ytd.find_element(By.CLASS_NAME, "wins").text
        wins_loses_career = player_stats_career.find_element(By.CLASS_NAME, "wins").text

        wins_ytd, loses_ytd = filter(utils.string_not_empty, map(keep_only_numbers, wins_loses_ytd.split('-')))
        wins_career, loses_career = filter(utils.string_not_empty,
                                           map(keep_only_numbers, wins_loses_career.split('-')))
        titles = utils.keep_only_numbers(player_stats_ytd.find_element(By.CLASS_NAME, "titles").text)
        global_titles = utils.keep_only_numbers(player_stats_career.find_element(By.CLASS_NAME, "titles").text)
        prize_money_ytd = utils.keep_only_numbers(
            player_stats_ytd.find_element(By.CLASS_NAME, "prize_money").text)
        prize_money_career = utils.keep_only_numbers(
            player_stats_career.find_element(By.CLASS_NAME, "prize_money").text)

        print("name: ", name)
        print("rank: ", rank)
        print("wins_ytd: ", wins_ytd)
        print("loses_ytd: ", loses_ytd)
        print("wins_career: ", wins_career)
        print("loses_career: ", loses_career)
        print("titles: ", titles)
        print("global_titles: ", global_titles)
        print("prize_money_ytd: ", prize_money_ytd)
        print("prize_money_career: ", prize_money_career)

        table_of_overview = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pd_left")))

        # this is the li element
        # we need to find how to tell which is the age weight height etc...
        age = utils.keep_only_numbers(
            table_of_overview.find_element(By.XPATH, "//*[text()='Age']/following-sibling::*[1]").text.split(
                " ")[
                0])
        weight = utils.keep_only_numbers(
            table_of_overview.find_element(By.XPATH, "//*[text()='Weight']/following-sibling::*[1]").text.split(
                " ")[2])
        height = utils.keep_only_numbers(
            table_of_overview.find_element(By.XPATH, "//*[text()='Height']/following-sibling::*[1]").text.split(
                " ")[1])
        turned_pro = utils.keep_only_numbers(
            table_of_overview.find_element(By.XPATH, "//*[text()='Turned pro']/following-sibling::*[1]").text)
        if turned_pro is None or turned_pro == "":
            turned_pro = input("Please insert turned pro")
        print("age: ", age)
        print("weight: ", weight)
        print("height: ", height)
        print("Turned pro: ", turned_pro)

        # also the winner ranking points

        navigation_bar = driver.find_element(By.CLASS_NAME, "tab-nav")
        stats_button = navigation_bar.find_element(By.XPATH, ".//*[text()='Ranking']")
        stats_button.click()

        rank_breakdown_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//*[text()='Rank Breakdown']")))
        rank_breakdown_button.click()
        winner_rank_points = utils.keep_only_numbers(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//*[text()='Points']/parent::div"))).text)

        print("Winner rank points: ", winner_rank_points)

        navigation_bar = driver.find_element(By.CLASS_NAME, "tab-nav")
        stats_button = navigation_bar.find_element(By.XPATH, ".//*[text()='Stats']")
        stats_button.click()
        # now we are in the stats tab we need to chose the type of stadium we want and the year
        year_selector = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "year")))
        year_options = year_selector.find_elements(By.TAG_NAME, "option")
        # chose the option we want to for statistics
        for option in year_options:
            if option.get_attribute("data-value") == str(YEAR):
                option.click()
                break
        # chose the surface we want
        surface_selector = driver.find_element(By.ID, "surface")
        surface_options = surface_selector.find_elements(By.TAG_NAME, "option")
        for surface_option in surface_options:
            if surface_option.get_attribute("data-value") == SURFACE:
                surface_option.click()
                break

        # wait a little bit for the statistics to appear
        statistics_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "statistics_content"))
        )
        # serve
        aces = statistics_container.find_element(By.XPATH,
                                                 ".//*[text()='Aces']/following-sibling::*[1]").text
        double_faults = statistics_container.find_element(By.XPATH,
                                                          ".//*[text()='Double Faults']/following-sibling::*[1]").text
        first_serve_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='1st Serve']/following-sibling::*[1]").text)
        first_serve_points_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='1st Serve Points Won']/following-sibling::*[1]").text)
        second_serve_points_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='2nd Serve Points Won']/following-sibling::*[1]").text)
        break_points_faced = statistics_container.find_element(By.XPATH,
                                                               ".//*[text()='Break Points Faced']/following-sibling::*[1]").text
        break_points_saved_percentage = utils.keep_only_numbers(statistics_container.find_element(By.XPATH,
                                                                                                  ".//*[text()='Break Points Saved']/following-sibling::*[1]").text)
        service_games_played = statistics_container.find_element(By.XPATH,
                                                                 ".//*[text()='Service Games Played']/following-sibling::*[1]").text
        service_games_won_percentage = utils.keep_only_numbers(statistics_container.find_element(By.XPATH,
                                                                                                 ".//*[text()='Service Games Won']/following-sibling::*[1]").text)
        total_service_points_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='Total Service Points Won']/following-sibling::*[1]").text)

        # return
        first_serve_return_points_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='1st Serve Return Points Won']/following-sibling::*[1]").text)
        second_serve_return_points_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='2nd Serve Return Points Won']/following-sibling::*[1]").text)
        break_point_opportunities = statistics_container.find_element(By.XPATH,
                                                                      ".//*[text()='Break Points Opportunities']/following-sibling::*[1]").text
        break_points_converted_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='Break Points Converted']/following-sibling::*[1]").text)
        return_games_played = statistics_container.find_element(By.XPATH,
                                                                ".//*[text()='Return Games Played']/following-sibling::*[1]").text
        return_games_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='Return Games Won']/following-sibling::*[1]").text)
        return_points_won_percentage = utils.keep_only_numbers(statistics_container.find_element(By.XPATH,
                                                                                                 ".//*[text()='Return Points Won']/following-sibling::*[1]").text)
        total_points_won_percentage = utils.keep_only_numbers(
            statistics_container.find_element(By.XPATH,
                                              ".//*[text()='Total Points Won']/following-sibling::*[1]").text)

        print("Aces: ", aces)
        print("Double faults: ", double_faults)
        print("First serve percentage: ", first_serve_percentage)
        print("First serve points won percentage: ", first_serve_points_won_percentage)
        print("Second serve points won percentage: ", second_serve_points_won_percentage)
        print("Break points faced: ", break_points_faced)
        print("Break points saved percentage: ", break_points_saved_percentage)
        print("Service games played: ", service_games_played)
        print("Service games won percentage: ", service_games_won_percentage)
        print("Total service points won percentage: ", total_service_points_won_percentage)
        print()
        print("First serve return points won percentage: ", first_serve_return_points_won_percentage)
        print("Second serve return points won percentage: ", second_serve_return_points_won_percentage)
        print("Break point opportunities: ", break_point_opportunities)
        print("Break points converted percentage: ", break_points_converted_percentage)
        print("Return games played: ", return_games_played)
        print("Return games won percentage: ", return_games_won_percentage)
        print("Return points won percentage: ", return_points_won_percentage)
        print("Total points won percentage: ", total_points_won_percentage)

        print()

        database_tuple = (
            try_to_convert_to_int(age),
            try_to_convert_to_int(weight),
            try_to_convert_to_int(height),
            try_to_convert_to_int(turned_pro),
            try_to_convert_to_int(rank),
            try_to_convert_to_int(winner_rank_points),
            try_to_convert_to_int(titles),
            try_to_convert_to_int(global_titles),
            try_to_convert_to_int(wins_ytd),
            try_to_convert_to_int(loses_ytd),
            try_to_convert_to_int(wins_career),
            try_to_convert_to_int(loses_career),
            try_to_convert_to_int(prize_money_ytd),
            try_to_convert_to_int(prize_money_career),
            try_to_convert_to_int(aces),
            try_to_convert_to_int(double_faults),
            try_to_convert_to_int(first_serve_percentage),
            try_to_convert_to_int(first_serve_points_won_percentage),
            try_to_convert_to_int(second_serve_points_won_percentage),
            try_to_convert_to_int(break_points_faced),
            try_to_convert_to_int(break_points_saved_percentage),
            try_to_convert_to_int(service_games_played),
            try_to_convert_to_int(service_games_won_percentage),
            try_to_convert_to_int(total_service_points_won_percentage),
            try_to_convert_to_int(first_serve_return_points_won_percentage),
            try_to_convert_to_int(second_serve_return_points_won_percentage),
            try_to_convert_to_int(break_point_opportunities),
            try_to_convert_to_int(break_points_converted_percentage),
            try_to_convert_to_int(return_games_played),
            try_to_convert_to_int(return_games_won_percentage),
            try_to_convert_to_int(return_points_won_percentage),
            try_to_convert_to_int(total_points_won_percentage),
            odds
        )

        player_tuples.append(database_tuple)

    driver.quit()
    return predict_winner(player_tuples[0], player_tuples[1], COURT_TYPE.convert_string_to_court_type(surface) ,wins_player_1, wins_player_2)

