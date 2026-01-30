from dash import callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title



@callback(
    Output('corredor-map', 'figure'),  
    [
        Input('ano-dropdown-principal', 'value'),
        Input('cidade-dropdown', 'value'),
    ],
    prevent_initial_call=False
)
def update_corredor_graph(selected_year, selected_city):
    theme_colors = get_theme_colors()

    if not selected_year:
        return (
            go.Figure()
            .update_layout(
                title="<b>Selecione um ano para visualizar o Canal Endêmico</b>",
                template=theme_colors["template"],
                plot_bgcolor=theme_colors["background_color"],
                paper_bgcolor=theme_colors["background_color"],
                font=dict(color=theme_colors["font_color"]),
            )
        )

    if selected_city == "Todos":
        df = store.df1

        df_filtered = df.copy()
        selected_city_name = "Todos os municípios"
    else:
        df_filtered = df[df["MUN_NOTI"].astype(str) == str(selected_city)]
        if df_filtered.empty:
            return go.Figure().update_layout(
                title="<b>Cidade desconhecida – sem dados disponíveis.</b>"
            )
        selected_city_name = df_filtered["NOME_NOTI"].iloc[0]

    selected_year = int(selected_year)
    anos_intervalo = [selected_year - i for i in range(1, 4)]
    anos_completos = [
        ano for ano in anos_intervalo if not df_filtered[df_filtered["ANO"] == ano].empty
    ]

    if len(anos_completos) < 3:
        anos_extras = [
            ano
            for ano in sorted(df_filtered["ANO"].unique())
            if ano not in anos_completos and ano < selected_year
        ]
        anos_completos.extend(anos_extras[: 3 - len(anos_completos)])

    df_anos = df_filtered[df_filtered["ANO"].isin(anos_completos)]
    df_selected_year = df_filtered[df_filtered["ANO"] == selected_year]

    df_stats = (
        df_anos.groupby(["MES", "ANO"])["NOTIFICACOES_MUNICIPIO_MES"]
        .sum()
        .reset_index()
    )
    summary_stats = (
        df_stats.groupby("MES")["NOTIFICACOES_MUNICIPIO_MES"]
        .agg(Q1=lambda x: x.quantile(0.25), Mediana="median", Q3=lambda x: x.quantile(0.75))
        .reset_index()
    )

    df_selected_year_monthly = (
        df_selected_year.groupby("MES")["NOTIFICACOES_MUNICIPIO_MES"]
        .sum()
        .reset_index()
    )

    corredor_fig = go.Figure()

    corredor_fig.add_trace(
        go.Scatter(
            x=summary_stats["MES"],
            y=summary_stats["Q3"],
            mode="lines",
            line=dict(color="red", dash="dash", width=3),
            name="Q3 (limite superior)",
            hovertemplate="Limite Superior (Q3): %{y}<extra></extra>",
        )
    )
    corredor_fig.add_trace(
        go.Scatter(
            x=summary_stats["MES"],
            y=summary_stats["Q1"],
            mode="lines",
            line=dict(color="blue", dash="dash", width=3),
            fill="tonexty",
            fillcolor="rgba(173,216,230,0.25)",
            name="Q1 (limite inferior)",
            hovertemplate="Limite Inferior (Q1): %{y}<extra></extra>",
        )
    )
    corredor_fig.add_trace(
        go.Scatter(
            x=df_selected_year_monthly["MES"],
            y=df_selected_year_monthly["NOTIFICACOES_MUNICIPIO_MES"],
            mode="lines+markers",
            line=dict(color="#17C3B2", width=4),
            marker=dict(size=8, color="#005F4B"),
            name=f"Notificações {selected_year}",
            hovertemplate="Casos em %{x}: %{y}<extra></extra>",
        )
    )
    
    corredor_fig.update_layout(
        title=(
            f"<b>Canal Endêmico: {selected_city_name} – Ano {selected_year}</b><br>"
            f"<span style='font-size:14px;color:#666;'>Base: {', '.join(map(str, sorted(anos_completos)))}</span>"
        ),
        title_x=0.5,

        xaxis_title="<b>Meses do Ano</b>",
        yaxis_title="<b>Número de Casos</b>",

        yaxis=dict(tickformat=".0f"),
        template=theme_colors["template"],
        plot_bgcolor=theme_colors["background_color"],
        paper_bgcolor=theme_colors["background_color"],
        font=dict(color=theme_colors["font_color"], family="Inter, sans-serif"),
        margin={"r": 20, "t": 100, "l": 60, "b": 60},
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12, family="Inter, sans-serif", color=theme_colors["font_color"]),
            bgcolor="rgba(240,240,240,0.8)",
            bordercolor="gray",
            borderwidth=1
        ),
        hovermode='x unified'
    )


    return corredor_fig
