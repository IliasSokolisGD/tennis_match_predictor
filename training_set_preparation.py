import traceback
from csv import reader
from operator import length_hint

#we will prepare a training data set

#it will be different for 2024 and 2025

#we need at least 6000 training data and 1000 test

import database.database_interface as database_interface
import numpy as np
from datetime import datetime
import utils
from database.database_interface import PlayersSqlDatabase, COURT_TYPE, HTWOHSqlDatabase

import joblib


#A dataset entry for a match will contain the following elements:
#surface -> the surface the match is being played at
#age -> calculate the difference between ages of each player
#weight -> calculate the weight difference of each player
#height -> calculate the height difference of each player
#turned pro -> check difference between players except if it is -1 where we keep it at -1 in this case
#rank -> check difference
#winner rank points -> check ratio
#aces -> check ratio
#double_faults -> check ratio
#first_serve -> check ratio
#first_serve_points_won -> check ratio
#second_serve_points_won -> check ratio
#break_points_faced -> check ratio
#break_points_saved -> check ratio
#service_games_played -> check ratio
#service_games_won -> check ratio
#total_service_points_won -> check ratio
#first_serve_return_points_won -> check ratio
#second_serve_return_points_won -> check ratio
#break_points_opportunities -> check ratio
#break_points_converted -> check ratio
#return_games_played -> check ratio
#return_games_won -> check ratio
#return_points_won -> check ratio
#total_points_won -> check ratio
#H2H ratios -> check our database
import random as random




def ratio_inversion(calculated_ratio:float, inverse: bool):
    if inverse:
        if calculated_ratio != 0:
            return 1/calculated_ratio
        else:
            return 1 / 1e-6
    else:
        return calculated_ratio

def sign_inversion(calculated_difference: float, inverse: bool):
    if inverse:
        return -calculated_difference
    else:
        return calculated_difference



