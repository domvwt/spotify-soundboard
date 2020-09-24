import settings as sts
import utils.s3 as s3u


def download_spotify_asset():
    # Download s3 resources
    spotify_s3 = s3u.BucketObjectConn(object_name=sts.SPOTIFY_ASSET_PATH.name)
    spotify_s3.download(sts.SPOTIFY_ASSET_PATH)


if __name__ == "__main__":
    download_spotify_asset()
