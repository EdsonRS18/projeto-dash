from server import app
from utils.visualization import build_responsive_title, get_theme_colors
from components.loading import create_loading_component
from domain.filters import get_available_states

import pandas as pd
from pathlib import Path
import os

# ---------------------------------------------------
# Imports de dados e armazenamento
# ---------------------------------------------------

from data.geojson_loader import load_geojson
from data.csv_loader import load_csv
from data import store
from itertools import chain

# =====================================================
# Exposição do servidor WSGI
# =====================================================

server = app.server
# =====================================================
# CARREGAMENTO DOS GEOJSONs
# =====================================================

# -------------------------
# GeoJSON dos estados
# -------------------------

brazil_geojson = load_geojson("brasil_estados_Geo.geojson")
store.brazil_geojson = brazil_geojson


# -------------------------
# GeoJSON dos municípios por UF
# -------------------------

store.geojson_municipios_por_uf = {}

geojson_dir = Path(__file__).resolve().parent / "geojson"

for file in geojson_dir.glob("*.json"):
    if file.stem.isdigit():  # garante que é 11.json, 12.json, etc.
        codigo_uf = file.stem
        store.geojson_municipios_por_uf[codigo_uf] = load_geojson(file.name)


# -------------------------
# GeoJSON do Brasil completo (montado uma única vez)
# -------------------------

store.geojson_municipios_brasil = {
    "type": "FeatureCollection",
    "features": list(
        chain.from_iterable(
            g["features"] for g in store.geojson_municipios_por_uf.values()
        )
    )
}


# =====================================================
# CARREGAMENTO DO CSV
# =====================================================


data_parts_dir = Path(__file__).resolve().parent / "datasets" / "data_parts"

arquivos_partes = sorted(data_parts_dir.glob("df_parte_*.csv"))

dfs = [load_csv(file) for file in arquivos_partes]

df1 = pd.concat(dfs, ignore_index=True)

store.df1 = df1

# =====================================================
# LAYOUT PRINCIPAL
# =====================================================

from layouts.base import layout
app.layout = layout(df1)


# =====================================================
# REGISTRO DOS CALLBACKS
# =====================================================

from callbacks import (
    choropleth_estado,
    choropleth_municipio,
    piramide_escolar,
    piramide_etaria,
    mapa_importacao,
    sankey_importacao,
    mapa_exportacao,
    sankey_exportacao,
    navigation,
    filtros,
    corredor
)


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == '__main__':
    app.run_server(
        debug=False,
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 8050))
    )