def prepare_training_and_test_set():
    #first prepare 2024 dataset

    dataset_to_return_features = []
    dataset_to_return_results = [] #this is an integer who is 1 if player 1 won and 0 if player 2 won

    with open("database/github_dataset/2024.csv") as matches_2024:
        r = reader(matches_2024)

        players_2024_hard = PlayersSqlDatabase(court_type=COURT_TYPE.HARD, year=2024)
        players_2024_clay = PlayersSqlDatabase(court_type=COURT_TYPE.CLAY, year=2024)
        players_2024_grass = PlayersSqlDatabase(court_type=COURT_TYPE.GRASS, year=2024)
        players_2024_carpet = PlayersSqlDatabase(court_type=COURT_TYPE.CARPET, year=2024)

        database_dict_players = {
            COURT_TYPE.HARD: players_2024_hard.get_all_players_from_database(),
            COURT_TYPE.CLAY: players_2024_clay.get_all_players_from_database(),
            COURT_TYPE.GRASS: players_2024_grass.get_all_players_from_database(),
            COURT_TYPE.CARPET: players_2024_carpet.get_all_players_from_database()
        }

        h2h_2024_database = HTWOHSqlDatabase(year=2024)

        for row in list(r)[1:]:
            try:
                surface = COURT_TYPE.convert_string_to_court_type(row[6])
                inverse_class = random.choices([True, False], weights=[0.5, 0.5], k=1)[0]  # to have balanced classes
                player_1 = row[9]
                player_2 = row[10]

                player1_database_tuple = None
                player2_database_tuple = None
                for player in database_dict_players[surface]:
                    if utils.custom_fuzzy_strategy_2(player_1, player[0]):
                        player1_database_tuple = player
                    if utils.custom_fuzzy_strategy_2(player_2, player[0]):
                        player2_database_tuple = player
                    if player1_database_tuple is not None and player2_database_tuple is not None:
                        break

                if player1_database_tuple is not None and player2_database_tuple is not None:

                    age_winner = float(player1_database_tuple[1] -1)
                    age_loser = float(player2_database_tuple[1] -1)
                    age = sign_inversion(age_winner - age_loser, inverse_class)
                    weight_winner = player1_database_tuple[2]
                    weight_loser = player2_database_tuple[2]
                    weight = sign_inversion(weight_winner - weight_loser, inverse_class)
                    height_winner = float(player1_database_tuple[3])
                    height_loser = float(player2_database_tuple[3])
                    height = sign_inversion(height_winner - height_loser, inverse_class)
                    turned_pro_winner = player1_database_tuple[4]
                    turned_pro_loser = player2_database_tuple[4]
                    turned_pro = None
                    if turned_pro_winner == -1 or turned_pro_loser == -1:
                        turned_pro = -1.0
                    else:
                        turned_pro = sign_inversion(turned_pro_winner - turned_pro_loser, inverse_class)
                    rank_winner = float(row[11])
                    rank_loser = float(row[12])
                    rank = sign_inversion(rank_winner - rank_loser, inverse_class)
                    rank_points_winner = float(row[13])
                    rank_points_loser = float(row[14]) + 1e-6
                    rank_points = ratio_inversion(rank_points_winner / rank_points_loser, inverse_class)

                    aces_winner = player1_database_tuple[16]
                    aces_loser = player2_database_tuple[16] + 1e-6
                    aces = ratio_inversion(aces_winner / aces_loser, inverse_class)
                    double_faults_winner = player1_database_tuple[17]
                    double_faults_loser = player2_database_tuple[17] + 1e-6
                    double_faults = ratio_inversion(double_faults_winner / double_faults_loser, inverse_class)
                    first_serve_winner = player1_database_tuple[18]
                    first_serve_loser = player2_database_tuple[18] + 1e-6
                    first_serve = ratio_inversion(first_serve_winner / first_serve_loser, inverse_class)
                    first_serve_points_won_winner = player1_database_tuple[19]
                    first_serve_points_won_loser = player2_database_tuple[19] + 1e-6
                    first_serve_points_won = ratio_inversion(
                        first_serve_points_won_winner / first_serve_points_won_loser, inverse_class)
                    second_serve_points_won_winner = player1_database_tuple[20]
                    second_serve_points_won_loser = player2_database_tuple[20] + 1e-6
                    second_serve_points_won = ratio_inversion(
                        second_serve_points_won_winner / second_serve_points_won_loser, inverse_class)

                    # break_points_faced
                    break_points_faced_winner = player1_database_tuple[21]
                    break_points_faced_loser = player2_database_tuple[21] + 1e-6
                    break_points_faced = ratio_inversion(break_points_faced_winner / break_points_faced_loser,
                                                         inverse_class)

                    # break_points_saved
                    break_points_saved_winner = player1_database_tuple[22]
                    break_points_saved_loser = player2_database_tuple[22] + 1e-6
                    break_points_saved = ratio_inversion(break_points_saved_winner / break_points_saved_loser,
                                                         inverse_class)

                    # service_games_played
                    service_games_played_winner = player1_database_tuple[23]
                    service_games_played_loser = player2_database_tuple[23] + 1e-6
                    service_games_played = ratio_inversion(service_games_played_winner / service_games_played_loser,
                                                           inverse_class)

                    # service_games_won
                    service_games_won_winner = player1_database_tuple[24]
                    service_games_won_loser = player2_database_tuple[24] + 1e-6
                    service_games_won = ratio_inversion(service_games_won_winner / service_games_won_loser,
                                                        inverse_class)

                    # total_service_points_won
                    total_service_points_won_winner = player1_database_tuple[25]
                    total_service_points_won_loser = player2_database_tuple[25] + 1e-6
                    total_service_points_won = ratio_inversion(
                        total_service_points_won_winner / total_service_points_won_loser, inverse_class)

                    # first_serve_return_points_won
                    first_serve_return_points_won_winner = player1_database_tuple[26]
                    first_serve_return_points_won_loser = player2_database_tuple[26] + 1e-6
                    first_serve_return_points_won = ratio_inversion(
                        first_serve_return_points_won_winner / first_serve_return_points_won_loser, inverse_class)

                    # second_serve_return_points_won
                    second_serve_return_points_won_winner = player1_database_tuple[27]
                    second_serve_return_points_won_loser = player2_database_tuple[27] + 1e-6
                    second_serve_return_points_won = ratio_inversion(
                        second_serve_return_points_won_winner / second_serve_return_points_won_loser, inverse_class)

                    # break_points_opportunities
                    break_points_opportunities_winner = player1_database_tuple[28]
                    break_points_opportunities_loser = player2_database_tuple[28] + 1e-6
                    break_points_opportunities = ratio_inversion(
                        break_points_opportunities_winner / break_points_opportunities_loser, inverse_class)

                    # break_points_converted
                    break_points_converted_winner = player1_database_tuple[29]
                    break_points_converted_loser = player2_database_tuple[29] + 1e-6
                    break_points_converted = ratio_inversion(
                        break_points_converted_winner / break_points_converted_loser, inverse_class)

                    # return_games_played
                    return_games_played_winner = player1_database_tuple[30]
                    return_games_played_loser = player2_database_tuple[30] + 1e-6
                    return_games_played = ratio_inversion(return_games_played_winner / return_games_played_loser,
                                                          inverse_class)

                    # return_games_won
                    return_games_won_winner = player1_database_tuple[31]
                    return_games_won_loser = player2_database_tuple[31] + 1e-6
                    return_games_won = ratio_inversion(return_games_won_winner / return_games_won_loser, inverse_class)

                    # return_points_won
                    return_points_won_winner = player1_database_tuple[32]
                    return_points_won_loser = player2_database_tuple[32] + 1e-6
                    return_points_won = ratio_inversion(return_points_won_winner / return_points_won_loser,
                                                        inverse_class)

                    # total_points_won
                    total_points_won_winner = player1_database_tuple[33]
                    total_points_won_loser = player2_database_tuple[33] + 1e-6
                    total_points_won = ratio_inversion(total_points_won_winner / total_points_won_loser, inverse_class)

                    winner_betting_odds = 1
                    loser_betting_odds = 1
                    if inverse_class:
                        winner_betting_odds = float(row[29])
                        loser_betting_odds = float(row[28])
                    else:
                        winner_betting_odds = float(row[28])
                        loser_betting_odds = float(row[29])

                    list_of_htwoh_pairs_found = h2h_2024_database.find_pairs_in_database_and_return_them(
                        player1_database_tuple[0], player2_database_tuple[0])

                    # we need to find the one with the closest date to the match date
                    match_date = datetime.strptime(row[3], "%m/%d/%Y")
                    difference = 10e6
                    index = -1
                    for i, pair in enumerate(list_of_htwoh_pairs_found):
                        found_date = datetime.strptime(pair[4], "%d-%m-%Y")
                        difference_in_dates = match_date - found_date
                        if difference_in_dates.days < difference:
                            difference = difference_in_dates.days
                            index = i

                    wins_first_player = 0
                    wins_second_player = 0
                    if len(list_of_htwoh_pairs_found) > 0:
                        if player1_database_tuple[0] == list_of_htwoh_pairs_found[index][0] and \
                                player2_database_tuple[
                                    0] == list_of_htwoh_pairs_found[index][1]:
                            wins_first_player = int(list_of_htwoh_pairs_found[index][2])
                            wins_second_player = int(list_of_htwoh_pairs_found[index][3])
                        else:
                            wins_first_player = int(list_of_htwoh_pairs_found[index][3])
                            wins_second_player = int(list_of_htwoh_pairs_found[index][2])

                    tuple_to_add_to_the_dataset = (
                        surface.value,
                        age,
                        weight,
                        height,
                        turned_pro,
                        rank,
                        rank_points,
                        aces,
                        double_faults,
                        first_serve,
                        first_serve_points_won,
                        second_serve_points_won,
                        break_points_faced,
                        break_points_saved,
                        service_games_played,
                        service_games_won,
                        total_service_points_won,
                        first_serve_return_points_won,
                        second_serve_return_points_won,
                        break_points_opportunities,
                        break_points_converted,
                        return_games_played,
                        return_games_won,
                        return_points_won,
                        total_points_won,
                        wins_first_player,
                        wins_second_player,
                        winner_betting_odds,
                        loser_betting_odds
                    )

                    tuple_to_add_to_the_dataset = tuple(float(x) for x in tuple_to_add_to_the_dataset)

                    number_to_add_to_results = 0 if inverse_class else 1
                    dataset_to_return_features.append(tuple_to_add_to_the_dataset)
                    dataset_to_return_results.append(number_to_add_to_results)
                else:
                    if player1_database_tuple is None:
                        print("PLAYER1 NOT FOUND: ", row[9])
                    if player2_database_tuple is None:
                        print("PLAYER2 NOT FOUND: ", row[10])
            except:
                print("An error occurred:")
                traceback.print_exc()
                continue

    with open("database/github_dataset/2025.csv") as matches_2025:
        r = reader(matches_2025)

        players_2024_hard = PlayersSqlDatabase(court_type=COURT_TYPE.HARD, year=2025)
        players_2024_clay = PlayersSqlDatabase(court_type=COURT_TYPE.CLAY, year=2025)
        players_2024_grass = PlayersSqlDatabase(court_type=COURT_TYPE.GRASS, year=2025)
        players_2024_carpet = PlayersSqlDatabase(court_type=COURT_TYPE.CARPET, year=2025)

        database_dict_players = {
            COURT_TYPE.HARD: players_2024_hard.get_all_players_from_database(),
            COURT_TYPE.CLAY: players_2024_clay.get_all_players_from_database(),
            COURT_TYPE.GRASS: players_2024_grass.get_all_players_from_database(),
            COURT_TYPE.CARPET: players_2024_carpet.get_all_players_from_database()
        }

        h2h_2024_database = HTWOHSqlDatabase(year=2025)

        for row in list(r)[1:]:
            try:
                surface = COURT_TYPE.convert_string_to_court_type(row[6])
                inverse_class = random.choices([True, False], weights=[0.5, 0.5], k=1)[0]  # to have balanced classes
                player_1 = row[9]
                player_2 = row[10]

                player1_database_tuple = None
                player2_database_tuple = None
                for player in database_dict_players[surface]:
                    if utils.custom_fuzzy_strategy_2(player_1, player[0]):
                        player1_database_tuple = player
                    if utils.custom_fuzzy_strategy_2(player_2, player[0]):
                        player2_database_tuple = player
                    if player1_database_tuple is not None and player2_database_tuple is not None:
                        break

                if player1_database_tuple is not None and player2_database_tuple is not None:

                    age_winner = float(player1_database_tuple[1] - 1)
                    age_loser = float(player2_database_tuple[1] - 1)
                    age = sign_inversion(age_winner - age_loser, inverse_class)
                    weight_winner = player1_database_tuple[2]
                    weight_loser = player2_database_tuple[2]
                    weight = sign_inversion(weight_winner - weight_loser, inverse_class)
                    height_winner = float(player1_database_tuple[3])
                    height_loser = float(player2_database_tuple[3])
                    height = sign_inversion(height_winner - height_loser, inverse_class)
                    turned_pro_winner = player1_database_tuple[4]
                    turned_pro_loser = player2_database_tuple[4]
                    turned_pro = None
                    if turned_pro_winner == -1 or turned_pro_loser == -1:
                        turned_pro = -1.0
                    else:
                        turned_pro = sign_inversion(turned_pro_winner - turned_pro_loser, inverse_class)
                    rank_winner = float(row[11])
                    rank_loser = float(row[12])
                    rank = sign_inversion(rank_winner - rank_loser, inverse_class)
                    rank_points_winner = float(row[13])
                    rank_points_loser = float(row[14]) + 1e-6
                    rank_points = ratio_inversion(rank_points_winner / rank_points_loser, inverse_class)

                    aces_winner = player1_database_tuple[16]
                    aces_loser = player2_database_tuple[16] + 1e-6
                    aces = ratio_inversion(aces_winner / aces_loser, inverse_class)
                    double_faults_winner = player1_database_tuple[17]
                    double_faults_loser = player2_database_tuple[17] + 1e-6
                    double_faults = ratio_inversion(double_faults_winner / double_faults_loser, inverse_class)
                    first_serve_winner = player1_database_tuple[18]
                    first_serve_loser = player2_database_tuple[18] + 1e-6
                    first_serve = ratio_inversion(first_serve_winner / first_serve_loser, inverse_class)
                    first_serve_points_won_winner = player1_database_tuple[19]
                    first_serve_points_won_loser = player2_database_tuple[19] + 1e-6
                    first_serve_points_won = ratio_inversion(
                        first_serve_points_won_winner / first_serve_points_won_loser, inverse_class)
                    second_serve_points_won_winner = player1_database_tuple[20]
                    second_serve_points_won_loser = player2_database_tuple[20] + 1e-6
                    second_serve_points_won = ratio_inversion(
                        second_serve_points_won_winner / second_serve_points_won_loser, inverse_class)

                    # break_points_faced
                    break_points_faced_winner = player1_database_tuple[21]
                    break_points_faced_loser = player2_database_tuple[21] + 1e-6
                    break_points_faced = ratio_inversion(break_points_faced_winner / break_points_faced_loser,
                                                         inverse_class)

                    # break_points_saved
                    break_points_saved_winner = player1_database_tuple[22]
                    break_points_saved_loser = player2_database_tuple[22] + 1e-6
                    break_points_saved = ratio_inversion(break_points_saved_winner / break_points_saved_loser,
                                                         inverse_class)

                    # service_games_played
                    service_games_played_winner = player1_database_tuple[23]
                    service_games_played_loser = player2_database_tuple[23] + 1e-6
                    service_games_played = ratio_inversion(service_games_played_winner / service_games_played_loser,
                                                           inverse_class)

                    # service_games_won
                    service_games_won_winner = player1_database_tuple[24]
                    service_games_won_loser = player2_database_tuple[24] + 1e-6
                    service_games_won = ratio_inversion(service_games_won_winner / service_games_won_loser,
                                                        inverse_class)

                    # total_service_points_won
                    total_service_points_won_winner = player1_database_tuple[25]
                    total_service_points_won_loser = player2_database_tuple[25] + 1e-6
                    total_service_points_won = ratio_inversion(
                        total_service_points_won_winner / total_service_points_won_loser, inverse_class)

                    # first_serve_return_points_won
                    first_serve_return_points_won_winner = player1_database_tuple[26]
                    first_serve_return_points_won_loser = player2_database_tuple[26] + 1e-6
                    first_serve_return_points_won = ratio_inversion(
                        first_serve_return_points_won_winner / first_serve_return_points_won_loser, inverse_class)

                    # second_serve_return_points_won
                    second_serve_return_points_won_winner = player1_database_tuple[27]
                    second_serve_return_points_won_loser = player2_database_tuple[27] + 1e-6
                    second_serve_return_points_won = ratio_inversion(
                        second_serve_return_points_won_winner / second_serve_return_points_won_loser, inverse_class)

                    # break_points_opportunities
                    break_points_opportunities_winner = player1_database_tuple[28]
                    break_points_opportunities_loser = player2_database_tuple[28] + 1e-6
                    break_points_opportunities = ratio_inversion(
                        break_points_opportunities_winner / break_points_opportunities_loser, inverse_class)

                    # break_points_converted
                    break_points_converted_winner = player1_database_tuple[29]
                    break_points_converted_loser = player2_database_tuple[29] + 1e-6
                    break_points_converted = ratio_inversion(
                        break_points_converted_winner / break_points_converted_loser, inverse_class)

                    # return_games_played
                    return_games_played_winner = player1_database_tuple[30]
                    return_games_played_loser = player2_database_tuple[30] + 1e-6
                    return_games_played = ratio_inversion(return_games_played_winner / return_games_played_loser,
                                                          inverse_class)

                    # return_games_won
                    return_games_won_winner = player1_database_tuple[31]
                    return_games_won_loser = player2_database_tuple[31] + 1e-6
                    return_games_won = ratio_inversion(return_games_won_winner / return_games_won_loser, inverse_class)

                    # return_points_won
                    return_points_won_winner = player1_database_tuple[32]
                    return_points_won_loser = player2_database_tuple[32] + 1e-6
                    return_points_won = ratio_inversion(return_points_won_winner / return_points_won_loser,
                                                        inverse_class)

                    # total_points_won
                    total_points_won_winner = player1_database_tuple[33]
                    total_points_won_loser = player2_database_tuple[33] + 1e-6
                    total_points_won = ratio_inversion(total_points_won_winner / total_points_won_loser, inverse_class)

                    winner_betting_odds = 1
                    loser_betting_odds = 1
                    if inverse_class:
                        winner_betting_odds = float(row[29])
                        loser_betting_odds = float(row[28])
                    else:
                        winner_betting_odds = float(row[28])
                        loser_betting_odds = float(row[29])

                    list_of_htwoh_pairs_found = h2h_2024_database.find_pairs_in_database_and_return_them(
                        player1_database_tuple[0], player2_database_tuple[0])

                    # we need to find the one with the closest date to the match date
                    match_date = datetime.strptime(row[3], "%m/%d/%Y")
                    difference = 10e6
                    index = -1
                    for i, pair in enumerate(list_of_htwoh_pairs_found):
                        found_date = datetime.strptime(pair[4], "%d/%m/%Y")
                        difference_in_dates = match_date - found_date
                        if difference_in_dates.days < difference:
                            difference = difference_in_dates.days
                            index = i

                    wins_first_player = 0
                    wins_second_player = 0
                    if len(list_of_htwoh_pairs_found) > 0:
                        if player1_database_tuple[0] == list_of_htwoh_pairs_found[index][0] and \
                                player2_database_tuple[
                                    0] == list_of_htwoh_pairs_found[index][1]:
                            wins_first_player = int(list_of_htwoh_pairs_found[index][2])
                            wins_second_player = int(list_of_htwoh_pairs_found[index][3])
                        else:
                            wins_first_player = int(list_of_htwoh_pairs_found[index][3])
                            wins_second_player = int(list_of_htwoh_pairs_found[index][2])

                    tuple_to_add_to_the_dataset = (
                        surface.value,
                        age,
                        weight,
                        height,
                        turned_pro,
                        rank,
                        rank_points,
                        aces,
                        double_faults,
                        first_serve,
                        first_serve_points_won,
                        second_serve_points_won,
                        break_points_faced,
                        break_points_saved,
                        service_games_played,
                        service_games_won,
                        total_service_points_won,
                        first_serve_return_points_won,
                        second_serve_return_points_won,
                        break_points_opportunities,
                        break_points_converted,
                        return_games_played,
                        return_games_won,
                        return_points_won,
                        total_points_won,
                        wins_first_player,
                        wins_second_player,
                        winner_betting_odds,
                        loser_betting_odds
                    )

                    tuple_to_add_to_the_dataset = tuple(float(x) for x in tuple_to_add_to_the_dataset)

                    number_to_add_to_results = 0 if inverse_class else 1
                    dataset_to_return_features.append(tuple_to_add_to_the_dataset)
                    dataset_to_return_results.append(number_to_add_to_results)
                else:
                    if player1_database_tuple is None:
                        print("PLAYER1 NOT FOUND: ", row[9])
                    if player2_database_tuple is None:
                        print("PLAYER2 NOT FOUND: ", row[10])
            except:
                print("An error occurred:")
                traceback.print_exc()
                continue



    """with open("database/github_dataset/atp_matches_2024.csv") as matches_2024:
        r = reader(matches_2024)

        players_2025_hard = PlayersSqlDatabase(court_type=COURT_TYPE.HARD, year=2024)
        players_2025_clay = PlayersSqlDatabase(court_type=COURT_TYPE.CLAY, year=2024)
        players_2025_grass = PlayersSqlDatabase(court_type=COURT_TYPE.GRASS, year=2024)
        players_2025_carpet = PlayersSqlDatabase(court_type=COURT_TYPE.CARPET, year=2024)

        database_dict_players = {
            COURT_TYPE.HARD: players_2025_hard.get_all_players_from_database(),
            COURT_TYPE.CLAY: players_2025_clay.get_all_players_from_database(),
            COURT_TYPE.GRASS: players_2025_grass.get_all_players_from_database(),
            COURT_TYPE.CARPET: players_2025_carpet.get_all_players_from_database()
        }

        h2h_2024_database = HTWOHSqlDatabase(year=2024)

        for row in list(r)[1:]: #for each
            try:

                inverse_class = random.choices([True, False], weights = [0.35,0.65], k=1)[0] #to have balanced classes
                player_1 = row[10]
                player_2 = row[18]
                surface = database_interface.COURT_TYPE.convert_string_to_court_type(str(row[2]))

                player1_database_tuple = None
                player2_database_tuple = None
                for player in database_dict_players[surface]:
                    if utils.custom_fuzzy_strategy(player_1, player[0]):
                        player1_database_tuple = player
                    if utils.custom_fuzzy_strategy(player_2, player[0]):
                        player2_database_tuple = player
                    if player1_database_tuple is not None and player2_database_tuple is not None:
                        break

                if player1_database_tuple is not None and player2_database_tuple is not None:

                    age_winner = float(row[14])
                    age_loser = float(row[22])
                    age = sign_inversion(age_winner - age_loser, inverse_class)
                    weight_winner = player1_database_tuple[2]
                    weight_loser = player2_database_tuple[2]
                    weight = sign_inversion(weight_winner - weight_loser, inverse_class)
                    height_winner = float(row[12])
                    height_loser = float(row[20])
                    height = sign_inversion(height_winner - height_loser, inverse_class)
                    turned_pro_winner = player1_database_tuple[4]
                    turned_pro_loser = player2_database_tuple[4]
                    turned_pro = None
                    if turned_pro_winner == -1 or turned_pro_loser == -1:
                        turned_pro = -1.0
                    else:
                        turned_pro = sign_inversion(turned_pro_winner - turned_pro_loser, inverse_class)
                    rank_winner = float(row[45])
                    rank_loser = float(row[47])
                    rank = sign_inversion(rank_winner - rank_loser, inverse_class)
                    rank_points_winner = float(row[46])
                    rank_points_loser = float(row[48]) + 1e-6
                    rank_points = ratio_inversion(rank_points_winner / rank_points_loser, inverse_class)

                    aces_winner = player1_database_tuple[16]
                    aces_loser = player2_database_tuple[16] + 1e-6
                    aces = ratio_inversion(aces_winner / aces_loser, inverse_class)
                    double_faults_winner = player1_database_tuple[17]
                    double_faults_loser = player2_database_tuple[17] + 1e-6
                    double_faults = ratio_inversion(double_faults_winner / double_faults_loser, inverse_class)
                    first_serve_winner = player1_database_tuple[18]
                    first_serve_loser = player2_database_tuple[18] + 1e-6
                    first_serve = ratio_inversion(first_serve_winner / first_serve_loser, inverse_class)
                    first_serve_points_won_winner = player1_database_tuple[19]
                    first_serve_points_won_loser = player2_database_tuple[19] + 1e-6
                    first_serve_points_won = ratio_inversion(
                        first_serve_points_won_winner / first_serve_points_won_loser, inverse_class)
                    second_serve_points_won_winner = player1_database_tuple[20]
                    second_serve_points_won_loser = player2_database_tuple[20] + 1e-6
                    second_serve_points_won = ratio_inversion(
                        second_serve_points_won_winner / second_serve_points_won_loser, inverse_class)

                    # break_points_faced
                    break_points_faced_winner = player1_database_tuple[21]
                    break_points_faced_loser = player2_database_tuple[21] + 1e-6
                    break_points_faced = ratio_inversion(break_points_faced_winner / break_points_faced_loser,
                                                         inverse_class)

                    # break_points_saved
                    break_points_saved_winner = player1_database_tuple[22]
                    break_points_saved_loser = player2_database_tuple[22] + 1e-6
                    break_points_saved = ratio_inversion(break_points_saved_winner / break_points_saved_loser,
                                                         inverse_class)

                    # service_games_played
                    service_games_played_winner = player1_database_tuple[23]
                    service_games_played_loser = player2_database_tuple[23] + 1e-6
                    service_games_played = ratio_inversion(service_games_played_winner / service_games_played_loser,
                                                           inverse_class)

                    # service_games_won
                    service_games_won_winner = player1_database_tuple[24]
                    service_games_won_loser = player2_database_tuple[24] + 1e-6
                    service_games_won = ratio_inversion(service_games_won_winner / service_games_won_loser,
                                                        inverse_class)

                    # total_service_points_won
                    total_service_points_won_winner = player1_database_tuple[25]
                    total_service_points_won_loser = player2_database_tuple[25] + 1e-6
                    total_service_points_won = ratio_inversion(
                        total_service_points_won_winner / total_service_points_won_loser, inverse_class)

                    # first_serve_return_points_won
                    first_serve_return_points_won_winner = player1_database_tuple[26]
                    first_serve_return_points_won_loser = player2_database_tuple[26] + 1e-6
                    first_serve_return_points_won = ratio_inversion(
                        first_serve_return_points_won_winner / first_serve_return_points_won_loser, inverse_class)

                    # second_serve_return_points_won
                    second_serve_return_points_won_winner = player1_database_tuple[27]
                    second_serve_return_points_won_loser = player2_database_tuple[27] + 1e-6
                    second_serve_return_points_won = ratio_inversion(
                        second_serve_return_points_won_winner / second_serve_return_points_won_loser, inverse_class)

                    # break_points_opportunities
                    break_points_opportunities_winner = player1_database_tuple[28]
                    break_points_opportunities_loser = player2_database_tuple[28] + 1e-6
                    break_points_opportunities = ratio_inversion(
                        break_points_opportunities_winner / break_points_opportunities_loser, inverse_class)

                    # break_points_converted
                    break_points_converted_winner = player1_database_tuple[29]
                    break_points_converted_loser = player2_database_tuple[29] + 1e-6
                    break_points_converted = ratio_inversion(
                        break_points_converted_winner / break_points_converted_loser, inverse_class)

                    # return_games_played
                    return_games_played_winner = player1_database_tuple[30]
                    return_games_played_loser = player2_database_tuple[30] + 1e-6
                    return_games_played = ratio_inversion(return_games_played_winner / return_games_played_loser,
                                                          inverse_class)

                    # return_games_won
                    return_games_won_winner = player1_database_tuple[31]
                    return_games_won_loser = player2_database_tuple[31] + 1e-6
                    return_games_won = ratio_inversion(return_games_won_winner / return_games_won_loser, inverse_class)

                    # return_points_won
                    return_points_won_winner = player1_database_tuple[32]
                    return_points_won_loser = player2_database_tuple[32] + 1e-6
                    return_points_won = ratio_inversion(return_points_won_winner / return_points_won_loser,
                                                        inverse_class)

                    # total_points_won
                    total_points_won_winner = player1_database_tuple[33]
                    total_points_won_loser = player2_database_tuple[33] + 1e-6
                    total_points_won = ratio_inversion(total_points_won_winner / total_points_won_loser, inverse_class)

                    # now we need to calculate the head two head ratios
                    # first we need to find the database
                    list_of_htwoh_pairs_found = h2h_2024_database.find_pairs_in_database_and_return_them(
                        player1_database_tuple[0], player2_database_tuple[0])

                    # we need to find the one with the closest date to the match date
                    match_date = datetime.strptime(row[5], "%Y%m%d")
                    difference = 10e6
                    index = -1
                    for i, pair in enumerate(list_of_htwoh_pairs_found):
                        found_date = datetime.strptime(pair[4], "%d-%m-%Y")
                        difference_in_dates = match_date - found_date
                        if difference_in_dates.days < difference:
                            difference = difference_in_dates.days
                            index = i

                    wins_first_player = 0
                    wins_second_player = 0
                    if len(list_of_htwoh_pairs_found) > 0:
                        if player1_database_tuple[0] == list_of_htwoh_pairs_found[index][0] and player2_database_tuple[
                            0] == list_of_htwoh_pairs_found[index][1]:
                            wins_first_player = int(list_of_htwoh_pairs_found[index][2])
                            wins_second_player = int(list_of_htwoh_pairs_found[index][3])
                        else:
                            wins_first_player = int(list_of_htwoh_pairs_found[index][3])
                            wins_second_player = int(list_of_htwoh_pairs_found[index][2])

                    # now we are ready to add the vector to the dataset
                    tuple_to_add_to_the_dataset = (
                        surface.value,
                        age,
                        weight,
                        height,
                        turned_pro,
                        rank,
                        rank_points,
                        aces,
                        double_faults,
                        first_serve,
                        first_serve_points_won,
                        second_serve_points_won,
                        break_points_faced,
                        break_points_saved,
                        service_games_played,
                        service_games_won,
                        total_service_points_won,
                        first_serve_return_points_won,
                        second_serve_return_points_won,
                        break_points_opportunities,
                        break_points_converted,
                        return_games_played,
                        return_games_won,
                        return_points_won,
                        total_points_won,
                        wins_first_player,
                        wins_second_player
                    )

                    tuple_to_add_to_the_dataset = tuple(float(x) for x in tuple_to_add_to_the_dataset)

                    number_to_add_to_results = 0 if inverse_class else 1
                    dataset_to_return_features.append(tuple_to_add_to_the_dataset)
                    dataset_to_return_results.append(number_to_add_to_results)
            except:
                continue
    matches_extracted_2024 = len(dataset_to_return_features)
    print("2024 matches extracted: ", matches_extracted_2024)
    with open("database/github_dataset/atp_tennis.csv", "r") as matches:
        r = reader(matches)
        sum = 0

        players_2025_hard = PlayersSqlDatabase(court_type=COURT_TYPE.HARD, year=2025)
        players_2025_clay = PlayersSqlDatabase(court_type=COURT_TYPE.CLAY, year=2025)
        players_2025_grass = PlayersSqlDatabase(court_type=COURT_TYPE.GRASS, year=2025)
        players_2025_carpet = PlayersSqlDatabase(court_type=COURT_TYPE.CARPET, year=2025)

        database_dict_players = {
            COURT_TYPE.HARD: players_2025_hard.get_all_players_from_database(),
            COURT_TYPE.CLAY: players_2025_clay.get_all_players_from_database(),
            COURT_TYPE.GRASS: players_2025_grass.get_all_players_from_database(),
            COURT_TYPE.CARPET: players_2025_carpet.get_all_players_from_database()
        }

        h2h_2025_database = HTWOHSqlDatabase(year=2025)

        for row in list(r)[1:]:
            if "2025" in row[1]:
                try:
                    surface = COURT_TYPE.convert_string_to_court_type(row[4])
                    player_1_name = row[7]
                    player_2_name = row[8]
                    winner = row[9]

                    player1_database_tuple = None
                    player2_database_tuple = None
                    winner_database_tuple = None
                    for player in database_dict_players[surface]:
                        if utils.custom_fuzzy_strategy(player_1_name, player[0]):
                            player1_database_tuple = player
                        if utils.custom_fuzzy_strategy(player_2_name, player[0]):
                            player2_database_tuple = player
                        if utils.custom_fuzzy_strategy(winner, player[0]):
                            winner_database_tuple = player
                        if player1_database_tuple is not None and player2_database_tuple is not None and winner_database_tuple is not None:
                            break

                    if player1_database_tuple is not None and player2_database_tuple is not None and winner_database_tuple is not None:
                        age_player_1 = player1_database_tuple[1]
                        age_player_2 = player2_database_tuple[1]
                        age = age_player_1 - age_player_2

                        weight_player_1 = player1_database_tuple[2]
                        weight_player_2 = player2_database_tuple[2]
                        weight = weight_player_1 - weight_player_2

                        height_player_1 = player1_database_tuple[3]
                        height_player_2 = player2_database_tuple[3]
                        height = height_player_1 - height_player_2

                        turned_pro_player_1 = player1_database_tuple[4]
                        turned_pro_player_2 = player2_database_tuple[4]

                        turned_pro = -1.0
                        if turned_pro_player_1 != -1 and turned_pro_player_2 != -1:
                            turned_pro = turned_pro_player_1 - turned_pro_player_2

                        rank_player_1 = float(row[10])
                        rank_player_2 = float(row[11])

                        rank = rank_player_1 - rank_player_2

                        rank_points_player_1 = float(row[12])
                        rank_points_player_2 = float(row[13])

                        rank_points = rank_points_player_1 / (rank_points_player_2 + 1e-6)

                        aces_winner = player1_database_tuple[16]
                        aces_loser = player2_database_tuple[16] + 1e-6
                        aces = aces_winner / aces_loser
                        double_faults_winner = player1_database_tuple[17]
                        double_faults_loser = player2_database_tuple[17] + 1e-6
                        double_faults = double_faults_winner / double_faults_loser
                        first_serve_winner = player1_database_tuple[18]
                        first_serve_loser = player2_database_tuple[18] + 1e-6
                        first_serve = first_serve_winner / first_serve_loser
                        first_serve_points_won_winner = player1_database_tuple[19]
                        first_serve_points_won_loser = player2_database_tuple[19] + 1e-6
                        first_serve_points_won = first_serve_points_won_winner / first_serve_points_won_loser
                        second_serve_points_won_winner = player1_database_tuple[20]
                        second_serve_points_won_loser = player2_database_tuple[20] + 1e-6
                        second_serve_points_won = second_serve_points_won_winner / second_serve_points_won_loser

                        # break_points_faced
                        break_points_faced_winner = player1_database_tuple[21]
                        break_points_faced_loser = player2_database_tuple[21] + 1e-6
                        break_points_faced = break_points_faced_winner / break_points_faced_loser

                        # break_points_saved
                        break_points_saved_winner = player1_database_tuple[22]
                        break_points_saved_loser = player2_database_tuple[22] + 1e-6
                        break_points_saved = break_points_saved_winner / break_points_saved_loser

                        # service_games_played
                        service_games_played_winner = player1_database_tuple[23]
                        service_games_played_loser = player2_database_tuple[23] + 1e-6
                        service_games_played = service_games_played_winner / service_games_played_loser

                        # service_games_won
                        service_games_won_winner = player1_database_tuple[24]
                        service_games_won_loser = player2_database_tuple[24] + 1e-6
                        service_games_won = service_games_won_winner / service_games_won_loser

                        # total_service_points_won
                        total_service_points_won_winner = player1_database_tuple[25]
                        total_service_points_won_loser = player2_database_tuple[25] + 1e-6
                        total_service_points_won = total_service_points_won_winner / total_service_points_won_loser

                        # first_serve_return_points_won
                        first_serve_return_points_won_winner = player1_database_tuple[26]
                        first_serve_return_points_won_loser = player2_database_tuple[26] + 1e-6
                        first_serve_return_points_won = first_serve_return_points_won_winner / first_serve_return_points_won_loser

                        # second_serve_return_points_won
                        second_serve_return_points_won_winner = player1_database_tuple[27]
                        second_serve_return_points_won_loser = player2_database_tuple[27] + 1e-6
                        second_serve_return_points_won = second_serve_return_points_won_winner / second_serve_return_points_won_loser

                        # break_points_opportunities
                        break_points_opportunities_winner = player1_database_tuple[28]
                        break_points_opportunities_loser = player2_database_tuple[28] + 1e-6
                        break_points_opportunities = break_points_opportunities_winner / break_points_opportunities_loser

                        # break_points_converted
                        break_points_converted_winner = player1_database_tuple[29]
                        break_points_converted_loser = player2_database_tuple[29] + 1e-6
                        break_points_converted = break_points_converted_winner / break_points_converted_loser

                        # return_games_played
                        return_games_played_winner = player1_database_tuple[30]
                        return_games_played_loser = player2_database_tuple[30] + 1e-6
                        return_games_played = return_games_played_winner / return_games_played_loser

                        # return_games_won
                        return_games_won_winner = player1_database_tuple[31]
                        return_games_won_loser = player2_database_tuple[31] + 1e-6
                        return_games_won = return_games_won_winner / return_games_won_loser

                        # return_points_won
                        return_points_won_winner = player1_database_tuple[32]
                        return_points_won_loser = player2_database_tuple[32] + 1e-6
                        return_points_won = return_points_won_winner / return_points_won_loser

                        # total_points_won
                        total_points_won_winner = player1_database_tuple[33]
                        total_points_won_loser = player2_database_tuple[33] + 1e-6
                        total_points_won = total_points_won_winner / total_points_won_loser

                        list_of_htwoh_pairs_found = h2h_2025_database.find_pairs_in_database_and_return_them(
                            player1_database_tuple[0], player2_database_tuple[0])

                        # we need to find the one with the closest date to the match date
                        match_date = datetime.strptime(row[1], "%Y-%m-%d")
                        difference = 10e6
                        index = -1
                        for i, pair in enumerate(list_of_htwoh_pairs_found):
                            found_date = datetime.strptime(pair[4], "%d/%m/%Y")
                            difference_in_dates = match_date - found_date
                            if difference_in_dates.days < difference:
                                difference = difference_in_dates.days
                                index = i

                        wins_first_player = 0
                        wins_second_player = 0
                        if len(list_of_htwoh_pairs_found) > 0:
                            if player1_database_tuple[0] == list_of_htwoh_pairs_found[index][0] and \
                                    player2_database_tuple[
                                        0] == list_of_htwoh_pairs_found[index][1]:
                                wins_first_player = int(list_of_htwoh_pairs_found[index][2])
                                wins_second_player = int(list_of_htwoh_pairs_found[index][3])
                            else:
                                wins_first_player = int(list_of_htwoh_pairs_found[index][3])
                                wins_second_player = int(list_of_htwoh_pairs_found[index][2])

                        tuple_to_add_to_the_dataset = (
                            surface.value if type(surface.value) is int else surface.value[0],
                            age,
                            weight,
                            height,
                            turned_pro,
                            rank,
                            rank_points,
                            aces,
                            double_faults,
                            first_serve,
                            first_serve_points_won,
                            second_serve_points_won,
                            break_points_faced,
                            break_points_saved,
                            service_games_played,
                            service_games_won,
                            total_service_points_won,
                            first_serve_return_points_won,
                            second_serve_return_points_won,
                            break_points_opportunities,
                            break_points_converted,
                            return_games_played,
                            return_games_won,
                            return_points_won,
                            total_points_won,
                            wins_first_player,
                            wins_second_player
                        )

                        #print(tuple_to_add_to_the_dataset)

                        tuple_to_add_to_the_dataset = tuple(float(x) for x in tuple_to_add_to_the_dataset)

                        number_to_add_to_results = 1 if player1_database_tuple[0] == winner[0] else 0

                        dataset_to_return_features.append(tuple_to_add_to_the_dataset)
                        dataset_to_return_results.append(number_to_add_to_results)
                except:
                    continue

    print("2025 matches extracted: ", length_hint(dataset_to_return_features) - matches_extracted_2024)"""
    print(len(dataset_to_return_features))
    return dataset_to_return_features, dataset_to_return_results

