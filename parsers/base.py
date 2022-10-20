import abc
import asyncio
from dataclasses import dataclass
from datetime import date
import hashlib
from typing import Optional

from bs4 import BeautifulSoup
from sqlitedict import SqliteDict
import httpx


@dataclass
class AnnoncementPreview:
    title: str
    update_date: Optional[date]
    link: str


@dataclass
class Announcement:
    title: str
    description: str
    price: int
    update_date: date

    link: str


class BaseParser(abc.ABC):
    BASE_SEARCH_LINK = ""
    BASE_PARAMS = {}
    PAGE_PARAM = ""

    @classmethod
    def process_previews_page(cls, bs: BeautifulSoup) -> list[AnnoncementPreview]:
        ...

    @classmethod
    @abc.abstractmethod
    def process_annoncement_data(cls, bs: BeautifulSoup, preview: AnnoncementPreview) -> Announcement:
        ...

    @classmethod
    async def get_annoncement_by_preview(cls, preview: AnnoncementPreview) -> Optional[Announcement]:
        print(f"Get annoncement by link: {preview.link} ...")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(preview.link)
            except httpx.ConnectError:
                return None
            except httpx.ReadTimeout:
                return None
            except httpx.ConnectTimeout:
                return None

        bs = BeautifulSoup(response.text, features="html.parser")

        return cls.process_annoncement_data(bs, preview)

    @classmethod
    async def parse(cls, db: SqliteDict, queue: asyncio.Queue) -> None:
        page = 1

        while page <= 20:
            params = {
                **cls.BASE_PARAMS,
                cls.PAGE_PARAM: page
            }

            print(f"Get {cls.__name__} page {page} previews...")

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(cls.BASE_SEARCH_LINK, params=params)
                except httpx.ReadTimeout:
                    return

            bs = BeautifulSoup(response.text, features="html.parser")

            previews = cls.process_previews_page(bs)

            last_annoncement_date = None

            for preview in previews:
                if preview.update_date:
                    last_annoncement_date = preview.update_date

                if preview.update_date is not None and preview.update_date != date.today():
                    continue

                link_hash = hashlib.md5(preview.link.encode()).hexdigest()
                if db.get(link_hash, None) == date.today().isoformat():
                    last_annoncement_date = date.today()
                    continue

                annoncement = await cls.get_annoncement_by_preview(preview)

                if annoncement:
                    await queue.put(annoncement)

                    last_annoncement_date = annoncement.update_date

            page += 1

            if last_annoncement_date is None:
                continue

            if (date.today() - last_annoncement_date).days >= 2:
                break

    @classmethod
    async def start_parse(cls, db: SqliteDict, queue: asyncio.Queue) -> None:
        while True:
            await cls.parse(db, queue)
            await asyncio.sleep(180)
