import datetime as dt
import pathlib

import asyncio
import aiohttp
import aiofiles
import async_timeout
import requests

from utils.dates import last_friday


class SpotifyDownloader:
    def __init__(
            self,
            start_date,
            end_date,
            target_directory,
            sem=1000
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.target_directory = target_directory
        self.base_url = "https://spotifycharts.com/regional"
        self.sem = sem
        self.event_loop = asyncio.get_event_loop()
        self.target_directory.mkdir(parents=True, exist_ok=True)
        self.country_codes = (
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

    def url_builder(self, country, start, end):
        return f"{self.base_url}/{country}/weekly/{start.strftime('%Y-%m-%d')}--{end.strftime('%Y-%m-%d')}/download"

    def is_available(self):
        response = requests.get(self.url_builder("global", self.start_date, self.end_date))
        return response.ok

    def generate_urls(self, countries, start_date, end_date):
        def generate_dates(start_date_, end_date_):
            period_start = last_friday(start_date_)
            period_end = period_start + dt.timedelta(7)

            while period_end <= end_date_:
                yield period_start, period_end
                period_start += dt.timedelta(7)
                period_end += dt.timedelta(7)

        urls = (
            self.url_builder(country, start, end)
            for country in countries
            for start, end in generate_dates(start_date, end_date)
        )

        return urls

    async def download(self):
        if self.is_available():
            async def fetch(url_, session_, target_directory_):
                with async_timeout.timeout(10):
                    async with session_.get(url_) as r:
                        if r.status == 200:
                            country = url_.split("/")[-4]
                            period_start = url_.split("/")[-2][:10]
                            file_name = f"{country}-streams-{period_start}.csv"
                            file_path = pathlib.Path.joinpath(target_directory_, file_name)
                            await asyncio.sleep(1 / 1000)

                            async with aiofiles.open(file_path, "wb") as f:
                                while True:
                                    chunk = await r.content.read(1024)
                                    if not chunk:
                                        break
                                    await f.write(chunk)

                        return await r.release()

            if self.start_date is None:
                last_download = list(self.target_directory.glob("*global*"))[-1].stem[-10:]
                self.start_date = dt.datetime.strptime(last_download, "%Y-%m-%d") + dt.timedelta(7)

            if self.end_date is None:
                self.end_date = dt.date.today()

            sem = asyncio.Semaphore(1000)
            urls = self.generate_urls(self.country_codes, self.start_date, self.end_date)

            async with aiohttp.ClientSession(loop=self.event_loop) as session:
                async with sem:
                    for url in urls:
                        await (fetch(url, session, self.target_directory))
            return True
        else:
            return False


if __name__ == "__main__":
    pass
