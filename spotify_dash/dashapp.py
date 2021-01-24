import sys
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_caching import Cache

from spotify_dash.core import charts
import spotify_dash.core.content as cnt
import spotify_dash.core.views as views
import spotify_dash.jobs.download_data as dld
import spotify_dash.settings as sts


print("Starting Dashboard application.")

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.SOLAR], title="SpotifySoundboard"
)

cache = Cache(
    app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache-directory-app"}
)

server = app.server

TIMEOUT = 1800  # In seconds; 1800s = 30 minutes

dld.download_spotify_asset()


@cache.memoize(timeout=TIMEOUT)
def cached_world_view():
    return views.world_view(sts.SPOTIFY_ASSET_PATH, sts.GEOGRAPHY_DATA_PATH)


@cache.memoize(timeout=TIMEOUT)
def cached_country_view(country_name):
    return views.country_view(
        country_name,
        sts.SPOTIFY_ASSET_PATH,
        sts.GEOGRAPHY_DATA_PATH,
        world_view_df=cached_world_view(),
    )


app.layout = html.Div(
    children=[
        # MAIN APP LAYOUT
        dbc.Container(
            style={
                "padding-left": "5%",
                "margin-left": "auto",
                "padding-right": "5%",
                "margin-right": "auto",
            },
            fluid=True,
            children=[
                html.Br(),
                html.Br(),
                dbc.Jumbotron(
                    style={
                        "background": "linear-gradient("
                        "to right top, "
                        "rgb(253, 159, 108), "
                        "rgb(182, 54, 121) 30%, "
                        "rgb(59, 15, 111)"
                        ")",
                        "color": "rgb(240, 240, 240)",
                    },
                    children=[*cnt.render_dashboard_status(cached_world_view())],
                ),
                html.Br(),
                dbc.Jumbotron(
                    style={"padding-left": 50, "padding-right": 50},
                    children=[
                        *cnt.render_world_map(
                            views.choropleth_view(cached_world_view())
                        )
                    ],
                ),
                html.Br(),
                dbc.Jumbotron(
                    style={"padding-left": 50, "padding-right": 50},
                    children=[
                        *cnt.render_country_profile(
                            cached_world_view(),
                            cached_country_view(country_name="United Kingdom"),
                        )
                    ],
                ),
                html.Br(),
                dbc.Jumbotron(
                    style={"padding-left": 50, "padding-right": 50},
                    children=[
                        *cnt.render_artists_trends(
                            views.artist_view(cached_world_view()), cached_world_view()
                        )
                    ],
                ),
                html.Br(),
                dbc.Jumbotron(
                    style={"padding-left": 50, "padding-right": 50},
                    children=[*cnt.render_genre_space(cached_world_view())],
                ),
                html.Br(),
                html.Div(
                    style={"padding-left": 50, "padding-right": 50},
                    children=[*cnt.render_genre_tree(cached_world_view(),)],
                ),
            ],
        ),
        html.Div(
            style={"padding-top": 20, "padding-bottom": 15, "background": "#073642"},
            children=[
                dbc.Row(
                    justify="start",
                    no_gutters=True,
                    children=[
                        dbc.Col(
                            width={"size": 1, "offset": 1},
                            children=[
                                html.A(
                                    "domvwt",
                                    className="lead",
                                    href="https://domvwt.github.io",
                                    style={"color": cnt.SILVER},
                                )
                            ],
                        ),
                    ],
                )
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


@app.callback(
    Output(component_id="artist-trends", component_property="figure"),
    [
        Input(component_id="artist-trends-date-options", component_property="value"),
        Input(component_id="artist-trends-axis-options", component_property="value"),
        Input(component_id="artist-trends-selection", component_property="value"),
    ],
)
def update_artist_trends(date_option, axis_option, artists):
    log = True if "log-y" in axis_option else False
    rolling = True if "rolling-avg" in axis_option else False

    cumulative = True if "cumulative" in date_option else False

    return charts.artist_trends(
        chart_data=views.artist_view(
            cached_world_view(),
            cumulative=cumulative,
            rolling_avg=rolling,
            artists=artists,
        ),
        log=log,
    )


# noinspection PyUnusedLocal
@app.callback(
    Output(component_id="country-clustering", component_property="figure"),
    [
        Input(component_id="tsne-dimension", component_property="value"),
        Input(component_id="tsne-pca", component_property="value"),
        Input(component_id="tsne-perplexity", component_property="value"),
        Input(component_id="tsne-regenerate", component_property="n_clicks"),
    ],
)
def update_country_clustering(tsne_3d, tsne_pca, tsne_perplexity, regen):
    return charts.country_tsne_clustering(
        chart_data=views.tsne_genre_view(
            world_view_df=cached_world_view(),
            principal_components=tsne_pca,
            dims3d=tsne_3d,
            perplexity=tsne_perplexity,
        ),
        plot3d=tsne_3d,
    )


if __name__ == "__main__":
    debug = True if "--debug" in sys.argv else False
    app.run_server(debug=debug)
