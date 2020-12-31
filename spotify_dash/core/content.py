import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as ddt
import numpy as np
from dash_table.Format import Format
import datetime as dt

from core import charts as charts, views as views

SILVER = "rgb(131, 148, 150)"
SLATE = "rgb(30, 67, 74)"
DARK_GREY = "rgb(8, 8, 8)"
DEEP_TEAL = "rgb(7, 54, 66)"


def render_dashboard_status(world_view):
    world_view = world_view.copy().reset_index()

    streams = world_view.loc[:, "Streams"].sum()
    artists = world_view.loc[:, "Artist"].nunique()
    genres = world_view.loc[:, "Genre"].nunique()
    countries = world_view.loc[:, "Country"].nunique()
    weeks = world_view.loc[:, "date"].nunique()
    date_start = world_view.loc[:, "date"].min().strftime("%Y-%m-%d")
    date_end = (world_view.loc[:, "date"].max() + dt.timedelta(6)).strftime("%Y-%m-%d")

    dash_stats = [
        {"name": "Streams", "value": f"{streams:,d}"},
        {"name": "Artists", "value": f"{artists:,d}"},
        {"name": "Genres", "value": f"{genres:,d}"},
        {"name": "Countries", "value": f"{countries:,d}"},
        {"name": "Period", "value": f"{date_start} to {date_end}"},
    ]

    def make_stats_items(header, body):
        return dcc.Markdown(f"**{header}**: {body}")

    stats_object = [make_stats_items(d["name"], d["value"]) for d in dash_stats]

    return [
        dbc.Row(
            justify="around",
            children=[
                dbc.Col(
                    md=12,
                    lg=8,
                    style={"padding-left": 22, "margin-bottom": 15,},
                    children=html.H1("Spotify Soundboard", className="display-4"),
                ),
                dbc.Col(md=12, lg=2,),
            ],
        ),
        dbc.Row(
            justify="around",
            children=[
                dbc.Col(
                    md=12,
                    lg=5,
                    align="start",
                    style={"margin-bottom": 15,},
                    children=[
                        html.Div(
                            style={
                                "padding-left": 13,
                                "margin-bottom": 15,
                                "font-size": "1.1rem",
                            },
                            children=[
                                html.P(
                                    "An interactive visualisation of music streaming around the world."
                                ),
                                html.P(),
                                html.Span(
                                    children=[
                                        dcc.Markdown(
                                            children=[
                                                "Updated weekly with data for the **top 100** streamed "
                                                f"tracks in each country over the last **{weeks}** weeks."
                                            ]
                                        ),
                                        html.Span(
                                            children=[
                                                "See the code on ",
                                                html.A(
                                                    "GitHub",
                                                    href="https://github.com/domvwt/spotify-soundboard/tree/master",
                                                    style={"color": "thistle"},
                                                ),
                                            ]
                                        ),
                                        html.Span(
                                            children=[
                                                " or say hello at ",
                                                html.A(
                                                    "domvwt.",
                                                    href="https://domvwt.github.io",
                                                    style={"color": "thistle"},
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
                dbc.Col(
                    md=12,
                    lg=5,
                    align="center",
                    children=html.Div(
                        style={"padding-left": 13, "font-size": "1.1rem"},
                        children=stats_object,
                    ),
                ),
            ],
        ),
    ]


def render_world_map(choropleth_view):
    scope_options = [
        {"label": "World", "value": "world"},
        {"label": "Europe", "value": "europe"},
        {"label": "North America", "value": "north america"},
        {"label": "South America", "value": "south america"},
        {"label": "Asia", "value": "asia"},
        {"label": "Africa", "value": "africa"},
    ]
    return [
        html.H1("World View"),
        dbc.Row(
            children=dbc.Col(
                width=12,
                children=html.Div(
                    children=[
                        html.Div(
                            children=[
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            md={"size": 12, "order": "first"},
                                            lg={"size": 9, "order": "last"},
                                            xl={"size": 10, "order": "last"},
                                            children=dcc.Graph(
                                                id="world-choropleth",
                                                figure=charts.world_choropleth(
                                                    choropleth_view,
                                                ),
                                                config={"displayModeBar": False},
                                            ),
                                        ),
                                        dbc.Col(
                                            md={"size": 12, "order": "last"},
                                            lg={"size": 3, "order": "first"},
                                            xl={"size": 2, "order": "first"},
                                            children=html.Div(
                                                children=[
                                                    dbc.CardBody(
                                                        style={"font-size": 14},
                                                        children=dbc.FormGroup(
                                                            children=[
                                                                dbc.Label("Scope"),
                                                                dbc.RadioItems(
                                                                    id="choropleth-input",
                                                                    options=scope_options,
                                                                    value="world",
                                                                ),
                                                            ]
                                                        ),
                                                    )
                                                ],
                                            ),
                                        ),
                                    ],
                                )
                            ]
                        ),
                    ]
                ),
            ),
        ),
    ]


def render_country_profile(world_view, country_view):
    country_table_col_dict = [
        {"name": column, "id": column} for column in ["Position", "Artist", "Genre"]
    ] + [
        {
            "name": "Streams",
            "id": "Streams",
            "type": "numeric",
            "format": Format(group=","),
        }
    ]

    return [
        html.H1("Country Profile", style={"margin-bottom": 20}),
        dbc.Row(
            [
                dbc.Col(
                    md={"size": 12, "order": "last"},
                    lg={"size": 6, "order": "first"},
                    children=[
                        html.Div(
                            style={
                                "padding-left": 20,
                                "padding-right": 30,
                                "margin-top": 30,
                            },
                            children=[
                                dcc.Dropdown(
                                    id="country-input",
                                    style={"padding-left": 0},
                                    options=[
                                        {"label": country, "value": country}
                                        for country in np.sort(
                                            world_view["Country"].unique()
                                        )
                                    ],
                                    placeholder="Select a country...",
                                ),
                                html.Br(),
                                ddt.DataTable(
                                    id="country-table",
                                    style_table={
                                        "padding-left": 17,
                                        "padding-right": 17,
                                    },
                                    columns=country_table_col_dict,
                                    data=country_view.to_dict("records"),
                                    style_header={
                                        "backgroundColor": DEEP_TEAL,
                                        "color": SILVER,
                                    },
                                    style_cell={
                                        "textAlign": "left",
                                        "backgroundColor": DEEP_TEAL,
                                        "color": SILVER,
                                        "fontSize": 14,
                                        "font-family": "Helvetica",
                                    },
                                    style_as_list_view=True,
                                    sort_action="native",
                                    page_action="native",
                                    page_current=0,
                                    page_size=10,
                                ),
                            ],
                        )
                    ],
                ),
                dbc.Col(
                    md={"size": 12, "order": "first"},
                    lg={"size": 6, "order": "last"},
                    children=[
                        dcc.Graph(
                            id="country-sunburst",
                            figure=charts.country_sunburst(country_view),
                            config={"displayModeBar": False},
                        ),
                    ],
                ),
            ]
        ),
    ]


def render_artists_trends(artist_view, world_view):
    artist_options = [
        {"label": artist, "value": artist}
        for artist in (
            world_view.groupby("Artist", group_keys=False)["Streams"]
            .sum()
            .reset_index()
            .sort_values(by="Streams", ascending=False)
            .Artist.unique()
        )
    ]

    return [
        html.H1("Artist Trends"),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(
                    width=6,
                    md=3,
                    children=[
                        dbc.FormGroup(
                            style={"padding-left": 35},
                            children=[
                                dbc.RadioItems(
                                    id="artist-trends-date-options",
                                    options=[
                                        {"label": "Snapshot", "value": "snapshot"},
                                        {"label": "Cumulative", "value": "cumulative"},
                                    ],
                                    value="snapshot",
                                ),
                            ],
                        )
                    ],
                ),
                dbc.Col(
                    width=6,
                    md=3,
                    children=dbc.FormGroup(
                        style={"padding-left": 0},
                        children=[
                            dbc.Checklist(
                                id="artist-trends-axis-options",
                                options=[
                                    {"label": "Log y Axis", "value": "log-y"},
                                    {
                                        "label": "Rolling 4wk Avg.",
                                        "value": "rolling-avg",
                                    },
                                ],
                                value=[],
                                switch=True,
                            ),
                        ],
                    ),
                ),
            ]
        ),
        dcc.Graph(
            id="artist-trends",
            style={"margin-bottom": 15},
            figure=charts.artist_trends(artist_view),
            config={"displayModeBar": False},
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    width=12,
                    children=dcc.Dropdown(
                        id="artist-trends-selection",
                        style={"padding-left": 0},
                        options=artist_options,
                        value=artist_view.groupby("Artist")["Streams"]
                        .sum()
                        .sort_values()[:10]
                        .index,
                        multi=True,
                    ),
                ),
            ]
        ),
    ]


def render_genre_space(world_view):
    return [
        html.H1("Genre Affinity Clusters"),
        dbc.Row(
            children=[
                dbc.Col(
                    width=12,
                    lg=3,
                    style={"padding-left": 20},
                    children=[
                        dbc.FormGroup(
                            children=[
                                dbc.Label("3D"),
                                dbc.Checklist(
                                    style={"padding-left": 20, "padding-bottom": 5},
                                    id="tsne-dimension",
                                    options=[dict(label="", value=True)],
                                    value=False,
                                    switch=True,
                                ),
                                dbc.Label("Principal Components"),
                                dcc.Slider(
                                    id="tsne-pca",
                                    min=10,
                                    max=30,
                                    step=1,
                                    value=14,
                                    marks={x: str(x) for x in range(10, 31, 4)},
                                ),
                                dbc.Label("Perplexity"),
                                dcc.Slider(
                                    id="tsne-perplexity",
                                    min=2,
                                    max=20,
                                    step=1,
                                    value=5,
                                    marks={x: str(x) for x in range(2, 21, 3)},
                                ),
                                dbc.Label("Regenerate Clusters"),
                                html.Br(),
                                dbc.Button(
                                    id="tsne-regenerate",
                                    outline=True,
                                    color="light",
                                    size="sm",
                                    style={"margin-left": 20, "margin-top": 9},
                                    children="Regenerate",
                                ),
                            ]
                        ),
                    ],
                ),
                dbc.Col(
                    width=12,
                    lg=9,
                    children=dcc.Graph(
                        id="country-clustering",
                        style={"margin-top": 15},
                        figure=charts.country_tsne_clustering(
                            chart_data=views.tsne_genre_view(world_view),
                        ),
                        config={"displayModeBar": False},
                    ),
                ),
            ],
        ),
    ]


def render_genre_tree(world_view):
    return [
        html.Div(
            style={"margin-bottom": 60},
            children=[
                html.H1("Genre Map"),
                dcc.Graph(
                    style={"height": "80vh"},
                    id="genre-tree",
                    figure=charts.genre_tree(world_view),
                    config={"displayModeBar": False},
                ),
            ],
        )
    ]
