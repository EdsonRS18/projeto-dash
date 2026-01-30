from dash import html
import dash_bootstrap_components as dbc
from components.loading import create_loading_component

def home_layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                create_loading_component('choropleth-estadual-map'),
            ], width=6, className="mb-4"),
            dbc.Col([
                create_loading_component('choropleth-municipal-map'),
            ], width=6, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                create_loading_component('piramide-map'),
            ], width=6, className="mb-4"),
            dbc.Col([
                create_loading_component('piramide-map2'),
            ], width=6, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                create_loading_component('corredor-map'),
            ], width=12, className="mb-4"),
        ]),
    ], className="fade-in")
