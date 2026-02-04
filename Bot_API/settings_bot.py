from os import getenv
from dotenv import load_dotenv

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from Bot_API.handlers.cmd_handlers import router_commands
from Bot_API.handlers.filters_handlers import router_filters
from Bot_API.handlers.callback_handlers import router_callback
from admin.handlers_admin import admin_router


from loguru import logger

from DB.requests.requests import init_db

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage()) # заменить на Redis для продакшена, это работа с кэшем


#####################################################
# Run the bot
async def start_bot() -> None:
    try:
        await init_db()
        dp.include_routers(router_commands, router_filters, router_callback, admin_router)
        await dp.start_polling(bot)
    except Exception as ex:
        logger.exception(f'Disconnect {ex}')

#####################################################
