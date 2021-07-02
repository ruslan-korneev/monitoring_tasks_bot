import asyncio
import logging
import os

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

from common import create_tables
from common import db

from emoji import emojize

from telegram_bot_pagination import InlineKeyboardPaginator


TG_TOKEN = os.environ.get('TG_TOKEN')

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

# Initialize bot and dispatcher
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Creation table for tasks
create_tables.create_tables()


class Form(StatesGroup):
    """ Fields for tasks """
    task_name = State()
    task = State()
    sleep = State()


@dp.callback_query_handler(lambda c: c.data.split('#')[0] == 'task')
async def task_page_callback(call):
    page = int(call.data.split('#')[1])
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id)
    await send_task_page(call.message, page)


@dp.callback_query_handler(lambda call: True, state='*')
async def process_callback_keyboard(call: types.CallbackQuery,
                                    callback_data=None,
                                    state='*'):
    if callback_data:
        code = callback_data
    else:
        code = call.data
    if code == 'cancel':
        await cancel_handler(
            message=call.message,
            from_user=call.from_user,
            state=state)
        await call.answer()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    Send info about bot and send keyboard with buttons
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_add_task = KeyboardButton(
        emojize('Добавить задачу :round_pushpin:'))
    button_task_list = KeyboardButton(emojize('Список задач :clipboard:'))
    keyboard.row(button_add_task, button_task_list)

    reply = """
    Привет!
    Бот для прохождения тестового задания
    От Руслана Корнеева @shaggy_axel
    Выполняет только два типа задач:
    - Выполнить разворот строки
    - Выполнить попарно перестановку четных и нечетных
    ____________________
    После нажатия на кнопку "Добавить задачу" идет три этапа:
        1. Название задачи (пример. Выполнить разворот строки)
        2. Передать данные для выполнения задачи (тевирп)
        3. Указать задержку в секундах
        4. Получить ответ (привет)
    """
    await message.reply(reply, reply_markup=keyboard)


@dp.message_handler()
async def echo(message: types.Message):
    if 'Добавить задачу' in message.text:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button_stop = InlineKeyboardButton(
            text=emojize('Отмена :no_entry:'),
            callback_data='cancel')
        keyboard.row(button_stop)
        await message.reply(
            emojize(':plus: Пришлите тип задачи :spiral_notepad:'),
            reply_markup=keyboard)
        await Form.task_name.set()
    elif 'Список задач' in message.text:
        await send_task_page(message)
    else:
        await message.answer(emojize('Не понял :thinking_face:'))


@dp.message_handler(state=Form.task_name)
async def process_add_task_name(message: types.Message, state: FSMContext):
    """
    Process adding task name
    """
    async with state.proxy() as task_data:
        task_data['name'] = message.text
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_stop = InlineKeyboardButton(
        emojize('Отмена :no_entry:'), callback_data='cancel')
    keyboard.row(button_stop)
    await message.answer(
        emojize('Пришлите входные данные задачи :envelope_with_arrow:'),
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
        emojize('Отмена :no_entry:'),
        callback_data='cancel')
    keyboard.row(button_stop)
    await message.answer(
        emojize(':timer_clock: Пришлите задержку (в секундах)'),
        reply_markup=keyboard)
    await Form.sleep.set()


@dp.message_handler(state=Form.sleep)
async def process_add_time_out(message: types.Message, state: FSMContext):
    """
    Process adding timeout
    """
    try:
        message.text = int(message.text)
        msg = await message.answer(
            emojize('Отлично, Задача выполняется! :zzz:'))
        async with state.proxy() as task_data:
            task_data['sleep'] = message.text
            id_task = db.add_task(task_data['name'], task_data['task'])
            await do_task(id_task, task_data['sleep'],
                          message.from_user.id, msg.message_id)
        await state.finish()
    except ValueError:
        await message.answer('Ошибка!\nПришлите число')


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


async def do_task(id_task, sleep, chat_id, message_id):
    await asyncio.sleep(1)
    db.task_in_process(id_task)
    # Пишем, что задача выполняется и засыпаем
    reply = f'Задача №{id_task} выполняется :hourglass_not_done:'
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=emojize(reply))
    await asyncio.sleep(sleep-1)
    # Выполняем задачу
    answer = get_answer(id_task)
    if not(answer is None):
        db.task_done(id_task, answer)
        reply = f'Задача {id_task} - Выполнена! :sparkles:\nОтвет: {answer}'
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=emojize(reply))
    else:
        db.task_fool(id_task)
        reply = f'Провал, не понятны условия задачи №{id_task}'
        reply += ' :exclamation_question_mark:'
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=emojize(reply))


def get_answer(id_task):
    name = db.get_name_task(id_task).lower()
    flag_swap = ('разворот' in name or 'поворот' in name or
                 'развернуть' in name or 'повернуть' in name or
                 'круть' in name or 'верть' in name)
    flag_odd_even = 'четных' in name or 'четные' in name or 'чет' in name
    if flag_swap:
        task = db.get_task(id_task)
        answer = task[::-1]
        return answer
    elif flag_odd_even:
        task = db.get_task(id_task)
        answer = ''
        for odd, even in zip(task[::2], task[1::2]):
            answer += even + odd
        if len(task) % 2 != 0:
            answer += task[-1]
        return answer
    return None


async def send_task_page(message, page=1):
    task_pages = db.get_task_list()
    paginator = InlineKeyboardPaginator(
        len(task_pages),
        current_page=page,
        data_pattern='task#{page}',
    )

    reply = f'ID: {task_pages[page-1][0]}\n'
    reply += f'Задача: {task_pages[page-1][1]}\n'
    reply += f'Дано: {task_pages[page-1][2]}\n'
    if 'в очереди' in task_pages[page-1][3]:
        status = f'Статус: {task_pages[page-1][3]} :zzz:'
        reply += emojize(status)
    elif 'выполняется' in task_pages[page-1][3]:
        status = f'Статус: {task_pages[page-1][3]} :pencil:'
        reply += emojize(status)
    elif 'готов' in task_pages[page-1][3]:
        status = f'Статус: {task_pages[page-1][3]} :party_popper:\n'
        reply += emojize(status)
        reply += f'Ответ: {task_pages[page-1][4]}'
    else:
        status = f'Статус: {task_pages[page-1][3]} :exclamation_question_mark:'

    await bot.send_message(
        message.chat.id,
        reply,
        reply_markup=paginator.markup,
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
