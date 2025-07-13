import os.path
import sqlite3
from enum import Enum
from abc import ABC

from sympy.strategies.core import switch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVALID_ENTRY = "-1"
#types INTEGER REAL TEXT DATE NULL etc...
class DATABASE_ENTRIES_ENUM(Enum):
    PLAYERS = (
        "PLAYERS.db",
        ["name",
         "age",
         "weight",
         "height",
         "turned_pro",
         "plays",
         "rank",
         "winner_rank_points",
         "titles_ytd",
         "global_titles",
         "wins_ytd",
         "loses_ytd",
         "wins_career",
         "loses_career",
         "prize_money_ytd",
         "prize_money_career",
         "aces",
         "double_faults",
         "first_serve",
         "first_serve_points_won",
         "second_serve_points_won",
         "break_points_faced",
         "break_points_saved",
         "service_games_played",
         "service_games_won",
         "total_service_points_won",
         "first_serve_return_points_won",
         "second_serve_return_points_won",
         "break_points_opportunities",
         "break_points_converted",
         "return_games_played",
         "return_games_won",
         "return_points_won",
         "total_points_won"],
        ["TEXT",
         "INTEGER",
         "REAL",
         "INTEGER",
         "INTEGER",
         "TEXT",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "REAL",
         "INTEGER",
         "INTEGER",
         "INTEGER",
         "REAL",
         "REAL",
         "REAL",
         "INTEGER",
         "REAL",
         "INTEGER",
         "REAL",
         "REAL",
         "REAL",
         "REAL",
         "INTEGER",
         "REAL",
         "INTEGER",
         "REAL",
         "REAL",
         "REAL"]
        , "players"
    )

    MATCHES = (
        "MATCHES.db",
        ["player_1_id", "player_2_id", "date", "type_of_court", "winner"]
        , ["INTEGER", "INTEGER", "DATE", "TEXT" , "INTEGER"],
        "matches"
    )

    HTWOH = (
        "H2H.db",
        ["player_1_name", "player_2_name", "player_1_wins", "player_2_wins", "date"],
        ["INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT"],
        "htwoh"
    )

class COURT_TYPE(Enum):
    CLAY = 1
    CARPET = 2
    GRASS = 3
    HARD = 4

    @staticmethod
    def convert_string_to_court_type(str_to_convert: str):
        return COURT_TYPE[f"{str_to_convert.upper()}"]



