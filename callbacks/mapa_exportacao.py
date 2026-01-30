
from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title
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
    estado_selecionado=None,
    selected_municipio = None,
    click_data=None, 
    selected_direction=None,
    min_notificacoes = 1
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

    # Remover linhas inválidas
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
    # 2) Direções (SOURCE = INFEÇÃO)
    # =======================================================
    if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
        source_col = 'SIGLA_INFE'
        target_col = 'SIGLA_NOTI'
        source_nome = 'NOME_INFE'
        target_nome = 'NOME_NOTI'
        source_lat = 'LATITUDE_INFE'
        source_lon = 'LONGITUDE_INFE'
        target_lat = 'LATITUDE_NOTI'
        target_lon = 'LONGITUDE_NOTI'
        label_apenas_origem = "Apenas Infecta"
        label_origem_destino = "Infecta e Notifica"

    elif selected_direction == SankeyDirection.INFECTION_TO_RESIDENCE.value:
        source_col = 'SIGLA_INFE'
        target_col = 'SIGLA_RESI'
        source_nome = 'NOME_INFE'
        target_nome = 'NOME_RESI'
        source_lat = 'LATITUDE_INFE'
        source_lon = 'LONGITUDE_INFE'
        target_lat = 'LATITUDE_RESI'
        target_lon = 'LONGITUDE_RESI'
        label_apenas_origem = "Apenas Infecta"
        label_origem_destino = "Infecta e Reside"

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

    # Apenas origem = estado selecionado
    df = df[df[source_col] == estado_selecionado]
    df = df[df['_SRC_NAME'] != df['_TGT_NAME']]

    # =======================================================
    # 3) Contagens de origem e destino
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

            def classificar(row):
                return 'Mesmo Estado' if row[source_col] == row[target_col] else 'Estados Diferentes'

            df_selected = df_selected.copy()
            df_selected['Tipo_Relacao'] = df_selected.apply(classificar, axis=1)

            edge_counts = (
                df_selected.groupby([source_lat, source_lon, target_lat, target_lon,
                                     '_SRC_NAME', '_TGT_NAME', 'Tipo_Relacao'],
                                    as_index=False)['QTD_NOTIFICACOES']
                .sum()
            )
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
                            "<b>Municipio de Exportação:</b> %{customdata[1]}<br>"
                            "<b>Municipio de Importação:</b> %{customdata[2]}<br>"
                            "<b>Casos exportados:</b> %{customdata[0]:,.0f}"
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

    

    def tipo(row):
        nome = row["NOME"]
        uf = row["UF"]

        # ORIGEM = estado selecionado (sempre INFECTA)
        if uf == estado_selecionado:
            if nome in origens and nome not in destinos: 
                return "Apenas Infecta"

            # Direção NOTIFICAÇÃO
            if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
                if nome in destinos and nome not in origens:
                    return "Apenas Notifica"
                if nome in origens and nome in destinos:
                    return "Notifica e Infecta"

            # Direção RESIDÊNCIA
            if selected_direction == SankeyDirection.INFECTION_TO_RESIDENCE.value:
                if nome in destinos and nome not in origens:
                    return "Apenas Residência"
                if nome in origens and nome in destinos:
                    return "Residência e Infecção"

            return None

        # NÓ EXTERNO — apenas NOTIFICA ou RESIDE
        if nome in destinos:
            if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
                return "Apenas Notifica"
            if selected_direction == SankeyDirection.INFECTION_TO_RESIDENCE.value:
                return "Apenas Residência"

        return None

    nodes["Tipo"] = nodes.apply(tipo, axis=1)
    nodes.dropna(subset=["Tipo"], inplace=True)

    cores_nos = {
    'Apenas Notifica': '#3498DB',
    'Notifica e Infecta': "#6103DB",
    'Apenas Residência': '#3498DB',
    'Residência e Infecção': "#6103DB",
    'Apenas Infecta': '#E74C3C'
}
        # Hover específico dependendo da direção
    if selected_direction == SankeyDirection.INFECTION_TO_NOTIFICATION.value:
        hover_txt = (
            "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
            "Infectou: %{customdata[2]} casos<br>"
            "Notificou: %{customdata[3]} casos<extra></extra>"
        )
    else:
        hover_txt = (
            "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
            "Infectou: %{customdata[2]} casos<br>"
            "Residiu: %{customdata[3]} casos<extra></extra>"
        )


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
    # 6) SE EXISTEM ARESTAS → CRIA LEGENDA
    # =======================================================
    if arestas_existem:
        # Legenda de arestas – Mesmo Estado
        fig.add_trace(go.Scattermapbox(
            lat=[0], lon=[0],
            mode="lines",
            line=dict(width=3, color="#000000"),
            name="Mesmo Estado",
            legendgroup="arestas_mesmo",
            showlegend=True,
            hoverinfo="skip"
        ))

        # Legenda de arestas – Diferentes Estados
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
        title=dict(
    text=f"<b>Exportações a partir de {estado_selecionado} — Ano {selected_year}</b>",
    x=0.5,
    font=dict(color="black")
),

        legend=dict(
            orientation="h",          # mantém horizontal sempre
            yanchor="bottom",
            y=0.95,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            itemwidth=100,            # maior largura → permanece lado a lado
            bgcolor="rgba(255,255,255,0.85)"  # leve fundo sólido
        )
    )

    return fig


