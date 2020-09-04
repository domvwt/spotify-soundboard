import numpy as np
import pandas as pd
import plotly.express as px

from processes.content import DEEP_TEAL, SILVER

SEQ_COLS = px.colors.sequential.Agsunset


def bg(plot_bg_colour=None, plot_paper_colour=None):
    plot_bg_colour = "rgba(0, 0, 0, 0)" if plot_bg_colour is None else plot_bg_colour
    plot_paper_colour = (
        "rgba(0, 0, 0, 0)" if plot_paper_colour is None else plot_paper_colour
    )

    def bg_helper(func):
        def wrapper(*args, **kwargs):
            fig = func(*args, **kwargs)
            fig.update_layout(
                {
                    "plot_bgcolor": plot_bg_colour,
                    "paper_bgcolor": plot_paper_colour,
                    "font_color": SILVER,
                }
            )
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        return wrapper

    return bg_helper


@bg()
def country_sunburst(chart_data):
    fig = px.sunburst(
        data_frame=chart_data,
        path=["Country", "Genre", "Artist"],
        values="Streams",
        color_discrete_sequence=SEQ_COLS,
    )
    return fig


@bg(plot_paper_colour=DEEP_TEAL)
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
        color_continuous_scale=SEQ_COLS,
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
    fig.update_layout(coloraxis_colorbar={"tickprefix": "10e"},)
    return fig


@bg()
def artist_trends(chart_data, log=False):
    # TODO: Capitalise "date" in axis label
    fig = px.line(
        data_frame=chart_data,
        x="date",
        y="Streams",
        color="Artist",
        # color_discrete_sequence=SEQ_COLS,
    )
    fig.update_xaxes(showgrid=False)

    if log:
        fig.update_layout(yaxis_type="log")

    return fig
