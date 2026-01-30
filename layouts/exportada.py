from dash import html
import dash_bootstrap_components as dbc
from components.loading import create_loading_component


def exportada_layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                create_loading_component('exported-sankey-graph'),
            ], width=6, className="mb-4"),
            dbc.Col([
                create_loading_component('map-exportacao'),
            ], width=6, className="mb-4"),
        ]),
    ], className="fade-in")
