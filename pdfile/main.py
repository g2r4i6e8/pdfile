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
from dotenv import load_dotenv
import re
from datetime import datetime
import json
import shutil

"""
Universal Telegram Bot for working with PDF files.
"""

# Enable logging
logfile = '../logs/{}.log'.format(datetime.now().strftime("%Y-%m-%dT%H"))
logging.basicConfig(filename=logfile, filemode="w",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

with open('../resources/txt_dict.json', 'r', encoding="utf8") as outfile:
    txt_dict = json.load(outfile)
            
    
def start(update, context):
    """Send a message when the command /start is issued."""
    logger.info('User "%s" with language code "%s" started the bot instance',
                update.effective_user.id, update.effective_user.language_code)
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
    
def idle(update, context, locale):
    logger.info('User "%s" is idle', update.effective_user.id)
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    reply_keyboard = [[txt_dict['compress_pdf_text'][locale],
                      txt_dict['merge_pdf_text'][locale],
                      txt_dict['split_pdf_text'][locale]],
                       [txt_dict['delete_pages_text'][locale]],
                       [txt_dict['ppt_to_pdf_text'][locale],
                        txt_dict['img_to_pdf_text'][locale],
                        txt_dict['doc_to_pdf_text'][locale]],
                       [txt_dict['donate_text'][locale]]]   
    
    # global markup
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    
    update.message.reply_text(txt_dict['idle_msg'][locale],
                              parse_mode='MarkdownV2',
                              reply_markup=markup)

def compress_cmd(update, context, locale):
    logger.info('User "%s" chose to compress PDF', update.effective_user.id)
    reply_keyboard = [[txt_dict['compress_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['compress_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []
    
def merge_cmd(update, context, locale):
    logger.info('User "%s" chose to merge PDF', update.effective_user.id)
    reply_keyboard = [[txt_dict['merge_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    
    update.message.reply_text(txt_dict['merge_input_text'][locale], 
                              reply_markup=markup)
    
    context.user_data['list_of_files'] = []

def split_cmd(update, context, locale):
    logger.info('User "%s" chose to split PDF', update.effective_user.id)
    update.message.reply_text(txt_dict['split_input_text'][locale])
    update.message.reply_text(txt_dict['available_range_text'][locale],
                              parse_mode='MarkdownV2')
    
    context.user_data['file_path'] = ''
    context.user_data['function'] = 'split'
    
def split_cmd_2(update, context, locale):
    reply_keyboard = [[txt_dict['split_one_text'][locale],
                       txt_dict['split_many_text'][locale],
                      txt_dict['cancel_text'][locale]]]
    
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    
    context.user_data['split_range'] = update.message.text
    update.message.reply_text(txt_dict['split_call_text'][locale],
                              reply_markup=markup)

def delete_cmd(update, context, locale):
    logger.info('User "%s" chose to delete pages', update.effective_user.id)
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
    logger.info('User "%s" chose to convert images to pdf', update.effective_user.id)
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
    logger.info('User "%s" chose to convert doc to pdf', update.effective_user.id)
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
    logger.info('User "%s" chose to convert ppt to pdf', update.effective_user.id)
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
    logger.info('User "%s" opened donate page', update.effective_user.id)
    keyboard = [[
        InlineKeyboardButton(txt_dict['donate_url_text'][locale],
                             url = 'https://yoomoney.ru/to/4100117228897097')
    ]]
    
    update.message.bot.send_photo(
    chat_id=update.message.chat.id,
    photo=open('../resources/myself.jpg','rb'),
    caption=txt_dict['donate_desc_text'][locale],
    reply_markup=InlineKeyboardMarkup(keyboard)
)
    
def file_handler(update, context):
    userid = update.message.from_user.id
    file = update.message.document.file_id        
    obj = context.bot.get_file(file)
    file_url = obj['file_path']
    data = requests.get(file_url).content
    output_folder = os.path.join('temp', str(userid))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, file_url.split('/')[-1])
    with open(file_path, 'wb') as file:
        file.write(data)
    if 'list_of_files' in context.user_data:
        context.user_data['list_of_files'].append(file_path)
    elif 'file_path' in context.user_data:
        context.user_data['file_path'] = file_path

def echo(update, context):
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    userid = update.message.from_user.id
    output_folder = os.path.join('temp', str(userid))
    if update.message.text == txt_dict['compress_pdf_text'][locale]:
        compress_cmd(update,context, locale)
    elif update.message.text == txt_dict['compress_text'][locale]:
        output_path = tools.compress(context.user_data['list_of_files'], 
                                     output_folder)
        update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
        shutil.rmtree(output_folder)
        del context.user_data['list_of_files']
        idle(update, context, locale)
    elif update.message.text == txt_dict['merge_pdf_text'][locale]:
        merge_cmd(update,context, locale)
    elif update.message.text == txt_dict['merge_text'][locale]:
        output_path = tools.merge(context.user_data['list_of_files'], 
                                  output_folder)
        update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
        shutil.rmtree(output_folder)
        del context.user_data['list_of_files']
        idle(update, context, locale)
    elif update.message.text == txt_dict['split_pdf_text'][locale]:
        split_cmd(update, context, locale)
    elif update.message.text == txt_dict['split_one_text'][locale]:
        output_path = tools.split(context.user_data['file_path'],
                                  context.user_data['split_range'],
                                  output_folder,
                                  separate_pages = False)
        update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
        shutil.rmtree(output_folder)
        del context.user_data['file_path']
        del context.user_data['function']
        idle(update, context, locale)
    elif update.message.text == txt_dict['split_many_text'][locale]:
        output_path = tools.split(context.user_data['file_path'],
                                  context.user_data['split_range'],
                                  output_folder,
                                  separate_pages = True)
        update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
        shutil.rmtree(output_folder)
        del context.user_data['file_path']
        del context.user_data['function']
        idle(update, context, locale)
    elif update.message.text == txt_dict['delete_pages_text'][locale]:
        delete_cmd(update, context, locale)
    elif update.message.text == txt_dict['delete_text'][locale]:
        output_path = tools.delete(context.user_data['list_of_files'],
                                   context.user_data['split_range'],
                                   output_folder)
        update.message.bot.send_document(update.message.chat.id,open(output_path,'rb'))
        shutil.rmtree(output_folder)
        del context.user_data['file_path']
        del context.user_data['function']
        idle(update, context, locale)
    elif update.message.text == txt_dict['ppt_to_pdf_text'][locale]:
        ppt2pdf(update, context, locale)
    elif update.message.text == txt_dict['img_to_pdf_text'][locale]:
        img2pdf(update, context, locale)
    elif update.message.text == txt_dict['doc_to_pdf_text'][locale]:
        doc2pdf(update, context, locale)
    elif update.message.text == txt_dict['convert_text'][locale]:
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
        shutil.rmtree(output_folder)
        del context.user_data['list_of_files']
        del context.user_data['function']
        idle(update, context, locale)
    elif re.match('^\s*\d+[-\d+]*\s*(,\s*\d+[-\d+]*\s*)*\s*$', update.message.text):
        if context.user_data['function'] == 'split':
            split_cmd_2(update, context, locale)
        elif context.user_data['function'] == 'delete':
            delete_cmd_2(update, context, locale)
    elif update.message.text == txt_dict['cancel_text'][locale]:
        idle(update, context, locale)
    elif update.message.text == txt_dict['donate_text'][locale]:
        donate(update, context, locale)
    else:
        update.message.reply_text(txt_dict['unknown_text'][locale])
        
def error(update, context):
    """Log Errors caused by Updates."""
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text(txt_dict['error_text'][locale])
    
def help_command(update, context):
    """Send a message when the command /help is issued."""
    locale = update.effective_user.language_code if update.effective_user.language_code in ['en', 'ru'] else 'en'
    update.message.reply_text(txt_dict['help_text'][locale])

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    load_dotenv('../credentials.env')
    updater = Updater(os.environ.get('secretToken'), use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(MessageHandler(Filters.document, file_handler))
    

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()