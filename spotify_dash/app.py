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


country_table_col_dict = [
    {"name": column, "id": column} for column in ["Position", "Artist", "Genre"]
] + [
    {"name": "Streams", "id": "Streams", "type": "numeric", "format": Format(group=",")}
]

app.layout = html.Div(
    style={"padding-bottom": "2rem"},
    children=[
        dbc.NavbarSimple(
            brand="clefbeam",
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
            children=[
                dbc.Row(
                    children=[  # ROW 1
                        dbc.Col([html.Br(), html.H1("Spotify Soundboard")]),
                    ],
                ),
                dbc.Row(
                    style={"mb": "10"},
                    children=[
                        dbc.Col(
                            md=12,
                            lg=6,
                            children=dcc.Dropdown(  # DROPDOWN MENU
                                id="country-input",
                                options=[
                                    {"label": country, "value": country}
                                    for country in np.sort(
                                        cached_world_view()["Country"].unique()
                                    )
                                ],
                                placeholder="Select a country...",
                            )
                        ),
                    ],
                ),
                dbc.Row(html.Br()),
                dbc.Row(
                    [
                        dbc.Col(
                            md=12,
                            lg=6,
                            children=[
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H3(
                                                "Country Profile",
                                                className="card-title",
                                            )
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
                                    ]
                                )
                            ]
                        ),
                        dbc.Col(
                            md=12,
                            lg=6,
                            children=[
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H3(
                                                "Top Artists", className="card-title"
                                            )
                                        ),
                                        dbc.CardBody(
                                            style={
                                                "padding-left": 40,
                                                "padding-right": 40,
                                            },
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
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
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
