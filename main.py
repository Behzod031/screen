# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import Memory
from config import API_TOKEN
from handlers import register_handlers

async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    register_handlers(dp, bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
