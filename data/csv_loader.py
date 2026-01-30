import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = BASE_DIR / "datasets"

DTYPES_ANO = {
    "NIV_ESCO": float,
    "SEXO": str,
    "ID_PACIE": float,
    "MUN_NOTI": str,
    "RES_EXAM": float,
    "ANO": int
}

def load_csv(filename: str, sep=";") -> pd.DataFrame:
    path = DATASETS_DIR / filename
    return pd.read_csv(path, sep=sep)

def load_data_for_year(selected_year: int) -> pd.DataFrame:
    file_path = DATASETS_DIR / f"dados_{selected_year}.csv"

    if file_path.exists():
        return pd.read_csv(file_path, dtype=DTYPES_ANO)
    else:
        return pd.DataFrame()
