from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title
from data.constants import direction_columns, direction_text,SankeyDirection
from collections import Counter
import numpy as np





@callback(
    Output('exported-sankey-graph', 'figure'),
    [
        Input('ano-dropdown-principal', 'value'),
        Input('estado-dropdown-exportacao', 'value'),
        Input('municipio-dropdown-exportacao', 'value'),

        Input('exported-sankey-direction-input', 'value'),
        Input('escopo-radioE', 'value'),
        Input('min-notificacoes-slider-exportacao', 'value'),
    ]
)

def update_exported_sankey(
    selected_year,
    selected_state=None,
    selected_municipio=None,
    selected_direction=SankeyDirection.INFECTION_TO_NOTIFICATION.value,
    selected_scope='estadual',
    min_notificacoes = 1
):
    theme_colors = get_theme_colors()

    # Obter colunas de source e target com base na direção
    source_col, target_col = direction_columns(selected_direction)

    if selected_direction not in {
        SankeyDirection.INFECTION_TO_NOTIFICATION.value,
        SankeyDirection.INFECTION_TO_RESIDENCE.value
    }:
        return go.Figure().update_layout(
            title_text="Direção não suportada. Use Infecção → Notificação ou Infecção → Residência.",
            title_x=0.5
        )
    df = store.df1
    filtered_df = df.copy()

    if selected_year != "Todos":
        filtered_df = filtered_df[filtered_df['ANO'] == selected_year]
    # O filtro de estado deve ser aplicado à coluna de origem (source_col)
    if selected_state and selected_state != "Todos":
        filtered_df = filtered_df[filtered_df[source_col] == selected_state]


    # Normalização
    for col in ['NOME_INFE', 'NOME_NOTI', 'NOME_RESI']:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].str.upper()

    # Remover auto-conexões municipais (apenas onde o nome da origem é igual ao nome do destino)
    src_name_col = 'NOME_INFE' if source_col == 'SIGLA_INFE' else ('NOME_RESI' if source_col == 'SIGLA_RESI' else 'NOME_NOTI')
    tgt_name_col = 'NOME_NOTI' if target_col == 'SIGLA_NOTI' else ('NOME_RESI' if target_col == 'SIGLA_RESI' else 'NOME_INFE')
    
    # A coluna NOME_INFE/NOME_NOTI já está em UPPER (linhas 1286-1289)
    filtered_df = filtered_df[filtered_df[src_name_col] != filtered_df[tgt_name_col]]

    if selected_scope == 'estadual':
        df_sankey = (
            filtered_df
            .groupby([source_col, target_col, 'ANO'], as_index=False)['QTD_NOTIFICACOES']
            .sum()
        )
        df_sankey = df_sankey[
        df_sankey['QTD_NOTIFICACOES'] >= min_notificacoes
        ]

        df_sankey["source_label"] = df_sankey[source_col]
        df_sankey["target_label"] = df_sankey[target_col]

    else:  # Municipal
        nome_map = {
            'SIGLA_NOTI': ('NOME_NOTI', 'SIGLA_NOTI'),
            'SIGLA_INFE': ('NOME_INFE', 'SIGLA_INFE'),
            'SIGLA_RESI': ('NOME_RESI', 'SIGLA_RESI'), # Alterado de MUN_RESI para NOME_RESI
        }

        if source_col not in nome_map or target_col not in nome_map:
            return go.Figure().update_layout(title_text="Direção não suportada para escopo municipal", title_x=0.5)

        src_nome, src_sigla = nome_map[source_col]
        tgt_nome, tgt_sigla = nome_map[target_col]

        if selected_municipio:
            filtered_df = filtered_df[
                filtered_df[src_nome] == selected_municipio
            ]

        df_sankey = (
            filtered_df
            .groupby([src_nome, tgt_nome, 'ANO', src_sigla, tgt_sigla], as_index=False)['QTD_NOTIFICACOES']
            .sum()
        )
        # 👇 FILTRO PELO SLIDER
        df_sankey = df_sankey[
            df_sankey['QTD_NOTIFICACOES'] >= min_notificacoes
        ]

        df_sankey["source_label"] = df_sankey[src_nome] + " - " + df_sankey[src_sigla]
        df_sankey["target_label"] = df_sankey[tgt_nome] + " - " + df_sankey[tgt_sigla]

    # Labels e indexação
    labels = list(set(df_sankey["source_label"].tolist() + df_sankey["target_label"].tolist()))
    label_dict = {label: i for i, label in enumerate(labels)}
    duplicated_labels = labels + [label + "_target" for label in labels]
    duplicated_label_dict = {label: i for i, label in enumerate(duplicated_labels)}

    source = [label_dict[src] for src in df_sankey["source_label"]]
    target = [duplicated_label_dict[dst] + len(labels) for dst in df_sankey["target_label"]]
    value = df_sankey["QTD_NOTIFICACOES"]

    # Agrupar valores iguais
    link_dict = Counter()
    for s, t, v in zip(source, target, value):
        link_dict[(s, t)] += v

    if link_dict:
        final_source, final_target, final_value = zip(*[(k[0], k[1], v) for k, v in link_dict.items()])
    else:
        final_source, final_target, final_value = [], [], []

    # Cores por UF
    def extract_uf(label):
        if " - " in label:
            return label.split(" - ")[-1]
        return label

    unique_ufs = sorted(set([extract_uf(label.replace("_target", "")) for label in duplicated_labels]))
    color_palette = px.colors.qualitative.Dark24
    while len(color_palette) < len(unique_ufs):
        color_palette += color_palette
    uf_color_map = {uf: color_palette[i] for i, uf in enumerate(unique_ufs)}
    node_colors = [uf_color_map[extract_uf(label.replace("_target", ""))] for label in duplicated_labels]
    visual_labels = [label.replace("_target", "") for label in duplicated_labels]

    # Título
    ano_text = "Todos os anos" if selected_year == "Todos" else f"Ano {selected_year}"
    escopo_text = "Estadual" if selected_scope == 'estadual' else "Municipal"
    title = f"<b>{direction_text(selected_direction)}, {ano_text} ({escopo_text})</b>"

    customdata = np.stack([
    df_sankey["source_label"],
    df_sankey["target_label"]
], axis=-1)

    # Construção do gráfico Sankey com hover em notação BR + origem/destino
    fig = go.Figure(go.Sankey(
        node=dict(
    pad=15,
    thickness=20,
    line=dict(color="gray", width=0.5),
    label=visual_labels,
    color=node_colors,
    hovertemplate=(
        "<b>%{label}</b><br>"
        " %{value:,}"
        "<extra></extra>"
    )
    ),

    valueformat=",d",
    valuesuffix="",
        link=dict(
            source=final_source,
            target=final_target,
            value=final_value,
            customdata=customdata,
            hovertemplate=(
                "<b>Estado de exportação:</b> %{customdata[0]}<br>" +
                "<b>Estado de importação:</b> %{customdata[1]}<br>" +
                "<b>Casos exportados:</b> " +
                "%{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") +
                "<extra></extra>"
            ),
            
        ),
        arrangement='fixed'
    ))

    # -------------------------
# TÍTULO (ESTADO x MUNICÍPIO)
# -------------------------
    if selected_scope == 'municipal':
        title_direction = direction_text(selected_direction).replace(
            'Estado', 'Município'
        )
    else:
        title_direction = direction_text(selected_direction)

    fig.update_layout(
        title=build_responsive_title(
            main_title=f"<b>{title_direction}, </b>",
            subtitle=f"<b>{ano_text} ({escopo_text})</b>"
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        plot_bgcolor=theme_colors["background_color"],
        paper_bgcolor=theme_colors["background_color"],
        font=dict(color=theme_colors["font_color"]),
        template=theme_colors["template"],
    )


    return fig

