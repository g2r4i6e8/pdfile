import os
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from unidecode import unidecode

from app.handlers.common import cmd_idle
from app.tools import tools
from app.tools.tools import check_invalid_format, count_pages, create_range
import logging

from app.modules.read_messages import txt_dict, errors_dict

logger = logging.getLogger(__name__)


class UserControlDelete(StatesGroup):
    handle_file = State()
    delete_pages = State()


async def delete_activate(message: types.Message, state: FSMContext):
    locale = str(message.from_user.locale) if str(message.from_user.locale) in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) chose to delete pages from PDF',
                message.from_user.id, message.from_user.username)
    await state.update_data(locale=locale)

    reply_keyboard = [[txt_dict['cancel_text'][locale]]]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=False)

    await message.answer(txt_dict['delete_input_text'][locale],
                         reply_markup=markup)

    await state.update_data(file_path=str, function='delete')

    await UserControlDelete.handle_file.set()


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

    pages = count_pages(file_path)
    await state.update_data(pages=pages)

    await message.answer(txt_dict['delete_queue_text'][locale].format(os.path.basename(file_path), pages))
    await message.answer(txt_dict['available_range_text'][locale],
                         parse_mode='MarkdownV2')

    await UserControlDelete.delete_pages.set()


async def delete_pages(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    locale = user_data['locale']
    pages = user_data['pages']

    if re.match('^\s*\d+[-\d+]*\s*(,\s*\d+[-\d+]*\s*)*\s*$', message.text):
        delete_range_string = message.text
        custom_range = create_range(message.text, pages)
        if any((i > pages for i in custom_range) or any(i <= 0 for i in custom_range)):
            logger.error('User "%s" (%s) defined unavailable range. Range: %s, number of pages: %s',
                         message.from_user.id, message.from_user.username, custom_range, pages)
            custom_range = [i for i in custom_range if (i <= pages) and (i > 0)]
            if len(custom_range) < 1:
                logger.error('User "%s" (%s) has range with zero length. Range: %s, number of pages: %s',
                             message.from_user.id, message.from_user.username, message.text, pages)
                await message.answer(errors_dict['unsupported_pattern'][locale])
                await message.answer(txt_dict['available_range_text'][locale],
                                     parse_mode='MarkdownV2')
                return None
            else:
                await message.answer(errors_dict['unsupported_range_exceed'][locale])
                delete_range = custom_range
        else:
            if len(custom_range) < 1:
                logger.error('User "%s" (%s) has range with zero length. Range: %s, number of pages: %s',
                             message.from_user.id, message.from_user.username, message.text, pages)
                await message.answer(errors_dict['unsupported_pattern'][locale])
                await message.answer(txt_dict['available_range_text'][locale],
                                     parse_mode='MarkdownV2')
            delete_range = custom_range

    else:
        logger.error('User "%s" (%s) raised unavailable pattern error. Message: %s',
                     message.from_user.id, message.from_user.username, message.text)
        await message.answer(errors_dict['unsupported_pattern'][locale])
        await message.answer(txt_dict['available_range_text'][locale],
                             parse_mode='MarkdownV2')
        return None

    file = user_data['file_path']
    output_folder: str = os.path.join('temp', str(message.from_user.id))

    try:
        output_path = tools.delete(file, delete_range_string, delete_range, output_folder)
        await types.ChatActions.upload_document()
        await message.answer_document(open(output_path, 'rb'))
        logger.info('User "%s" (%s) deleted pages from file successfully',
                    message.from_user.id, message.from_user.username)
        await cmd_idle(message, state, headless=False)
    except Exception as e:
        await message.answer(errors_dict['func_failed'][locale])
        logger.error('User "%s" (%s) raised error %s while deleting pages',
                     message.from_user.id, message.from_user.username, e)
        await cmd_idle(message, state, headless=True)


def register_handlers_delete(dp: Dispatcher):
    dp.register_message_handler(delete_activate,
                                lambda message: message.text in txt_dict['delete_pages_text'].values(), state="*")
    dp.register_message_handler(handle_single_file, content_types=ContentType.DOCUMENT,
                                state=UserControlDelete.handle_file)
    dp.register_message_handler(delete_pages, content_types=ContentType.TEXT, state=UserControlDelete.delete_pages)
    dp.register_message_handler(handle_errors, content_types=ContentType.ANY,
                                state=UserControlDelete.handle_file)
    dp.register_message_handler(handle_errors, content_types=ContentType.ANY,
                                state=UserControlDelete.delete_pages)
