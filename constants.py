from enum import Enum

class DB_columns(Enum):
    GAME_ID = "game_id"
    TIME = "time"
    NAME = "name"
    HP = "hp"
    MAX_HP = "max_hp"
    MANA = "mana"
    MAX_MANA = "max_mana"
    ARMOR = "armor"
    MR = "mr"
    AD = "ad"
    AP = "ap"
    LEVEL = "level"
    ATK_RANGE = "atk_range"
    VISIBLE = "visible"
    TEAM = "team"
    POS_X = "pos_x"
    POS_Z = "pos_z"
    Q_NAME = "q_name"
    Q_CD = "q_cd"
    W_NAME = "w_name"
    W_CD = "w_cd"
    E_NAME = "e_name"
    E_CD = "e_cd"
    R_NAME = "r_name"
    R_CD = "r_cd"
    D_NAME = "d_name"
    D_CD = "d_cd"
    F_NAME = "f_name"
    F_CD = "f_cd"
    NORMALIZED_GAME_ID = "normalized_game_id"
    NORMALIZED_TIME = "normalized_time"
    NORMALIZED_NAME = "normalized_name"
    NORMALIZED_HP = "normalized_hp"
    NORMALIZED_MAX_HP = "normalized_max_hp"
    NORMALIZED_MANA = "normalized_mana"
    NORMALIZED_MAX_MANA = "normalized_max_mana"
    NORMALIZED_ARMOR = "normalized_armor"
    NORMALIZED_MR = "normalized_mr"
    NORMALIZED_AD = "normalized_ad"
    NORMALIZED_AP = "normalized_ap"
    NORMALIZED_LEVEL = "normalized_level"
    NORMALIZED_ATK_RANGE = "normalized_atk_range"
    NORMALIZED_VISIBLE = "normalized_visible"
    NORMALIZED_TEAM = "normalized_team"
    NORMALIZED_POS_X = "normalized_pos_x"
    NORMALIZED_POS_Z = "normalized_pos_z"
    NORMALIZED_Q_NAME = "normalized_q_name"
    NORMALIZED_Q_CD = "normalized_q_cd"
    NORMALIZED_W_NAME = "normalized_w_name"
    NORMALIZED_W_CD = "normalized_w_cd"
    NORMALIZED_E_NAME = "normalized_e_name"
    NORMALIZED_E_CD = "normalized_e_cd"
    NORMALIZED_R_NAME = "normalized_r_name"
    NORMALIZED_R_CD = "normalized_r_cd"
    NORMALIZED_D_NAME = "normalized_d_name"
    NORMALIZED_D_CD = "normalized_d_cd"
    NORMALIZED_F_NAME = "normalized_f_name"
    NORMALIZED_F_CD = "normalized_f_cd"
    COMPOUND_KEY = "compound_key"


DEFAULT_DATA_FEATURES = [DB_columns.NORMALIZED_POS_X.value, DB_columns.NORMALIZED_POS_Z.value]

GAME_AREA_WIDTH = 15000
MAX_TIME = 1800
MAX_HP = 5000
