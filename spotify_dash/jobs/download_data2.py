import datetime as dt
import os
import time
from multiprocessing.pool import ThreadPool
from typing import Union

import asyncio
import aiohttp

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


def get_valid_dates(start_date, end_date=dt.date.today()):
    print(f"Date start: {start_date}")
    print(f"Date end: {end_date}")

    def to_friday(x):
        return x - dt.timedelta(x.weekday() + 3)

    period_start = to_friday(start_date)
    period_end = period_start + dt.timedelta(7)

    while period_end <= end_date:
        yield period_start, period_end
        period_start += dt.timedelta(7)
        period_end += dt.timedelta(7)


async def fetch(session, url, base_msg):
    async with session.request("GET", url) as r:
        print(base_msg, "Request sent")
        if r.status == 200:
            return await r.text()


async def download_spotify_data(
        country: str,
        frequency: str = "weekly",
        start_date: dt.date = dt.date(2017, 12, 29),
        end_date: dt.date = dt.date.today(),
        directory_path: str = "../resources/test/spotifycharts/weekly/"
):
    """

    Args:
        directory_path:
        country (str):
        frequency (str):
        start_date (datetime.date):
        end_date (datetime.date):
        path (str):
        retries (int):

    Returns:
        Nothing (None)
    """
    week_start_str = start_date.strftime("%Y-%m-%d")
    week_end_str = end_date.strftime("%Y-%m-%d")

    base_msg = f"{country} - {week_start_str} to {week_end_str} - "
    base_url = "https://spotifycharts.com/regional"

    url = f"{base_url}/{country}/{frequency}/{week_start_str}--{week_end_str}/download"
    file_path = os.path.join(directory_path, f"{country}-streams-{week_start_str}.csv")

    sem = asyncio.Semaphore(5)

    if not os.path.isfile(file_path):
        async with aiohttp.ClientSession(headers={"Connection": "close"}) as session, sem:
            response = await fetch(session, url, base_msg)  # , country, start_date
            if response:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response)


def main(request_dates):
    path: str = "../resources/spotifycharts/weekly/"
    os.makedirs(path, exist_ok=True)

    loop = asyncio.get_event_loop()
    coros = (
        loop.create_task(
            download_spotify_data(
                country=country,
                start_date=start,
                end_date=end,
                directory_path=path
            )
        )
        for start, end in request_dates
        for country in country_codes
    )
    tasks = asyncio.gather(*coros)
    return loop.run_until_complete(tasks)


if __name__ == "__main__":
    valid_dates = get_valid_dates(dt.date(2018, 1, 1))
    main(valid_dates)
