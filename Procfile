web: cd spotify_dash && python -m  bin.download_data && gunicorn app:server
worker: cd spotify_dash && python -m bin.maintain_data_asset