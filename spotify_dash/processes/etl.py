import datetime
import itertools
import os
import pickle
from collections import Counter
from typing import Iterable

import pandas as pd
from tqdm import tqdm

from processes import apicall as api
from settings import (
    STREAM_DATA_DIR,
    SPOTIFY_ASSET_PATH,
    ARTIST_GENRE_ONE_MAP,
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
    df00.index.names = ["ISO2"]
    return df00


def build_spotify_asset(start_date=None, top_tracks=100):
    if start_date is None:
        start_date = datetime.datetime.now() - datetime.timedelta(weeks=53)

    weekly_data = os.listdir(STREAM_DATA_DIR)
    spotify_weekly_paths = [
        os.path.join(STREAM_DATA_DIR, file)
        for file in weekly_data
        if file[-14:-4] >= start_date.strftime("%Y-%m-%d")
    ]

    def concatenate_country_csvs(csv_list: Iterable[str]) -> pd.DataFrame:
        df_dict = {
            (os.path.split(file)[1][:2].upper(), file[-14:-4]): read_try_csv(file)[
                :top_tracks
            ]
            for file in tqdm(csv_list)
        }
        return pd.concat(
            df_dict, axis=0, keys=df_dict.keys(), names=("ISO2", "date", "orig")
        ).droplevel(level="orig")

    if os.path.isfile(ARTIST_GENRE_MANY_MAP):
        print(f"Loaded artist -> all genre map from: {ARTIST_GENRE_MANY_MAP}")
        with open(ARTIST_GENRE_MANY_MAP, "rb") as f:
            artist_to_genre_many = pickle.load(f, encoding="utf-8")
    else:
        print(f"No map found at {ARTIST_GENRE_MANY_MAP}")
        artist_to_genre_many = dict()
    if os.path.isfile(ARTIST_GENRE_ONE_MAP):
        print(f"Loaded artist -> primary genre many map from: {ARTIST_GENRE_ONE_MAP}")
        with open(ARTIST_GENRE_ONE_MAP, "rb") as f:
            artist_to_genre_one = pickle.load(f, encoding="utf-8")
    else:
        print(f"No map found at {ARTIST_GENRE_ONE_MAP}")
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
        spotify_df_01.loc[(spotify_df_01["Genre"].isna()) & (spotify_df_01["Artist"])]
        .groupby("Artist")["URL"]
        .first()
    )
    # Add new artists to the artist -> genre map.
    if not new_artist_tracks.empty:
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

    with open(ARTIST_GENRE_ONE_MAP, "wb") as f:
        pickle.dump(artist_to_genre_one, f)

    spotify_df_01.to_pickle(SPOTIFY_ASSET_PATH)


def load_spotify_asset(mode="local"):
    if mode == "local":
        return pd.read_pickle(SPOTIFY_ASSET_PATH)


def read_try_csv(path):
    try:
        result = pd.read_csv(path, skiprows=1, encoding="utf-8")
    except pd.errors.ParserError:
        print(Exception(f"File is not a csv: {path}"))
        result = pd.DataFrame()
    return result
