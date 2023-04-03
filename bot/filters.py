from pathlib import Path
from telebot.asyncio_filters import SimpleCustomFilter
from telebot.async_telebot import types

class ExistDb(SimpleCustomFilter):
    key = 'exist_db'
    @staticmethod
    async def check(message: types.Message):
       return Path(f'db/{message.chat.id}.db').exists()

