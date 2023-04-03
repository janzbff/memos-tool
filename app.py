from fire import Fire
from bot.server import main
from memos.memosapi import Memo, Tag, Resource
from memos.tools import Tool
from loguru import logger

logger.remove(handler_id=None)
logger.add('logs/memos-info-{time}.log', format="{time} {level} {message}", filter=lambda record: 'INFO' in record['level'].name, enqueue=True, rotation='00:00', retention='15 days')
logger.add('logs/memos-debug-{time}.log', format="{time} {level} {message}", filter=lambda record: 'DEBUG' or 'ERROR' in record['level'].name, enqueue=True, rotation='00:00', retention='15 days')

if __name__ == '__main__':
    Fire({
        'bot': main,
        'memo': Memo,
        'tag': Tag,
        'resource': Resource,
        'tool': Tool
    })