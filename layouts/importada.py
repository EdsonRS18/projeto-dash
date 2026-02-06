from dash import html
import dash_bootstrap_components as dbc
from components.loading import create_loading_component


def importada_layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                create_loading_component('imported-sankey-graph'),
            ], width=6, className="mb-4", style={"height": "800px"}),

            dbc.Col([
                create_loading_component('map-importacao'),
            ], width=6, className="mb-4"),
        ]),

    ], className="fade-in")
