from dash import callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import json

from data import store
from data.constants import estado_para_sigla
from utils.visualization import get_theme_colors
@callback(
    Output("choropleth-municipal-map", "figure"),
    [
        Input("ano-dropdown-principal", "value"),
        Input("choropleth-estadual-map", "clickData"),  # Adicionando o clickData

    ]
)
def create_municipal_choropleth(selected_year, clickData):
    theme_colors = get_theme_colors()

    df_anos = store.df1

    df_anos = df_anos[df_anos['ANO'] == selected_year].copy()

    # Mapeamento de cores
    color_map = {
        "Transmissão: IPA zero": "white",
        "Controle: 0 <= IPA <= 1": "#ffffb2",
        "Baixo risco: 1 < IPA <= 10": "#fecc5c",
        "Médio risco: 10 < IPA <= 50": "#fd8d3c",
        "Alto risco: 50 < IPA <= 100": "#f54e34",
        "Muito alto risco: IPA > 100": "#8a001c"
    }

    # Intervalos
    bins = [0, 1, 10, 50, 100, float('inf')]
    labels = [
        "Controle: 0 <= IPA <= 1",
        "Baixo risco: 1 < IPA <= 10",
        "Médio risco: 10 < IPA <= 50",
        "Alto risco: 50 < IPA <= 100",
        "Muito alto risco: IPA > 100"
    ]

    df_anos['INTERVALO_IPA_MUNICIPIO'] = pd.cut(
        df_anos['IPA_MUNICIPIO'], bins=bins, labels=labels, right=True
    )

    df_anos['MUN_NOTI'] = df_anos['MUN_NOTI'].astype(str).str.zfill(6)

    df_anos['INTERVALO_IPA_MUNICIPIO'] = (
        df_anos['INTERVALO_IPA_MUNICIPIO']
        .cat.add_categories(['Transmissão: IPA zero'])
        .fillna('Transmissão: IPA zero')
    )

    estado_selecionado = None
    geojson_path = None
    geojson_base = store.brasil_municipios_geojson


    if clickData:
        estado_selecionado = clickData['points'][0]['location']
        sigla_estado = estado_para_sigla.get(estado_selecionado)

        if sigla_estado:
            # 🔑 FILTRO REAL DOS DADOS
            df_anos = df_anos[df_anos['SIGLA_NOTI'] == sigla_estado.upper()].copy()
            geojson_path = f"geojson/{sigla_estado}.json"

    if estado_selecionado:
        title_text = f"<b>IPA por Município - {estado_selecionado} - {selected_year}</b>"
    else:
        title_text = f"<b>IPA por Município no Brasil - {selected_year}</b>"

    # GeoJSON do estado
    if geojson_path and os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_municipios = json.load(f)
    else:
        ufs_presentes = df_anos['MUN_NOTI'].str[:2].unique().tolist()

        geojson_municipios = {
            "type": "FeatureCollection",
            "features": [
                f for f in geojson_base["features"]
                if f["properties"]["id"][:2] in ufs_presentes
            ]
        }


    # Lista de todos os municípios do GeoJSON mostrado
    todos_municipios = pd.DataFrame([{
        'MUN_NOTI': f["properties"]["id"],
        'NOME_NOTI': f["properties"]["name"]
    } for f in geojson_municipios["features"]])

    df_mapa = todos_municipios.merge(df_anos, on='MUN_NOTI', how='left')
    df_mapa.rename(columns={'NOME_NOTI_x': 'NOME_NOTI'}, inplace=True)

    df_mapa['INTERVALO_IPA_MUNICIPIO'] = df_mapa['INTERVALO_IPA_MUNICIPIO'].fillna('Transmissão: IPA zero')
    df_mapa['IPA_MUNICIPIO'] = df_mapa['IPA_MUNICIPIO'].fillna(0)

    # -------------------------------
    # NOVO → custom_data para hover
    # -------------------------------
    df_mapa["IPA_MUNICIPIO_ROUND"] = df_mapa["IPA_MUNICIPIO"].astype(float).round(2)

    fig = px.choropleth(
        df_mapa,
        geojson=geojson_municipios,
        locations='MUN_NOTI',
        featureidkey="properties.id",
        color='INTERVALO_IPA_MUNICIPIO',
        hover_name='NOME_NOTI',

        # CUSTOM DATA → usado no hovertemplate
        custom_data=[
            'NOME_NOTI',
            'INTERVALO_IPA_MUNICIPIO',
            'IPA_MUNICIPIO_ROUND',
            'ANO'
        ],

        category_orders={
            "INTERVALO_IPA_MUNICIPIO": [
                "Transmissão: IPA zero",
                "Controle: 0 <= IPA <= 1",
                "Baixo risco: 1 < IPA <= 10",
                "Médio risco: 10 < IPA <= 50",
                "Alto risco: 50 < IPA <= 100",
                "Muito alto risco: IPA > 100"
            ]
        },
        color_discrete_map=color_map,
        title=title_text
    )

    # ---------------------------------------
    # HOVER ORGANIZADO (igual ao mapa estadual)
    # ---------------------------------------
    fig.update_traces(
        hovertemplate=
            "<b>%{customdata[0]}</b><br>" +
            "Intervalo IPA: %{customdata[1]}<br>" +
            "IPA: %{customdata[2]:.2f}<br>" +
            "Ano: %{customdata[3]}<br>" +
            "<extra></extra>"
    )

    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'pad': {'t': 40},
            'font': {'color': theme_colors['font_color']}
        },
        geo=dict(
            scope="south america",
            projection=dict(type="mercator"),
            fitbounds="locations",
            visible=True,
            showcountries=False,
            showsubunits=True,
            showland=True,
            landcolor="white",
            showlakes=False,
            lakecolor="white",
            bgcolor="white"
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={"r": 10, "t": 40, "l": 10, "b": 10},
        legend=dict(
            x=0.85,
            y=0.95,
            bgcolor='rgba(240,240,240,0.8)',
            bordercolor='gray',
            borderwidth=1,
            title="<b>Classificação de IPA:</b>",
            font=dict(size=14, family='Poppins, sans-serif', color='black'),
        )
    )

    return fig