class SqlDatabase:

    def __init__(self, type: DATABASE_ENTRIES_ENUM, court_type: COURT_TYPE, year: int):
        self.type = type
        self.court_type = court_type
        self.year = year
        self.path = os.path.join(BASE_DIR, str(self.year) + "/" + self.court_type.name + "/")
        self.file_path = os.path.join(self.path, self.type.value[0])
        self.create_database()

    def create_database(self):
        os.makedirs(self.path, exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                pass
            conn = sqlite3.connect(self.file_path)
            headers_string = SqlDatabase.create_database_headers(self.type)
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.type.value[3]} (
                {headers_string});
                """
            )
            conn.commit()
            conn.close()


    @staticmethod
    def create_database_headers(type: DATABASE_ENTRIES_ENUM):
        length = len(type.value[1])
        headers = "".join(
        [f"{type.value[1][i]} {type.value[2][i]},"  if i < length -1 else f"{type.value[1][i]} {type.value[2][i]}" for i in range(length)]
        )
        return headers

    @staticmethod
    def create_headers(type:DATABASE_ENTRIES_ENUM):
        length = len(type.value[1])
        headers = "".join(
            [f"{type.value[1][i]}," if i < length - 1 else f"{type.value[1][i]}"
             for i in range(length)]
        )
        return headers

    @staticmethod
    def create_row_place_holders(type: DATABASE_ENTRIES_ENUM):
        length = len(type.value[1])
        placeholders = "".join(
            [f"?," if i < length - 1 else f"?"
             for i in range(length)]
        )
        return placeholders


    def access_database(self):
        """
            This method returns a connection to the sql database
        """
        #if database does not exist it will be created
        self.create_database()
        conn = sqlite3.connect(self.file_path)
        return conn

    def execute_sql_query(self, sql_query: str, args: tuple):
        """
            This method executes an sql query that we want
        :return:
        """
        conn = self.access_database()
        c = conn.cursor()
        if args is not None:
            c.execute(sql_query, args)
        else:
            c.execute(sql_query)
        c.close()
        


class PlayersSqlDatabase(SqlDatabase):
    def __init__(self, court_type: COURT_TYPE, year: int):
        super().__init__(DATABASE_ENTRIES_ENUM.PLAYERS, court_type, year)


    def write_player_entry_to_database(self, information_tuple: tuple):
        """Writes a valid tuple to the database"""
        assert len(information_tuple) == len(DATABASE_ENTRIES_ENUM.PLAYERS.value[1])

        #get connection to the database
        conn = self.access_database()
        sql = f"""
        INSERT INTO {self.type.value[3]}({SqlDatabase.create_headers(self.type)})
        VALUES ({SqlDatabase.create_row_place_holders(self.type)})
        """
        curr = conn.cursor()
        curr.execute(sql, information_tuple)
        conn.commit()
        conn.close()

    def check_if_name_is_in_database(self, name: str):
        sql_query = f"""
        SELECT * FROM {DATABASE_ENTRIES_ENUM.PLAYERS.value[3]} WHERE name = ?;
        """
        conn = self.access_database()
        cursor = conn.cursor()
        return len(cursor.execute(sql_query, (name,)).fetchall()) > 0

    def get_all_players_from_database(self):
        sql_query = """
        SELECT * FROM players;
        """
        conn = self.access_database()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        list_to_return = cursor.fetchall()
        conn.close()
        return list_to_return


class MatchesSqlDatabase(SqlDatabase):
    def __init__(self, court_type: COURT_TYPE, year: int):
        super().__init__(DATABASE_ENTRIES_ENUM.MATCHES, court_type, year)


    def write_match_entry_to_database(self, information_tuple: tuple):
        """Writes a valid tuple to the database"""
        assert len(information_tuple) == len(DATABASE_ENTRIES_ENUM.MATCHES.value[1])

        #get connection to the database
        conn = self.access_database()
        sql = f"""
        INSERT INTO {self.type.value[3]}({SqlDatabase.create_headers(self.type)})
        VALUES ({SqlDatabase.create_row_place_holders(self.type)})
        """
        curr = conn.cursor()
        curr.execute(sql, information_tuple)
        conn.commit()
        conn.close()

class HTWOHSqlDatabase(SqlDatabase):
    def __init__(self, year: int):
        super().__init__(DATABASE_ENTRIES_ENUM.HTWOH, COURT_TYPE.HARD, year)


    def write_htwoh_entry_to_database(self, information_tuple: tuple):
        """Writes a valid tuple to the database"""
        assert len(information_tuple) == len(DATABASE_ENTRIES_ENUM.HTWOH.value[1])

        #get connection to the database
        conn = self.access_database()
        sql = f"""
        INSERT INTO {self.type.value[3]}({SqlDatabase.create_headers(self.type)})
        VALUES ({SqlDatabase.create_row_place_holders(self.type)})
        """
        curr = conn.cursor()
        curr.execute(sql, information_tuple)
        conn.commit()
        conn.close()

    def check_if_names_are_on_the_database(self, name1: str, name2: str):
        sql_query = f"""
        SELECT * FROM htwoh WHERE player_1_name = ? AND player_2_name = ?;
        """
        conn = self.access_database()
        c = conn.cursor()
        c.execute(sql_query, (name1, name2))
        list_to_return = c.fetchall()
        conn.close()
        return len(list_to_return) > 0

    def find_pairs_in_database_and_return_them(self, name1: str, name2: str):
        sql_query = f"""
        SELECT * FROM htwoh WHERE player_1_name = ? AND player_2_name = ? OR player_1_name = ? AND player_2_name = ?;
        """
        conn = self.access_database()
        c = conn.cursor()
        c.execute(sql_query, (name1, name2, name2, name1))
        list_to_return = c.fetchall()
        c.close()
        return list_to_return

    def find_all_from_database(self):
        sql_query = f"""
        SELECT * FROM htwoh;
        """
        conn = self.access_database()
        c = conn.cursor()
        list_to_return = c.fetchall()
        conn.close(

        )
        return list_to_return


HTWOHSqlDatabase(year=2025).execute_sql_query("""
UPDATE htwoh
SET date = '03/07/2025';
""", None)

"""
PlayersSqlDatabase(COURT_TYPE.CLAY, 2025).write_player_entry_to_database(("n", 1, 1.0, 12, 2020,
         "plays", 15, 0.5, 1,
         5, 5, 0.2,
        0.2, 0.2,
         5, 5,
         4, 4,
         4, 4,
         4, 5,
         6, 7, 8,
         7, 10))"""

