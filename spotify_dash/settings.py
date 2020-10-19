import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

BASE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
RESOURCE = os.path.abspath(os.path.join(BASE_DIRECTORY, "resources"))

SPOTIFY_ASSET_PATH = pathlib.Path(RESOURCE, "processed/spotify_data.pkl.bz")
SPOTIFY_DATA_DIR = pathlib.Path(RESOURCE, "external/spotifycharts/weekly/")
ARTIST_GENRE_MANY_PATH = pathlib.Path(
    RESOURCE, "interim/artists/artist-to-genre-many.pkl"
)
ARTIST_GENRE_PRIME_PATH = pathlib.Path(
    RESOURCE, "interim/artists/artist-to-genre-one.pkl"
)
GEOGRAPHY_DATA_PATH = pathlib.Path(RESOURCE, "external/geography/countryInfo.txt")
