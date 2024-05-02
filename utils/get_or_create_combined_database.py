import os
import sqlite3

from constants import DB_columns


def get_or_create_combined_database(database_folder):
    """
    Get the path to a combined SQLite database file containing all the data from the individual database files in the folder specified by the DATABASE_FOLDER environment variable.
    """
    if not database_folder:
        raise ValueError(
            "DATABASE_FOLDER environment variable not set. Please set it to the folder containing the database file.")

    # Find all SQLite databases in the folder
    database_files = []
    for file in os.listdir(database_folder):
        if file.endswith(".db"):
            database_files.append(os.path.join(database_folder, file))

    if len(database_files) == 0:
        raise ValueError(
            "No SQLite database files found in the folder specified by DATABASE_FOLDER")

    if len(database_files) > 1:
        print(
            f"Found {len(database_files)} database files in the folder specified by DATABASE_FOLDER")
        # See if a database with the name "combined" exists
        combined_db = os.path.join(database_folder, "combined2.db")
        if combined_db in database_files:
            print(f"Found combined database {combined_db}")
            database_files = [combined_db]
        else:
            print(
                f"Combined database {combined_db} not found. Creating a new combined database")
            # If there are multiple databases, create a combined database
            conn = sqlite3.connect(combined_db)
            cursor = conn.cursor()
            # Create the table in the database
            # Column names are the same as the keys in the game_dict
            columns = [DB_columns.NAME.value, DB_columns.POS_X.value, DB_columns.POS_Z.value,
                       DB_columns.TIME.value, DB_columns.HP.value, DB_columns.TEAM.value, DB_columns.GAME_ID.value]
            # column_names = [f"{column}" for column in columns]
            cursor.execute(
                "CREATE TABLE champs (name TEXT, pos_x REAL, pos_z REAL, time REAL, hp REAL, team INTEGER, game_id INTEGER)")

            for database_file in database_files:
                cursor.execute(f"ATTACH DATABASE '{database_file}' AS db")
                cursor.execute(
                    f"INSERT INTO champs SELECT {','.join(columns)} FROM db.champs")
                conn.commit()
                cursor.execute("DETACH DATABASE db")
            conn.close()

            database_files = [combined_db]

    return database_files[0]
