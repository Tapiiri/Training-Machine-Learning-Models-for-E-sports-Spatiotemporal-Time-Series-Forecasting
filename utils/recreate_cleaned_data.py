import sqlite3

from constants import DB_columns
from utils.create_compound_key_and_index import create_compound_key_and_index
from utils.get_data import clear_cache

from constants import GAME_AREA_WIDTH, MAX_TIME, MAX_HP

def recreate_cleaned_data(database_file, table_name):
    conn = sqlite3.connect(database_file)

    cursor = conn.cursor()

    clear_cache(cursor)

    tlol_db_table_name = "champs"

    # Drop previous table

    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.commit()

    cursor.execute(


        f"CREATE TABLE {table_name} AS SELECT * FROM {tlol_db_table_name} WHERE 1=0")

    # Add normalized columns

    cursor.execute(


        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_POS_X.value} FLOAT GENERATED ALWAYS AS ({DB_columns.POS_X.value} / {GAME_AREA_WIDTH}) STORED")

    cursor.execute(


        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_POS_Z.value} FLOAT GENERATED ALWAYS AS ({DB_columns.POS_Z.value} / {GAME_AREA_WIDTH}) STORED")

    cursor.execute(

        f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_TIME.value} FLOAT GENERATED ALWAYS AS ({DB_columns.TIME.value} / {MAX_TIME}) STORED")

    cursor.execute(
            
            f"ALTER TABLE {table_name} ADD COLUMN {DB_columns.NORMALIZED_HP.value} FLOAT GENERATED ALWAYS AS ({DB_columns.HP.value} / {MAX_HP}) STORED")
    conn.commit()

    conn.close()

    # Add data to the new table from original table according to a filter

    # Conditions:

    # Only rows with a name that is not empty

    not_empty_name = f"{DB_columns.NAME.value} IS NOT ''"

    # Only rows with a name that is not "Turret"

    # Only rows with timestamp greater than 5

    timestamp_greater_than_5 = f"{DB_columns.TIME.value} > 5"

    # Only rows with pos_x and pos_y greater between [0, GAME_AREA_WIDTH]

    pos_x_greater_than_0 = f"{DB_columns.POS_X.value} > 0"

    pos_x_less_than_max = f"{DB_columns.POS_X.value} < {GAME_AREA_WIDTH}"

    pos_z_greater_than_0 = f"{DB_columns.POS_Z.value} > 0"

    pos_z_less_than_max = f"{DB_columns.POS_Z.value} < {GAME_AREA_WIDTH}"

    position_between_0_and_max = " AND ".join(


        [pos_x_greater_than_0, pos_x_less_than_max, pos_z_greater_than_0, pos_z_less_than_max])

    # Combine all above filters

    filter_conditions = " AND ".join(


        [not_empty_name, timestamp_greater_than_5, position_between_0_and_max])

    conn = sqlite3.connect(database_file)

    cursor = conn.cursor()

    cursor.execute(


        f"INSERT INTO {table_name} SELECT * FROM {tlol_db_table_name} WHERE {filter_conditions}")

    conn.commit()

    conn.close()

    # Create indices for given columns

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()


    def create_index(cursor, table_name, column_name):
        cursor.execute(
            f"DROP INDEX IF EXISTS {table_name}_{column_name}_index")
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS {table_name}_{column_name}_index ON {table_name}({column_name})")


    columns_to_be_indexed = [DB_columns.NAME.value]

    for column in columns_to_be_indexed:
        create_index(cursor, table_name, column)
    conn.commit()
    conn.close()

    # List out indices

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    cursor.execute(
        f"DROP INDEX IF EXISTS {table_name}_compound_index")
    print(create_compound_key_and_index(database_file, table_name, [
        DB_columns.GAME_ID.value, DB_columns.TEAM.value, DB_columns.NAME.value]))

    indices = cursor.execute(
        f"PRAGMA index_list({table_name})").fetchall()

    table_info = cursor.execute(
        f"PRAGMA table_info({table_name})").fetchall()

    conn.close()

    print(indices)
    print(table_info)