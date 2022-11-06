import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db.crud import create_user
from db.database import Base, engine, get_session
from db.db_utils import login, check_user_exists

API_TOKEN = os.environ['TOKEN']

# Configure logging
logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(engine)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    logged_in = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await state.update_data(logged_in=False)
    await message.reply("Hi!\nPlease proceed to sign up or login option")


@dp.message_handler(commands=['sign_up', 'login'], content_types=[types.ContentType.TEXT])
async def sign_up(message: types.Message, state: FSMContext):
    await message.reply("Write your login and password in the following manner:\n login: password: ")


@dp.message_handler(text_contains=['login:', 'password:'], content_types=[types.ContentType.TEXT])
async def create_or_login(message: types.Message, state: FSMContext):
    async with state.proxy() as curr_state:
        print(curr_state, file=sys.stderr)
        if curr_state['logged_in']:
            await message.reply("You're already logged in")
        else:
            with get_session() as session:
                text = message.text.split()

                user_data = {}
                user_data['login'] = text[text.index('login:') + 1]
                user_data['password'] = text[text.index('password:') + 1]

                if check_user_exists(user_data['login'], session):
                    logged_in = login(user_data, session)
                    if not logged_in:
                        await message.reply("Login or password is wrong")
                    else:
                        curr_state['logged_in'] = True
                else:
                    create_user(user_data, session)
                    curr_state['logged_in'] = True

                print(curr_state, file=sys.stderr)


@dp.message_handler(commands=['find_by'], content_types=[types.ContentType.TEXT])
async def find_by(message: types.Message):
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
