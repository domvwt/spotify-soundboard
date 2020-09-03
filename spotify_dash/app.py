import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_caching import Cache

import processes.charts as charts
import processes.content as cnt
import processes.views as views

# TODO: Tips: hover for info, scroll to zoom, drag to change view, click to drill down...
# TODO: TSNE Viz - 2d / 3d - Colour by continent - Space Exploration
# TODO: Artist Trends
# TODO: Decouple data pipeline from dashboard - move data to cloud storage

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.SOLAR], title="SpotifySoundboard"
)

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
                        "Github",
                        href="https://github.com/domvwt/spotify-soundboard/tree/master",
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
                *cnt.render_dashboard_status(cached_world_view()),
                html.Br(),
                *cnt.render_world_map(cached_world_view()),
                html.Br(),
                *cnt.render_country_profile(
                    cached_world_view(),
                    cached_country_view(country_name="United Kingdom"),
                ),
                html.Br(),
            ],
        ),
    ],
)


@app.callback(
    Output(component_id="world-choropleth", component_property="figure"),
    [Input(component_id="choropleth-input", component_property="value")],
)
def update_stream_atlas(input_value):
    return charts.world_choropleth(
        chart_data=views.choropleth_view(cached_world_view()), scope=input_value
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
