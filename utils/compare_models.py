from collections import defaultdict
import sqlite3
import numpy as np
from tqdm import tqdm
from constants import DEFAULT_DATA_FEATURES
from utils.get_data import fetch_data_batches
from utils.create_sequences_in_batches import create_sequences_from_database_rows
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error  # type: ignore
from sklearn.model_selection import train_test_split

def compare_models(database_file, table_name, H_values, T_values, model_getters, data_features=DEFAULT_DATA_FEATURES, filter="1=1", total_keys_to_fetch=100, batch_size=20, train=True):
    absolute_errors = defaultdict(list)
    mse_results = defaultdict(list)
    trained_models = {}
    max_H = max(H_values)
    max_T = max(T_values)

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    pbar = tqdm(total=len(H_values) * len(T_values) *
                len(model_getters), desc='Model loop')

    offset = 0  # Start offset
    remaining_keys = total_keys_to_fetch

    while remaining_keys > 0:
        limit = min(batch_size, remaining_keys)

        # Fetch and process data in batches
        data = fetch_data_batches(
            cursor, table_name, filter, offset, limit, data_features)

        if len(data) == 0:
            break  # No more data to process

        for H in H_values:
            for T in tqdm(T_values, desc=f'H={H}', leave=False):
                # Calculate the sequence on the fly
                sequence = create_sequences_from_database_rows(
                    data, H, T, max_H, max_T)
                X, y = sequence
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, train_size=0.8, shuffle=True)
                if X_train.size == 0 or y_train.size == 0:
                    print(f'No data for H={H}, T={T}')
                    pbar.update(len(model_getters))
                    continue
                models = {model_name: model_getter(
                    H, T) for model_name, model_getter in model_getters.items()}
                for model_name, (model, features, input_shape) in tqdm(models.items(), desc=f'T={T}', leave=False):
                    print(
                        f'Fitting model {model_name} with features {features}')
                    X_train_features = X_train[:, :, [
                        data_features.index(feature) for feature in features]]
                    X_train_reshaped = X_train_features.reshape(input_shape)
                    model.fit(X_train_reshaped, y_train)
                    X_test_features = X_test[:, :, [
                        data_features.index(feature) for feature in features]].reshape(input_shape)
                    X_test_reshaped = X_test_features.reshape(input_shape)
                    y_pred = model.predict(X_test_reshaped)
                    mse = np.sqrt(mean_squared_error(y_test, y_pred))
                    mse_results[(H, T, model_name)] += [mse]
                    absolute_errors[(H, T, model_name)] = [np.abs(
                        y_test - y_pred)]
                    if train:
                        trained_models[(H, T, model_name)] = model
                    pbar.update(1)

        # Update offset and remaining keys
        offset += limit
        remaining_keys -= limit

    pbar.close()
    conn.close()
    return trained_models, mse_results, absolute_errors