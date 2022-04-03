import asyncio
import os

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


class UserControlMerge(StatesGroup):
    merge_files = State()


async def merge_activate(message: types.Message, state: FSMContext):
    global added_files, lst
    added_files = 0
    lst = []
    locale = str(message.from_user.locale) if str(message.from_user.locale) in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) chose to merge PDF',
                message.from_user.id, message.from_user.username)
    await state.update_data(locale=locale)

    reply_keyboard = [[txt_dict['merge_text'][locale],
                       txt_dict['cancel_text'][locale]]]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=False)

    await message.answer(txt_dict['merge_input_text'][locale],
                         reply_markup=markup)

    await state.update_data(list_of_files=list(), function='merge')

    await UserControlMerge.merge_files.set()


async def handle_errors(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    locale = user_data['locale']
    logger.info('User "%s" (%s) raised error',
                message.from_user.id, message.from_user.username)

    await message.answer(txt_dict['unknown_text'][locale])


async def handle_files(message: types.Message, state: FSMContext):
    await types.ChatActions.typing()
    user_data = await state.get_data()
    locale = user_data['locale']
    function = user_data['function']

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

    user_data = await state.get_data()
    list_of_files = user_data['list_of_files']
    list_of_files.append(file_path)
    await state.update_data(list_of_files=list_of_files)

    global added_files
    await asyncio.sleep(1)

    # this crutch helps with mutiple file processing:
    # https://stackoverflow.com/questions/70420866/handle-files-in-media-group-using-aiogram
    handler_tasks = [task for task in asyncio.all_tasks() if 'Handler' in str(task.get_coro())]
    lst.append(len(handler_tasks))
    max_value = max(lst)
    if len(list_of_files) == max_value + added_files:
        printed_list = ['{}. {}'.format(n + 1, os.path.basename(f)) for n, f in enumerate(list_of_files)]
        await message.answer(txt_dict['merge_queue_text'][locale].format('\n'.join(printed_list)))
        lst.clear()
        added_files += max_value

async def merge_files(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    locale = user_data['locale']
    files = user_data['list_of_files']
    output_folder: str = os.path.join('temp', str(message.from_user.id))

    if len(files) > 1:
        try:
            output_path = tools.merge(files, output_folder)
            await types.ChatActions.upload_document()
            await message.answer_document(open(output_path, 'rb'))
            logger.info('User "%s" (%s) merged file(s) successfully',
                        message.from_user.id, message.from_user.username)
            await cmd_idle(message, state, headless=False)
        except Exception as e:
            await message.answer(errors_dict['func_failed'][locale])
            logger.error('User "%s" (%s) raised error %s while merging',
                         message.from_user.id, message.from_user.username, e)
            await cmd_idle(message, state, headless=True)
    elif len(files) == 1:
        await message.answer(errors_dict['one_file'][locale])
        return None
    else:
        await message.answer(errors_dict['no_files'][locale])
        return None

def register_handlers_merge(dp: Dispatcher):
    dp.register_message_handler(merge_activate,
                                lambda message: message.text in txt_dict['merge_pdf_text'].values(), state="*")
    dp.register_message_handler(handle_files, content_types=ContentType.DOCUMENT, state=UserControlMerge.merge_files)
    dp.register_message_handler(merge_files, lambda message: message.text in txt_dict['merge_text'].values(),
                                state=UserControlMerge.merge_files)
    dp.register_message_handler(handle_errors, lambda message: message.text not in txt_dict['merge_text'].values(),
                                state=UserControlMerge.merge_files)
    dp.register_message_handler(handle_errors, content_types=ContentType.ANY,
                                state=UserControlMerge.merge_files)
