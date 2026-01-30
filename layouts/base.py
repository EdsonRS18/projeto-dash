from dash import html, dcc
import dash_bootstrap_components as dbc
from data.constants import SankeyDirection


# ===== LAYOUT PRINCIPAL =====

def layout(df1):

    return html.Div([

        # CSS customizado
        html.Link(
            rel='stylesheet',
            href='/assets/custom_styles.css'
        ),

        # Stores para gerenciamento de estado
        dcc.Store(id='data-cache', data={}),
        dcc.Store(id='store-aba-atual', data='btn-home'),
        dcc.Store(id="store-estado-selecionado"),


        # ================= HEADER =================
        html.Div(
            id="header-container",
            className="header fade-in",
            children=[
                html.H2(
                    className="header-title",
                    children=[
                        html.A(
                            href="http://iara-dotlab.com.br",
                            children=html.Img(src="/assets/Logo.png", className="header-logo"),
                            target="_blank"
                        ),
                        "Vis",
                    ],
                ),
            ],
        ),

        # ================= BARRA DE NAVEGAÇÃO (ABAS) =================
        html.Div(
            id="nav-bar-container",
            style={"padding": "1rem 2rem 0.5rem 2rem", "backgroundColor": "#fff"},
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button(
        [html.I(className="bi bi-house-fill me-2"), "Home"],
        id="btn-home",
        className="nav-btn px-4",
        color="primary"
    ),
                            dbc.Button(
        [html.I(className="bi bi-arrow-down-left-circle me-2"), "Malária Importada"],
        id="btn-importada",
        className="nav-btn px-4",
        color="primary"
    )
    ,
                            dbc.Button(
        [html.I(className="bi bi-arrow-up-right-circle me-2"), "Malária Exportada"],
        id="btn-exportada",
        className="nav-btn px-4",
        color="primary"
    )
    ,
                        ], size="md"),
                    ], width=12),
                ]),
            ]
        ),

    html.Div(
        id="top-filter-bar",
        className="shadow-sm",
        style={
            "padding": "1rem 2rem",
            "backgroundColor": "#fff",
            "borderBottom": "1px solid #eee"
        },
        children=[

            # ===================== LINHA 1 — FILTROS PRINCIPAIS =====================
            dbc.Row(
                [

                    # ===== COLUNA 1 — ANO =====
                    dbc.Col(
                        [
                            html.Label("Ano", className="small fw-bold mb-1"),
                            dcc.Dropdown(
                                id="ano-dropdown-principal",
                                options=sorted(
                                    [{'label': str(ano), 'value': ano}
                                    for ano in df1["ANO"].dropna().unique()],
                                    key=lambda x: int(x['label']),
                                    reverse=True
                                ),
                                value=2022,
                                clearable=False,
                            ),
                        ],
                        md=2,
                        lg=2
                    ),

                    # ===== COLUNA 2 — MUNICÍPIO / ESTADO =====
                    dbc.Col(
                        [

                            # MUNICÍPIO DE NOTIFICAÇÃO
                            html.Div(
                                id="container-cidade",
                                children=[
                                    html.Label(
                                        "Município de Notificação",
                                        className="small fw-bold mb-1"
                                    ),
                                    dcc.Dropdown(
                                        id="cidade-dropdown",
                                        options=[{'label': 'Todos os Municípios', 'value': 'Todos'}] + sorted(
                                            [
                                                {
                                                    'label': f"{row['NOME_NOTI']} - {row['SIGLA_NOTI']}",
                                                    'value': str(int(row['MUN_NOTI']))
                                                }
                                                for _, row in df1[['MUN_NOTI', 'NOME_NOTI', 'SIGLA_NOTI']]
                                                .drop_duplicates()
                                                .iterrows()
                                            ],
                                            key=lambda x: x['label']
                                        ),
                                        value='Todos',
                                    ),
                                ],
                                style={"display": "block"}
                            ),

                            # IMPORTAÇÃO
                            html.Div(
                                id="container-estado-importacao",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Estado de Origem (Importação)",
                                                        className="small fw-bold mb-1"
                                                    ),
                                                    dcc.Dropdown(
                                                        id="estado-dropdown-importacao"
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Município",
                                                        id="label-municipio-importacao",
                                                        className="small fw-bold mb-1"
                                                    ),
                                                    dcc.Dropdown(
                                                        id="municipio-dropdown-importacao",
                                                        disabled=True,
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                        ],
                                        className="g-2",
                                    ),
                                ],
                                style={"display": "none"},
                            ),

                            # EXPORTAÇÃO
                            html.Div(
                                id="container-estado-exportacao",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Estado de Origem (Exportação)",
                                                        className="small fw-bold mb-1"
                                                    ),
                                                    dcc.Dropdown(
                                                        id="estado-dropdown-exportacao"
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Município",
                                                        id="label-municipio-exportacao",
                                                        className="small fw-bold mb-1"
                                                    ),
                                                    dcc.Dropdown(
                                                        id="municipio-dropdown-exportacao",
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                        ],
                                        className="g-2",
                                    ),
                                ],
                                style={"display": "none"},
                            ),
                        ],
                        md=4,
                        lg=4
                    ),

                    # ===== COLUNA 3 — GRANULARIDADE / FLUXO =====
                    dbc.Col(
                        [
                            html.Div(
                                id="radio-granularidade-importacao",
                                children=[
                                    html.Label(
                                        "Granularidade",
                                        className="small fw-bold mb-1"
                                    ),
                                    dbc.RadioItems(
                                        id='escopo-radio',
                                        options=[
                                            {'label': 'Estadual', 'value': 'estadual'},
                                            {'label': 'Municipal', 'value': 'municipal'}
                                        ],
                                        value='estadual',
                                        inline=True,
                                        className="small"
                                    ),
                                ],
                                style={"display": "none"}
                            ),

                            html.Div(
                                id="radio-granularidade-exportacao",
                                children=[
                                    html.Label(
                                        "Granularidade",
                                        className="small fw-bold mb-1"
                                    ),
                                    dbc.RadioItems(
                                        id='escopo-radioE',
                                        options=[
                                            {'label': 'Estadual', 'value': 'estadual'},
                                            {'label': 'Municipal', 'value': 'municipal'}
                                        ],
                                        value='estadual',
                                        inline=True,
                                        className="small"
                                    ),
                                ],
                                style={"display": "none"}
                            ),

                            html.Div(
                                id="radio-fluxo-importacao",
                                children=[
                                    html.Label(
                                        "Fluxo",
                                        className="small fw-bold mb-1"
                                    ),
                                    dbc.RadioItems(
                                        id="imported-sankey-direction-input",
                                        options=[
                                            {
                                                "label": "Notif. → Infec.",
                                                "value": SankeyDirection.NOTIFICATION_TO_INFECTION.value
                                            },
                                            {
                                                "label": "Resid. → Infec.",
                                                "value": SankeyDirection.RESIDENCE_TO_INFECTION.value
                                            },
                                        ],
                                        value=SankeyDirection.NOTIFICATION_TO_INFECTION.value,
                                        inline=True,
                                        className="small"
                                    ),
                                ],
                                style={"display": "none"}
                            ),

                            html.Div(
                                id="radio-fluxo-exportacao",
                                children=[
                                    html.Label(
                                        "Fluxo",
                                        className="small fw-bold mb-1"
                                    ),
                                    dbc.RadioItems(
                                        id="exported-sankey-direction-input",
                                        options=[
                                            {
                                                "label": "Infec. → Notif.",
                                                "value": SankeyDirection.INFECTION_TO_NOTIFICATION.value
                                            },
                                            {
                                                "label": "Infec. → Resid.",
                                                "value": SankeyDirection.INFECTION_TO_RESIDENCE.value
                                            },
                                        ],
                                        value=SankeyDirection.INFECTION_TO_NOTIFICATION.value,
                                        inline=True,
                                        className="small"
                                    ),
                                ],
                                style={"display": "none"}
                            ),
                        ],
                        md=4,
                        lg=4,
                        className="col-flex-duplo"
                    ),

                    # ===== COLUNA 4 — LIMPAR =====
                    dbc.Col(
                        [
                            dbc.Button(
                                [
                                    html.I(
                                        className="bi bi-arrow-counterclockwise me-1"
                                    ),
                                    "Limpar"
                                ],
                                id="limpar-filtros-button",
                                color="secondary",
                                outline=True,
                                size="sm",
                                className="w-100",
                                style={"marginTop": "24px"}
                            )
                        ],
                        md=2,
                        lg=1
                    ),

                ],
                className="g-4 align-items-start mb-3"
            ),

            # ===================== LINHA 2 — SLIDERS =====================
            dbc.Row(
                [

                    dbc.Col(
                        [
                            html.Div(
                                id="container-slider-importacao",
                                children=[
                                    html.Label(
                                        "Número mínimo de notificações (Importação)",
                                        className="small fw-bold mb-1"
                                    ),
                                    dcc.Slider(
                                        id='min-notificacoes-slider-importacao',
                                        min=1,
                                        max=1000,
                                        step=1,
                                        value=1,
                                        marks={
                                            1: '1',
                                            50: '50',
                                            100: '100',
                                            500: '500',
                                            1000: '1000'
                                        },
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True
                                        }
                                    ),
                                ],
                                style={"display": "none"}
                            ),

                            html.Div(
                                id="container-slider-exportacao",
                                children=[
                                    html.Hr(className="my-2"),
                                    html.Label(
                                        "Número mínimo de notificações (Exportação)",
                                        className="small fw-bold mb-1"
                                    ),
                                    dcc.Slider(
                                        id='min-notificacoes-slider-exportacao',
                                        min=1,
                                        max=1000,
                                        step=1,
                                        value=1,
                                        marks={
                                            1: '1',
                                            50: '50',
                                            100: '100',
                                            500: '500',
                                            1000: '1000'
                                        },
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True
                                        }
                                    ),
                                ],
                                style={"display": "none"}
                            ),
                        ],
                        width=6
                    )

                ],
                className="g-3"
            ),
        ]
    )
    ,

        # ================= CONTEÚDO PRINCIPAL =================
        html.Div(
            id="page-content",
            className="content-area fade-in",
            style={"padding": "2rem", "minHeight": "80vh", "backgroundColor": "#f1f3f5"}
        )
    ])
