import logging
import os
import sys
import pprint
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db.crud import create_user
from db.database import Base, engine, get_session
from db.db_utils import *

API_TOKEN = os.environ["TOKEN"]

# Configure logging
logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(engine)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("""Welcome to paper service bot!\n
If you want to find paper by some parameter use command /find_by\n
For example:\n
/find_by year 2007 \n
Currently this function supports year/name/topic\n
If you want to find top-10 referenced authors in certain topic use command /top_10_authors_by_topic\n
For example: \n
/top_10_authors_by_topic Computer Science\n
Amount of answers is limited to 20 for more usability""")
    with get_session() as session:
        user = check_user_exists(message.from_user.id, session)
        if user is None:
            await message.reply("You are not registered yet, I will add you to my database now")
            create_user(message.from_user.id)


@dp.message_handler(commands=["find_by"], content_types=[types.ContentType.TEXT])
async def find_by(message: types.Message):
    _, query, value = message.text.split(' ', 2)
    with get_session() as session:
        if query == "year":
            papers = find_by_year(int(value), session)
        elif query == "name":
            papers = find_by_author(value, session)
        elif query == "topic":
            papers = find_by_topic(value, session)
    if len(papers):
        for paper in papers:
            await message.reply(pprint.pformat(paper, depth=3, indent=4)[1:-1])
    else:
        await message.reply("No such papers")


@dp.message_handler(commands=["top_10_authors_by_topic"], content_types=[types.ContentType.TEXT])
async def topics(message: types.Message):
    _, topic = message.text.split(' ', 1)
    print(topic, file=sys.stderr)
    with get_session() as session:
        authors = top_10_authors(topic, session)
    if len(authors):
        for author in authors:
            await message.reply(pprint.pformat(author, depth=2, indent=4)[1:-1])
    else:
        await message.reply("No such authors")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
