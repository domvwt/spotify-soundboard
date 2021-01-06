import asyncio
import datetime as dt
import pathlib
import time

import aiofiles
import aiohttp
import async_timeout
import requests

from spotify_dash.utils.dates import get_last_friday_from


class SpotifyDownloader:
    def __init__(
        self,
        target_directory,
        start_date: dt.datetime = None,
        end_date: dt.datetime = None,
        sem=1000,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.target_directory = target_directory
        self.base_url = "https://spotifycharts.com/regional"
        self.sem = sem
        self.target_directory.mkdir(parents=True, exist_ok=True)

    country_codes = (
        # "global",
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

    def _url_builder(self, country, start, end):
        return f"{self.base_url}/{country}/weekly/{start.strftime('%Y-%m-%d')}--{end.strftime('%Y-%m-%d')}/download"

    def is_available(self):
        url = self._url_builder(
            "global", self.start_date, self.start_date + dt.timedelta(7)
        )
        for _ in range(5):
            response = requests.get(url)
            if response.ok:
                return True
            else:
                time.sleep(0.2)

    def generate_urls(self, countries, start_date, end_date):
        def generate_dates(start_date_, end_date_):
            period_start = get_last_friday_from(start_date_)
            period_end = period_start + dt.timedelta(7)

            while period_end <= end_date_:
                yield period_start, period_end
                period_start += dt.timedelta(7)
                period_end += dt.timedelta(7)

        urls = (
            self._url_builder(country, start, end)
            for country in countries
            for start, end in generate_dates(start_date, end_date)
        )

        return urls

    async def download(self, event_loop):
        if self.is_available():
            print(
                f"Downloading data from {self.base_url}\n"
                f"Date start: {self.start_date}\n"
                f"Date end:   {self.end_date}\n"
            )

            async def fetch(url_, session_, target_directory_):
                with async_timeout.timeout(10):
                    async with session_.get(url_) as r:
                        if r.status == 200:
                            country = url_.split("/")[-4]
                            period_start = url_.split("/")[-2][:10]
                            file_name = f"{country}-streams-{period_start}.csv"
                            file_path = pathlib.Path.joinpath(
                                target_directory_, file_name
                            )
                            await asyncio.sleep(1 / 1000)

                            async with aiofiles.open(file_path, "wb") as f:
                                while True:
                                    chunk = await r.content.read(1024)
                                    if not chunk:
                                        break
                                    await f.write(chunk)

                        return await r.release()

            sem = asyncio.Semaphore(1000)
            urls = self.generate_urls(
                self.country_codes, self.start_date, self.end_date
            )

            async with aiohttp.ClientSession(loop=event_loop) as session:
                async with sem:
                    for url in urls:
                        await (fetch(url, session, self.target_directory))
            print("Download complete.")
            return True
        else:
            print("Spotify chart data unavailable.")
            return False


if __name__ == "__main__":
    pass
