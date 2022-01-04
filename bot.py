import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime

from app.config_reader import load_config
from app.handlers.abracadabra import register_handlers_abracadabra
from app.handlers.common import register_handlers_common
from app.handlers.compress import register_handlers_compress
from app.handlers.convert import register_handlers_convert
from app.handlers.delete import register_handlers_delete
from app.handlers.merge import register_handlers_merge
from app.handlers.split import register_handlers_split


async def main():
    # setting up logging
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.makedirs('logs', exist_ok=True)
    logfile = 'logs/{}.log'.format(datetime.now().strftime("%Y-%m-%dT%H"))
    logging.basicConfig(
        # stream=sys.stdout,
        filename=logfile,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting bot")

    # parsing config
    config = load_config(os.path.join('config', 'bot.ini'))
    # ininitalizing bot
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # registering handlers
    register_handlers_common(dp)
    # register_handlers_abracadabra(dp, config.tg_bot.admin_id)
    register_handlers_compress(dp)
    register_handlers_merge(dp)
    register_handlers_split(dp)
    register_handlers_delete(dp)
    register_handlers_convert(dp)

    # start polling
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
