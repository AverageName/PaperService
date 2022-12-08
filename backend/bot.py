import logging
import os
import sys
import pprint
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import markdown
#from aiogram.dispatcher.filters.callback_data import CallbackData
#from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.dispatcher.filters import Text
#from magic_filter import F
from db.crud import create_user
from db.database import Base, engine, get_session
from db.db_utils import *
from db.crud import update_by_id, insert_user_paper_interaction, read_by_id
import random
import db.models
import recommender


# class FeedbackOnPaperCallbackFactory(CallbackData, prefix="feedback"):
#     value: str


def get_feedback_keyboard(paper_id: str):
    # builder = InlineKeyboardBuilder()
    # builder.button(
    #     text="like", callback_data="feedback_like"#FeedbackOnPaperCallbackFactory(value="like")
    # )
    # builder.button(
    #     text="dislike", callback_data="feedback_dislike"#FeedbackOnPaperCallbackFactory(value="dislike")
    # )
    # builder.adjust(2)
    buttons = [
        [
            types.InlineKeyboardButton(text="like", callback_data=f"feedback_like_{paper_id}"),
            types.InlineKeyboardButton(text="dislike", callback_data=f"feedback_dislike_{paper_id}")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard #builder.as_markup()


def paper_markdowner(paper: dict):
    content = list()
    if paper["title"]:
        content.append(markdown.bold(paper["title"]))
    if paper["abstract"]:
        content.append(markdown.text(paper["abstract"][:300]+"..."))
    tail = "\n"
    if paper["authors"]:
        tail += paper["authors"][0]["name"] + " et al., "
    if paper["year"]:
        tail += str(paper["year"])
    content.append(markdown.text(tail))
    if paper["topic"]:
        content.append(markdown.text("Topic: " + paper["topic"]))
    if paper["url"] and len(paper["url"]) > 2:
        content.append(markdown.link("Read full paper here", paper["url"][1:-1]))
    return markdown.text(*content, sep='\n')


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
    await message.answer("""Welcome to paper service bot!\n
If you want to find paper by some parameter use command /find_by\n
For example:\n
/find_by year 2007 \n
Currently this function supports year/name/topic\n
If you want to find top-10 referenced authors in certain topic use command /top_10_authors_by_topic\n
For example: \n
/top_10_authors_by_topic Computer Science\n
Amount of answers is limited to 20 for more usability""")
    with get_session() as session:
        if not check_user_exists(message.from_user.id, session):
            await message.answer(f"You are not registered yet, I will add you to my database now")
            create_user(message.from_user.id, session)


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
        for paper in random.shuffle(papers)[:5]:
            await message.reply(paper_markdowner(paper),#pprint.pformat(paper, depth=3, indent=4)[1:-1],
                                reply_markup=get_feedback_keyboard(paper["id"]),
                                parse_mode=types.ParseMode.MARKDOWN)
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


@dp.message_handler(commands=["what_should_i_read_next"], content_types=[types.ContentType.TEXT])
async def recommend_paper(message: types.Message):
    with get_session() as session:
        last_liked_paper = None
        readed_papers = list()
        user = session.query(db.models.User).filter_by(tg_id=message.from_user.id).one_or_none()
        if user is not None:
            last_liked_paper = session.query(db.models.Paper).filter_by(id=user.last_like_paper_id).one_or_none()
            if last_liked_paper is not None:
                last_liked_paper = {"title": last_liked_paper.title, "abstract": last_liked_paper.abstract}
            user_interactions = session.query(db.models.UserPaper).filter_by(user_id=user.id)
            if user_interactions is not None:
                readed_papers = [interaction.paper_id for interaction in user_interactions]
        recommended_paper_ids = recommender.get_recommended_paper_id(last_liked_paper,
                                                                     readed_papers)
        recommended_paper = None
        for recommended_paper_id in recommended_paper_ids:
            recommended_paper = session.query(db.models.Paper).filter_by(id=recommended_paper_id).one_or_none()
            if recommended_paper is not None:
                break
        if recommended_paper is None:
            await message.reply("Ups, something went wrong, we are already working on it"
                                f"\n{len(recommended_paper_ids)}"
                                f"\n{' '.join(recommended_paper_ids)}")
        else:
            await message.reply(paper_markdowner(recommended_paper.as_dict()),
                                reply_markup=get_feedback_keyboard(recommended_paper_id),
                                parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(Text(startswith="feedback_"))
async def callbacks_feedback_on_paper(
        callback: types.CallbackQuery,
):
    _, feedback_value, paper_id = callback.data.split("_")
    with get_session() as session:
        user = session.query(db.models.User).filter_by(tg_id=callback.from_user.id).one_or_none()
        if feedback_value == "like" and user is not None:
            update_by_id(user.id, {"last_like_paper_id": paper_id}, "user", session)
            insert_user_paper_interaction(user.id, paper_id, True, session)
        elif feedback_value == "dislike" and user is not None:
            if user.last_like_paper_id == paper_id:
                update_by_id(user.id, {"last_like_paper_id": None}, "user", session)
            insert_user_paper_interaction(user.id, paper_id, False, session)
        # for interaction in session.query(db.models.UserPaper):
        #     paper = read_by_id(interaction.paper_id, "paper", session)
        #     await callback.message.answer(f"user_id: {interaction.user_id}\n"
        #                                   f"paper_id: {interaction.paper_id}\n"
        #                                   f"paper_title: {paper.title}\n"
        #                                   f"like: {interaction.like}\n"
        #                                   f"ts: {interaction.ts}\n")
    await callback.answer()

            # if user is not None:
            #     await callback.message.answer(callback.message.text + '\nlike on ' + paper_id + \
            #                                   '\nlast like prev:' + str(user.last_like_paper_id))
            # user = session.query(db.models.User).filter_by(tg_id=callback.from_user.id).one_or_none()
            # if user is not None:
            #     await callback.message.answer(callback.message.text + '\nlike on ' + paper_id + \
            #                                   '\nlast like curr:' + str(user.last_like_paper_id))
            #user = session.query(db.models.User).filter_by(tg_id=callback.message.from_user.id).one_or_none()
            #await callback.message.reply(f"Dis is you {user} {callback.message.from_user.id} {user is None}")
            # await callback.message.answer(callback.message.text + '\nlike on ' + paper_id + \
            #                               f"\nyour id: {callback.from_user.id}")
            # if check_user_exists(callback.from_user.id, session):
            #     # await callback.message.answer(callback.message.text + '\nlike on ' + paper_id + \
            #     #                               '\nEboy last like is:')
            #     # update_user_like(callback.message.from_user.id, paper_id, session)
            #     for user in session.query(db.models.User):
            #         print(user)
            #         await callback.message.answer(callback.message.text+'\nlike on '+paper_id+\
            #                                       '\nEboy last like is:'+str(user.last_like_paper_id))
        # else if (feedback_value == "dislike" and user is not None):
        #     update_by_id(user.id, {"last_like_paper_id": None}, "user", session)

            # for user in session.query(db.models.User):
            #     #print(user)
            #     await callback.message.answer(callback.message.text+'\ndislike on '+paper_id+\
            #                                   '\nEboy last like is:'+str(user.last_like_paper_id))
    #await callback.answer()


# @dp.callback_query(FeedbackOnPaperCallbackFactory.filter())
# async def callbacks_feedback_on_paper(
#         callback: types.CallbackQuery,
#         callback_data: FeedbackOnPaperCallbackFactory
# ):
#     if callback_data.value == "like":
#         await callback.message.answer(callback.message.text)
#     else:
#         await callback.message.answer(callback.message.text)
#     await callback.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
