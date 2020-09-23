# Logic
# Check if bucket and object exist
# True:
#   Check if object last updated >= 7 days
#       True:
#           Pass
#       False:
#           Download object
#           Download spotify data from last update to today's date
#           Delete old data from file
#           Load new data to file
#           Upload bucket object
# False:
#       Download spotify data from last update to today's date
#       Delete old data from file
#       Load new data to file
#       Upload bucket object
#
# ALSO:
#   maintain artist -> genre map on s3
#   maintain artist -> primary genre map on s3

import os
import utils.s3 as s3u
import datetime as dt
import settings as sts
import utils.io as iou
from utils.spotify import SpotifyDownloader
from utils.dates import last_friday
import utils.etl as etl

spotify_s3conn = s3u.BucketObjectConn(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    bucket_name=sts.S3_BUCKET_NAME,
    object_name=sts.SPOTIFY_ASSET_PATH.name
)

artist_genre_many_s3conn = s3u.BucketObjectConn(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    bucket_name=sts.S3_BUCKET_NAME,
    object_name=sts.ARTIST_GENRE_MANY_MAP.name
)

artist_genre_prime_s3conn = s3u.BucketObjectConn(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    bucket_name=sts.S3_BUCKET_NAME,
    object_name=sts.ARTIST_GENRE_PRIME_MAP.name
)


last_update = spotify_s3conn.last_update()
last_friday = last_friday(dt.datetime.today())
report_start = last_friday - dt.timedelta(weeks=51)

# If spotify asset exists
if spotify_s3conn.exists():

    last_update = spotify_s3conn.last_update()

    # Check if spotify asset was last updated more than 7 days ago
    if dt.datetime.today() - last_update() >= dt.timedelta(7):

        # Download new spotify data
        spotify_downloader = SpotifyDownloader(
            start_date=last_update,
            end_date=last_friday,
            target_directory=sts.SPOTIFY_DATA_DIR
        )

        # Returns False if unavailable
        if spotify_downloader.download():

            # Download the asset from s3 bucket
            spotify_s3conn.download(sts.SPOTIFY_ASSET_PATH)
            spotify_df = iou.decompress_pickle(sts.SPOTIFY_ASSET_PATH)

            # Aggregate the new spotify data
            spotify_new_df = etl.build_spotify_asset(sts.SPOTIFY_DATA_DIR, start_date=report_start)

        else:
            print("Spotify data unavailable.")


# If spotify asset does not exist
else:
    # Try to download new spotify data
    spotify_downloader = SpotifyDownloader(
        start_date=report_start,
        end_date=last_friday,
        target_directory=sts.SPOTIFY_DATA_DIR
    )

    # If spotify data is available
    if spotify_downloader.is_available():
        print("Downloading Spotify data.")
        if spotify_downloader.download():      
            # Create DataFrame from Spotify data
            spotify_new_df = etl.build_spotify_asset(sts.SPOTIFY_DATA_DIR, start_date=report_start)

            # Remember to upload new assets to s3
            # spotify data
            # artist -> genre map x 2

    # If spotify data unavailable
    else:
        print("Spotify data unavailable.")  # PROCESS FAILURE!

