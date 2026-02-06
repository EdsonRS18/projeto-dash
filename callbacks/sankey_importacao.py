from dash import callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import store
from utils.visualization import get_theme_colors, build_responsive_title
from data.constants import direction_columns, direction_text



@callback(
    Output('imported-sankey-graph', 'figure'),
    [
        Input('ano-dropdown-principal', 'value'),
        Input('estado-dropdown-importacao', 'value'),
        Input('municipio-dropdown-importacao', 'value'),
        Input('imported-sankey-direction-input', 'value'),
        Input('escopo-radio', 'value'),
        Input('min-notificacoes-slider-importacao', 'value'),  
    ]
)
def update_imported_sankey(
    selected_year,
    selected_state,
    selected_municipio,
    selected_direction,
    selected_scope,
    min_notificacoes  # 👈 NOVO PARÂMETRO
):

    theme_colors = get_theme_colors()
    source_col, target_col = direction_columns(selected_direction)
    df = store.df1
    filtered_df = df.copy()

    # -------------------------
    # FILTROS BÁSICOS
    # -------------------------
    if selected_year != "Todos":
        filtered_df = filtered_df[filtered_df['ANO'] == selected_year]

    if selected_state and selected_state != "Todos":
        filtered_df = filtered_df[filtered_df[source_col] == selected_state]

    # Normalização
    for col in ['NOME_INFE','NOME_NOTI','NOME_RESI']:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].str.upper()

    # Identificação dos nomes
    src_name_col = (
        'NOME_NOTI' if source_col == 'SIGLA_NOTI'
        else 'NOME_RESI' if source_col == 'SIGLA_RESI'
        else 'NOME_INFE'
    )

    tgt_name_col = (
        'NOME_NOTI' if target_col == 'SIGLA_NOTI'
        else 'NOME_RESI' if target_col == 'SIGLA_RESI'
        else 'NOME_INFE'
    )

    filtered_df = filtered_df[
        filtered_df[src_name_col] != filtered_df[tgt_name_col]
    ]

    # -------------------------
    # VISÃO ESTADUAL
    # -------------------------
    if selected_scope == 'estadual':

        df_sankey = (
            filtered_df
            .groupby([source_col, target_col, 'ANO'], as_index=False)
            ['QTD_NOTIFICACOES']
            .sum()
        )

# 👇 FILTRO PELO SLIDER
        df_sankey = df_sankey[
        df_sankey['QTD_NOTIFICACOES'] >= min_notificacoes
]

        df_sankey['source_label'] = df_sankey[source_col]
        df_sankey['target_label'] = df_sankey[target_col]

    # -------------------------
    # VISÃO MUNICIPAL
    # -------------------------
    else:

        nome_map = {
            'SIGLA_NOTI': ('NOME_NOTI', 'SIGLA_NOTI'),
            'SIGLA_INFE': ('NOME_INFE', 'SIGLA_INFE'),
            'SIGLA_RESI': ('NOME_RESI', 'SIGLA_RESI'),
        }

        if source_col not in nome_map or target_col not in nome_map:
            return go.Figure().update_layout(
                title_text="Direção não suportada para escopo municipal",
                title_x=0.5
            )

        src_nome, src_sigla = nome_map[source_col]
        tgt_nome, tgt_sigla = nome_map[target_col]

        # Filtro por município (drill-down)
        if selected_municipio:
            filtered_df = filtered_df[
                filtered_df[src_nome] == selected_municipio
            ]

        df_sankey = (
            filtered_df
            .groupby(
                [src_nome, tgt_nome, 'ANO', src_sigla, tgt_sigla],
                as_index=False
            )['QTD_NOTIFICACOES']
            .sum()
        )

        # 👇 FILTRO PELO SLIDER
        df_sankey = df_sankey[
            df_sankey['QTD_NOTIFICACOES'] >= min_notificacoes
        ]


        df_sankey['source_label'] = (
            df_sankey[src_nome] + " - " + df_sankey[src_sigla]
        )
        df_sankey['target_label'] = (
            df_sankey[tgt_nome] + " - " + df_sankey[tgt_sigla]
        )

    # -------------------------
    # CONSTRUÇÃO DO SANKEY
    # -------------------------
    labels = list(set(
        df_sankey['source_label'].tolist() +
        df_sankey['target_label'].tolist()
    ))

    label_dict = {label: i for i, label in enumerate(labels)}

    duplicated_labels = labels + [l + "_target" for l in labels]
    duplicated_label_dict = {
        label: i for i, label in enumerate(duplicated_labels)
    }

    source = [label_dict[s] for s in df_sankey['source_label']]
    target = [
        duplicated_label_dict[t] + len(labels)
        for t in df_sankey['target_label']
    ]
    value = df_sankey['QTD_NOTIFICACOES']

    # Agrupar links iguais
    link_dict = {}
    for s, t, v in zip(source, target, value):
        link_dict[(s, t)] = link_dict.get((s, t), 0) + v

    if link_dict:
        final_source, final_target, final_value = zip(
            *[(k[0], k[1], v) for k, v in link_dict.items()]
        )
    else:
        final_source, final_target, final_value = [], [], []

    # -------------------------
    # CORES DOS NÓS (POR UF)
    # -------------------------
    def extract_uf(label):
        return label.split(" - ")[-1] if " - " in label else label

    unique_ufs = sorted(set(
        extract_uf(l.replace("_target", "")) for l in duplicated_labels
    ))

    palette = px.colors.qualitative.Dark24
    while len(palette) < len(unique_ufs):
        palette += palette

    uf_color_map = {
        uf: palette[i] for i, uf in enumerate(unique_ufs)
    }

    node_colors = [
        uf_color_map[extract_uf(l.replace("_target", ""))]
        for l in duplicated_labels
    ]

    visual_labels = [
        l.replace("_target", "") for l in duplicated_labels
    ]

    # -------------------------
    # TÍTULO
    # -------------------------
    ano_text = "Todos os anos" if selected_year == "Todos" else f"Ano {selected_year}"
    escopo_text = "Estadual" if selected_scope == 'estadual' else "Municipal"


    # -------------------------
    # FIGURA FINAL
    # -------------------------
    sankey_fig = go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="gray", width=0.5),
            label=visual_labels,
            color=node_colors,
            hovertemplate="<b>%{label}</b><br>%{value:,}<extra></extra>",
        ),
        link=dict(
            source=final_source,
            target=final_target,
            value=final_value,
            hovertemplate=(
                "<b>Estado de Notificaçao:</b> %{source.label}<br>"
                "<b>Estado de Infecção:</b> %{target.label}<br>"
                "<b>Casos importados:</b> %{value:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig = go.Figure(sankey_fig)

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
        margin=dict(r=0, t=50, l=0, b=0),
        plot_bgcolor=theme_colors['background_color'],
        paper_bgcolor=theme_colors['background_color'],
        font=dict(color=theme_colors['font_color']),
        template=theme_colors['template']
    )

    return fig


