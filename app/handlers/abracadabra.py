import os
from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.config_reader import load_config
from app.handlers.common import cmd_idle
import logging


logger = logging.getLogger(__name__)


class UserControlAdmin(StatesGroup):
    create_message = State()
    send_message = State()


async def secret_command(message: types.Message):
    logger.info('User "%s" (%s) entered to the secret mode',
                message.from_user.id, message.from_user.username)
    await message.answer('Write down your message to users')
    await UserControlAdmin.create_message.set()


async def create_msg(message: types.Message, state: FSMContext):
    custom_message = message.text
    await state.update_data(message=custom_message)

    reply_keyboard = [['Preview']]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)

    await message.answer('Ready for preview?',
                         reply_markup=markup)


async def preview_msg(message: types.Message, state: FSMContext):
    admin_data = await state.get_data()
    custom_message = admin_data['message']
    await message.answer(custom_message,
                             parse_mode='MarkdownV2')

    reply_keyboard = [['Send',
                       'Delete',
                       'Cancel']]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)

    await message.answer('What to do?',
                         reply_markup=markup)

    await UserControlAdmin.next()


async def delete_msg(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer('Message is deleted. You can write new message')
    await UserControlAdmin.create_message.set()


async def send_msg(message: types.Message, state: FSMContext):
    admin_data = await state.get_data()
    custom_message = admin_data['message']
    config = load_config(os.path.join('config', 'bot.ini'))
    bot = Bot(token=config.tg_bot.token)
    await bot.send_message(758696505, custom_message,
                             parse_mode='MarkdownV2')
    await bot.send_message(511002883, custom_message,
                             parse_mode='MarkdownV2')
    await cmd_idle(message, state, headless=False)


def register_handlers_abracadabra(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands="abracadabra", state="*")
    dp.register_message_handler(preview_msg, lambda message: message.text in ['Preview'],
                                state=UserControlAdmin.create_message)
    dp.register_message_handler(delete_msg, lambda message: message.text in ['Delete'],
                                state=UserControlAdmin.send_message)
    dp.register_message_handler(send_msg, lambda message: message.text in ['Send'],
                                state=UserControlAdmin.send_message)
    dp.register_message_handler(create_msg, state=UserControlAdmin.create_message)
