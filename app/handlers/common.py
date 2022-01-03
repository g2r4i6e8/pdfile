import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from app.modules.clean_output import cleaner
from app.modules.read_messages import txt_dict

import logging

logger = logging.getLogger(__name__)


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await cleaner(os.path.join('temp', str(message.from_user.id)))
    locale = message.from_user.locale if message.from_user.locale in ['en', 'ru'] else 'en'
    await state.update_data(locale=locale)
    logger.info('User "%s" (%s) with language code "%s" started the bot instance',
                message.from_user.id, message.from_user.username, locale)

    reply_keyboard = [[txt_dict['compress_pdf_text'][locale],
                       txt_dict['merge_pdf_text'][locale],
                       txt_dict['split_pdf_text'][locale]],
                      [txt_dict['delete_pages_text'][locale]],
                      [txt_dict['ppt_to_pdf_text'][locale],
                       txt_dict['img_to_pdf_text'][locale],
                       txt_dict['doc_to_pdf_text'][locale]]]

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)

    await message.answer(
        txt_dict['start_msg'][locale],
        reply_markup=markup,
        parse_mode='MarkdownV2'
    )


async def cmd_idle(message: types.Message, state: FSMContext, headless=True):
    await state.finish()
    await cleaner(os.path.join('temp', str(message.from_user.id)))
    locale = message.from_user.locale if message.from_user.locale in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) is idle',
                message.from_user.id, message.from_user.username)

    reply_keyboard = [[txt_dict['compress_pdf_text'][locale],
                       txt_dict['merge_pdf_text'][locale],
                       txt_dict['split_pdf_text'][locale]],
                      [txt_dict['delete_pages_text'][locale]],
                      [txt_dict['ppt_to_pdf_text'][locale],
                       txt_dict['img_to_pdf_text'][locale],
                       txt_dict['doc_to_pdf_text'][locale]]]

    if not headless: reply_keyboard.append([txt_dict['donate_text'][locale]])

    markup = types.ReplyKeyboardMarkup(reply_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)

    idle_txt = txt_dict['idle_msg'][locale]
    if headless: idle_txt = idle_txt.split('\n\n')[1]

    await message.answer(
        idle_txt,
        reply_markup=markup,
        parse_mode='MarkdownV2'
    )


async def cmd_donate(message: types.Message, state: FSMContext):
    await state.finish()
    locale = message.from_user.locale if message.from_user.locale in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) opened donate page',
                message.from_user.id, message.from_user.username)

    inline_kb = types.InlineKeyboardMarkup()
    inline_kb.row(types.InlineKeyboardButton(txt_dict['donate_url_text'][locale],
                                             url='https://yoomoney.ru/to/4100117228897097'))

    await message.answer_photo(
        photo=open(os.path.join('resources', 'myself.jpg'), 'rb'),
        caption=txt_dict['donate_desc_text'][locale],
        reply_markup=inline_kb
    )

    await cmd_idle(message, state, headless=True)


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    locale = message.from_user.locale if message.from_user.locale in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) entered unknown text: %s',
                message.from_user.id, message.from_user.username, message.text)

    await message.answer(txt_dict['help_text'][locale])


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_idle, commands="idle", state="*")
    dp.register_message_handler(cmd_idle, lambda message: message.text in txt_dict['cancel_text'].values(), state="*")
    dp.register_message_handler(cmd_donate, commands="donate", state="*")
    dp.register_message_handler(cmd_donate, lambda message: message.text in txt_dict['donate_text'].values())
    dp.register_message_handler(cmd_help, commands="help", state="*")
