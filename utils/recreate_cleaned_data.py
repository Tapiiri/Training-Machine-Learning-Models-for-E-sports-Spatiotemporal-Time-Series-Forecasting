import sqlite3
import json

from constants import DB_columns
from utils.create_compound_key_and_index import create_compound_key_and_index
from utils.get_data import clear_cache

from constants import GAME_AREA_WIDTH, MAX_TIME, MAX_HP

def recreate_cleaned_data(database_file, table_name):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Check if cache exists in db, clear if it does
    cache_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='count_cache'").fetchone()
    if cache_exists:
        clear_cache(cursor)

    tlol_db_table_name = "champs"

    # Read champions info from JSON
    champions_dict = {}
    with open("denormalization_data.json", "r") as f:
        champions_mapping = json.load(f)["champion_mapping"]
        with open("normalized_champions.json", "r") as f2:
            normalized_champions = json.load(f2)
            for champion_name, champion_id in champions_mapping.items():
                champion = [champ for champ in normalized_champions if champ["Champion"] == champion_id][0]
                champions_dict[champion_name] = champion

    print(champions_dict)

    # Drop previous tables if they exist
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"DROP TABLE IF EXISTS champion_lookup")
    conn.commit()

    # Create a lookup table for champions
    cursor.execute("""
        CREATE TABLE champion_lookup (
            champion_id INTEGER PRIMARY KEY,
            champion_name TEXT UNIQUE
        )
    """)

    # Insert data into the lookup table
    for champion_name, champion_dict in champions_dict.items():
        idx = champion_dict["Champion"]
        cursor.execute("INSERT INTO champion_lookup (champion_id, champion_name) VALUES (?, ?)", (idx, champion_name))

    conn.commit()

    # Create the main table
    cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {tlol_db_table_name} WHERE 1=0")

    # Add normalized columns
    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_POS_X.value} FLOAT GENERATED ALWAYS AS ({DB_columns.POS_X.value} / {GAME_AREA_WIDTH}) STORED")

    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_POS_Z.value} FLOAT GENERATED ALWAYS AS ({DB_columns.POS_Z.value} / {GAME_AREA_WIDTH}) STORED")

    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_TIME.value} FLOAT GENERATED ALWAYS AS ({DB_columns.TIME.value} / {MAX_TIME}) STORED")

    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_HP.value} FLOAT GENERATED ALWAYS AS ({DB_columns.HP.value} / {MAX_HP}) STORED")

    # Generate the CASE statement for the champion_id column
    case_statement = "CASE "
    for champion_name, champion_dict in champions_dict.items():
        idx = champion_dict["Champion"]
        escaped_champion_name = champion_name.replace("'", "''")
        case_statement += f"WHEN {DB_columns.NAME.value} = '{escaped_champion_name}' THEN {idx} "
    case_statement += "ELSE NULL END"

    # Add the generated column using the CASE statement
    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_NAME.value} INTEGER GENERATED ALWAYS AS ({case_statement}) STORED"
    )

    conn.commit()
    conn.close()

    # Add data to the new table from the original table according to a filter
    not_empty_name = f"{DB_columns.NAME.value} IS NOT ''"
    timestamp_greater_than_5 = f"{DB_columns.TIME.value} > 5"
    pos_x_greater_than_0 = f"{DB_columns.POS_X.value} > 0"
    pos_x_less_than_max = f"{DB_columns.POS_X.value} < {GAME_AREA_WIDTH}"
    pos_z_greater_than_0 = f"{DB_columns.POS_Z.value} > 0"
    pos_z_less_than_max = f"{DB_columns.POS_Z.value} < {GAME_AREA_WIDTH}"
    position_between_0_and_max = " AND ".join([pos_x_greater_than_0, pos_x_less_than_max, pos_z_greater_than_0, pos_z_less_than_max])
    filter_conditions = " AND ".join([not_empty_name, timestamp_greater_than_5, position_between_0_and_max])

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO {table_name} SELECT * FROM {tlol_db_table_name} WHERE {filter_conditions}")

    conn.commit()
    conn.close()

    # Create indices for given columns
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    def create_index(cursor, table_name, column_name):
        cursor.execute(f"DROP INDEX IF EXISTS {table_name}_{column_name}_index")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {table_name}_{column_name}_index ON {table_name}({column_name})")

    columns_to_be_indexed = [DB_columns.NAME.value]

    for column in columns_to_be_indexed:
        create_index(cursor, table_name, column)
    conn.commit()
    conn.close()

    # List out indices
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    cursor.execute(f"DROP INDEX IF EXISTS {table_name}_compound_index")
    print(create_compound_key_and_index(database_file, table_name, [DB_columns.GAME_ID.value, DB_columns.TEAM.value, DB_columns.NAME.value]))

    indices = cursor.execute(f"PRAGMA index_list({table_name})").fetchall()
    table_info = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()

    conn.close()

    print(indices)
    print(table_info)