import os
from typing import List

import requests
from tqdm import tqdm

import spotify_dash.settings as sts
sts.load_dotenv()

BASE_URL = "https://api.spotify.com/v1/"
TRACKS_ENDPOINT = BASE_URL + "tracks"
ARTIST_ENDPOINT = BASE_URL + "artists"

AUTH_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]


def get_spotify_api_token():
    # POST
    auth_response = requests.post(
        AUTH_URL,
        {
            "grant_type": "client_credentials",
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        },
    )

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


def get_artists_from_tracks(track_ids: List[str], retries=3):
    endpoint = TRACKS_ENDPOINT
    headers = get_spotify_api_token()
    results_dict = {}

    for r_json in api_get(endpoint, headers, track_ids, retries):
        results_dict.update(
            {
                artist["name"]: artist["id"]
                for track in r_json["tracks"]
                for artist in track["artists"]
            }
        )

    return results_dict


def get_genres_from_artists(artist_ids: List[str], retries=3):
    endpoint = ARTIST_ENDPOINT
    headers = get_spotify_api_token()
    results_dict = {}

    for r_json in api_get(endpoint, headers, artist_ids, retries):
        results_dict.update(
            {item["name"]: item["genres"] for item in r_json["artists"]}
        )

    return results_dict


def api_get(endpoint, headers, ids, retries):
    id_chunks = list(divide_chunks(ids, 50))

    for chunk in tqdm(id_chunks):
        params = {"ids": ",".join(chunk)}
        r_json = None

        attempts = 0
        while attempts < retries:
            r_raw = requests.get(endpoint, headers=headers, params=params)

            if r_raw.ok:
                r_json = r_raw.json()
                break
            else:
                attempts += 1
                print(f"Request failed - attempts: {attempts}")

        if r_json:
            yield r_json


def get_genres_from_tracks(track_ids: List[str]):
    artist_id_map = get_artists_from_tracks(track_ids)
    artist_id_list = list(artist_id_map.values())
    artist_genre_map = get_genres_from_artists(artist_id_list)
    return artist_genre_map


def divide_chunks(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i: i + n]