#print(prepare_training_and_test_set()[0][0])
#we do not have all h2h stats from 2025

# Modelling
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint

def split_set_into_training_and_test_set():
    dataset, dataset_results = prepare_training_and_test_set()
    length_of_dataset = len(dataset)
    print("Entire dataset length: ", length_of_dataset)
    training_length = int(0.8*length_of_dataset)
    #shuffle the dataset and the dataset results
    combined = list(zip(dataset, dataset_results))
    random.shuffle(combined)
    dataset[:], dataset_results[:] = zip(*combined)

    return dataset[:training_length], dataset_results[:training_length], dataset[training_length:], dataset_results[training_length:]

def train_decision_forest():
    X_train, Y_train, X_test, Y_test = split_set_into_training_and_test_set()

    print("Count of classes: ", np.bincount(Y_train))

    print("Xtrain length: ", len(X_train))
    max_accuracy = 0
    argmax_depth = 0
    argmax_estimators = 0
    for i in range(29, 51):
        for j in range(30, 100):
            random_forest = RandomForestClassifier(max_depth=i, n_estimators=j)

            random_forest.fit(np.array(X_train, dtype=np.float64), np.array(Y_train, dtype=np.float64))

            y_pred = random_forest.predict(np.array(X_test, dtype=np.float64))

            accuracy = accuracy_score(np.array(Y_test), y_pred)
            print("Final accuracy: ", accuracy_score(np.array(Y_test), y_pred))
            print("With max depth: ", i)
            print(f"With {j} estimators")

            if accuracy > max_accuracy:
                max_accuracy = accuracy
                argmax_depth = i
                argmax_estimators = j

    print("max accuracy: ", max_accuracy)
    print("With depth: ", argmax_depth)
    print("With estimators: ", argmax_estimators)

