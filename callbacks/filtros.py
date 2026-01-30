from dash import callback, Input, Output, State
import dash
from domain.filters import get_available_states
from data import store


# Callback para mostrar/esconder filtros regionais
@callback(
    [
        Output("container-cidade", "style"),
        Output("container-estado-importacao", "style"),
        Output("container-estado-exportacao", "style"),
        Output("container-slider-importacao", "style"),
        Output("container-slider-exportacao", "style"),
    ],
    [
        Input("btn-home", "n_clicks"),
        Input("btn-importada", "n_clicks"),
        Input("btn-exportada", "n_clicks"),
    ],
)
def toggle_filtros_regionais(n_home, n_importada, n_exportada):
    visible = {"display": "block"}
    hidden = {"display": "none"}

    pagina = dash.callback_context.triggered_id or "btn-home"

    if pagina == "btn-home":
        return visible, hidden, hidden, hidden, hidden

    elif pagina == "btn-importada":
        return hidden, visible, hidden, visible, hidden

    elif pagina == "btn-exportada":
        return hidden, hidden, visible, hidden, visible

    return hidden, hidden, hidden, hidden, hidden



@callback(
    [
        Output('estado-dropdown-importacao', 'options'),
        Output('estado-dropdown-importacao', 'value', allow_duplicate=True),
        Output('estado-dropdown-exportacao', 'options'),
        Output('estado-dropdown-exportacao', 'value', allow_duplicate=True),
    ],
    [
        Input('ano-dropdown-principal', 'value'),
        Input('imported-sankey-direction-input', 'value'),
        Input('exported-sankey-direction-input', 'value'),
        Input('store-aba-atual', 'data'),
    ],
    prevent_initial_call=True
)
def update_estado_dropdowns(selected_year, direction_imported, direction_exported, aba_atual):

    if aba_atual == 'btn-importada':
        estados_import = get_available_states(store.df1,selected_year, direction_imported)

        options_import = [{'label': 'Todos', 'value': 'Todos'}] + \
                         [{'label': e, 'value': e} for e in estados_import]

        return options_import, "Todos", [], None

    elif aba_atual == 'btn-exportada':
        estados_export = get_available_states(store.df1,selected_year, direction_exported)

        options_export = [{'label': 'Todos', 'value': 'Todos'}] + \
                         [{'label': e, 'value': e} for e in estados_export]

        return [], None, options_export, "Todos"

    else:
        return [], None, [], None


