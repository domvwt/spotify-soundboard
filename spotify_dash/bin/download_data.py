import datetime as dt
import pathlib

import asyncio
import aiohttp
import aiofiles
import async_timeout

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


def generate_dates(start_date, end_date):
    def to_friday(x):
        return x - dt.timedelta(x.weekday() + 3)

    period_start = to_friday(start_date)
    period_end = period_start + dt.timedelta(7)

    while period_end <= end_date:
        yield period_start, period_end
        period_start += dt.timedelta(7)
        period_end += dt.timedelta(7)


def generate_urls(countries, start_date, end_date):
    base_url = "https://spotifycharts.com/regional"

    urls = (
        f"{base_url}/{country}/weekly/"
        f"{start.strftime('%Y-%m-%d')}--{end.strftime('%Y-%m-%d')}/download"
        for country in countries
        for start, end in generate_dates(start_date, end_date)
    )

    return urls


async def fetch(url, session, target_directory):
    with async_timeout.timeout(10):
        async with session.get(url) as r:
            if r.status == 200:
                country = url.split("/")[-4]
                period_start = url.split("/")[-2][:10]
                file_name = f"{country}-streams-{period_start}.csv"
                file_path = pathlib.Path.joinpath(target_directory, file_name)
                await asyncio.sleep(1 / 1000)

                async with aiofiles.open(file_path, "wb") as f:
                    while True:
                        chunk = await r.content.read(1024)
                        if not chunk:
                            break
                        await f.write(chunk)

            return await r.release()


async def main(loop, start_date=None, end_date=None, target_directory=None):
    if target_directory is None:
        target_directory = pathlib.Path("../resources/spotifycharts/weekly/")

    target_directory.mkdir(parents=True, exist_ok=True)

    if start_date is None:
        last_download = list(target_directory.glob("*global*"))[-1].stem[-10:]
        start_date = dt.datetime.strptime(last_download, "%Y-%m-%d") + dt.timedelta(7)

    if end_date is None:
        end_date = dt.date.today()

    sem = asyncio.Semaphore(1000)
    urls = generate_urls(country_codes, start_date, end_date)

    async with aiohttp.ClientSession(loop=loop) as session:
        async with sem:
            for url in urls:
                await (fetch(url, session, target_directory))


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main(loop=event_loop))