def train_single_decision_forest(max_depth: int, n_estimators: int):
    random_forest = RandomForestClassifier(max_depth=max_depth, n_estimators=n_estimators)
    X_train, Y_train, X_test, Y_test = split_set_into_training_and_test_set()



    random_forest.fit(np.array(X_train, dtype=np.float64), np.array(Y_train, dtype=np.float64))

    y_pred = random_forest.predict(np.array(X_test, dtype=np.float64))

    accuracy = accuracy_score(np.array(Y_test), y_pred)
    print("Final accuracy: ", accuracy_score(np.array(Y_test), y_pred))

    cm = confusion_matrix(Y_test, y_pred)
    print("Confusion matrix: ", cm)
    #[[TN FP]
    #[FN TP]]
    joblib.dump(random_forest, "model.pkl")

def predict_sample(sample: tuple):
    model = joblib.load("model.pkl")
    sample_1 = model.predict([sample])
    probality = model.predict_proba(np.array(sample).reshape(1,-1))
    print("Probability of winning: ", probality)
    if sample_1 == 0:
        print("Model prediction: Player 2 wins")
    elif sample_1 == 1:
        print("Model prediction: Player 1 wins")

    return f"The probability of player 1 winning is {probality[0][1]} and the probability of player 2 winning is {probality[0][0]}"

