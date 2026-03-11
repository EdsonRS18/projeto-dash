from dash import callback, Input, Output
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors,build_responsive_title
from data.constants import SankeyDirection


@callback(
    Output('map-exportacao', 'figure'),
    [
        Input('ano-dropdown-principal', 'value'),
        Input('estado-dropdown-exportacao', 'value'),
        Input('municipio-dropdown-exportacao', 'value'),
        Input('map-exportacao', 'clickData'),
        Input('exported-sankey-direction-input', 'value'),
        Input('min-notificacoes-slider-exportacao', 'value')
    ]
)
def update_mapa_exportacao(
    selected_year,
    estado_selecionado,
    selected_municipio,
    click_data,
    selected_direction,
    min_notificacoes
):

    theme_colors = get_theme_colors()
    df = store.df1.copy()

    # =======================================================
    # 0) Nenhum estado
    # =======================================================
    if not estado_selecionado:
        return go.Figure().update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=3.4,
            mapbox_center={"lat": -14.2350, "lon": -51.9253},
            title_text="Selecione um estado no seletor",
            title_x=0.5,
            height=800
        )

    # =======================================================
    # 1) Filtro de ano
    # =======================================================
    if selected_year != "Todos":
        df = df[df['ANO'] == selected_year]

    df.dropna(subset=[
        'SIGLA_NOTI', 'SIGLA_INFE', 'SIGLA_RESI',
        'LATITUDE_NOTI', 'LONGITUDE_NOTI',
        'LATITUDE_INFE', 'LONGITUDE_INFE',
        'LATITUDE_RESI', 'LONGITUDE_RESI',
        'NOME_NOTI', 'NOME_INFE', 'NOME_RESI'
    ], inplace=True)

    for col in ['NOME_INFE', 'NOME_NOTI', 'NOME_RESI']:
        df[col] = df[col].astype(str).str.upper()

    # =======================================================
    # 2) Direção (EXPORTAÇÃO)
    # =======================================================
    if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
        source_col, target_col = 'SIGLA_INFE', 'SIGLA_NOTI'
        source_nome, target_nome = 'NOME_INFE', 'NOME_NOTI'
        source_lat, source_lon = 'LATITUDE_INFE', 'LONGITUDE_INFE'
        target_lat, target_lon = 'LATITUDE_NOTI', 'LONGITUDE_NOTI'
        label_apenas_origem = "local de infecção"
        label_origem_destino = "local de infecção e notificação"

    elif selected_direction == SankeyDirection.INFECTION_TO_RESIDENCE.value:
        source_col, target_col = 'SIGLA_INFE', 'SIGLA_RESI'
        source_nome, target_nome = 'NOME_INFE', 'NOME_RESI'
        source_lat, source_lon = 'LATITUDE_INFE', 'LONGITUDE_INFE'
        target_lat, target_lon = 'LATITUDE_RESI', 'LONGITUDE_RESI'
        label_apenas_origem = "local de infecção"
        label_origem_destino = "local de infecção e residencia"

    else:
        return go.Figure()
    

    if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
        edge_source_label = "Município de Infecção"
        edge_target_label = "Município de Notificação"
        edge_cases_label = "Casos exportados"
    else:
        edge_source_label = "Município de Infecção"
        edge_target_label = "Município de Residência"
        edge_cases_label = "Casos exportados"
    hover_edge_template = (
        f"<b>{edge_source_label}:</b> %{{customdata[1]}}<br>"
        f"<b>{edge_target_label}:</b> %{{customdata[2]}}<br>"
        f"<b>{edge_cases_label}:</b> %{{customdata[0]:,.0f}}"
        "<extra></extra>"
)

    df[source_col] = df[source_col].str.upper()
    df[target_col] = df[target_col].str.upper()
    df['_SRC_NAME'] = df[source_nome]
    df['_TGT_NAME'] = df[target_nome]

    if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
        label_apenas_destino = "Local de notificação"

    elif selected_direction == SankeyDirection.INFECTION_TO_RESIDENCE.value:
        label_apenas_destino = "local de residência"

    # =======================================================
    # 3) Apenas fluxos que SAEM do estado
    # =======================================================
    df = df[df[source_col] == estado_selecionado]
    df = df[df['_SRC_NAME'] != df['_TGT_NAME']]

    total_origem_real = (
        df.groupby(['_SRC_NAME'], as_index=True)['QTD_NOTIFICACOES']
        .sum()
    )

    total_destino_real = (
        df.groupby(['_TGT_NAME'], as_index=True)['QTD_NOTIFICACOES']
        .sum()
    )

    # =======================================================
    # 4) 🔥 FILTRO DO SLIDER (IGUAL AO SANKEY / IMPORTAÇÃO)
    # =======================================================
    if min_notificacoes and min_notificacoes > 0:
        df = (
            df.groupby(
                [
                    source_col, target_col,
                    '_SRC_NAME', '_TGT_NAME',
                    source_lat, source_lon,
                    target_lat, target_lon
                ],
                as_index=False
            )['QTD_NOTIFICACOES']
            .sum()
        )

        df = df[df['QTD_NOTIFICACOES'] >= min_notificacoes]

    # =======================================================
    # 5) Contagens
    # =======================================================
    source_counts = (
        df.groupby(['_SRC_NAME', source_col, source_lat, source_lon], as_index=False)
        ['QTD_NOTIFICACOES'].sum()
    )

    target_counts = (
        df.groupby(['_TGT_NAME', target_col, target_lat, target_lon], as_index=False)
        ['QTD_NOTIFICACOES'].sum()
    )

    soma_origem = source_counts.set_index('_SRC_NAME')['QTD_NOTIFICACOES']
    soma_destino = target_counts.set_index('_TGT_NAME')['QTD_NOTIFICACOES']

    fig = go.Figure()

    # =======================================================
    # 6) Município ativo
    # =======================================================
    if selected_municipio:
        municipio_ativo = selected_municipio.upper()
    elif click_data:
        municipio_ativo = click_data['points'][0]['customdata'][0].upper()
    else:
        municipio_ativo = None

    # =======================================================
    # 7) ARESTAS
    # =======================================================
    arestas_existem = False

    if municipio_ativo:
        df_sel = df[df['_SRC_NAME'] == municipio_ativo]

        if not df_sel.empty:
            df_sel = (
                df_sel.groupby(
                    [
                        source_lat, source_lon,
                        target_lat, target_lon,
                        '_SRC_NAME', '_TGT_NAME',
                        source_col, target_col
                    ],
                    as_index=False
                )['QTD_NOTIFICACOES']
                .sum()
            )

            df_sel['Tipo_Relacao'] = df_sel.apply(
                lambda r: 'Mesmo Estado'
                if r[source_col] == r[target_col]
                else 'Estados Diferentes',
                axis=1
            )

            arestas_existem = True

            cores_relacao = {
                'Mesmo Estado': "#000000",
                'Estados Diferentes': "#817D7C"
            }

       
            for tipo, cor in cores_relacao.items():
                fig.add_trace(go.Scattermapbox(
                    lat=[None],
                    lon=[None],
                    mode='lines',
                    line=dict(width=3, color=cor),
                    name=tipo,
                    showlegend=True,
                    hoverinfo='skip'
                ))

            for _, r in df_sel.iterrows():
                mid_lat = (r[source_lat] + r[target_lat]) / 2
                mid_lon = (r[source_lon] + r[target_lon]) / 2

                fig.add_trace(go.Scattermapbox(
                    lat=[r[source_lat], mid_lat, r[target_lat]],
                    lon=[r[source_lon], mid_lon, r[target_lon]],
                    mode='lines+markers',
                    line=dict(
                        width=3,
                        color=cores_relacao[r['Tipo_Relacao']]
                    ),
                    marker=dict(size=0),
                    customdata=[
                        [r['QTD_NOTIFICACOES'], r['_SRC_NAME'], r['_TGT_NAME']]
                    ] * 3,
                    hovertemplate=hover_edge_template,
                    showlegend=False
                ))


    # =======================================================
    # 8) NÓS (RECONSTRUÇÃO IGUAL AO MAPA DE IMPORTAÇÃO)
    # =======================================================
    nodes = pd.concat([
        source_counts.rename(columns={
            '_SRC_NAME': 'NOME',
            source_col: 'UF',
            source_lat: 'LAT',
            source_lon: 'LON',
            'QTD_NOTIFICACOES': 'NUM'
        }),
        target_counts.rename(columns={
            '_TGT_NAME': 'NOME',
            target_col: 'UF',
            target_lat: 'LAT',
            target_lon: 'LON',
            'QTD_NOTIFICACOES': 'NUM'
        })
    ]).drop_duplicates(subset=['NOME', 'LAT', 'LON'])

    nodes['ORIGEM_SUM'] = nodes['NOME'].map(total_origem_real).fillna(0).astype(int)
    nodes['DESTINO_SUM'] = nodes['NOME'].map(total_destino_real).fillna(0).astype(int)


    def class_tipo(r):
        origem = r['ORIGEM_SUM']
        destino = r['DESTINO_SUM']
        uf = r['UF']

        # 🔥 perdeu infecção por causa do filtro
        if origem < (min_notificacoes or 0) and destino > 0:
            return label_apenas_destino


        if uf == estado_selecionado:
            if origem > 0 and destino > 0:
                return label_origem_destino
            if origem > 0:
                return label_apenas_origem

        if destino > 0:
            return label_apenas_destino


        return None

    nodes['Tipo'] = nodes.apply(class_tipo, axis=1)

    cores_nos = {
        label_apenas_origem: '#E74C3C',
        label_origem_destino: "#6103DB",
        label_apenas_destino: '#3498DB'
    }

    if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
                hover_txt = (
                    "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
                    "%{customdata[2]} infecções<extra></extra><br>"
                    "%{customdata[3]} notificações<br>"
                    
                )
    else:
                hover_txt = (
                    "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
                    "%{customdata[2]} infecções<extra></extra><br>"
                    "%{customdata[3]} casos em residentes<br>"
                    
                )

    for tipo in nodes['Tipo'].dropna().unique():
        sub = nodes[nodes['Tipo'] == tipo]
        fig.add_trace(go.Scattermapbox(
            lat=sub['LAT'],
            lon=sub['LON'],
            mode='markers',
            marker=dict(size=10, color=cores_nos[tipo]),
            customdata=sub[['NOME', 'UF', 'ORIGEM_SUM', 'DESTINO_SUM']].values,
            hovertemplate=hover_txt,
            name=tipo
        ))

    # =======================================================
    # 9) Layout
    # =======================================================
    centro_lat = nodes['LAT'].mean() if not nodes.empty else -14.235
    centro_lon = nodes['LON'].mean() if not nodes.empty else -51.925

        
    if municipio_ativo and arestas_existem:

        main_title = f"<b>Exportações a partir de {municipio_ativo} ({estado_selecionado})</b>"
    else:
        main_title = f"<b>Exportações a partir de {estado_selecionado}<b>"

    title_cfg = build_responsive_title(
    main_title=main_title,
    subtitle=f"<b>Ano {selected_year}<b>"
)

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=4,
        mapbox_center={"lat": centro_lat, "lon": centro_lon},
        height=700,
        margin={"r": 0, "t": 80, "l": 0, "b": 70},
        hovermode='closest',
        title=title_cfg,
        legend=dict(
            orientation="h",
            y=0.95,
            x=0.5,
            xanchor="center",
            yanchor="bottom",
        ),
        plot_bgcolor=theme_colors["background_color"],
        paper_bgcolor=theme_colors["background_color"],
        font=dict(color=theme_colors["font_color"]),
        template=theme_colors["template"],
    )
    fig.add_annotation(
    text=(
        "<i>Os casos de infecção de municípios fora do estado selecionado não são exibidos no mapa.<br> "
        "Exemplo: ao selecionar o estado “Pará”, municípios como Manaus aparecerão com 0 infecções.</i>"
    ),
    x=0.5,
    y=-0.10,            # 👈 abaixo do gráfico
    xref="paper",
    yref="paper",
    showarrow=False,
    align="center",
    font=dict(
        size=13,
        color=theme_colors["font_color"]
    )
)

    return fig
