from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title
import math
from data.csv_loader import load_data_for_year

#piramide nivel escolar por sexo
@callback(
    
    Output('piramide-map', 'figure'),

    [
        Input('ano-dropdown-principal', 'value'),
        Input('cidade-dropdown', 'value'),
    ]

)

def create_piramide_escolaridade(selected_year, selected_cidade):
    
    theme_colors = get_theme_colors()
    mapa_niv_esco = {
        8: 'Educação superior completa',
        7: 'Educação superior incompleto',
        6: 'Ensino médio completo',
        5: 'Ensino médio incompleto',
        4: 'Ensino fundamental completo',
        3: '5ª a 8ª série incompleta do EF',
        2: '4ª série completa do EF',
        1: '1ª a 4ª série incompleta do EF',
        0: 'Analfabeto',
        10: 'Não se aplica'
    }

    df2 = load_data_for_year(selected_year)
    if df2.empty:
        return go.Figure().update_layout(
            title="Sem dados para o ano selecionado",
            template=theme_colors["template"],
            plot_bgcolor=theme_colors["background_color"],
            paper_bgcolor=theme_colors["background_color"],
            font=dict(color=theme_colors["font_color"]),
        )

    # Definindo o filtro baseado na existência da coluna 'ANO'

    filtered_df = df2[(df2['ANO'] == selected_year)]
    selected_cidade_nome = "Todos"
    
    # Filtra pela cidade se não for 'Todos'
    if selected_cidade != 'Todos':
        filtered_df = filtered_df[filtered_df['MUN_NOTI'].astype(str) == selected_cidade]
        # Pega nome legível da cidade no df1, se possível
        df = store.df1
        cidade_nome_series = df[df["MUN_NOTI"].astype(str) == selected_cidade]["NOME_NOTI"]
        if not cidade_nome_series.empty:
            selected_cidade_nome = cidade_nome_series.iloc[0]
        else:
            selected_cidade_nome = selected_cidade

    # Filtragem extra
    filtered_df = filtered_df[filtered_df['RES_EXAM'] != 1]
    filtered_df = filtered_df.dropna(subset=['NIV_ESCO'])

    if filtered_df.empty:
        return go.Figure().update_layout(
            title=f"Sem dados disponíveis para {selected_cidade_nome} no ano {selected_year}",
            template=theme_colors["template"],
            plot_bgcolor=theme_colors["background_color"],
            paper_bgcolor=theme_colors["background_color"],
            font=dict(color=theme_colors["font_color"]),
        )

    filtered_df['NIV_ESCO'] = filtered_df['NIV_ESCO'].map(mapa_niv_esco)

    df_male = filtered_df[filtered_df['SEXO'] == 'M']
    df_female = filtered_df[filtered_df['SEXO'] == 'F']

    count_male = df_male.groupby('NIV_ESCO').size()
    count_female = df_female.groupby('NIV_ESCO').size()

    if count_male.sum() == 0 and count_female.sum() == 0:
        return go.Figure().update_layout(
            title=f"Sem dados de escolaridade para {selected_cidade_nome} no ano {selected_year}",
            template=theme_colors["template"],
            plot_bgcolor=theme_colors["background_color"],
            paper_bgcolor=theme_colors["background_color"],
            font=dict(color=theme_colors["font_color"]),
        )

    count_male_percent = (count_male / count_male.sum()) * 100 if count_male.sum() > 0 else count_male
    count_female_percent = (count_female / count_female.sum()) * 100 if count_female.sum() > 0 else count_female

    color_male = theme_colors["male_color"]
    color_female = theme_colors["female_color"]

    valid_categories = [cat for cat in mapa_niv_esco.values() if cat in count_male.index or cat in count_female.index]

    count_male = count_male.reindex(valid_categories).fillna(0)
    count_female = count_female.reindex(valid_categories).fillna(0)
    count_male_percent = count_male_percent.reindex(valid_categories).fillna(0)
    count_female_percent = count_female_percent.reindex(valid_categories).fillna(0)

    fig = go.Figure()

    # Ajuste do eixo X para não exibir valores negativos e manter padrão de 10 em 10

    # maior percentual entre os sexos
    max_percent = max(count_male_percent.max(), count_female_percent.max())

    # arredonda para múltiplo de 10
    max_tick = math.ceil(max_percent / 10) * 10

    # gera ticks simétricos (-max_tick até +max_tick)
    ticks = list(range(-max_tick, max_tick + 1, 10))

    # remove sinal negativo na visualização
    ticktext = [str(abs(t)) for t in ticks]

    fig.update_xaxes(
        tickmode="array",
        tickvals=ticks,
        ticktext=ticktext,
        range=[-max_tick, max_tick],
        title="Percentual"
    )


    fig.add_trace(go.Bar(
        y=valid_categories,
        x=count_male_percent,
        name='Masculino',
        orientation='h',
        marker_color=color_male,
        text=count_male.astype(int).astype(str) + ' (' + count_male_percent.round(1).astype(str) + '%)',
        hoverinfo='text'
    ))

    fig.add_trace(go.Bar(
        y=valid_categories,
        x=-count_female_percent,
        name='Feminino',
        orientation='h',
        marker_color=color_female,
        text=count_female.astype(int).astype(str) + ' (' + count_female_percent.round(1).astype(str) + '%)',
        hoverinfo='text'
    ))

    fig.update_layout(
        title=build_responsive_title(
        main_title="Distribuição da Escolaridade por Sexo",
        subtitle=f"{selected_cidade_nome}, {selected_year}"
    ),
              xaxis_title='Percentual',
        yaxis_title='Escolaridade',
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

    return fig


