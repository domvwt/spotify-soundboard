import plotly.express as px

QUAL_COLS = px.colors.qualitative.Bold
SILVER = "rgb(131, 148, 150)"


def no_bg(func):
    def wrapper(*args, **kwargs):
        fig = func(*args, **kwargs)
        fig.update_layout(
            {
                # "plot_bgcolor": "rgba(0, 0, 0, 0)",
                "paper_bgcolor": "rgba(0, 0, 0, 0)",
                "font_color": SILVER,
            }
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig

    return wrapper


# TODO: Drop global steams (ISO2 = gl)
@no_bg
def country_sunburst(chart_data):
    fig = px.sunburst(
        data_frame=chart_data,
        path=["Country", "Genre", "Artist"],
        values="Streams",
        color_discrete_sequence=QUAL_COLS,
    )
    return fig
