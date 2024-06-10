import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm


def create_sequences(rows, H, T):
    num_sequences = len(rows) - H - T + 1
    if num_sequences <= 0:
        return np.array([]), np.array([])

    X = np.lib.stride_tricks.sliding_window_view( # type: ignore
        rows, window_shape=(H, rows.shape[1]))[:-T]
    X = X.reshape(X.shape[0], H, -1)
    y = rows[H+T-1:num_sequences+H+T-1]

    return X, y


def create_sequences_from_database_rows(data, H, T, max_H=None, max_T=None, batch_size=1000):
    max_H = max_H or H
    max_T = max_T or T
    X_list, y_list = [], []
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        for rows in batch:
            if len(rows) < H + T:
                continue
            # Ensure all sequences are from the same points in time
            equilength_rows = np.array(rows)[max_H-H:-(max_T-T+1)]
            _X, _y = create_sequences(equilength_rows, H, T)
            if _X.size > 0 and _y.size > 0:
                X_list.append(_X)
                y_list.append(_y)

    if X_list and y_list:
        X = np.concatenate(X_list, axis=0)
        y = np.concatenate(y_list, axis=0)
    else:
        X, y = np.array([]), np.array([])

    return X, y


def calculate_sequences_in_batches(H_values, T_values, data, batch_size=1000, split=True, test_size=0.2, random_state=None, show_progress=True):
    sequences = {}

    # Get the max H and T values
    max_H = max(H_values)
    max_T = max(T_values)

    for H in tqdm(H_values, desc='H loop', leave=False):
        for T in tqdm(T_values, desc='T loop', leave=False):
            X, y = create_sequences_from_database_rows(
                data, H, T, max_H, max_T, batch_size)
            if X.size > 0 and y.size > 0:
                if split:
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=test_size, random_state=random_state)
                    sequences[(H, T)] = (X_train, X_test, y_train, y_test)
                else:
                    sequences[(H, T)] = (X, None, y, None)
            else:
                sequences[(H, T)] = (np.array([]), np.array([]),
                                     np.array([]), np.array([]))

    return sequences