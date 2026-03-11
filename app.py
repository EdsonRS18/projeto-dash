from server import app
from utils.visualization import build_responsive_title, get_theme_colors
from components.loading import create_loading_component
from domain.filters import get_available_states

# ---------------------------------------------------
# Imports de dados e armazenamento
# ---------------------------------------------------

from data.geojson_loader import load_geojson
from data.csv_loader import load_csv
from data import store
from pathlib import Path
from itertools import chain


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

df1 = load_csv("df_geografico_finalizado2.csv")
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
    app.run_server(debug=True)