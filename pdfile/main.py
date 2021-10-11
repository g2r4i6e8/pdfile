#!/usr/bin/env python
"""
Created on Wed Sep 29 12:21:01 2021

@author: kolomatskiy
"""

import tools
import os
import requests
import logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
from datetime import datetime
import json
import shutil
import credentials
from unidecode import unidecode

"""
Universal Telegram Bot for working with PDF files.
"""

#Setting up cwd
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Enable logging
os.makedirs('../logs', exist_ok=True)
logfile = '../logs/{}.log'.format(datetime.now().strftime("%Y-%m-%dT%H"))
logging.basicConfig(filename=logfile, filemode="w",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

with open('txt_dict.json', 'r', encoding="utf8") as file:
    txt_dict = json.load(file)
    
with open('errors_dict.json', 'r', encoding="utf8") as file:
    errors_dict = json.load(file)
    
def start(update, context):
    """Send a message when the command /start is issued."""
    logger.info('User "%s" (%s) with language code "%s" started the bot instance',
                update.effective_user.id, update.effective_user.username, update.effective_user.language_code)
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    reply_keyboard = [[txt_dict['compress_pdf_text'][locale],
                      txt_dict['merge_pdf_text'][locale],
                      txt_dict['split_pdf_text'][locale]],
                       [txt_dict['delete_pages_text'][locale]],
                       [txt_dict['ppt_to_pdf_text'][locale],
                        txt_dict['img_to_pdf_text'][locale],
                        txt_dict['doc_to_pdf_text'][locale]]]
    
    # global markup
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    
    update.message.reply_text(txt_dict['start_msg'][locale],
                              parse_mode='MarkdownV2',
                              reply_markup=markup)
        
def idle(update, context, headless=True):
    logger.info('User "%s" (%s) is idle',
                update.effective_user.id, update.effective_user.username)
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    reply_keyboard = [[txt_dict['compress_pdf_text'][locale],
                      txt_dict['merge_pdf_text'][locale],
                      txt_dict['split_pdf_text'][locale]],
                       [txt_dict['delete_pages_text'][locale]],
                       [txt_dict['ppt_to_pdf_text'][locale],
                        txt_dict['img_to_pdf_text'][locale],
                        txt_dict['doc_to_pdf_text'][locale]]]   
    
    if not headless: reply_keyboard.append([txt_dict['donate_text'][locale]])
    
    # global markup
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    idle_txt = txt_dict['idle_msg'][locale]
    
    if headless: idle_txt = idle_txt.split('\n\n')[1]
    
    update.message.reply_text(idle_txt,
                              parse_mode='MarkdownV2',
                              reply_markup=markup)

def compress_cmd(update, context, locale):
    logger.info('User "%s" (%s) chose to compress PDF',
                update.effective_user.id, update.effective_user.username)
    reply_keyboard = [[txt_dict['compress_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['compress_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []
    context.user_data['function'] = 'compress'
    
def merge_cmd(update, context, locale):
    logger.info('User "%s" (%s) chose to merge PDF',
                update.effective_user.id, update.effective_user.username)
    reply_keyboard = [[txt_dict['merge_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['merge_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []
    context.user_data['function'] = 'merge'

def split_cmd(update, context, locale):
    logger.info('User "%s" (%s) chose to split PDF',
                update.effective_user.id, update.effective_user.username)
    update.message.reply_text(txt_dict['split_input_text'][locale])
    update.message.reply_text(txt_dict['available_range_text'][locale],
                              parse_mode='MarkdownV2')
    
    context.user_data['file_path'] = ''
    context.user_data['function'] = 'split'
    
def split_cmd_2(update, context, locale):
    reply_keyboard = [[txt_dict['split_one_text'][locale]],
                       [txt_dict['split_many_text'][locale]],
                      [txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    
    context.user_data['split_range'] = update.message.text
    update.message.reply_text(txt_dict['split_call_text'][locale],
                              reply_markup=markup)

def delete_cmd(update, context, locale):
    logger.info('User "%s" (%s) chose to delete pages',
                update.effective_user.id, update.effective_user.username)
    update.message.reply_text(txt_dict['delete_input_text'][locale])
    update.message.reply_text(txt_dict['available_range_text'][locale],
                              parse_mode='MarkdownV2')
    
    context.user_data['file_path'] = ''
    context.user_data['function'] = 'delete'
    
def delete_cmd_2(update, context, locale):
    reply_keyboard = [[txt_dict['delete_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    
    context.user_data['split_range'] = update.message.text
    update.message.reply_text(txt_dict['delete_call_text'][locale],
                              reply_markup=markup)
        
def img2pdf(update, context, locale):
    logger.info('User "%s" (%s) chose to convert images to pdf',
                update.effective_user.id, update.effective_user.username)
    reply_keyboard = [[txt_dict['convert_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['convert_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []
    context.user_data['function'] = 'img2pdf'
    
def doc2pdf(update, context, locale):
    logger.info('User "%s" (%s) chose to convert doc to pdf',
                update.effective_user.id, update.effective_user.username)
    reply_keyboard = [[txt_dict['convert_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['convert_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []
    context.user_data['function'] = 'doc2pdf'
    
def ppt2pdf(update,context, locale):
    logger.info('User "%s" (%s) chose to convert ppt to pdf',
                update.effective_user.id, update.effective_user.username)
    reply_keyboard = [[txt_dict['convert_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['convert_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []
    context.user_data['function'] = 'ppt2pdf'

def donate(update,context, locale):
    logger.info('User "%s" (%s) opened donate page',
                update.effective_user.id, update.effective_user.username)
    keyboard = [[
        InlineKeyboardButton(txt_dict['donate_url_text'][locale],
                             url = credentials.donateLink)
    ]]
    
    update.message.bot.send_photo(
    chat_id=update.message.chat.id,
    photo=open('../resources/myself.jpg','rb'),
    caption=txt_dict['donate_desc_text'][locale],
    reply_markup=InlineKeyboardMarkup(keyboard)
)
    
def check_invalid_format(file_name, function):
    format_functions = {'compress': ['pdf'], 'merge': ['pdf'], 'split': ['pdf'],
                        'delete': ['pdf'], 'ppt2pdf': ['ppt', 'pptx', 'odp'],
                        'img2pdf': ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'WebP', 'bmp'],
                        'doc2pdf': ['odt', 'doc', 'docx']}
    if file_name.split('.')[-1].lower() not in format_functions[function]:
        return True, format_functions[function]
    else:
        return False, format_functions[function]
    
    
def file_handler(update, context):
    userid = update.message.from_user.id
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    try:
        file = update.message.document
        file_name = file['file_name']
    except:
        file = update.message.photo[-1]
        file_name = context.bot.get_file(file)['file_path'].split('/')[-1]
    file_name = unidecode(file_name)
    file_size = file['file_size']
    logger.info('User "%s" (%s) uploaded a file %s with file size %d bytes',
                update.effective_user.id, update.effective_user.username, file_name, file_size)
    if file_size >= 20971520:
        update.message.reply_text(errors_dict['big_file'][locale])
        logger.error('User "%s" (%s) raised big file error',
                     update.effective_user.id, update.effective_user.username)
        return None
    invalid_format, formats = check_invalid_format(file_name, context.user_data['function'])
    if invalid_format:
        update.message.reply_text(file_name + errors_dict['unsupported_format'][locale] + ', '.join(formats))
        logger.error('User "%s" (%s) raised unsupported file format error',
                     update.effective_user.id, update.effective_user.username)
        return None
    obj = context.bot.get_file(file)
    file_url = obj['file_path']
    data = requests.get(file_url).content
    output_folder = os.path.join('temp', str(userid))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, file_name)
    with open(file_path, 'wb') as file:
        file.write(data)
    if 'list_of_files' in context.user_data:
        context.user_data['list_of_files'].append(file_path)
    elif 'file_path' in context.user_data:
        context.user_data['file_path'] = file_path
    
def cleaner(output_folder, context):
    try:
        shutil.rmtree(output_folder)
    except:
        pass
    try:
        context.user_data.clear()
    except: 
        pass

def control(update, context):
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    userid = update.message.from_user.id
    output_folder = os.path.join('temp', str(userid))
    if update.message.text in txt_dict['compress_pdf_text'].values():
        compress_cmd(update,context, locale)
    elif update.message.text in txt_dict['compress_text'].values():
        if len(context.user_data['list_of_files']) >= 1:
            try:
                output_path = tools.compress(context.user_data['list_of_files'], 
                                         output_folder)
                update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
                logger.info('User "%s" (%s) compressed file(s) successfully',
                            update.effective_user.id, update.effective_user.username)
                idle(update, context, headless=False)
            except Exception as e:
                update.message.reply_text(errors_dict['func_failed'][locale])
                logger.error('User "%s" (%s) raised error %s while compressing',
                             update.effective_user.id, update.effective_user.username, e)
                idle(update, context, headless=True)
        else:
            update.message.reply_text(errors_dict['no_files'][locale])
            idle(update, context, headless=True)
        cleaner(output_folder, context)
    elif update.message.text in txt_dict['merge_pdf_text'].values():
        merge_cmd(update,context, locale)
    elif update.message.text in txt_dict['merge_text'].values():
        if len(context.user_data['list_of_files']) >= 1:
            try:
                output_path = tools.merge(context.user_data['list_of_files'], 
                                          output_folder)
                update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
                logger.info('User "%s" (%s) merged files successfully',
                            update.effective_user.id, update.effective_user.username)
                idle(update, context, headless=False)
            except Exception as e:
                update.message.reply_text(errors_dict['func_failed'][locale])
                logger.error('User "%s" (%s) raised error %s while merging',
                             update.effective_user.id, update.effective_user.username, e)
                idle(update, context, headless=True)
        else:
            update.message.reply_text(errors_dict['no_files'][locale])
            idle(update, context, headless=True)
        cleaner(output_folder, context)
    elif update.message.text in txt_dict['split_pdf_text'].values():
        split_cmd(update, context, locale)
    elif update.message.text in txt_dict['split_one_text'].values():
        if context.user_data['file_path'] != '':
            try:
                output_path = tools.split(context.user_data['file_path'],
                                          context.user_data['split_range'],
                                          output_folder,
                                          separate_pages = False)
                update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
                logger.info('User "%s" (%s) splitted file successfully',
                            update.effective_user.id, update.effective_user.username)
                idle(update, context, headless=False)
            except Exception as e:
                update.message.reply_text(errors_dict['func_failed'][locale])
                logger.error('User "%s" (%s) raised error %s while splitting',
                             update.effective_user.id, update.effective_user.username, e)
                idle(update, context, headless=True)
        cleaner(output_folder, context)
    elif update.message.text in txt_dict['split_many_text'].values():
        if context.user_data['file_path'] != '':
            try:
                output_path = tools.split(context.user_data['file_path'],
                                          context.user_data['split_range'],
                                          output_folder,
                                          separate_pages = True)
                update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
                logger.info('User "%s" (%s) splitted file successfully',
                            update.effective_user.id, update.effective_user.username)
                idle(update, context, headless=False)
            except Exception as e:
                update.message.reply_text(errors_dict['func_failed'][locale])
                logger.error('User "%s" (%s) raised error %s while splitting',
                             update.effective_user.id, update.effective_user.username, e)
                idle(update, context, headless=True)
        cleaner(output_folder, context)
    elif update.message.text in txt_dict['delete_pages_text'].values():
        delete_cmd(update, context, locale)
    elif update.message.text in txt_dict['delete_text'].values():
        if context.user_data['file_path'] != '':
            try:
                output_path = tools.delete(context.user_data['file_path'],
                                           context.user_data['split_range'],
                                           output_folder)
                update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
                logger.info('User "%s" (%s) deleted pages from file successfully',
                            update.effective_user.id, update.effective_user.username)
                idle(update, context, headless=False)
            except Exception as e:
                update.message.reply_text(errors_dict['func_failed'][locale])
                logger.error('User "%s" (%s) raised error %s while deleting',
                             update.effective_user.id, update.effective_user.username, e)
                idle(update, context, headless=True)
        cleaner(output_folder, context)
    elif update.message.text in txt_dict['ppt_to_pdf_text'].values():
        ppt2pdf(update, context, locale)
    elif update.message.text in txt_dict['img_to_pdf_text'].values():
        img2pdf(update, context, locale)
    elif update.message.text in txt_dict['doc_to_pdf_text'].values():
        doc2pdf(update, context, locale)
    elif update.message.text in txt_dict['convert_text'].values():
        if len(context.user_data['list_of_files']) >= 1:
            try:
                if context.user_data['function'] == 'img2pdf':
                    output_path = tools.img2pdf(context.user_data['list_of_files'],
                                               output_folder)
                elif context.user_data['function'] == 'doc2pdf':
                    output_path = tools.doc2pdf(context.user_data['list_of_files'],
                                               output_folder)
                elif context.user_data['function'] == 'ppt2pdf':
                    output_path = tools.ppt2pdf(context.user_data['list_of_files'],
                                               output_folder)
                update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
                logger.info('User "%s" (%s) converted file(s) successfully',
                            update.effective_user.id, update.effective_user.username)
                idle(update, context, headless=False)
            except Exception as e:
                update.message.reply_text(errors_dict['func_failed'][locale])
                logger.error('User "%s" (%s) raised error %s while converting %s',
                             update.effective_user.id, update.effective_user.username,
                             e, context.user_data['function'])
                idle(update, context, headless=True)
        else:
            update.message.reply_text(errors_dict['no_files'][locale])
            idle(update, context, headless=True)
        cleaner(output_folder, context)
    elif re.match('^\s*\d+[-\d+]*\s*(,\s*\d+[-\d+]*\s*)*\s*$', update.message.text):
        if context.user_data['file_path'] != '':
            if context.user_data['function'] == 'split':
                split_cmd_2(update, context, locale)
            elif context.user_data['function'] == 'delete':
                delete_cmd_2(update, context, locale)
        else:
            update.message.reply_text(errors_dict['no_files'][locale])
            idle(update, context, headless=True)
            cleaner(output_folder, context)
    elif update.message.text in txt_dict['cancel_text'].values():
        cleaner(output_folder, context)
        logger.info('User "%s" (%s) canceled operation',
                    update.effective_user.id, update.effective_user.username)
        idle(update, context, headless=True)
    elif update.message.text in txt_dict['donate_text'].values():
        donate(update, context, locale)
        idle(update, context, headless=True)
    else:
        logger.info('User "%s" (%s) entered unknown text: %s',
                    update.effective_user.id, update.effective_user.username,
                    update.message.text)
        update.message.reply_text(txt_dict['unknown_text'][locale])
            
def help_command(update, context):
    """Send a message when the command /help is issued."""
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    logger.info('User "%s" (%s) asked for help',
                update.effective_user.id, update.effective_user.username)
    update.message.reply_text(txt_dict['help_text'][locale])

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(credentials.secretToken, use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('idle', idle))
    dispatcher.add_handler(MessageHandler(Filters.document, file_handler))
    dispatcher.add_handler(MessageHandler(Filters.photo, file_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, control))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()