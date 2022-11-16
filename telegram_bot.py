import json
import time

from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text
from aiofiles import os

from telegram_token import token
from main import collect_data_novus


bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_button = ['Всі акції у csv', "Акції по категоріям"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_button)

    await message.answer("Оберіть категорію", reply_markup=keyboard)


@dp.message_handler(Text(equals="Всі акції у csv"))
async def get_sales(message: types.Message):
    await message.answer("Please wait ...")
    chat_id = message.chat.id
    await send_data(chat_id=chat_id)


async def send_data(chat_id=''):
    file = await collect_data_novus()
    await bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
    await os.remove(file)


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
