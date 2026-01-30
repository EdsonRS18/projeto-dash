from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title
import math
from data.csv_loader import load_data_for_year


#piramide faixa etaria por sexo
@callback(
    
    Output('piramide-map2', 'figure'),

    [
        Input('ano-dropdown-principal', 'value'),
        Input('cidade-dropdown', 'value'),
    ]
)
def create_piramide_faixa_etaria(selected_year, selected_cidade):
    theme_colors = get_theme_colors()
    df2 = load_data_for_year(selected_year)

    if df2.empty:
        return go.Figure()

    df2 = df2[df2['ANO'] == selected_year]
    
    selected_cidade_nome = "Todos"
    if selected_cidade != 'Todos':
        df2 = df2[df2['MUN_NOTI'] == selected_cidade]
        
        # Buscar nome legível da cidade no df1, se possível
        df = store.df1

        cidade_nome_series = df[df["MUN_NOTI"].astype(str) == selected_cidade]["NOME_NOTI"]
        if not cidade_nome_series.empty:
            selected_cidade_nome = cidade_nome_series.iloc[0]
        else:
            selected_cidade_nome = selected_cidade

    df2 = df2.dropna(subset=['ID_PACIE'])
    if df2.empty:
        return go.Figure()

    max_age = int(df2['ID_PACIE'].max())
    age_limit = 109
    bins = list(range(0, min(max_age, age_limit) + 10, 10))
    bins.append(float('inf'))
    labels = [f'{i}-{i+9}' for i in bins[:-2]] + ['Idades Desconhecidas']
    df2['FAIXA_ETARIA'] = pd.cut(df2['ID_PACIE'], bins=bins, labels=labels, right=False)

    df_male = df2[df2['SEXO'] == 'M']
    df_female = df2[df2['SEXO'] == 'F']

    count_male = df_male.groupby('FAIXA_ETARIA').size()
    count_female = df_female.groupby('FAIXA_ETARIA').size()

    valid_categories = list(set(count_male.index).union(set(count_female.index)))
    valid_categories.sort(key=lambda x: int(x.split('-')[0]) if '-' in x else float('inf'))

    count_male = count_male.reindex(valid_categories).fillna(0)
    count_female = count_female.reindex(valid_categories).fillna(0)

    percent_male = (count_male / count_male.sum()) * 100
    percent_female = (count_female / count_female.sum()) * 100

    color_male = theme_colors["male_color"]
    color_female = theme_colors["female_color"]

    fig2 = go.Figure()
    # Ajuste do eixo X para não mostrar valores negativos
    # Calcula o maior percentual entre homens e mulheres para definir o range
    max_percent = max(percent_male.max(), percent_female.max())

    # Arredonda para cima para ficar múltiplo de 10
    max_tick = math.ceil(max_percent / 10) * 10

    # Criar ticks simétricos: -max_tick ... max_tick de 10 em 10
    ticks = list(range(-max_tick, max_tick + 1, 10))

    # Criar textos SEM sinal negativo
    ticktext = [str(abs(t)) for t in ticks]

    fig2.update_xaxes(
        tickmode='array',
        tickvals=ticks,
        ticktext=ticktext,
        range=[-max_tick, max_tick],
        title='Percentual'
    )

    fig2.add_trace(go.Bar(
        y=valid_categories,
        x=percent_male,
        name='Masculino',
        orientation='h',
        marker_color=color_male,
        text=count_male.astype(int).astype(str) + ' (' + percent_male.round(1).astype(str) + '%)',
        hoverinfo='text'
    ))

    fig2.add_trace(go.Bar(
        y=valid_categories,
        x=-percent_female,
        name='Feminino',
        orientation='h',
        marker_color=color_female,
        text=count_female.astype(int).astype(str) + ' (' + percent_female.round(1).astype(str) + '%)',
        hoverinfo='text'
    ))

    fig2.update_layout(
        title=build_responsive_title(
        main_title="Distribuição Etária por Sexo",
        subtitle=f"{selected_cidade_nome}, {selected_year}"
    ),
    xaxis_title='Percentual',
        yaxis_title='Faixa Etária',
        barmode='relative',
        template=theme_colors["template"],
        font=dict(color=theme_colors["font_color"]),
        plot_bgcolor=theme_colors["background_color"],
        paper_bgcolor=theme_colors["background_color"],
        legend=dict(
            title='<b>Classificação de Sexo:</b>',
            font=dict(size=14, family='Poppins, sans-serif', color='black'),
            bgcolor='rgba(240,240,240,0.8)', bordercolor='gray', borderwidth=1
        ),
    )

    return fig2

