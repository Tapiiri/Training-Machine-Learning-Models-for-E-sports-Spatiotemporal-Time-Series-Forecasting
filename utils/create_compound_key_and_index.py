import sqlite3

from constants import DB_columns


def create_compound_key_and_index(db_path, table_name, column_names):
    """
    Create a compound key and an index on the given columns in the specified SQLite database table.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Construct the compound key by concatenating the given columns with underscores
    compound_key_expr = " || '_' || ".join(column_names)

    # Check if the compound key column already exists
    check_compound_key_column_sql = f"""
    PRAGMA table_info({table_name});
    """

    cursor.execute(check_compound_key_column_sql)
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    compound_key_exists = DB_columns.COMPOUND_KEY.value in column_names

    if not compound_key_exists:
        # Add a new column for the compound key
        add_compound_key_column_sql = f"""
        ALTER TABLE {table_name}
        ADD COLUMN {DB_columns.COMPOUND_KEY.value} TEXT;
        """
        cursor.execute(add_compound_key_column_sql)

        # Update the new column with the compound key
        update_compound_key_sql = f"""
        UPDATE {table_name}
        SET {DB_columns.COMPOUND_KEY.value} = {compound_key_expr};
        """
        cursor.execute(update_compound_key_sql)

    check_compound_key_index_sql = f"""
        PRAGMA index_list({table_name});
    """

    cursor.execute(check_compound_key_index_sql)
    indices = cursor.fetchall()

    compound_key_index_exists = any(
        index[1] == f"{DB_columns.COMPOUND_KEY.value}_idx" for index in indices)

    if compound_key_index_exists:
        return f"Compound key and index already exist for table '{table_name}' with key expression: {compound_key_expr}"
    else:
        # Create an index on the compound key
        create_index_sql = f"""
        CREATE INDEX IF NOT EXISTS {table_name}_{DB_columns.COMPOUND_KEY.value}_idx ON {table_name} ({DB_columns.COMPOUND_KEY.value});
        """
        cursor.execute(create_index_sql)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    return f"Compound key and index created for table '{table_name}' with key expression: {compound_key_expr}"
