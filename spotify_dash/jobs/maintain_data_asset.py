import asyncio
import datetime as dt
import shutil

import pandas as pd

import spotify_dash.settings as sts
import spotify_dash.utils.etl as etl
import spotify_dash.utils.io as iou
import spotify_dash.utils.s3 as s3u
from spotify_dash.utils.dates import get_last_friday_from
from spotify_dash.utils.spotify import SpotifyDownloader


def main(mode="update"):
    # Connect to s3 resources
    spotify_s3 = s3u.BucketObjectConn(object_name=sts.SPOTIFY_ASSET_PATH.name)
    artist_genre_many_s3 = s3u.BucketObjectConn(
        object_name=sts.ARTIST_GENRE_MANY_PATH.name
    )
    artist_genre_prime_s3 = s3u.BucketObjectConn(
        object_name=sts.ARTIST_GENRE_PRIME_PATH.name
    )

    # Calculate dates
    today = dt.datetime.now(dt.timezone.utc).date()
    last_friday_from_today = get_last_friday_from(today)
    report_start = last_friday_from_today - dt.timedelta(weeks=53)

    # Initialise Spotify downloader
    spotify_downloader = SpotifyDownloader(target_directory=sts.SPOTIFY_DATA_DIR)

    # If spotify asset exists
    if mode == "update":
        last_update = spotify_s3.last_data_date()

        spotify_downloader.start_date = last_update + dt.timedelta(days=7)
        spotify_downloader.end_date = last_friday_from_today

        # Check if new spotify data available
        if spotify_downloader.is_available():
            print("Updating spotify assets...")
            # Download new spotify data
            loop = asyncio.get_event_loop()
            download_success = loop.run_until_complete(
                spotify_downloader.download(loop)
            )

            if download_success:
                # Download assets from s3 bucket
                spotify_s3.download(sts.SPOTIFY_ASSET_PATH)
                artist_genre_many_s3.download(sts.ARTIST_GENRE_MANY_PATH)
                artist_genre_prime_s3.download(sts.ARTIST_GENRE_PRIME_PATH)

                # Unpickle spotify assets
                spotify_hist = iou.decompress_pickle(sts.SPOTIFY_ASSET_PATH)
                artist_genre_many = iou.load_pickle(sts.ARTIST_GENRE_MANY_PATH)
                artist_genre_prime = iou.load_pickle(sts.ARTIST_GENRE_PRIME_PATH)

                # Aggregate spotify data
                (
                    spotify_new,
                    artist_genre_many_new,
                    artist_genre_prime_new,
                ) = etl.build_spotify_assets(
                    sts.SPOTIFY_DATA_DIR,
                    start_date=report_start,
                    artist_genre_many=artist_genre_many,
                    artist_genre_prime=artist_genre_prime,
                )
                spotify_all = spotify_hist.merge(
                    spotify_new, how="outer"
                ).drop_duplicates()

                spotify_all = etl.filter_one_year(spotify_all)

            else:
                print("Spotify download failed!")
                return False

        else:
            print("No new Spotify data available.")
            return False

    elif mode == "deploy":
        # Download spotify data
        spotify_downloader.start_date = report_start
        spotify_downloader.end_date = last_friday_from_today

        loop = asyncio.get_event_loop()
        download_success = loop.run_until_complete(spotify_downloader.download(loop))
        if download_success:
            # Aggregate spotify data
            (
                spotify_all,
                artist_genre_many_new,
                artist_genre_prime_new,
            ) = etl.build_spotify_assets(
                sts.SPOTIFY_DATA_DIR,
                start_date=report_start,
                artist_genre_many=dict(),
                artist_genre_prime=dict(),
            )

        # If spotify data unavailable
        else:
            print("Spotify data unavailable.")
            return False

    elif mode == "refresh":

        spotify_s3 = s3u.BucketObjectConn(object_name=sts.SPOTIFY_ASSET_PATH.name)
        spotify_s3.download(sts.SPOTIFY_ASSET_PATH)
        spotify_hist = iou.decompress_pickle(sts.SPOTIFY_ASSET_PATH)

        dtypes = {
            "Position": "uint16",
            "Track Name": pd.CategoricalDtype(),
            "Artist": pd.CategoricalDtype(),
            "Streams": "uint32",
            "URL": "object",
            "date": "datetime64[ns]",
            "ISO2": pd.CategoricalDtype(),
            "Genre": pd.CategoricalDtype(),
        }

        spotify_all = spotify_hist.astype(dtypes)

        # Keep two years of data
        spotify_all = etl.filter_one_year(spotify_all)

        iou.compress_pickle(sts.SPOTIFY_ASSET_PATH, spotify_all)
        spotify_s3.upload(sts.SPOTIFY_ASSET_PATH, last_data_date=spotify_all.date.max())

        return True
    else:
        raise Exception(f"Unrecognised mode: {mode}")

    # Save spotify data and upload to s3
    iou.compress_pickle(sts.SPOTIFY_ASSET_PATH, spotify_all)
    iou.save_pickle(sts.ARTIST_GENRE_MANY_PATH, artist_genre_many_new)
    iou.save_pickle(sts.ARTIST_GENRE_PRIME_PATH, artist_genre_prime_new)

    spotify_s3.upload(sts.SPOTIFY_ASSET_PATH, last_data_date=spotify_all.date.max())
    artist_genre_many_s3.upload(sts.ARTIST_GENRE_MANY_PATH)
    artist_genre_prime_s3.upload(sts.ARTIST_GENRE_PRIME_PATH)

    # Delete the spotify chart data and other assets
    shutil.rmtree(sts.SPOTIFY_DATA_DIR)
    sts.ARTIST_GENRE_MANY_PATH.unlink()
    sts.ARTIST_GENRE_PRIME_PATH.unlink()

    return True


if __name__ == "__main__":
    main(mode="update")
