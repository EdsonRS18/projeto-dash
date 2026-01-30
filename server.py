import dash
import dash_bootstrap_components as dbc

# =====================================================
# Instância central da aplicação
# =====================================================

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    ]
)

# =====================================================
# Exposição do servidor WSGI (deploy)
# =====================================================

server = app.server
