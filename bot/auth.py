import shelve
from pathlib import Path
from telebot import types
from loguru import logger
from telebot.asyncio_filters import IsReplyFilter, TextContainsFilter
from telebot.async_telebot import AsyncTeleBot


async def send_auth(message: types.Message, bot: AsyncTeleBot):
    await bot.reply_to(message, '''
        不保存任何信息，但需要绑定Memos Open API用于推送。\n
        实现了文字、单张图文和多张图文的功能，日志功能有时间再说了。\n
        简单使用方法：https://blog.529213.xyz/article/memos-bot
        ''')

async def bind(message: types.Message, bot: AsyncTeleBot):
    logger.info(f'{message.chat.id}.db正在申请注册')
    markup = types.ForceReply(selective=False)
    await bot.send_message(message.chat.id, "请输入Memos Open Api.", reply_markup=markup)

async def unbind(message: types.Message, bot: AsyncTeleBot):
    if (Path(f'db/{message.chat.id}.db')).exists():
        Path(f'db/{message.chat.id}.db').unlink()
        await bot.reply_to(message, f'{message.chat.id}.db已经解绑，建议您去Memos后台重置api！')
        logger.info(f'{message.chat.id}.db已经解绑了，删除{message.chat.id}.db配置文件')
    else:
        logger.info(f'{message.chat.id}.db想要解绑，但未找到{message.chat.id}.db配置文件')
        await bot.reply_to(message, f'{message.chat.id}.db未找到您的绑定信息！')

async def save_info(message: types.Message, bot: AsyncTeleBot):
    if message.text.startswith("http"):
        if Path('db').exists():
            pass
        else:
            Path('db').mkdir()

        with shelve.open(f'db/{message.chat.id}.db', flag='c', protocol=None, writeback=True) as f:
            f['token'] = message.text
        await bot.reply_to(message, f'{message.chat.id}.db绑定{message.text}成功！')
        logger.info(f'{message.chat.id}.db已经注册')

def register_auth_handlers(bot: AsyncTeleBot):
    bot.add_custom_filter(TextContainsFilter())
    bot.add_custom_filter(IsReplyFilter())

    bot.register_message_handler(send_auth, commands=['start'], pass_bot=True)
    bot.register_message_handler(bind, commands=['bind'], pass_bot=True)
    bot.register_message_handler(unbind, commands=['unbind'], pass_bot=True)
    bot.register_message_handler(save_info, is_reply=True, text_contains='api/memo?openId', pass_bot=True)