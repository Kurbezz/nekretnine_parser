import asyncio
from asyncio.queues import Queue

from datetime import date

import hashlib
from sqlitedict import SqliteDict
from parsers import PARSERS
from parsers.base import Announcement
import aiogram


BOT_TOKEN = "1111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
CHANNEL_ID = -1001872853621

bot = aiogram.Bot(BOT_TOKEN)


async def start_parsers(db: SqliteDict, queue: Queue) -> None:
    await asyncio.gather(
        *[parser.start_parse(db, queue) for parser in PARSERS]
    )


async def notify(item: Announcement) -> bool:
    message = item.link

    try:
        await bot.send_message(CHANNEL_ID, message)
        return True
    except aiogram.exceptions.TelegramAPIError:
        return False


async def start_notifier(db: SqliteDict, queue: Queue) -> None:
    while True:
        item: Announcement = await queue.get()

        link_hash = hashlib.md5(item.link.encode()).hexdigest()

        current_value = db.get(link_hash, None)
        item_date = item.update_date

        if current_value != item_date.isoformat():
            if item_date == date.today():
                if await notify(item):
                    db[link_hash] = item_date.isoformat()
                    db.commit()
            else:
                db[link_hash] = item_date.isoformat()
                db.commit()

                await asyncio.sleep(1)


async def main():
    db = SqliteDict("notify.sqlite")

    queue = Queue()

    try:
        await asyncio.gather(
            start_parsers(db, queue),
            start_notifier(db, queue)
        )
    finally:
        db.close()


if __name__ == "__main__":
    while True:
        asyncio.run(main())
