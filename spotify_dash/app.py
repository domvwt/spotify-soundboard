import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask_caching import Cache

import processes.charts as charts
import processes.content as cnt
import processes.views as views

# TODO: Tips: hover for info, scroll to zoom, drag to change view, click to drill down...
# TODO: Decouple data pipeline from dashboard - move data to cloud storage
# TODO: New style with colour gradient:
#  style={'background': f'linear-gradient({DEEP_TEAL}, {DEEP_TEAL} 20%, {DARK_GREY})'},
# TODO: Take everything OUT of card containers
# TODO: Genre explorer in tree map - between country profile and artist trends

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
def cached_country_view(country_name="United Kingdom"):
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
        # MAIN APP LAYOUT
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
                *cnt.render_artists_trends(views.artist_view(cached_world_view())),
            ],
        ),
        html.Br(),
        dbc.Row(
            justify="center",
            children=dbc.Col(width=10, *cnt.render_genre_space(cached_world_view()),),
        ),
        html.Br(),
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
    ],
)
def update_artist_trends(date_option, axis_option):
    log = True if "log-y" in axis_option else False
    rolling = True if "rolling-avg" in axis_option else False

    cumulative = True if "cumulative" in date_option else False

    return charts.artist_trends(
        chart_data=views.artist_view(
            cached_world_view(), cumulative=cumulative, rolling_avg=rolling
        ),
        log=log,
    )


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
    app.run_server(debug=True)
