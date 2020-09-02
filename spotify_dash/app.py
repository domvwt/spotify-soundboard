import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as ddt
import numpy as np
from dash.dependencies import Input, Output
from dash_table.Format import Format
from flask_caching import Cache

import processes.charts as charts
import processes.views as views

# TODO: Board status - coverage stats: date range, countries, artists, streams; top global genre, artist; last updated
# TODO: Tips: hover for info, scroll to zoom, drag to change view, click to drill down...
# TODO: Global settings at top of page - date range
# TODO: Refactor content to functions and modules for each view
# TODO: TSNE Viz - 2d / 3d - Colour by continent

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

SILVER = "rgb(131, 148, 150)"
SLATE = "rgb(30, 67, 74)"
DARK_GREY = "rgb(8, 8, 8)"

cache = Cache(
    app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache-directory-app"}
)

server = app.server

TIMEOUT = 1800  # In seconds; 1800s = 30 minutes


@cache.memoize(timeout=TIMEOUT)
def cached_world_view():
    return views.world_view()


@cache.memoize(timeout=TIMEOUT)
def cached_country_view(country_name):
    return views.country_view(country_name, cached_world_view())


def render_world_map():
    return [
        html.H1("Global View"),
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
                                        views.choropleth_view(cached_world_view())
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


def render_country_profile():
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
                    lg=6,
                    style={"padding-top": 10},
                    children=dcc.Dropdown(  # DROPDOWN MENU
                        id="country-input",
                        options=[
                            {"label": country, "value": country}
                            for country in np.sort(
                                cached_world_view()["Country"].unique()
                            )
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
                                    html.H3("Stream Breakdown", className="card-title",)
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(
                                            id="country-sunburst",  # COUNTRY SUNBURST CHART
                                            figure=charts.country_sunburst(
                                                cached_country_view(
                                                    country_name="United Kingdom"
                                                )
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
                                            data=cached_country_view(
                                                country_name="United Kingdom"
                                            ).to_dict("records"),
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


app.layout = html.Div(
    style={"padding-bottom": "2rem",},
    children=[
        dbc.NavbarSimple(
            brand="SpotifySoundboard",
            color="dark",
            dark=True,
            brand_style={"font-weight": "bold", "color": "white"},
            children=dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Menu",
                children=[
                    dbc.DropdownMenuItem(
                        "LinkedIn", href="https://www.linkedin.com/in/dominic-thorn/"
                    ),
                    dbc.DropdownMenuItem(
                        "Github", href="https://github.com/domvwt/spotify-soundboard"
                    ),
                ],
            ),
        ),
        # MAIN APP CONTAINER
        dbc.Container(
            style={
                "padding-left": "auto",
                "margin-left": "auto",
                "padding-right": "auto",
                "margin-right": "auto",
            },
            children=[
                html.Br(),
                *render_world_map(),
                html.Br(),
                *render_country_profile(),
                html.Br(),
            ],
        ),
    ],
)


@app.callback(
    Output(component_id="country-sunburst", component_property="figure"),
    [Input(component_id="country-input", component_property="value")],
)
def update_country_sunburst(input_value):
    return charts.country_sunburst(chart_data=cached_country_view(input_value))


@app.callback(
    Output(component_id="country-table", component_property="data"),
    [Input(component_id="country-input", component_property="value")],
)
def update_country_table(input_value):
    return cached_country_view(input_value).to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
