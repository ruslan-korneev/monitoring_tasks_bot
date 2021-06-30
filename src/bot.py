import logging
import os

from emoji import emojize
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
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


class Form(StatesGroup):
    task_name = State()
    task = State()
    sleep = State()


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
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button_stop = InlineKeyboardButton(
            text='Отмена', callback_data='cancel')
        keyboard.row(button_stop)
        await message.reply(
            emojize(':plus: Пришлите тип задачи :spiral_notepad:'),
            reply_markup=keyboard)
        await Form.task_name.set()
    elif 'Список задач' in message.text:
        await message.reply(
            emojize('Вот список задач :clipboard: :\n [отправить пагинатор]'))
    else:
        await message.answer(emojize('Не понял :thinking_face:'))


@dp.message_handler(state=Form.task_name)
async def process_url(message: types.Message, state: FSMContext):
    """
    Process adding task name
    """
    async with state.proxy() as task_data:
        task_data['name'] = message.text
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_stop = InlineKeyboardButton(
        'Отмена', callback_data='cancel')
    keyboard.row(button_stop)
    await message.answer(
        'Пришлите задачу',
        reply_markup=keyboard)
    await Form.task.set()


@dp.message_handler(state=Form.task)
async def process_url(message: types.Message, state: FSMContext):
    """
    Process adding task
    """
    async with state.proxy() as task_data:
        task_data['task'] = message.text
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_stop = InlineKeyboardButton(
        'Отмена', callback_data='cancel')
    keyboard.row(button_stop)
    await message.answer(
        'Пришлите задержку (в секундах)',
        reply_markup=keyboard)
    # await Form.sleep.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message,
                         state: FSMContext, from_user=None):
    """
    Отмена формы
    """
    logging.info('Get user id - {}'.format(from_user.id))
    if from_user:
        message.from_user.id = from_user.id
    current_state = await state.get_state()
    if current_state is None:
        logging.info('CURRENT STATE IS NONE')

    logging.debug('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    logging.info('FINISHED')
    await bot.edit_message_text(
        message_id=message.message_id,
        chat_id=from_user.id,
        text='Отменено.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
