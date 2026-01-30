from dash import dcc

# ===== COMPONENTES DE LOADING =====
def create_loading_component(graph_id):
    return dcc.Loading(
        id=f"loading-{graph_id}",
        type="default",
        children=dcc.Graph(
            id=graph_id,
            className=f"graph-container cursor-{graph_id}",
            style={
                'height': '800px' if 'map' in graph_id or 'piramide' in graph_id else '800px'
            }
        ),
        style={
            "background": "rgba(255, 255, 255, 0.8)",
            "border-radius": "12px"
        },
        color="#043241"
    )