# Botão de resetar filtros
@callback(
    [
        Output('ano-dropdown-principal', 'value'),
        Output('cidade-dropdown', 'value'),
        Output('estado-dropdown-importacao', 'value'),
        Output('estado-dropdown-exportacao', 'value'),
    ],
    Input('limpar-filtros-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filtros(n_clicks):
    if n_clicks:
        return 2022, 'Todos', None, None
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update



# Callback para controlar as opções do RadioItems de granularidade (Importação)
@callback(
    Output('escopo-radio', 'options'),
    Input('estado-dropdown-importacao', 'value')
)
def update_escopo_radio_options(selected_state):
    # Se o estado for "Todos", desabilitar a opção municipal
    if selected_state == "Todos" or not selected_state:
        return [
            {'label': ' Visão Estadual', 'value': 'estadual'},
            {'label': ' Visão Municipal (selecione um estado)', 'value': 'municipal', 'disabled': True}
        ]
    else:
        return [
            {'label': ' Visão Estadual', 'value': 'estadual'},
            {'label': ' Visão Municipal', 'value': 'municipal'}
        ]

# Callback para controlar as opções do RadioItems de granularidade (Exportação)
@callback(
    Output('escopo-radioE', 'options'),
    Input('estado-dropdown-exportacao', 'value')
)
def update_escopo_radioE_options(selected_state):
    # Se o estado for "Todos", desabilitar a opção municipal
    if selected_state == "Todos" or not selected_state:
        return [
            {'label': ' Visão Estadual', 'value': 'estadual'},
            {'label': ' Visão Municipal (selecione um estado)', 'value': 'municipal', 'disabled': True}
        ]
    else:
        return [
            {'label': ' Visão Estadual', 'value': 'estadual'},
            {'label': ' Visão Municipal', 'value': 'municipal'}
        ]

# Callback para resetar o escopo para estadual quando o estado for "Todos" (Importação)
@callback(
    Output('escopo-radio', 'value'),
    Input('estado-dropdown-importacao', 'value'),
    State('escopo-radio', 'value')
)
def reset_escopo_radio_value(selected_state, current_escopo):
    # Se o estado for "Todos" e o escopo atual for municipal, resetar para estadual
    if (selected_state == "Todos" or not selected_state) and current_escopo == 'municipal':
        return 'estadual'
    return dash.no_update

# Callback para resetar o escopo para estadual quando o estado for "Todos" (Exportação)
@callback(
    Output('escopo-radioE', 'value'),
    Input('estado-dropdown-exportacao', 'value'),
    State('escopo-radioE', 'value')
)
def reset_escopo_radioE_value(selected_state, current_escopo):
    # Se o estado for "Todos" e o escopo atual for municipal, resetar para estadual
    if (selected_state == "Todos" or not selected_state) and current_escopo == 'municipal':
        return 'estadual'
    return dash.no_update



@callback(
    [
        Output('estado-dropdown-exportacao', 'value', allow_duplicate=True),
        Output('municipio-dropdown-exportacao', 'value', allow_duplicate=True),
    ],
    Input('exported-sankey-graph', 'clickData'),
    State('escopo-radioE', 'value'),
    prevent_initial_call=True
)
def update_dropdowns_from_sankey_exportacao(clickData, escopo):

    if not clickData or 'points' not in clickData:
        return dash.no_update, dash.no_update

    label = clickData['points'][0].get('label')
    if not label:
        return dash.no_update, dash.no_update

    # Escopo ESTADUAL
    if escopo == 'estadual':
        uf = label.split(" - ")[-1] if " - " in label else label
        return uf, None

    # Escopo MUNICIPAL
    if escopo == 'municipal' and " - " in label:
        municipio, uf = label.split(" - ")
        return uf, municipio

    return dash.no_update, dash.no_update


@callback(
    [
        Output("municipio-dropdown-exportacao", "disabled"),
        Output("label-municipio-exportacao", "style"),
        Output("municipio-dropdown-exportacao", "value"),
    ],
    [
        Input("escopo-radioE", "value"),
        Input("estado-dropdown-exportacao", "value"),
    ]
)
def control_municipio_dropdown_exportacao(escopo, estado):

    base_style = {
        "fontWeight": "bold",
        "marginTop": "8px",
    }

    if escopo != "municipal":
        return True, {**base_style, "color": "#888"}, None

    if not estado or estado == "Todos":
        return True, {**base_style, "color": "#888"}, None

    return False, {**base_style, "color": "#000"}, dash.no_update

@callback(
    Output('municipio-dropdown-exportacao', 'options'),
    Input('estado-dropdown-exportacao', 'value')
)
def update_municipio_dropdown_exportacao(selected_state):

    if not selected_state or selected_state == "Todos":
        return []
    df = store.df1
    df_municipios = df[df['SIGLA_INFE'] == selected_state]

    municipios = (
        df_municipios['NOME_INFE']
        .dropna()
        .str.upper()
        .sort_values()
        .unique()
    )

    return [{'label': m, 'value': m} for m in municipios]

@callback(
    [
        Output('estado-dropdown-importacao', 'value', allow_duplicate=True),
        Output('municipio-dropdown-importacao', 'value', allow_duplicate=True),
    ],
    Input('imported-sankey-graph', 'clickData'),
    State('escopo-radio', 'value'),
    prevent_initial_call=True
)
def update_dropdowns_from_sankey(clickData, escopo):
    if not clickData or 'points' not in clickData:
        return dash.no_update, dash.no_update

    label = clickData['points'][0].get('label')
    if not label:
        return dash.no_update, dash.no_update

    # Escopo ESTADUAL → seleciona UF
    if escopo == 'estadual':
        uf = label.split(" - ")[-1] if " - " in label else label
        return uf, None

    # Escopo MUNICIPAL → seleciona município
    if escopo == 'municipal' and " - " in label:
        municipio = label.split(" - ")[0]
        uf = label.split(" - ")[-1]
        return uf, municipio

    return dash.no_update, dash.no_update


@callback(
    [
        Output("municipio-dropdown-importacao", "disabled"),
        Output("label-municipio-importacao", "style"),
        Output("municipio-dropdown-importacao", "value"),
    ],
    [
        Input("escopo-radio", "value"),
        Input("estado-dropdown-importacao", "value"),
    ]
)
def control_municipio_dropdown(escopo, estado):

    base_style = {
        "fontWeight": "bold",
        "marginTop": "8px",
    }

    if escopo != "municipal":
        return True, {**base_style, "color": "#888"}, None

    if not estado or estado == "Todos":
        return True, {**base_style, "color": "#888"}, None

    return False, {**base_style, "color": "#000"}, dash.no_update

@callback(
    Output('municipio-dropdown-importacao', 'options'),
    Input('estado-dropdown-importacao', 'value')
)
def update_municipio_dropdown(selected_state):

    if not selected_state or selected_state == "Todos":
        return []
    df = store.df1
    df_municipios = df[df['SIGLA_INFE'] == selected_state]

    municipios = (
        df_municipios['NOME_INFE']
        .dropna()
        .str.upper()
        .sort_values()
        .unique()
    )

    return [{'label': m, 'value': m} for m in municipios]

