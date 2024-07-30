import sqlite3
import json
import os
from enum import Enum

from utils.get_or_create_combined_database import get_or_create_combined_database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to the SQLite database
db_folder = os.getenv("DATABASE_FOLDER")
db_path = get_or_create_combined_database(db_folder)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Retrieve column names and types from the "champs" table
cursor.execute("PRAGMA table_info(champs)")
columns_info = cursor.fetchall()

# Retrieve max values for numeric columns and unique values for string columns
max_values = {}
normalization_columns = []
string_columns = {}

# Add filter to disregard some rows
value_filter = f"time > 5"

for column in columns_info:
    column_name = column[1]
    column_type = column[2]
    
    if column_type in ["REAL", "INTEGER"]:
        cursor.execute(f"SELECT MAX({column_name}) FROM champs WHERE {value_filter}")
        max_value = cursor.fetchone()[0]
        if max_value is not None:
            max_values[column_name] = max_value
            normalization_columns.append(column_name)
    elif column_type == "TEXT":
        cursor.execute(f"SELECT DISTINCT {column_name} FROM champs WHERE {value_filter}")
        unique_values = cursor.fetchall()
        string_columns[column_name] = {value[0]: idx+1 for idx, value in enumerate(unique_values)}

# Close the connection
conn.close()

# Print results for verification
print("Columns Info:")
print(columns_info)

print("\nMax Values:")
print(max_values)

print("\nNormalization Columns:")
print(normalization_columns)

print("\nString Columns:")
print(string_columns)

# Generate the DB_columns enum
db_columns_dict = {col[1].upper(): col[1] for col in columns_info}

# Include normalized versions
for col in columns_info:
    column_name = col[1]
    normalized_column_name = f"normalized_{column_name.lower()}"
    db_columns_dict[normalized_column_name.upper()] = normalized_column_name

DB_columns = Enum('DB_columns', db_columns_dict)

# Print DB_columns enum for verification
print("\nDB_columns Enum:")
for name, member in DB_columns.__members__.items():
    print(f"{name} = {member.value}")

# Helper function to make enum serializable
def enum_to_str(obj):
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Generate normalization configuration
normalization_config = []

for column in columns_info:
    column_name = column[1]
    column_type = column[2]
    
    if column_name in normalization_columns:
        if column_type in ["REAL", "INTEGER"]:
            max_value = max_values.get(column_name, 1)
            config = {
                "column_enum": getattr(DB_columns, column_name.upper()),
                "normalization_type": "expression",
                "normalization_expression": "({column_name} / {max_value})",
                "parameters": {"max_value": max_value}
            }
            normalization_config.append(config)
    elif column_name in string_columns:
        # Add case normalization for string columns
        cases = string_columns[column_name]
        config = {
            "column_enum": getattr(DB_columns, column_name.upper()),
            "normalization_type": "case",
            "cases": cases
        }
        normalization_config.append(config)

# Print normalization config for verification
print("\nNormalization Config:")
print(json.dumps(normalization_config, indent=4, default=enum_to_str))

# Save the normalization config to a JSON file
with open("normalization_config.json", "w") as f:
    json.dump(normalization_config, f, indent=4, default=enum_to_str)

# Generate constants.py file content
constants_content = """from enum import Enum

class DB_columns(Enum):
"""

for name, member in DB_columns.__members__.items():
    constants_content += f"    {name} = \"{member.value}\"\n"

constants_content += """

DEFAULT_DATA_FEATURES = [DB_columns.NORMALIZED_POS_X.value, DB_columns.NORMALIZED_POS_Z.value]

GAME_AREA_WIDTH = 15000
MAX_TIME = 1800
MAX_HP = 5000
"""

# Save the constants.py file
with open("constants.py", "w") as f:
    f.write(constants_content)

# Print constants.py content for verification
print("\nconstants.py Content:")
print(constants_content)