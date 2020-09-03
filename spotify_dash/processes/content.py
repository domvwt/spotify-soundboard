import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as ddt
import numpy as np
from dash_table.Format import Format

from processes import charts as charts, views as views

SILVER = "rgb(131, 148, 150)"
SLATE = "rgb(30, 67, 74)"
DARK_GREY = "rgb(8, 8, 8)"
DEEP_TEAL = "rgb(7, 54, 66)"


# TODO: Sparklines
# TODO: Daterange in header
# TODO: Top artists and top genres alongside the stream atlas


def render_dashboard_status(world_view):
    world_view = world_view.copy().reset_index()

    streams = world_view.loc[:, "Streams"].sum()
    artists = world_view.loc[:, "Artist"].nunique()
    genres = world_view.loc[:, "Genre"].nunique()
    countries = world_view.loc[:, "Country"].nunique()

    dash_stats = [
        {"name": "Streams", "value": f"{streams:,d}"},
        {"name": "Artists", "value": f"{artists:,d}"},
        {"name": "Genres", "value": f"{genres:,d}"},
        {"name": "Countries", "value": f"{countries:,d}"},
    ]

    def make_stats_items(header, body):
        return html.Div(
            children=[
                html.H4(header, style={"padding-left": 5}),
                html.H5(body, style={"margin-bottom": 20, "padding-left": 5}),
            ]
        )

    stats_object = [make_stats_items(d["name"], d["value"]) for d in dash_stats]

    return [
        dbc.Row(
            children=[
                dbc.Col(
                    md=12,
                    lg=7,
                    style={"margin-bottom": 15},
                    children=html.Div(children=[html.H1("Spotify Soundboard"),]),
                ),
                dbc.Col(
                    md=12,
                    lg=5,
                    align="end",
                    # style={"padding-right": 0,},
                    children=html.Div(
                        style={"padding-top": 50}, children=[html.Br(), *stats_object]
                    ),
                ),
            ]
        )
    ]


def render_world_map(choropleth_view):
    scope_options = [
        {"label": "Europe", "value": "europe"},
        {"label": "North America", "value": "north america"},
        {"label": "South America", "value": "south america"},
        {"label": "Asia", "value": "asia"},
        {"label": "Africa", "value": "africa"},
        {"label": "World", "value": "world"},
    ]
    return [
        html.H1("World View"),
        dbc.Row(
            dbc.Col(
                md=12,
                style={"padding-top": 10},
                children=dcc.Dropdown(
                    id="choropleth-input",
                    options=scope_options,
                    placeholder="Select a region...",
                ),
            )
        ),
        html.Br(),
        dbc.Row(
            children=dbc.Col(
                width=12,
                children=dbc.Card(
                    children=[
                        dbc.CardHeader(html.H3("Stream Atlas", className="card-title")),
                        dbc.CardBody(
                            html.Div(
                                children=dcc.Graph(
                                    id="world-choropleth",
                                    figure=charts.world_choropleth(
                                        views.choropleth_view(choropleth_view),
                                        scope=None,
                                    ),
                                    config={"displayModeBar": False},
                                )
                            )
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
        html.Br(),
        dbc.Row(dbc.Col(html.H1("Country Profile"))),
        dbc.Row(
            children=[
                dbc.Col(
                    md=12,
                    style={"padding-top": 10},
                    children=dcc.Dropdown(
                        id="country-input",
                        options=[
                            {"label": country, "value": country}
                            for country in np.sort(world_view["Country"].unique())
                        ],
                        placeholder="Select a country...",
                    ),
                ),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    md=12,
                    lg=6,
                    children=[
                        dbc.Card(
                            style={"margin-bottom": 15},
                            children=[
                                dbc.CardHeader(
                                    html.H3("Stream Breakdown", className="card-title")
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(
                                            id="country-sunburst",
                                            figure=charts.country_sunburst(
                                                country_view
                                            ),
                                            config={"displayModeBar": False},
                                        )
                                    ]
                                ),
                            ],
                        )
                    ],
                ),
                dbc.Col(
                    md=12,
                    lg=6,
                    children=[
                        dbc.Card(
                            style={"margin-bottom": 15},
                            children=[
                                dbc.CardHeader(
                                    html.H3("Top Artists", className="card-title")
                                ),
                                dbc.CardBody(
                                    style={"padding-left": 40, "padding-right": 40,},
                                    children=[
                                        html.Br(),
                                        ddt.DataTable(
                                            id="country-table",
                                            columns=country_table_col_dict,
                                            data=country_view.to_dict("records"),
                                            style_header={
                                                "backgroundColor": SLATE,
                                                "color": SILVER,
                                            },
                                            style_cell={
                                                "textAlign": "left",
                                                "backgroundColor": SILVER,
                                                "color": DARK_GREY,
                                            },
                                            style_as_list_view=True,
                                            sort_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=10,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ]
        ),
    ]
