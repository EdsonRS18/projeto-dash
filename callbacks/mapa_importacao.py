from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title
from data.constants import SankeyDirection






@callback(
    Output('map-importacao', 'figure'),
    [
        Input('ano-dropdown-principal', 'value'),
        Input('estado-dropdown-importacao', 'value'),
        Input('municipio-dropdown-importacao', 'value'),
        Input('map-importacao', 'clickData'),
        Input('imported-sankey-direction-input', 'value'),
        Input('min-notificacoes-slider-importacao', 'value')  # 👈 NOVO
    ]
)


def update_mapa_importacao(
    selected_year,
    estado_selecionado,
    selected_municipio,
    click_data,
    selected_direction,
    min_notificacoes  # 👈 NOVO
):

    theme_colors = get_theme_colors()
    df = store.df1
    df = df.copy()

    # =======================================================
    # 0) Nenhum estado selecionado → mapa vazio
    # =======================================================
    if not estado_selecionado:
        return go.Figure().update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=3.4,
            mapbox_center={"lat": -14.2350, "lon": -51.9253},
            title_text="Selecione um estado no seletor",
            title_x=0.5,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
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

    df['NOME_INFE'] = df['NOME_INFE'].astype(str).str.upper()
    df['NOME_NOTI'] = df['NOME_NOTI'].astype(str).str.upper()
    df['NOME_RESI'] = df['NOME_RESI'].astype(str).str.upper()

    # =======================================================
    # 2) Direções
    # =======================================================
    if selected_direction == SankeyDirection.NOTIFICATION_TO_INFECTION.value:
        source_col = 'SIGLA_NOTI'
        target_col = 'SIGLA_INFE'
        source_nome = 'NOME_NOTI'
        target_nome = 'NOME_INFE'
        source_lat = 'LATITUDE_NOTI'
        source_lon = 'LONGITUDE_NOTI'
        target_lat = 'LATITUDE_INFE'
        target_lon = 'LONGITUDE_INFE'
        label_apenas_origem = "Apenas Notifica"
        label_origem_destino = "Notifica e Infecta"

    elif selected_direction == SankeyDirection.RESIDENCE_TO_INFECTION.value:
        source_col = 'SIGLA_RESI'
        target_col = 'SIGLA_INFE'
        source_nome = 'NOME_RESI'
        target_nome = 'NOME_INFE'
        source_lat = 'LATITUDE_RESI'
        source_lon = 'LONGITUDE_RESI'
        target_lat = 'LATITUDE_INFE'
        target_lon = 'LONGITUDE_INFE'
        label_apenas_origem = "Apenas Residência"
        label_origem_destino = "Residência e Infecção"

    else:
        return go.Figure().update_layout(
            title_text="Direção inválida.",
            title_x=0.5
        )

    # Normalizações
    df[source_col] = df[source_col].astype(str).str.upper()
    df[target_col] = df[target_col].astype(str).str.upper()
    df['_SRC_NAME'] = df[source_nome].astype(str).str.upper()
    df['_TGT_NAME'] = df[target_nome].astype(str).str.upper()

    df = df[df[source_col] == estado_selecionado]
    df = df[df['_SRC_NAME'] != df['_TGT_NAME']]

    

    # =======================================================
    # 3) Contagens
    # =======================================================
    source_counts = (
        df.groupby(['_SRC_NAME', source_col, source_lat, source_lon], as_index=False)['QTD_NOTIFICACOES']
        .sum()
        .rename(columns={'_SRC_NAME': source_nome, 'QTD_NOTIFICACOES': 'num'})
    )

    target_counts = (
        df.groupby(['_TGT_NAME', target_col, target_lat, target_lon], as_index=False)['QTD_NOTIFICACOES']
        .sum()
        .rename(columns={'_TGT_NAME': target_nome, 'QTD_NOTIFICACOES': 'num'})
    )

    fig = go.Figure()

    municipio_ativo = None

    if selected_municipio:
        municipio_ativo = selected_municipio.upper()

    elif click_data:
        municipio_ativo = click_data['points'][0]['customdata'][0].upper()

    # =======================================================
    # 4) ARESTAS
    # =======================================================
    edge_counts = pd.DataFrame()
    arestas_existem = False

    soma_origem = df.groupby('_SRC_NAME')['QTD_NOTIFICACOES'].sum()
    soma_destino = df.groupby('_TGT_NAME')['QTD_NOTIFICACOES'].sum()

    if municipio_ativo:
        # 🔒 Cancela município ativo se ele não passa no filtro do slider
        total_origem = soma_origem.get(municipio_ativo, 0)
        total_destino = soma_destino.get(municipio_ativo, 0)

        if (
            min_notificacoes
            and min_notificacoes > 0
            and total_origem < min_notificacoes
            and total_destino < min_notificacoes
        ):
            municipio_ativo = None

    if municipio_ativo:
        df_selected = df[df['_SRC_NAME'] == municipio_ativo]

        if not df_selected.empty:

            # Classificação da relação
            def classificar(row):
                return (
                    'Mesmo Estado'
                    if row[source_col] == row[target_col]
                    else 'Estados Diferentes'
                )

            df_selected = df_selected.copy()
            df_selected['Tipo_Relacao'] = df_selected.apply(classificar, axis=1)

            # Agrupamento das arestas
            edge_counts = (
                df_selected.groupby(
                    [
                        source_lat, source_lon,
                        target_lat, target_lon,
                        '_SRC_NAME', '_TGT_NAME',
                        'Tipo_Relacao'
                    ],
                    as_index=False
                )['QTD_NOTIFICACOES']
                .sum()
            )

            # 🔥 Filtro do slider
            if min_notificacoes and min_notificacoes > 0:
                edge_counts = edge_counts[
                    edge_counts['QTD_NOTIFICACOES'] >= min_notificacoes
                ]

            # Só desenha se sobrou alguma aresta
            if not edge_counts.empty:
                arestas_existem = True

                cores_relacao = {
                    'Mesmo Estado': "#000000",
                    'Estados Diferentes': "#817D7C"
                }

                for _, row in edge_counts.iterrows():
                    legendgroup = (
                        "arestas_mesmo"
                        if row['Tipo_Relacao'] == 'Mesmo Estado'
                        else "arestas_dif"
                    )

                    # Ajuste para hover: Adicionamos pontos médios para facilitar a captura do mouse
                    # e garantimos que o customdata tenha o mesmo tamanho que o número de pontos.
                    mid_lat = (row[source_lat] + row[target_lat]) / 2
                    mid_lon = (row[source_lon] + row[target_lon]) / 2
                    
                    lats = [row[source_lat], mid_lat, row[target_lat]]
                    lons = [row[source_lon], mid_lon, row[target_lon]]
                    
                    hover_data = [
                        int(row['QTD_NOTIFICACOES']),
                        row['_SRC_NAME'],
                        row['_TGT_NAME']
                    ]

                    fig.add_trace(go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode='lines+markers', # Adicionado markers para facilitar o hover
                        line=dict(
                            width=3,
                            color=cores_relacao[row['Tipo_Relacao']]
                        ),
                        marker=dict(
                            size=0, # Markers invisíveis mas capturáveis pelo hover
                            color=cores_relacao[row['Tipo_Relacao']]
                        ),
                        # Customdata deve ter o mesmo comprimento que a lista de coordenadas
                        customdata=[hover_data] * len(lats),
                        hovertemplate=(
                            "<b>Municipio de Notificacao:</b> %{customdata[1]}<br>"
                            "<b>Municipio de Infecção:</b> %{customdata[2]}<br>"
                            "<b>Casos importados:</b> %{customdata[0]:,.0f}"
                            "<extra></extra>"
                        ),
                        showlegend=False,
                        legendgroup=legendgroup,
                        hoverlabel=dict(namelength=0)
                    ))




    # =======================================================
    # 5) NÓS
    # =======================================================
    origens = set(df['_SRC_NAME'].unique())
    destinos = set(df['_TGT_NAME'].unique())

    

    source_nodes = source_counts.rename(columns={
        source_nome: "NOME", source_col: "UF",
        source_lat: "LAT", source_lon: "LON", "num": "NUM"
    })

    target_nodes = target_counts.rename(columns={
        target_nome: "NOME", target_col: "UF",
        target_lat: "LAT", target_lon: "LON", "num": "NUM"
    })

    nodes = pd.concat([source_nodes, target_nodes]).drop_duplicates(subset=["NOME", "LAT", "LON"])
    nodes["ORIGEM_SUM"] = nodes["NOME"].map(soma_origem).fillna(0).astype(int)
    nodes["DESTINO_SUM"] = nodes["NOME"].map(soma_destino).fillna(0).astype(int)

    if min_notificacoes and min_notificacoes > 0:
        nodes = nodes[
            (nodes["ORIGEM_SUM"] >= min_notificacoes) |
            (nodes["DESTINO_SUM"] >= min_notificacoes)
        ]
    # =======================================================
    # 🔥 TIPO FINAL — sem "origem"
    # =======================================================
    def tipo(row):
        nome = row["NOME"]
        uf = row["UF"]

        # Nó do próprio estado selecionado → classificação correta
        if uf == estado_selecionado:
            if nome in origens and nome not in destinos:
                return label_apenas_origem      # ← Já muda para Notifica/Residência
            if nome in origens and nome in destinos:
                return label_origem_destino
            if nome in destinos and nome not in origens:
                return "Apenas Infecta"
            return None

        # Nó externo → sempre destino
        if nome in destinos:
            return "Apenas Infecta"

        return None

    nodes["Tipo"] = nodes.apply(tipo, axis=1)
    nodes.dropna(subset=["Tipo"], inplace=True)

    # Paleta final
    cores_nos = {
        'Apenas Notifica': '#3498DB',
        'Notifica e Infecta': "#6103DB",
        'Apenas Residência': '#3498DB',
        'Residência e Infecção': "#6103DB",
        'Apenas Infecta': '#E74C3C'
    }

    # Hover
    if selected_direction == SankeyDirection.NOTIFICATION_TO_INFECTION.value:
        hover_txt = (
            "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
            "Notificou: %{customdata[2]} casos<br>"
            "Infectou: %{customdata[3]} casos<extra></extra>"
        )
    else:
        hover_txt = (
            "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
            "Residiu: %{customdata[2]} casos<br>"
            "Infectou: %{customdata[3]} casos<extra></extra>"
        )

    # Plotagem dos nós
    for tipo_v in nodes["Tipo"].unique():
        subset = nodes[nodes["Tipo"] == tipo_v]
        fig.add_trace(go.Scattermapbox(
            lat=subset["LAT"],
            lon=subset["LON"],
            mode="markers",
            marker=dict(size=10, color=cores_nos.get(tipo_v, "#000")),
            customdata=subset[["NOME", "UF", "ORIGEM_SUM", "DESTINO_SUM"]].values,
            hovertemplate=hover_txt,
            name=tipo_v
        ))

    # =======================================================
    # 6) LEGENDA DE ARESTAS
    # =======================================================
    if arestas_existem:
        fig.add_trace(go.Scattermapbox(
            lat=[0], lon=[0],
            mode="lines",
            line=dict(width=3, color="#000000"),
            name="Mesmo Estado",
            legendgroup="arestas_mesmo",
            showlegend=True,
            hoverinfo="skip"
        ))
        fig.add_trace(go.Scattermapbox(
            lat=[0], lon=[0],
            mode="lines",
            line=dict(width=3, color="#817D7C"),
            name="Estados Diferentes",
            legendgroup="arestas_dif",
            showlegend=True,
            hoverinfo="skip"
        ))

    # =======================================================
    # 7) LAYOUT FINAL
    # =======================================================
    centro_lat = source_counts[source_lat].mean() if not source_counts.empty else -14.235
    centro_lon = source_counts[source_lon].mean() if not source_counts.empty else -51.925

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=4,
        mapbox_center={"lat": centro_lat, "lon": centro_lon},
        margin={"r": 0, "t": 80, "l": 0, "b": 0},
        height=700,
        hovermode='closest', # Garante que o hover pegue o item mais próximo
        title=dict(
            text=f"<b>Importações para {estado_selecionado} — Ano {selected_year}</b>",
            x=0.5,
            font=dict(color="black")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.95,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            itemwidth=100,
            bgcolor="rgba(255,255,255,0.85)"
        )
    )

    return fig


