


def build_responsive_title(
    main_title,
    subtitle=None,
    max_subtitle_length=35,
    main_size=20,
    subtitle_size=14
):
    """
    Cria um título responsivo para figuras Plotly com quebra de linha e
    ajuste tipográfico controlado.
    """

    # Ajuste dinâmico do tamanho da fonte do subtítulo
    if subtitle and len(subtitle) > max_subtitle_length:
        subtitle_size -= 2

    # Montagem do texto
    if subtitle:
        text = (
            f"<b>{main_title}</b><br>"
            f"<b><span style='font-size:{subtitle_size}px'>{subtitle}</span></b>"
        )
    else:
        text = f"<b>{main_title}</b>"

    return dict(
        text=text,
        x=0.5,
        xanchor="center",
        yanchor="top",
        xref="paper",
        font=dict(size=main_size)
    )

def get_theme_colors():
    return {
        "background_color": "#FFFFFF",
        "font_color": "#000000",
        "template": "plotly_white",
        "bar_color": "#005F4B",
        "male_color": "#3988a1",
        "female_color": "#e83d7a",
        "style-mapbox": "open-street-map",
        "noti_color": "#005F4B",
        "infe_color": "#0A2C47",
        'default_color': 'rgb(169, 169, 169)',
    }