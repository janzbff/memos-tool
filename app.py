import asyncio
from fire import Fire
from bot.server import main
from memos.memosapi import Memo, Tag, Resource
from memos.tools import Tool

main = asyncio.run(main())
if __name__ == '__main__':
    Fire({
        'bot': main,
        'memo': Memo,
        'tag': Tag,
        'resource': Resource,
        'tool': Tool
    })