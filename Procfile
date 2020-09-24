web: cd spotify_dash && python3 bin/download_data.py && gunicorn app:server
worker: cd spotify_dash && python3 bin/maintain_data_asset.py