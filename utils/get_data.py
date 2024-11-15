import dis
import sqlite3
from collections import defaultdict
import numpy as np
from tqdm import tqdm
from typing import Any, Dict, List

from constants import DB_columns, DEFAULT_DATA_FEATURES

# Get table columns
def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return columns

# In-memory cache
cache: Dict[str, Any] = {
    "counts": {},
    "keys": {}
}

# Function to create cache table if it doesn't exist
def create_cache_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS count_cache (
            table_name TEXT,
            filter TEXT,
            counts TEXT,
            PRIMARY KEY (table_name, filter)
        )
    """)
    cursor.connection.commit()

def clear_cache(cursor):
    global cache
    cache["counts"] = {}

    # Clear cache table
    cursor.execute("DELETE FROM count_cache")
    cursor.connection.commit()

# Function to fetch count from cache
def fetch_count_from_cache(cursor, table_name, filter):
    cursor.execute("""
        SELECT counts FROM count_cache WHERE table_name = ? AND filter = ?
    """, (table_name, filter))
    row = cursor.fetchone()
    if row:
        counts = eval(row[0])
        return counts
    return None

# Function to save count to cache
def save_count_to_cache(cursor, table_name, filter, counts):
    global cache 

    counts_str = str(counts)
    cursor.execute("""
        INSERT OR REPLACE INTO count_cache (table_name, filter, counts) VALUES (?, ?, ?)
    """, (table_name, filter, counts_str))

    cursor.connection.commit()
    cache["counts"][filter] = {
        "counts": counts
    }


# Get amount of unique keys in a table
def get_unique_key_count(cursor, table_name, filter="1=1"):
    global cache

    # Create cache table if it doesn't exist
    create_cache_table(cursor)

    count_query = f"""
        SELECT COUNT(DISTINCT {DB_columns.COMPOUND_KEY.value})
        FROM {table_name}
        WHERE {filter}
    """
        
    # Check in-memory cache
    if count_query in cache["keys"]:
        print("Using in-memory cache for keys")
        keys = cache["keys"][count_query]
        return keys

    # Check database cache
    keys = fetch_count_from_cache(cursor, table_name, count_query)

    if keys is not None:
        print("Using database cache for key count")
        cache["keys"][count_query] = keys
        return keys

    print("Counting keys...")
    cursor.execute(count_query)
    key_count = cursor.fetchone()[0]
    print(f"Key count: {key_count}")

    # Save results to cache table
    save_count_to_cache(cursor, table_name, count_query, key_count)

    return key_count


def get_counts(cursor, table_name, filter="1=1", limit=None, offset=None, recreate_cache=False):
    global cache
    
    if recreate_cache:
        cursor.execute("DELETE FROM count_cache")
    # Create cache table if it doesn't exist
    create_cache_table(cursor)
    
    count_query = f"""
        SELECT COUNT(*), {DB_columns.COMPOUND_KEY.value}
        FROM {table_name}
        WHERE {filter}
        GROUP BY {DB_columns.COMPOUND_KEY.value}
        ORDER BY {DB_columns.COMPOUND_KEY.value}
    """
    if limit is not None:
        count_query += f" LIMIT {limit}"
    if offset is not None:
        count_query += f" OFFSET {offset}"

    # Check in-memory cache
    if count_query in cache["counts"]:
        print("Using in-memory cache for counts")
        counts = cache["counts"][count_query]["counts"]
        return counts

    # Check database cache
    counts = fetch_count_from_cache(cursor, table_name, count_query)
    if counts is not None:
        print("Using database cache for counts")
        cache["counts"][count_query] = {
            "counts": counts
        }
        return counts
            
    print("Counting rows...")
    cursor.execute(count_query)
    counts = cursor.fetchall()
    print(f"Counts: {counts}")
    
    # Save results to cache table
    save_count_to_cache(cursor, table_name, count_query, counts)
    
    return counts

def get_data_by_compound_key(cursor, table_name, offset, limit, filter, data_features=DEFAULT_DATA_FEATURES):
    query = f"""
        SELECT {','.join(data_features)}
        FROM {table_name}
        WHERE {filter}
        ORDER BY {DB_columns.COMPOUND_KEY.value}
        LIMIT {limit} OFFSET {offset}
    """
    return cursor.execute(query).fetchall()

def fetch_data_batches(cursor, table_name, filter, offset, limit, data_features=DEFAULT_DATA_FEATURES):
    counts = get_counts(cursor, table_name, filter, limit=offset+limit, offset=0)
    
    offsets = []
    cumulative_sum = 0
    for count in counts:
        offsets.append(cumulative_sum)
        cumulative_sum += count[0]
    
    rows_per_key = defaultdict(list)
    total_row_offset = offsets[min(offset, len(offsets)-1)]
    total_row_limit = cumulative_sum - total_row_offset
    all_rows = get_data_by_compound_key(cursor, table_name, total_row_offset, total_row_limit, filter, data_features)
    
    for i in range(len(counts))[offset:offset+limit]:
        result_offset = offsets[i] - total_row_offset
        result_count = counts[i][0]
        key_slice = all_rows[result_offset:result_offset + result_count]
        if len(key_slice) > 0:
            rows_per_key[counts[i][1]].extend(key_slice)

    print(f"Fetched {len(rows_per_key.keys())} keys for offset: {offset}, limit: {limit}")    
    return np.array(list(rows_per_key.values()), dtype=object)
