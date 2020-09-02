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
        html.H1("Global View"),
        dbc.Row(
            dbc.Col(
                md=12,
                # lg=6,
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
                            dbc.Jumbotron(
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
                    # lg=6,
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
                                            id="country-sunburst",  # COUNTRY SUNBURST CHART
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
                                        ddt.DataTable(  # COUNTRY TABLE
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
