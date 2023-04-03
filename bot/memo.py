import shelve
import os

from telebot import types
from loguru import logger
from telebot.async_telebot import AsyncTeleBot
from urllib.parse import urlparse
from memos.memosapi import Memo, Tag, Resource
from bot.parse import parse_text, parse_html
from bot.filters import ExistDb
from telebot.asyncio_filters import IsReplyFilter

media_ids = {}

async def send_memo_by_words(message: types.Message, bot: AsyncTeleBot):
    with shelve.open(f'../db/{message.chat.id}.db', flag='c', protocol=None, writeback=True) as f:
        if f['token']:
            url = f['token']
            o = urlparse(str(url))
            domain = f'{o.scheme}://{o.netloc}/m/'

            try:
                memo = Memo(url)

                # text, tags, res_ids, visibility, _ = parse_text(message.text)
                text, tags, res_ids, visibility, status = parse_html(message.text, message.html_text, message.entities)
                logger.debug(f'\nMemo为: {text}\n Tags为: {tags}\n 公开：{visibility}\n 资源ID：{res_ids}\n 状态为：{status}')
                memo_id = await memo.send_memo(text=text, visibility=visibility, res_ids=res_ids)
                memo_url = f'{domain}{memo_id}'
                f[str(message.message_id)] = memo_id

                logger.info(f'{message.chat.id}发送了成功发送了1条Memos, MemoID为{memo_id}')

                memo_tag = Tag(url)
                for tag in tags:
                    await memo_tag.create_tag(tag)
                    logger.info(f'{message.chat.id}发送了成功创建1个TAG, TAG为{tag}')
                await bot.reply_to(message, memo_url)
            except Exception as e:
                logger.error(f'{message.chat.id}创建Memo出错，{e}')
                await bot.reply_to(message, f"出错了，重来吧！{e}")
        else:
            logger.debug(f'{message.chat.id}没有找到token信息')
            await bot.reply_to(message, f'{message.chat.id}未找到您的绑定信息！')

async def send_memo_by_words_and_resource(message: types.Message, bot: AsyncTeleBot):
    with shelve.open(f'../db/{message.chat.id}.db', flag='c', protocol=None, writeback=True) as f:
        if f['token']:
            url = f['token']
            o = urlparse(str(url))
            domain = f'{o.scheme}://{o.netloc}/m/'

            try:
                memo = Memo(url)
                # text, tags, visibility, _ = parse_text(message.text)
                text, tags, _, visibility, _ = parse_html(message.text, message.html_text, message.entities)
                if message.reply_to_message.media_group_id:
                    res_ids = media_ids[message.reply_to_message.media_group_id]
                else:
                    res_ids = media_ids[message.reply_to_message.message_id]
                logger.debug(f'\nMemo为: {text}\n Tags为: {tags}\n 公开：{visibility}\n 资源ID：{res_ids}')

                memo_id = await memo.send_memo(text=text, visibility=visibility, res_ids=res_ids)
                f[str(message.message_id)] = memo_id
                logger.info(f'{message.chat.id}发送了成功发送了图文Memos, MemoID为{memo_id}')

                memo_url = f'{domain}{memo_id}'
                memo_tag = Tag(url)
                for tag in tags:
                    await memo_tag.create_tag(tag)

                await bot.reply_to(message, memo_url)
            except Exception as e:
                logger.error(f'{message.chat.id}发送图文失败，{e}')
                await bot.reply_to(message, f"出错了，重来吧！{e}")
        else:
            await bot.reply_to(message, "未绑定Memos Open API，请先绑定后再使用。")
            return

async def send_resource(message: types.Message, bot: AsyncTeleBot):
    with shelve.open(f'../db/{message.chat.id}.db', flag='c', protocol=None, writeback=False) as f:
        if f['token']:
            url = f['token']
        else:
            await bot.reply_to(message, "未绑定Memos Open API，请先绑定后再使用。")
            return

    logger.info(f'{message.chat.id}请求上传资源')
    file_path = await bot.get_file(message.photo[-1].file_id)
    file_url = f'https://api.telegram.org/file/bot{os.getenv("API_TOKEN")}/{file_path.file_path}'

    try:
        res = Resource(url)
        filename = file_path.file_path.split('/')[1]
        res_id = await res.upload_resource_by_stream(file_url, filename=filename)
        logger.info(f'{message.chat.id}发送了成功上传资源, ResID为{res_id}')
        if message.media_group_id is not None:
            media_ids.setdefault(message.media_group_id, []).append(res_id)
        else:
            media_ids.setdefault(message.message_id, []).append(res_id)
        # markup = types.ForceReply(selective=False)
        await bot.reply_to(message, f'资源ID：{res_id}')
    except Exception as e:
        logger.error(f'{message.chat.id}上传资源出错，{e}')
        await bot.reply_to(message, f"出错了，重来吧！{e}")

async def update_edited_memo(message: types.Message, bot: AsyncTeleBot):
    with shelve.open(f'../db/{message.chat.id}.db', flag='c', protocol=None, writeback=False) as f:
        if f['token']:
            url = f['token']
            memo_id = f[str(message.message_id)]
        else:
            await bot.reply_to(message, "未绑定Memos Open API，请先绑定后再使用。")
            return

    try:
        memo = Memo(url)
        # text, tags, visibility, res_ids, status = parse_text(message.text)
        text, tags, res_ids, visibility, status = parse_html(message.text, message.html_text, message.entities)
        await memo.update_memo(memo_id, text, visibility, res_ids, status=status)
        logger.debug(f'\nMemo为: {text}\n Tags为: {tags}\n 公开：{visibility}\n 资源ID：{res_ids}\n 状态: {status}\n')
        memo_tag = Tag(url)
        for tag in tags:
            await memo_tag.create_tag(tag)
            logger.info(f'{message.chat.id}发送了成功创建1个TAG, TAG为{tag}')
        await bot.reply_to(message, '已经更新了')
    except Exception as e:
        logger.error(f'{message.chat.id}更新Memo失败，更新ID为{memo_id}，{e}')
        await bot.reply_to(message, f"出错了，重来吧！{e}")


def register_memo_handlers(bot: AsyncTeleBot):
    bot.add_custom_filter(ExistDb())
    bot.add_custom_filter(IsReplyFilter())

    bot.register_message_handler(send_resource, content_types=['photo'],  pass_bot=True)
    bot.register_message_handler(send_memo_by_words_and_resource, content_types=['text', 'photo'], is_reply=True, exist_db=True, pass_bot=True)
    bot.register_message_handler(send_memo_by_words, content_types=['text'], exist_db=True, is_reply=False, pass_bot=True)
    bot.register_edited_message_handler(update_edited_memo, content_types=['text'], exist_db=True, pass_bot=True)