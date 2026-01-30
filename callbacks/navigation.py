from dash import callback, Input, Output, State
import dash

from layouts.home import home_layout
from layouts.importada import importada_layout
from layouts.exportada import exportada_layout

@callback(
    [
        Output('page-content', 'children'),
        Output('btn-home', 'className'),
        Output('btn-importada', 'className'),
        Output('btn-exportada', 'className'),
        Output("radio-granularidade-importacao", "style"),
        Output("radio-fluxo-importacao", "style"),
        Output("radio-granularidade-exportacao", "style"),
        Output("radio-fluxo-exportacao", "style"),
        Output('store-aba-atual', 'data')
    ],
    [
        Input('btn-home', 'n_clicks'),
        Input('btn-importada', 'n_clicks'),
        Input('btn-exportada', 'n_clicks'),
    ],
    State('store-aba-atual', 'data'),
    prevent_initial_call=False
)
def render_page(btn_home, btn_importada, btn_exportada, aba_atual):

    ctx = dash.callback_context

    # ===== ABA ATUAL =====
    pagina = aba_atual or 'btn-home'
    if ctx.triggered:
        pagina = ctx.triggered[0]['prop_id'].split('.')[0]

    # ===== CLASSES DOS BOTÕES =====
    def cls(btn):
        return "nav-btn px-4 active" if btn == pagina else "nav-btn px-4"

    # ===== STYLES =====
    hidden = {"display": "none"}
    visible = {"display": "block"}

    radio_gran_import = hidden
    radio_fluxo_import = hidden
    radio_gran_export = hidden
    radio_fluxo_export = hidden

    # ===== CONTEÚDO =====
    if pagina == 'btn-importada':
        content = importada_layout()
        radio_gran_import = visible
        radio_fluxo_import = visible

    elif pagina == 'btn-exportada':
        content = exportada_layout()
        radio_gran_export = visible
        radio_fluxo_export = visible

    else:
        content = home_layout()

    return (
        content,
        cls('btn-home'),
        cls('btn-importada'),
        cls('btn-exportada'),
        radio_gran_import,
        radio_fluxo_import,
        radio_gran_export,
        radio_fluxo_export,
        pagina
    )

