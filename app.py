from server import app
from utils.visualization import build_responsive_title, get_theme_colors
from components.loading import create_loading_component
from domain.filters import get_available_states

#import de df e geojson
from data.geojson_loader import load_geojson
from data.csv_loader import load_csv


brazil_geojson = load_geojson("brasil_estados_Geo.geojson")
brasil_municipios_geojson = load_geojson("brasil_municipios_Geo.geojson")
df1 = load_csv("df_geografico_finalizado2.csv")

from data import store

store.df1 = df1
store.brazil_geojson = brazil_geojson
store.brasil_municipios_geojson = brasil_municipios_geojson

# Layout principal
from layouts.base import layout

# Importação dos callbacks (registro automático)
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
# Definição do layout
# =====================================================

app.layout = layout(df1)

# =====================================================
# Execução
# =====================================================

if __name__ == "__main__":
    app.run_server(debug=True)
# if __name__ == '__main__':
#     app.run_server(debug=False, port=80, host='0.0.0.0')