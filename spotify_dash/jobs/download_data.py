import spotify_dash.settings as sts
import spotify_dash.utils.s3 as s3u


from datetime import datetime
from pathlib import Path


def download_spotify_asset():
    # Download s3 resources
    dl_required = False
    asset_path = Path(sts.SPOTIFY_ASSET_PATH)

    if asset_path.is_file():
        last_update = datetime.fromtimestamp(asset_path.stat().st_ctime)
        gt_7_days = (datetime.now() - last_update).days > 7

        if gt_7_days:
            dl_required = True
    else:
        dl_required = True

    if dl_required:
        spotify_s3 = s3u.BucketObjectConn(object_name=sts.SPOTIFY_ASSET_PATH.name)
        spotify_s3.download(sts.SPOTIFY_ASSET_PATH)


if __name__ == "__main__":
    download_spotify_asset()
