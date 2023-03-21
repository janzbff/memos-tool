#!/usr/bin/env python
# coding=utf-8

import asyncio
from typing import List
from loguru import logger
from memos.memosapi import  Memo, Resource, Tag, VISIBILITY
from fire import Fire

class Tool:
    """一些网页不好操作的批量操作工具
    """
    def __init__(self):
        self.memo = Memo()
        self.tag = Tag()
        self.res = Resource()

    async def rename_tag(self, old_tag: str, new_tag: str, deleted: bool =False) -> None:
        """重命名tag

        Args:
            old_tag (str): 旧的名字
            new_tag (str): 新的名字
            deleted (bool, optional): 旧的tag是否删除,默认不删除. Defaults to False.
        """
        tags = await self.tag.get_tags()
        if old_tag in tags:
            logger.debug('找到TAG，删除并新建')
        else:
            logger.debug(f'未找到需要重命名的TAG')
            return

        memos = self.memo.filter_memo(tag=old_tag)
        data: List[dict] = []
        for m in await memos:
            content_list: List[str] = m['content'].split(' ')
            text = []
            for content in content_list:
                # 解析无法处理一下特殊情况
                if content.startswith(f'#{old_tag}'):
                    text.append(f'#{new_tag}')
                # elif f'#{old_tag}' in content:
                #     text.append(content)
                else:
                    text.append(content)
            data.append({'id': m['id'], 'content': ' '.join(text)})


        if data:
            func = lambda x: self.memo.update_memo(memo_id=x['id'], text=x['content'])
            tasks = [asyncio.create_task(func(d)) for d in data]
            finished, unfinished = await asyncio.wait(tasks)
            all_results = [r.result() for r in finished]
            logger.debug(all_results)
            for result in all_results:
                logger.debug(f'{result}\n')

        await self.tag.create_tag(new_tag)
        if deleted:
            await self.tag.delete_tag(old_tag)

    async def public_memos(self, tags_list: str | List[str], visibility: VISIBILITY = 'PUBLIC', reverse: bool = True) -> None:
        """批量调整memo的状态

        Args:
            tags_list (str | List[str]): 让某个tag或tag列表全部调整可见性
            visibility (VISIBILITY, optional): 可见性. Defaults to 'PUBLIC'.
            reverse (bool, optional): List可用, True时取交集, 默认为并集. Defaults to True.
        """
   
        memo_ids = set()
        reverse_ids = set()
        tags = await self.tag.get_tags()
        if type(tags_list) is list:
            logger.debug('公开List')
            for t in tags_list:
                if t in tags:
                    logger.debug(f'{t}在tags中，准备公开TAG')
                    ml = await self.memo.filter_memo(tag=t)
                    logger.debug(f'包含TAG:{t}的内容为{ml}')
                    for m in ml:
                        logger.debug(f'TAG的内容为{m}')
                        if reverse:
                            memo_ids.add(m['id'])
                        elif m['id'] in memo_ids:
                            reverse_ids.add(m['id'])
                        else:
                            memo_ids.add(m['id'])
                else:
                    logger.debug(f'{t}不在tags中，不处理')
        else:
            logger.debug('公开一个tag')
            ml = await self.memo.filter_memo(tag=tags_list)
            for m in ml:
                memo_ids.add(m['id'])


        func = lambda x:  self.memo.update_memo(memo_id=x, visibility=visibility)
        if reverse and len(memo_ids) != 0:
            logger.debug(f'memos_id为：{memo_ids}')
            tasks = [asyncio.create_task(func(a)) for a in list(memo_ids)]
        elif len(reverse_ids) != 0:
            logger.debug(f'reverse_ids为：{reverse_ids}')
            tasks = [asyncio.create_task(func(a)) for a in list(reverse_ids)]
        else:
            logger.debug(f'Tag未匹配，不执行任何操作')
            return
        await asyncio.wait(tasks)

    async def send_memos(self):
        """测试用

        Returns:
            _type_: _description_
        """
        tasks = [asyncio.create_task(self.memo.send_memo(text=f'#test #ssss {i}')) for i in range(10)]
        return await asyncio.wait(tasks)

if __name__ == '__main__':
    Fire({
        'memo': Memo,
        'tag': Tag,
        'resource': Resource,
        'tool': Tool
    })


