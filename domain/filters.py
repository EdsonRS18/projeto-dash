from data.constants import direction_columns, SankeyDirection

def get_available_states(df, selected_year, selected_direction):
    if not isinstance(selected_direction, SankeyDirection):
        selected_direction = SankeyDirection(selected_direction)

    source_column, target_column = direction_columns(selected_direction)

    filtered_df = df[df[source_column] != df[target_column]]
    filtered_df = filtered_df[filtered_df["ANO"] == selected_year]

    estados = filtered_df[source_column].dropna().unique()
    return sorted(estados)