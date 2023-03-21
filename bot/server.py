import os
import asyncio

from pathlib import Path
from aiohttp import web
from telebot.async_telebot import AsyncTeleBot, types
from dotenv import load_dotenv
from loguru import logger
from bot.auth import register_auth_handlers
from bot.memo import register_memo_handlers


load_dotenv(Path('../.env'))
bot = AsyncTeleBot(os.getenv('API_TOKEN'))

register_auth_handlers(bot)
register_memo_handlers(bot)
#Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = types.Update.de_json(request_body_dict)
        asyncio.ensure_future(bot.process_new_updates([update]))
        return web.Response()
    else:
        return web.Response(status=403)


async def shutdown(app):
    await bot.remove_webhook()
    await bot.close_session()

async def setup():
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    await bot.remove_webhook()
    # Set webhook

    # await bot.set_webhook(url=config['WEBHOOK_URL_BASE'] + config['WEBHOOK_URL_PATH'])
    host = os.getenv('WEBHOOK_HOST')
    token = os.getenv('API_TOKEN')
    url = f'{host}/{token}/'
    await bot.set_webhook(url=url)

    app = web.Application()
    app.router.add_post('/{token}/', handle)
    app.on_cleanup.append(shutdown)
    return app

async def main():
    mode = os.getenv('MODE', default='polling')
    if mode == 'webhook':
        logger.debug(f'webhook模式')
        # Start aiohttp server
        web.run_app(
            setup(),
            host=os.getenv('WEBHOOK_LISTEN'),
            port=os.getenv('WEBHOOK_PORT')
        )
    elif mode == 'polling':
        await bot.remove_webhook()
        logger.debug(f'polling模式')
        await bot.infinity_polling()
    else:
        pass


if __name__ == '__main__':
    asyncio.run(main())
