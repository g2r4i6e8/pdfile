import os
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from unidecode import unidecode

from app.handlers.common import cmd_idle
from app.tools import tools
from app.tools.tools import check_invalid_format
import logging

from app.modules.read_messages import txt_dict, errors_dict

logger = logging.getLogger(__name__)

split_text = list(txt_dict['split_one_text'].values()) + list(txt_dict['split_many_text'].values())


class UserControlSplit(StatesGroup):
    handle_file = State()
    set_range = State()
    split_pages = State()


async def split_activate(message: types.Message, state: FSMContext):
    locale = message.from_user.locale if message.from_user.locale in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) chose to split PDF',
                message.from_user.id, message.from_user.username)
    await state.update_data(locale=locale)
    reply_keyboard = [[txt_dict['cancel_text'][locale]]]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=False)

    await message.answer(txt_dict['split_input_text'][locale],
                         reply_markup=markup)

    await state.update_data(file_path=str, function='split')

    await UserControlSplit.handle_file.set()


async def handle_errors(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    locale = user_data['locale']
    logger.info('User "%s" (%s) raised error',
                message.from_user.id, message.from_user.username)

    await message.answer(txt_dict['unknown_text'][locale])


async def handle_single_file(message: types.Message, state: FSMContext):
    await types.ChatActions.typing()
    user_data = await state.get_data()
    locale = user_data['locale']
    function = user_data['function']
    await types.ChatActions.typing()

    try:
        file = message.document
        file_name = file['file_name']
    except Exception as e:
        await message.answer(errors_dict['download_error'][locale])
        logger.error('User "%s" (%s) raised error %s while %s',
                     message.from_user.id, message.from_user.username, e, function)
        return None
    file_name = unidecode(file_name)
    file_size = file['file_size']
    logger.info('User "%s" (%s) uploaded a file %s with file size %d bytes (%s megabytes)',
                message.from_user.id, message.from_user.username, file_name, file_size,
                round(file_size / 1024 / 1024, 2))
    if file_size >= 20971520:
        await message.answer(errors_dict['big_file'][locale])
        logger.error('User "%s" (%s) raised big file error',
                     message.from_user.id, message.from_user.username)
        return None
    invalid_format, formats = check_invalid_format(file_name, function)
    if invalid_format:
        await message.answer(file_name + errors_dict['unsupported_format'][locale] + ', '.join(formats))
        logger.error('User "%s" (%s) raised unsupported file format error',
                     message.from_user.id, message.from_user.username)
        return None
    output_folder = os.path.join('temp', str(message.from_user.id))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, file_name)

    await file.download(destination_file=file_path)

    await state.update_data(file_path=file_path)

    await message.answer(txt_dict['split_queue_text'][locale].format(os.path.basename(file_path)))
    await message.answer(txt_dict['available_range_text'][locale],
                         parse_mode='MarkdownV2')

    await UserControlSplit.set_range.set()


async def setting_range(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    locale = user_data['locale']

    if re.match('^\s*\d+[-\d+]*\s*(,\s*\d+[-\d+]*\s*)*\s*$', message.text):
        await state.update_data(split_range=message.text)
        pass
    else:
        logger.error('User "%s" (%s) raised unavailable pattern error. Message: %s',
                     message.from_user.id, message.from_user.username, message.text)
        await message.answer(message.text + errors_dict['unsupported_pattern'][locale])
        await message.answer(txt_dict['available_range_text'][locale],
                             parse_mode='MarkdownV2')
        return None

    reply_keyboard = [[txt_dict['split_one_text'][locale]],
                      [txt_dict['split_many_text'][locale]],
                      [txt_dict['cancel_text'][locale]]]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)

    await message.answer(txt_dict['split_call_text'][locale],
                         reply_markup=markup)

    await UserControlSplit.split_pages.set()


async def split_file(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    locale = user_data['locale']
    file = user_data['file_path']
    split_range = user_data['split_range']
    output_folder: str = os.path.join('temp', str(message.from_user.id))

    try:
        if message.text in txt_dict['split_one_text'].values():
            output_path = tools.split(file, split_range, output_folder, separate_pages=False)
        elif message.text in txt_dict['split_many_text'].values():
            output_path = tools.split(file, split_range, output_folder, separate_pages=True)
        await types.ChatActions.upload_document()
        await message.answer_document(open(output_path, 'rb'))
        logger.info('User "%s" (%s) splitted file successfully',
                    message.from_user.id, message.from_user.username)
        await cmd_idle(message, state, headless=False)
    except Exception as e:
        await message.answer(errors_dict['func_failed'][locale])
        logger.error('User "%s" (%s) raised error %s while splitting',
                     message.from_user.id, message.from_user.username, e)
        await cmd_idle(message, state, headless=True)


def register_handlers_split(dp: Dispatcher):
    dp.register_message_handler(split_activate,
                                lambda message: message.text in txt_dict['split_pdf_text'].values(), state="*")
    dp.register_message_handler(handle_single_file, content_types=ContentType.DOCUMENT,
                                state=UserControlSplit.handle_file)
    dp.register_message_handler(setting_range, content_types=ContentType.TEXT, state=UserControlSplit.set_range)
    dp.register_message_handler(split_file, lambda message: message.text in split_text,
                                state=UserControlSplit.split_pages)
    dp.register_message_handler(handle_errors, lambda message: message.text not in split_text,
                                state=UserControlSplit.split_pages)
    dp.register_message_handler(handle_errors, content_types=ContentType.ANY,
                                state=UserControlSplit.split_pages)
    dp.register_message_handler(handle_errors, content_types=ContentType.ANY,
                                state=UserControlSplit.set_range)
    dp.register_message_handler(handle_errors, content_types=ContentType.ANY,
                                state=UserControlSplit.handle_file)
