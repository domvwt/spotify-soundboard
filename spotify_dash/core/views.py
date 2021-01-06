import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from spotify_dash.utils import etl


def world_view(spotify_asset_path, geographic_data_path) -> pd.DataFrame:
    # IMPORTANT: Pandas has issues performing groupby operations on DataFrames containing categorical data.
    # Categorical fields are explicitly converted to object type in the next step.

    dtypes = {
        "Position": "uint16",
        "Track Name": "object",
        "Artist": "object",
        "Streams": "uint32",
        "URL": "object",
        "date": "datetime64[ns]",
        "ISO2": "object",
        "Genre": "object",
    }

    spotify_df_00 = etl.load_spotify_asset(spotify_asset_path).astype(dtypes)
    spotify_df_01 = (
        spotify_df_00.groupby(["ISO2", "date", "Artist", "Genre"])["Streams"]
        .sum()
        .to_frame()
    )
    country_info_00 = etl.load_country_info(geographic_data_path)
    country_info_00.loc[:, "Continent"] = country_info_00.loc[:, "Continent"].map(
        {
            "AF": "Africa",
            "AS": "Asia",
            "NA": "North America",
            "OC": "Asia",
            "EU": "Europe",
            "SA": "South America",
        }
    )
    world_view_df = spotify_df_01.join(country_info_00, how="inner")

    # Drop incorrectly labelled Greenland streams...
    world_view_df = world_view_df[world_view_df["Country"] != "Greenland"]

    return world_view_df


def country_view(
    country_name, spotify_asset_path, geographic_data_path, world_view_df=None
):
    country_name = "United Kingdom" if country_name is None else country_name
    country_view_df = (
        world_view(spotify_asset_path, geographic_data_path)
        if world_view_df is None
        else world_view_df
    )

    # Get streams by Artist
    country_view_df = (
        country_view_df.groupby(["Country", "Artist", "Genre"])["Streams"]
        .sum()
        .reset_index()
    )

    # Filter for Country
    if country_name:
        country_view_df = country_view_df.loc[
            country_view_df.loc[:, "Country"] == country_name
        ].reset_index()[:100]

    # Sort records
    country_view_df = country_view_df.sort_values(by="Streams", ascending=False)

    # Add position
    country_view_df["Position"] = range(1, len(country_view_df) + 1)

    return country_view_df


def choropleth_view(world_view_df):
    top_artists = (
        world_view_df.copy()
        .groupby(["Country"], group_keys=False)
        .apply(lambda x: x.sort_values(by="Streams", ascending=False))
        .reset_index()
        .groupby(["Country"], group_keys=False)
        .first()
        .reset_index()
        .loc[:, ["Country", "Artist"]]
        .set_index("Country")
    )

    top_genres = (
        world_view_df.copy()
        .groupby(["Country", "Genre"], group_keys=False)[["Streams"]]
        .sum()
        .reset_index()
        .groupby(["Country"], group_keys=False)
        .apply(lambda x: x.sort_values(by="Streams", ascending=False))
        .reset_index()
        .groupby(["Country"], group_keys=False)
        .first()
        .reset_index()
        .loc[:, ["Country", "Genre"]]
        .set_index("Country")
    )

    total_streams = (
        world_view_df.copy()
        .groupby(["Country", "ISO3"])[["Streams"]]
        .sum()
        .reset_index()
        .set_index("Country")
    )

    result = pd.concat([total_streams, top_artists, top_genres], axis=1).reset_index()
    result["ISO3"] = result["ISO3"].str.upper()
    result = result.rename(columns={"Artist": "Top Artist", "Genre": "Top Genre"})

    return result


def artist_view(
    world_view_df, countries=None, artists=None, cumulative=False, rolling_avg=False
) -> pd.DataFrame:
    data = world_view_df.copy().reset_index()

    if countries:
        data = data.loc[data.loc[:, "Country"].isin(countries), :]

    # Get top 10 artists
    if artists is None:
        artists = (
            data.groupby("Artist", group_keys=False)["Streams"]
            .sum()
            .reset_index()
            .sort_values(by="Streams", ascending=False)
            .Artist.values[:10]
        )

    artist_view_df = (
        data.loc[data.loc[:, "Artist"].isin(artists), :]
        .groupby(["date", "Artist"])["Streams"]
        .sum()
        .reset_index()
    )

    if cumulative:
        artist_view_df = (
            artist_view_df.groupby(["date", "Artist"])
            .sum()
            .unstack()
            .expanding()
            .sum()
            .stack()
            .reset_index()
        )

    if rolling_avg:
        artist_view_df = (
            artist_view_df.groupby(["date", "Artist"])
            .sum()
            .unstack()
            .rolling(4)
            .mean()
            .stack()
            .reset_index()
        )

    return artist_view_df


def tsne_genre_view(
    world_view_df, principal_components=14, perplexity=5, learning_rate=10, dims3d=False
):
    genre_df = (
        world_view_df.groupby(["Country", "Continent", "ISO2", "Genre"])["Streams"]
        .sum()
        .unstack()
        .fillna(0)
    )
    genre_df = genre_df.divide(genre_df.sum(axis=1), axis=0)

    dims = 3 if dims3d else 2

    pca = PCA(n_components=principal_components)
    genre_pca = pca.fit_transform(genre_df)

    tsne = TSNE(
        n_components=dims,
        perplexity=perplexity,
        learning_rate=learning_rate,
        method="exact",
    )
    genre_tsne = tsne.fit_transform(genre_pca)
    genre_tsne_df = pd.DataFrame(genre_tsne, index=genre_df.index).reset_index()
    genre_tsne_df = genre_tsne_df.sort_values(by="Continent")

    return genre_tsne_df
