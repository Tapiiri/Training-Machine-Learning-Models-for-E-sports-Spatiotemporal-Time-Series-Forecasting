import dis
import sqlite3
from collections import defaultdict
import numpy as np
from tqdm import tqdm
from typing import Any, Dict, List

from constants import DB_columns, DEFAULT_DATA_FEATURES
# In-memory cache
cache: Dict[str, Any] = {
    "unique_keys": None,
    "counts": None
}

# Function to create cache table if it doesn't exist
def create_cache_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS count_cache (
            table_name TEXT,
            filter TEXT,
            unique_keys INTEGER,
            counts TEXT,
            PRIMARY KEY (table_name, filter)
        )
    """)
    cursor.connection.commit()

# Function to fetch count from cache
def fetch_count_from_cache(cursor, table_name, filter):
    cursor.execute("""
        SELECT unique_keys, counts FROM count_cache WHERE table_name = ? AND filter = ?
    """, (table_name, filter))
    row = cursor.fetchone()
    if row:
        unique_keys = row[0]
        counts = eval(row[1])
        return unique_keys, counts
    return None, None

# Function to save count to cache
def save_count_to_cache(cursor, table_name, filter, unique_keys, counts):
    global cache 

    counts_str = str(counts)
    cursor.execute("""
        INSERT OR REPLACE INTO count_cache (table_name, filter, unique_keys, counts) VALUES (?, ?, ?, ?)
    """, (table_name, filter, unique_keys, counts_str))

    cursor.connection.commit()
    cache["unique_keys"] = unique_keys
    cache["counts"] = counts

def get_counts(cursor, table_name, filter, limit=None, offset=None):
    global cache
    
    # Create cache table if it doesn't exist
    create_cache_table(cursor)
    
    # Check cache for unique_keys and counts
    if cache["unique_keys"] is not None and cache["counts"] is not None:
        unique_keys = cache["unique_keys"]
        counts = cache["counts"]
        return unique_keys, counts
    
    # Check cache table first
    unique_keys, counts = fetch_count_from_cache(cursor, table_name, filter)
    if unique_keys is not None and counts is not None:
        return unique_keys, counts
    
    query = f"SELECT COUNT(DISTINCT {DB_columns.COMPOUND_KEY.value}) FROM {table_name} WHERE {filter}"
    cursor.execute(query)
    unique_keys = cursor.fetchone()[0]
    
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
        
    cursor.execute(count_query)
    counts = cursor.fetchall()
    
    # Save results to cache table
    save_count_to_cache(cursor, table_name, filter, unique_keys, counts)
    
    return unique_keys, counts
def get_data_by_compound_key(cursor, table_name, offset, limit, filter, data_features=DEFAULT_DATA_FEATURES):
    query = f"""
        SELECT {','.join(data_features)}
        FROM {table_name}
        WHERE {filter}
        ORDER BY {DB_columns.COMPOUND_KEY.value}
        LIMIT {limit} OFFSET {offset}
    """
    return cursor.execute(query).fetchall()

# def _get_data(cursor, table_name, offset, limit, counts, offsets, total, filter, data_features=DEFAULT_DATA_FEATURES, show_progress=True):
#     all_rows = get_data_by_compound_key(cursor, table_name, offset, limit, filter, data_features)
#     rows_per_key = defaultdict(list)
    
#     for i in tqdm(range(total), disable=not show_progress):
#         result_offset = offsets[i] - offset
#         result_count = counts[i][0]
#         key_slice = all_rows[result_offset:result_offset + result_count]
#         if len(key_slice) > 0:
#             rows_per_key[counts[i][1]].extend(key_slice)
    
#     return rows_per_key

# def get_data(database_file, table_name, filter="1=1", total_keys_to_fetch=100, batch_size=20, data_features=DEFAULT_DATA_FEATURES, show_progress=True):
#     global cache
    
#     conn = sqlite3.connect(database_file)
#     cursor = conn.cursor()
    
#     # Create cache table if it doesn't exist
#     create_cache_table(cursor)
    
#     # Check cache for unique_keys and counts
#     if cache["unique_keys"] is None or cache["counts"] is None:
#         unique_keys, counts = get_counts(cursor, table_name, filter)
#         cache["unique_keys"] = unique_keys
#         cache["counts"] = counts
#     else:
#         unique_keys = cache["unique_keys"]
#         counts = cache["counts"]
    
#     offsets = []
#     cumulative_sum = 0
#     for count in counts:
#         offsets.append(cumulative_sum)
#         cumulative_sum += count[0]
#     offsets.append(cumulative_sum)
    
#     total = min(total_keys_to_fetch, unique_keys)
#     total_count = offsets[total]
    
#     batches = min(total, batch_size)
#     batch_key_counts = [total // batches] * batches
#     batch_key_counts[-1] += total % batches
    
#     batch_offsets = []
#     batch_counts = []
#     batch_cumulative_sum = []
#     cumulative_sum = 0
    
#     for count in batch_key_counts:
#         batch_offsets.append(offsets[cumulative_sum:count + cumulative_sum])
#         batch_counts.append(counts[cumulative_sum:count + cumulative_sum])
#         batch_cumulative_sum.append(cumulative_sum)
#         cumulative_sum += count
    
#     rows_per_key = defaultdict(list)
#     with tqdm(total=total_count) as pbar:
#         for i in range(batches):
#             offset = offsets[batch_cumulative_sum[i]]
#             limit = offsets[batch_cumulative_sum[i] + batch_key_counts[i]] - offset
#             keys_per_batch = batch_key_counts[i]
            
#             offsets_of_batch = batch_offsets[i]
#             counts_of_batch = batch_counts[i]
            
#             batch_rows_per_key = _get_data(
#                 cursor, table_name, offset, limit, counts_of_batch, offsets_of_batch, keys_per_batch, filter, data_features)
#             for key, rows in batch_rows_per_key.items():
#                 pbar.update(len(rows))
#                 rows_per_key[key].extend(rows)
    
#     conn.close()
    
#     return rows_per_key

def fetch_data_batches(cursor, table_name, filter, offset, limit, data_features=DEFAULT_DATA_FEATURES):
    unique_keys, counts = get_counts(cursor, table_name, filter, limit=limit, offset=offset)
    
    if not counts:
        print(f"No counts returned for offset: {offset}, limit: {limit}")
        return defaultdict(list)
    
    offsets = []
    cumulative_sum = 0
    for count in counts:
        offsets.append(cumulative_sum)
        cumulative_sum += count[0]
    offsets.append(cumulative_sum)
    
    rows_per_key = defaultdict(list)
    all_rows = get_data_by_compound_key(cursor, table_name, offsets[0], cumulative_sum, filter, data_features)
    
    for i in range(len(counts)):
        result_offset = offsets[i]
        result_count = counts[i][0]
        key_slice = all_rows[result_offset:result_offset + result_count]
        if len(key_slice) > 0:
            rows_per_key[counts[i][1]].extend(key_slice)
    
    print(f"Fetched {len(rows_per_key)} keys for offset: {offset}, limit: {limit}")    
    return np.array(list(rows_per_key.values()), dtype=object)
