import numpy as np
import pandas as pd
import plotly.express as px

QUAL_COLS = px.colors.qualitative.Bold
SILVER = "rgb(131, 148, 150)"


def no_bg(func):
    def wrapper(*args, **kwargs):
        fig = func(*args, **kwargs)
        fig.update_layout(
            {
                "plot_bgcolor": "rgba(0, 0, 0, 0)",
                "paper_bgcolor": "rgba(0, 0, 0, 0)",
                "font_color": SILVER,
            }
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig

    return wrapper


@no_bg
def country_sunburst(chart_data):
    fig = px.sunburst(
        data_frame=chart_data,
        path=["Country", "Genre", "Artist"],
        values="Streams",
        color_discrete_sequence=QUAL_COLS,
    )
    return fig


@no_bg
def world_choropleth(chart_data: pd.DataFrame, scope=None):
    if scope is None:
        scope = "world"
    chart_data.loc[:, "Streams (log10)"] = np.log(chart_data["Streams"])
    fig = px.choropleth(
        data_frame=chart_data,
        locations=chart_data["ISO3"],
        color="Streams (log10)",
        hover_name="Country",
        hover_data={
            "ISO3": False,
            "Streams (log10)": False,
            "Streams": ":,0f",
            "Top Artist": True,
            "Top Genre": True,
        },
        locationmode="ISO-3",
        color_continuous_scale=px.colors.sequential.Agsunset,
        projection="miller",
        scope=scope,
    )
    fig.update_geos(
        visible=False,
        resolution=110,
        bgcolor="rgba(0,0,0,0)",
        showcountries=False,
        showland=True,
        landcolor=SILVER,
        lataxis={"range": [-40, 90]} if scope == "world" else None,
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={"tickprefix": "10e"},
    )
    return fig
