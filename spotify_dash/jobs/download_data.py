import datetime as dt
import os
import time
from multiprocessing.pool import ThreadPool
from typing import Union

import requests

country_codes = (
    "global",
    "us",
    "gb",
    # "ad", # Data unavailable for Andorra.
    "ar",
    "at",
    "au",
    "bg",
    "bo",
    "br",
    "ca",
    "ch",
    "cl",
    "co",
    "cr",
    "cy",
    "cz",
    "de",
    "dk",
    "do",
    "ec",
    "ee",
    "es",
    "fi",
    "fr",
    "gr",
    "gt",
    "hk",
    "hn",
    "hu",
    "id",
    "ie",
    "il",
    "in",
    "is",
    "it",
    "jp",
    "lt",
    "lu",
    "lv",
    "mx",
    "my",
    "ni",
    "nl",
    "no",
    "nz",
    "pa",
    "pe",
    "ph",
    "pl",
    "pt",
    "py",
    "ro",
    "ru",
    "se",
    "sg",
    "sk",
    "sv",
    "th",
    "tr",
    "tw",
    "ua",
    "uy",
    "vn",
    "za",
    "be",
)


def download_spotify_data(
    country: str,
    frequency: str = "weekly",
    start_date: dt.date = dt.date(2017, 12, 29),
    end_date: Union[dt.date, str] = "last-monday",
    path: str = "../resources/spotifycharts/",
    retries: int = 3,
) -> None:
    """

    Args:
        country (str):
        frequency (str):
        start_date (datetime.date):
        end_date (datetime.date):
        path (str):
        retries (int):

    Returns:
        Nothing (None)
    """
    print(f"Downloading Spotify resources for: {country}")

    os.makedirs(f"{path}/{frequency}", exist_ok=True)

    if end_date == "last-monday":
        end_date = dt.date.today() - dt.timedelta(
            days=-dt.date.today().weekday(), weeks=2
        )

    if frequency == "weekly":
        time_delta = dt.timedelta(7)
    elif frequency == "daily":
        time_delta = dt.timedelta(1)
    else:
        raise Exception("Unknown frequency value.")

    while start_date < end_date:
        week_start_str = start_date.strftime("%Y-%m-%d")
        week_end_str = (start_date + dt.timedelta(7)).strftime("%Y-%m-%d")
        download_path = (
            f"{os.path.join(path, frequency)}/{country}-streams-{week_start_str}.csv"
        )

        base_msg = f"{country} - {week_start_str} to {week_end_str} - "
        base_url = "https://spotifycharts.com/regional"

        # Only attempt to download if resources does not exist or file size under 10kb.
        if (
            not os.path.isfile(download_path)
            or os.path.getsize(download_path) / 1024 < 10
        ):
            attempts = 0
            while attempts < retries:
                url = f"{base_url}/{country}/{frequency}/{week_start_str}--{week_end_str}/download"
                r = requests.get(url)
                print(base_msg, "Request sent")
                response_text = r.text

                # Check response code and content size.
                if len(r.content) > 100 and r.ok:
                    with open(download_path, "w", encoding="utf-8") as f:
                        f.write(response_text)
                    print(base_msg, "Success")
                    break
                else:
                    attempts += 1
                    print(base_msg, f"Failed - Attempts: {attempts}")
                    time.sleep(1)

        start_date += time_delta

    print("Complete.")


if __name__ == "__main__":
    threads = 4
    print(f"Using {threads} threads.")
    pool = ThreadPool(threads)
    pool.map(download_spotify_data, country_codes)
