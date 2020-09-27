import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.content import SILVER

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
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            return fig

        return wrapper

    return bg_helper


@bg()
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
    fig.update_layout(dict(coloraxis_colorbar=dict(tickprefix="10e")))

    return fig


@bg()
def country_sunburst(chart_data):
    fig = px.sunburst(
        data_frame=chart_data,
        path=["Country", "Genre", "Artist"],
        values="Streams",
        color_discrete_sequence=SEQ_COLS,
    )
    return fig


@bg()
def artist_trends(chart_data, log=False):
    if not chart_data.empty:
        fig = px.line(
            data_frame=chart_data,
            x="date",
            y="Streams",
            labels={"date": "Date"},
            color="Artist",
            # color_discrete_sequence=SEQ_COLS,
        )
    else:
        fig = go.Figure()

    fig.update_xaxes(visible=True, showgrid=False)
    fig.update_yaxes(
        visible=True,
        showgrid=True,
        gridwidth=1,
        gridcolor=SILVER,
        zerolinewidth=1,
        zerolinecolor=SILVER,
    )

    if log:
        fig.update_layout(yaxis_type="log")

    return fig


@bg()
def country_tsne_clustering(chart_data, plot3d=False):
    if plot3d:
        fig = px.scatter_3d(
            data_frame=chart_data,
            x=0,
            y=1,
            z=2,
            color="Continent",
            hover_name="Country",
            color_discrete_sequence=SEQ_COLS,
        )
        fig.update_layout(scene_aspectmode="cube")
        fig.update_layout(
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                xaxis=dict(
                    gridcolor=SILVER, showbackground=False, zerolinecolor=SILVER,
                ),
                yaxis=dict(
                    gridcolor=SILVER, showbackground=False, zerolinecolor=SILVER
                ),
                zaxis=dict(
                    gridcolor=SILVER, showbackground=False, zerolinecolor=SILVER,
                ),
            ),
        )
    else:
        fig = px.scatter(
            data_frame=chart_data,
            x=0,
            y=1,
            color="Continent",
            hover_name="Country",
            color_discrete_sequence=SEQ_COLS,
        )
        fig.update_xaxes(
            visible=True,
            showgrid=False,
            zerolinewidth=1,
            zerolinecolor=SILVER,
            title_text="X",
        )
        fig.update_yaxes(
            visible=True,
            showgrid=False,
            zerolinewidth=1,
            zerolinecolor=SILVER,
            title_text="Y",
        )
        fig.update_layout(dict(yaxis=dict(scaleanchor="x", scaleratio=1)))

    return fig


@bg()
def genre_tree(chart_data):
    chart_data = chart_data.groupby(["Artist", "Genre"]).sum()
    chart_data = chart_data.loc[chart_data.Streams >= 1e8, :]
    chart_data = chart_data.reset_index()
    fig = px.treemap(
        data_frame=chart_data,
        path=["Genre", "Artist"],
        values="Streams",
        color_discrete_sequence=SEQ_COLS,
    )
    return fig
