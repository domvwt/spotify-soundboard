import settings as sts
import utils.s3 as s3u


from datetime import datetime
from pathlib import Path


def download_spotify_asset():
    # Download s3 resources
    asset_path = Path(sts.SPOTIFY_ASSET_PATH)
    last_update = datetime.fromtimestamp(asset_path.stat().st_ctime)
    gt_7_days = (datetime.now() - last_update).days > 7

    if not asset_path.is_file() or gt_7_days:
        spotify_s3 = s3u.BucketObjectConn(object_name=sts.SPOTIFY_ASSET_PATH.name)
        spotify_s3.download(sts.SPOTIFY_ASSET_PATH)


if __name__ == "__main__":
    download_spotify_asset()
