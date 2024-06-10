from enum import Enum
from tkinter import NORMAL


class DB_columns(Enum):
    NAME = "name"
    POS_X = "pos_x"
    POS_Z = "pos_z"
    TIME = "time"
    HP = "hp"
    TEAM = "team"
    GAME_ID = "game_id"
    COMPOUND_KEY = "compound_key"
    NORMALIZED_POS_X = "normalized_pos_x"
    NORMALIZED_POS_Z = "normalized_pos_z"

DEFAULT_DATA_FEATURES = [DB_columns.NORMALIZED_POS_X.value, DB_columns.NORMALIZED_POS_Z.value]

GAME_AREA_WIDTH = 15000
