import logging
import os

from emoji import emojize
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


TG_TOKEN = os.environ.get('TG_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    Send info about bot and send keyboard with buttons
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_add_task = KeyboardButton('Добавить задачу')
    button_task_list = KeyboardButton('Список задач')
    keyboard.row(button_add_task, button_task_list)

    await message.reply("Hi! [ INFO ABOUT BOT ]", reply_markup=keyboard)


@dp.message_handler()
async def echo(message: types.Message):
    if 'Добавить задачу' in message.text:
        await message.reply(
            emojize(':plus: Пришлите тип задачи :spiral_notepad:'))
    elif 'Список задач' in message.text:
        await message.reply(
            emojize('Вот список задач :clipboard: :\n [отправить пагинатор]'))
    await message.answer(emojize('Не понял :thinking_face:'))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