def predict_winner(player1_tuple: tuple, player2_tuple: tuple, surface: COURT_TYPE, wins_first_player: int, wins_second_player: int):
    age = player1_tuple[0] - player2_tuple[0]
    weight = player1_tuple[1] - player2_tuple[1]
    height = player1_tuple[2] - player2_tuple[2]
    turned_pro = player1_tuple[3] - player2_tuple[3]
    rank = player1_tuple[4] - player2_tuple[4]
    rank_points = (player1_tuple[5]) / (player2_tuple[5] + 1e-6)
    aces = (player1_tuple[6]) / (player2_tuple[6] + 1e-6)

    double_faults = (player1_tuple[7]) / (player2_tuple[7] + 1e-6)
    first_serve = (player1_tuple[8]) / (player2_tuple[8] + 1e-6)
    first_serve_points_won = (player1_tuple[9]) / (player2_tuple[9] + 1e-6)
    second_serve_points_won = (player1_tuple[10]) / (player2_tuple[10] + 1e-6)
    break_points_faced = (player1_tuple[11]) / (player2_tuple[11] + 1e-6)
    break_points_saved = (player1_tuple[12]) / (player2_tuple[12] + 1e-6)
    service_games_played = (player1_tuple[13]) / (player2_tuple[13] + 1e-6)
    service_games_won = (player1_tuple[14]) / (player2_tuple[14] + 1e-6)
    total_service_points_won = (player1_tuple[15]) / (player2_tuple[15] + 1e-6)
    first_serve_return_points_won = (player1_tuple[16]) / (player2_tuple[16] + 1e-6)
    second_serve_return_points_won = (player1_tuple[17]) / (player2_tuple[17] + 1e-6)
    break_points_opportunities = (player1_tuple[18]) / (player2_tuple[18] + 1e-6)
    break_points_converted = player1_tuple[19] / (player2_tuple[19] + 1e-6)
    return_games_played = player1_tuple[20] / (player2_tuple[20] + 1e-6)
    return_games_won = player1_tuple[21] / (player2_tuple[21] + 1e-6)
    return_points_won = player1_tuple[22] / (player2_tuple[22] + 1e-6)
    total_points_won = player1_tuple[23] / (player2_tuple[23] + 1e-6)

    player1_odds = player1_tuple[24]
    player2_odds = player2_tuple[24]

    features = (
        surface.value,
        age,
        weight,
        height,
        turned_pro,
        rank,
        rank_points,
        aces,
        double_faults,
        first_serve,
        first_serve_points_won,
        second_serve_points_won,
        break_points_faced,
        break_points_saved,
        service_games_played,
        service_games_won,
        total_service_points_won,
        first_serve_return_points_won,
        second_serve_return_points_won,
        break_points_opportunities,
        break_points_converted,
        return_games_played,
        return_games_won,
        return_points_won,
        total_points_won,
        wins_first_player,
        wins_second_player,
        player1_odds,
        player2_odds
    )

    return predict_sample(features)


#train_decision_forest()



#(
 #                           surface.value if type(surface.value) is int else surface.value[0],
#                          age,
#                            weight,
 #                           height,
  #                          turned_pro,
   #                         rank,
    #                        rank_points,
     #                       aces,
      #                      double_faults,
       #                     first_serve,
        #                    first_serve_points_won,
         #                   second_serve_points_won,
          #                  break_points_faced,
           #                 break_points_saved,
            #                service_games_played,
             #               service_games_won,
              #              total_service_points_won,
               #             first_serve_return_points_won,
                #            second_serve_return_points_won,
                 #           break_points_opportunities,
                  #          break_points_converted,
                   #         return_games_played,
                    #        return_games_won,
                    #        return_points_won,
                     #       total_points_won,
                      #      wins_first_player,
                       #     wins_second_player
                        #)


#train_single_decision_forest(30,76)

#depth 30
#estimators 76
#max accuracy 75%