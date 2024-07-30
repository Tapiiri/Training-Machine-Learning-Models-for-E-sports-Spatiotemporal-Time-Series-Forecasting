import sqlite3
import json
from utils.create_compound_key_and_index import create_compound_key_and_index
from utils.get_data import clear_cache
from constants import GAME_AREA_WIDTH, DB_columns

def get_normalized_column_name(column_enum):
    return f"normalized_{column_enum.value.lower()}"

def normalize_column(cursor, table_name, config):
    column_enum = DB_columns[config["column_enum"].upper()]
    column_name = column_enum.value
    normalized_column_name = get_normalized_column_name(column_enum)
    normalization_type = config["normalization_type"]
    
    if normalization_type == "expression":
        normalization_expression = config["normalization_expression"].format(
            column_name=column_name,
            **config["parameters"]
        )
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {normalized_column_name} FLOAT GENERATED ALWAYS AS ({normalization_expression}) STORED"
        )
    elif normalization_type == "case":
        case_statement = "CASE "
        for key, value in config["cases"].items():
            case_statement += f"WHEN {column_name} = '{key}' THEN {value} "
        case_statement += "ELSE NULL END"
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {normalized_column_name} INTEGER GENERATED ALWAYS AS ({case_statement}) STORED"
        )

def clean_and_normalize_table(database_file, table_name, tlol_db_table_name):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Check if cache exists in db, clear if it does
    cache_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='count_cache'").fetchone()
    if cache_exists:
        clear_cache(cursor)

    # Read normalization config from JSON
    with open("normalization_config.json", "r") as f:
        normalization_config = json.load(f)

    # Drop previous tables if they exist
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Create the main table
    cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {tlol_db_table_name} WHERE 1=0")

    # Normalize columns based on the configuration
    for config in normalization_config:
        normalize_column(cursor, table_name, config)

    conn.commit()
    conn.close()

    # Add data to the new table from the original table according to a filter
    filter_conditions = [
        f"{DB_columns.NAME.value} IS NOT ''",
        f"{DB_columns.TIME.value} > 5",
        f"{DB_columns.POS_X.value} > 0",
        f"{DB_columns.POS_X.value} < {GAME_AREA_WIDTH}",
        f"{DB_columns.POS_Z.value} > 0",
        f"{DB_columns.POS_Z.value} < {GAME_AREA_WIDTH}"
    ]
    filter_conditions_str = " AND ".join(filter_conditions)

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO {table_name} SELECT * FROM {tlol_db_table_name} WHERE {filter_conditions_str}")

    conn.commit()
    conn.close()

    # Create indices for given columns
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    def create_index(cursor, table_name, column_enum):
        cursor.execute(f"DROP INDEX IF EXISTS {table_name}_{column_enum.value.lower()}_index")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {table_name}_{column_enum.value.lower()}_index ON {table_name}({column_enum.value})")

    columns_to_be_indexed = [DB_columns.NAME]

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


if __name__ == "__main__":
    database_file = 'EUN1-3502081367.db'
    table_name = 'champs_cleaned'
    tlol_db_table_name = 'champs'
    clean_and_normalize_table(database_file, table_name, tlol_db_table_name)
