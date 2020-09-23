import csv
import datetime as dt
import itertools
import os
import pickle
from collections import Counter
from typing import Iterable

import pandas as pd
from tqdm import tqdm

from utils import apicall as api
from settings import (
    STREAM_DATA_DIR,
    SPOTIFY_ASSET_PATH,
    ARTIST_GENRE_PRIME_MAP,
    ARTIST_GENRE_MANY_MAP,
    GEOGRAPHY_DATA_PATH,
)


def load_country_info() -> pd.DataFrame:
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
        GEOGRAPHY_DATA_PATH,
        delimiter="\t",
        skiprows=49,
        usecols=keepcols,
        index_col="#ISO",
        keep_default_na=False,
    )
    # TODO: Specify dtypes here - shorter nums and categoricals
    df00.index.names = ["ISO2"]
    return df00


def build_spotify_asset(start_date=None):
    weekly_data = os.listdir(STREAM_DATA_DIR)
    most_recent = max([file[-14:-4] for file in weekly_data])

    if start_date is None:
        start_date = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(
            weeks=51
        )

    print("Start date:", start_date)

    spotify_weekly_paths = [
        os.path.join(STREAM_DATA_DIR, file)
        for file in weekly_data
        if file[-14:-4] >= start_date.strftime("%Y-%m-%d")
    ]

    def concatenate_country_csvs(csv_list: Iterable[str]) -> pd.DataFrame:
        expected_columns = 'Position,"Track Name",Artist,Streams,URL'
        target_columns = expected_columns.replace('"', "").split(",") + ["date", "ISO2"]

        def process_csv(file_path):
            date = file_path[-14:-4]
            country = os.path.split(file_path)[1][:2].upper()
            records = list()

            with open(file_path, "r", encoding="utf-8") as f:
                next(f)  # Skip the first row
                if expected_columns in f.readline():  # Check and skip the headers
                    lines = list(csv.reader(f))
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

    if os.path.isfile(ARTIST_GENRE_MANY_MAP):
        print(f"Loaded artist -> all genre map from: {ARTIST_GENRE_MANY_MAP}")
        with open(ARTIST_GENRE_MANY_MAP, "rb") as f:
            artist_to_genre_many = pickle.load(f, encoding="utf-8")
    else:
        print(f"No map found at {ARTIST_GENRE_MANY_MAP}")
        artist_to_genre_many = dict()
    if os.path.isfile(ARTIST_GENRE_PRIME_MAP):
        print(f"Loaded artist -> primary genre many map from: {ARTIST_GENRE_PRIME_MAP}")
        with open(ARTIST_GENRE_PRIME_MAP, "rb") as f:
            artist_to_genre_one = pickle.load(f, encoding="utf-8")
    else:
        print(f"No map found at {ARTIST_GENRE_PRIME_MAP}")
        artist_to_genre_one = dict()

    # Load raw data files.
    print("Concatenating files...")
    spotify_df_00 = concatenate_country_csvs(spotify_weekly_paths)
    spotify_df_01 = spotify_df_00.copy()
    spotify_df_01.loc[:, "Genre"] = spotify_df_01.loc[:, "Artist"].map(
        lambda x: artist_to_genre_one.get(x, None)
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
        artist_to_genre_many.update(new_artists_map)

        all_genres = list(
            filter(lambda x: isinstance(x, list), artist_to_genre_many.values())
        )
        genre_list = list(itertools.chain.from_iterable(all_genres))
        c = Counter
        artists_per_genre = c(genre_list)

        # Map each new artist to the most common genre they are associated with.
        artist_to_genre_one.update(
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
            lambda x: artist_to_genre_one.get(x, None)
        )

    with open(ARTIST_GENRE_MANY_MAP, "wb") as f:
        pickle.dump(artist_to_genre_many, f)

    with open(ARTIST_GENRE_PRIME_MAP, "wb") as f:
        pickle.dump(artist_to_genre_one, f)

    spotify_df_01.to_pickle(SPOTIFY_ASSET_PATH)
    print("Complete.")


def load_spotify_asset(mode="local"):
    if mode == "local":
        return pd.read_pickle(SPOTIFY_ASSET_PATH)
