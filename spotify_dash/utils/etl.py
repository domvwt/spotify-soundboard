import csv
import datetime as dt
import itertools
import pathlib
from collections import Counter
from typing import Iterable

import pandas as pd
from tqdm import tqdm

import spotify_dash.utils.io as iou
import spotify_dash.utils.apicall as api


# TODO: Replace os with pathlib
# TODO: Take artist -> genre maps as input and keep on s3


def load_country_info(geographic_data_path) -> pd.DataFrame:
    keepcols = [
        "#ISO",
        "ISO3",
        "ISO-Numeric",
        "fips",
        "Country",
        "Capital",
        "Population",
        "Continent",
    ]
    # Ignore the first 49 rows as these are not part of the tabular data.
    df00 = pd.read_csv(
        geographic_data_path,
        delimiter="\t",
        skiprows=49,
        usecols=keepcols,
        index_col="#ISO",
        keep_default_na=False,
    )
    # TODO: Specify dtypes here - shorter nums and categoricals
    df00.index.names = ["ISO2"]
    return df00


def build_spotify_assets(
    spotify_weekly_dir: pathlib.Path,
    artist_genre_many: dict,
    artist_genre_prime: dict,
    start_date=None,
):
    weekly_data = spotify_weekly_dir.iterdir()

    spotify_weekly_paths = [
        pathlib.Path(spotify_weekly_dir, file)
        for file in weekly_data
        if file.name[-14:-4] >= start_date.strftime("%Y-%m-%d")
    ]

    def concatenate_country_csvs(csv_list: Iterable[str]) -> pd.DataFrame:
        expected_columns = 'Position,"Track Name",Artist,Streams,URL'
        target_columns = expected_columns.replace('"', "").split(",") + ["date", "ISO2"]

        def process_csv(file_path: pathlib.Path):
            date = file_path.name[-14:-4]
            country = file_path.name[:2].upper()
            records = list()

            with file_path.open("r", encoding="utf-8") as f:
                next(f)  # Skip the first row
                if expected_columns in f.readline():  # Check and skip the headers
                    lines = list(csv.reader(f))[:100]  # Keep only the top 100
                    records += [x + [date, country] for x in lines]
                else:
                    print(f"Unexpected file format: {file_path}")

            return records

        data = [process_csv(csv_path) for csv_path in tqdm(csv_list)]
        data = list(itertools.chain.from_iterable(data))

        dtypes = {
            "Position": int,
            "Track Name": pd.CategoricalDtype(),
            "Artist": pd.CategoricalDtype(),
            "Streams": int,
            "URL": str,
            "date": str,
            "ISO2": pd.CategoricalDtype(),
        }

        df = pd.DataFrame(data, columns=target_columns).astype(dtypes)
        df.date = pd.to_datetime(df.date, format="%Y-%m-%d")

        return df

    # Load raw data files.
    print("Concatenating files...")
    spotify_df_00 = concatenate_country_csvs(spotify_weekly_paths)
    spotify_df_01 = spotify_df_00.copy()
    spotify_df_01.loc[:, "Genre"] = (
        spotify_df_01.loc[:, "Artist"]
        .map(lambda x: artist_genre_prime.get(x, None))
        .astype(pd.CategoricalDtype())
    )

    # Check for new artists.
    new_artist_tracks = (
        spotify_df_01.loc[
            ((spotify_df_01["Genre"].isna()) & (~spotify_df_01["Artist"].isna())), :
        ]
        .groupby("Artist")["URL"]
        .first()
        .dropna()
    )
    # Add new artists to the artist -> genre map.
    if new_artist_tracks.any():
        print("Cataloguing new artists...")
        new_artist_track_ids = new_artist_tracks.apply(
            lambda x: x.split("/")[-1]
        ).to_list()
        new_artists_map = api.get_genres_from_tracks(new_artist_track_ids)
        artist_genre_many.update(new_artists_map)

        all_genres = list(
            filter(lambda x: isinstance(x, list), artist_genre_many.values())
        )
        genre_list = list(itertools.chain.from_iterable(all_genres))
        c = Counter
        artists_per_genre = c(genre_list)

        # Map each new artist to the most common genre they are associated with.
        artist_genre_prime.update(
            {
                artist: (
                    sorted(genres, key=lambda x: -artists_per_genre[x])[0].title()
                    if isinstance(genres, list) and genres
                    else "Unknown"
                )
                for artist, genres in new_artists_map.items()
            }
        )

        # Map primary genre to new songs.
        spotify_df_01.loc[:, "Genre"] = spotify_df_01.loc[:, "Artist"].map(
            lambda x: artist_genre_prime.get(x, None)
        )

    return spotify_df_01, artist_genre_many, artist_genre_prime


def filter_one_year(df, date_col="date"):
    return df.loc[df[date_col] >= df[date_col].max() - dt.timedelta(weeks=51)]


def load_spotify_asset(spotify_asset_path):
    return iou.decompress_pickle(spotify_asset_path)
