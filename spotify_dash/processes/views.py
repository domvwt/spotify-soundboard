import pandas as pd
import processes.etl as etl


def world_view() -> pd.DataFrame:
    spotify_df_00 = etl.load_spotify_asset()
    spotify_df_01 = (
        spotify_df_00.groupby(["ISO2", "date", "Artist", "Genre"])["Streams"]
        .sum()
        .to_frame()
    )
    country_info_00 = etl.load_country_info()
    world_view_df = spotify_df_01.join(country_info_00, how="inner")
    world_view_df.loc[:, "Streams_per_capita"] = (
        world_view_df.loc[:, "Streams"] / world_view_df.loc[:, "Population"]
    )

    # Drop Greenland streams since they are actually Global!
    # TODO: Fix this at source
    world_view_df = world_view_df[world_view_df["Country"] != "Greenland"]

    return world_view_df


def country_view(country_name, world_view_df=None):
    country_name = "United Kingdom" if country_name is None else country_name
    country_view_df = world_view() if world_view_df is None else world_view_df

    # Get streams by Artist
    country_view_df = (
        country_view_df.groupby(["Country", "Artist", "Genre"])["Streams"]
        .sum()
        .reset_index()
    )

    # Filter for Country
    country_view_df = country_view_df.loc[
        country_view_df.loc[:, "Country"] == country_name
    ].reset_index()[:100]

    # Sort records
    country_view_df = country_view_df.sort_values(by="Streams", ascending=False)

    # Add position
    country_view_df["Position"] = range(1, len(country_view_df) + 1)

    return country_view_df
