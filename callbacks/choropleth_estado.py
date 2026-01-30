from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title





# Choropleth Estadual com highlight no clique
@callback(
    Output("choropleth-estadual-map", "figure"),
    [
        Input("ano-dropdown-principal", "value"),
        Input("choropleth-estadual-map", "clickData")  # <<< clique
    ],
    prevent_initial_call=False
)
def choropleth_estadual_map(selected_year, clickData):

    theme_colors = get_theme_colors()

    df = store.df1
    filtered_df = df[df['ANO'] == selected_year].copy()


    # Intervalos
    bins = [0, 1, 10, 50, 100, float('inf')]
    labels = [
        "Controle / IPA >= 0 e <= 1",
        "Baixo risco / IPA > 1 e <= 10",
        "Médio risco / IPA > 10 e <= 50",
        "Alto risco / IPA > 50 e <= 100",
        "Muito alto risco / IPA > 100"
    ]
    filtered_df['INTERVALO_IPA_ESTADO'] = pd.cut(
        filtered_df['IPA_ESTADO'], bins=bins, labels=labels, right=True
    )

    # Título
    title_text = f"<b>IPA por Estado no Brasil - {selected_year}</b>"
    title = dict(
        text=title_text,
        x=0.5,
        xanchor='center',
        font=dict(color=theme_colors['font_color'], size=18)
    )

    # Cores
    color_map = {
        "Controle / IPA >= 0 e <= 1": "#ffffb2",
        "Baixo risco / IPA > 1 e <= 10": "#fecc5c",
        "Médio risco / IPA > 10 e <= 50": "#fd8d3c",
        "Alto risco / IPA > 50 e <= 100": "#f54e34",
        "Muito alto risco / IPA > 100": "#8a001c",
        "Sem Dados": "gray"
    }

    # Mapa base
    fig = px.choropleth(
        filtered_df,
        geojson=store.brazil_geojson,

        locations="ESTADO",
        featureidkey="properties.name",
        color="INTERVALO_IPA_ESTADO",
        hover_name="ESTADO",
        custom_data=["ESTADO", "INTERVALO_IPA_ESTADO", "IPA_ESTADO", "NOTIFICACOES_ESTADO_ANO"],
        color_discrete_map=color_map,
        category_orders={"INTERVALO_IPA_ESTADO": labels + ["Sem Dados"]}
    )

# ------- HOVER TEMPLATE BONITO E ORGANIZADO ----------
    fig.update_traces(
        hovertemplate=
            "<b>%{customdata[0]}</b><br>" +
            "Intervalo IPA: %{customdata[1]}<br>" +
            "IPA: %{customdata[2]:.2f}<br>" +
            "Notificações: %{customdata[3]}<br>" +
            "<extra></extra>"
    )

    # ------------------------------------------------------
    #  CLique: pegar estado selecionado
    # ------------------------------------------------------
    clicked_state = None

    if clickData:
        clicked_state = clickData["points"][0].get("location")

    # ------------------------------------------------------
    # Overlay: highlight APENAS no estado clicado
    # ------------------------------------------------------
    overlay = go.Choropleth(
        geojson=store.brazil_geojson,
        locations=[clicked_state] if clicked_state else [],
        z=[1] if clicked_state else [0],
        featureidkey="properties.name",
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
        showscale=False,
        marker=dict(
            line=dict(
                width=5 if clicked_state else 0,
                color="black"
            )
        ),
        hoverinfo="skip",
        name="click-highlight"
    )

    fig.add_trace(overlay)

    # Layout
    fig.update_layout(
        title=title,
        geo=dict(
            fitbounds="locations",
            visible=False,
            showcountries=False,
            scope="south america"
        ),
        legend=dict(
            x=0.85,
            y=0.95,
            bgcolor='rgba(240,240,240,0.8)',
            bordercolor='gray',
            borderwidth=1,
            title="<b>Classificação de IPA:</b>",
            font=dict(size=14, family='Poppins, sans-serif', color='black'),
        ),
        hovermode="closest",
        template=theme_colors["template"],
        paper_bgcolor=theme_colors["background_color"],
        plot_bgcolor=theme_colors["background_color"]
    )

    return fig



@callback(
    Output("store-estado-selecionado", "data"),
    Input("choropleth-estadual-map", "clickData"),
    State("store-estado-selecionado", "data"),
    prevent_initial_call=True
)
def store_estado_clicado(clickData, estado_atual):
    if not clickData:
        return estado_atual

    return clickData["points"][0]["location"]
