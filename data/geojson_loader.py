import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

def load_geojson(filename: str) -> dict:
    path = BASE_DIR / "geojson" / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)