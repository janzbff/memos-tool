#!/usr/bin/env python
# coding=utf-8

import asyncio
import os

from pathlib import Path
from typing import List, Dict, Literal
from urllib.parse import urlparse
from aiohttp.formdata import FormData
from aiohttp import ClientResponse, ClientTimeout
from aiohttp_retry import RetryClient, ClientSession
from loguru import logger
from dotenv import load_dotenv


load_dotenv()
class Request:
    def __init__(self, *args, **kwargs):
        self.client_session = ClientSession(trust_env=False)
        self.retry_client = RetryClient(client_session=self.client_session)
        self.request = self.retry_client.request(*args, **kwargs)

    async def __aenter__(self) -> ClientResponse:
        return await self.request

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_session.close()
        await self.retry_client.close()


def request(method, url, params=None, headers=None, data=None, json=None):
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    if json is not None:
        return Request(method, url, params=params, headers=headers, ssl=False, json=json,
                       timeout=ClientTimeout(total=100))
    else:
        return Request(method, url, params=params, headers=headers, data=data, ssl=False,
                       timeout=ClientTimeout(total=100))


STATUS = Literal['NORMAL', 'ARCHIVED']
VISIBILITY = Literal['PRIVATE', 'PROTECTED', 'PUBLIC']


class Base:
    def __init__(self, token: str = os.getenv('OPEN_API')):
        try:
            url_parts = urlparse(token)
            self.scheme = url_parts.scheme
            self.netloc = url_parts.netloc
            self.path = url_parts.path
            self.query = url_parts.query

            if self.path == '/api/memo':
                logger.debug(f'token正确')
            else:
                logger.debug(f'token错误')
                raise ValueError("token错误")
        except Exception as e:
            logger.debug(f'token错误, {e}')

        self.memo_path = 'api/memo'
        self.tag_path = 'api/tag'
        self.res_path = 'api/resource'


class Memo(Base):

    async def get_memos(self, limit: int = None, status: STATUS = 'NORMAL') -> List[dict]:
        """获取所有memos

        Args:
            limit (int, optional): 请求限制，如果有很多条，可以限制. Defaults to None.
            status (STATUS, optional): 获取正常memo还是归档的memo. Defaults to 'NORMAL'.

        Returns:
            List[dict]: 成功返回所有数据
            Example:
            {
                "id": 1023,
                "rowStatus": "NORMAL",
                "creatorId": 101,
                "createdTs": 1678672993,
                "updatedTs": 1679279516,
                "content": "#memo",
                "visibility": "PRIVATE",
                "pinned": true,
                "creatorName": "Demo Hero",
                "resourceList": []
            }

        """
        url = f'{self.scheme}://{self.netloc}/{self.memo_path}?{self.query}'
        params = {
            'rowStatus': status
        }
        if limit is not None:
            params.update({'limit': limit})
        logger.debug(f'参数数据为：{params}')
        async with Request("GET", url, params=params) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200
            data = await resp.json()
            return data['data']

    async def get_memo(self, memo_id: int) ->List[dict]:
        """根据ID获取memo

        Args:
            memo_id (int): memo的id

        Returns:
            List[dict]: 成功返回数据
        """
        memo_id = str(memo_id)
        url = f'{self.scheme}://{self.netloc}/{self.memo_path}/{memo_id}?{self.query}'
        async with Request("GET", url) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200
            data = await resp.json()
            return data['data']

    async def send_memo(self, text: str = None, visibility: VISIBILITY = "PRIVATE", res_ids: List[int] = None) -> int:
        """发送图文memo

        Args:
            text (str, optional): memo的内容. Defaults to None.
            visibility (VISIBILITY, optional): 私人、公开和登录可见. Defaults to "PRIVATE".
            res_ids (List[int], optional): 图片等资源ID, 通过上传资源返回的id. Defaults to None.

        Returns:
            int: 成功返回memo id
        """
        if res_ids is None:
            res_ids = []
        data = {
            "content": text,
            "visibility": visibility,
            "resourceIdList": res_ids
        }
        logger.debug(f'请求数据为：{data}')
        url = f'{self.scheme}://{self.netloc}/{self.memo_path}?{self.query}'
        async with request("POST", url=url, json=data) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200
            resp_data = await resp.json()
            return resp_data['data']['id']

    async def update_memo(self, memo_id: int, text: str = None, visibility: VISIBILITY = "PRIVATE", res_ids: List[int] = None, status: STATUS = 'NORMAL') -> None:
        """更新memo,主要用于修改已经发送的memo,可用于更新可见和状态

        Args:
            memo_id (int): memo id
            text (str, optional): 更新的内容, 默认为不更新内容. Defaults to None.
            visibility (VISIBILITY, optional): 可见状态, 默认为私人. Defaults to "PRIVATE".
            res_ids (List[int], optional): 资源ID. Defaults to None.
            status (STATUS, optional): memo状态. Defaults to 'NORMAL'.
        """
        data = {
            # "id": memo_id,
        }
        if text is not None:
            data.update({'content': text})
        if visibility is not None:
            data.update({'visibility': visibility})
        if res_ids is not None:
            data.update({'resourceIdList': res_ids})
        if status is not None:
            data.update({'rowStatus': status})
        logger.debug(f'请求数据为：{data}')
        memo_id = str(memo_id)
        url = f'{self.scheme}://{self.netloc}/{self.memo_path}/{memo_id}?{self.query}'
        async with request("PATCH", url, json=data) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200

    async def filter_memo(self,
                          tag: str = None,
                          offset: int = None,
                          limit: int = None,
                          status: STATUS = 'NORMAL',
                          visibility: VISIBILITY | None = None,
                          ) -> List[dict]:
        """筛选memo, 可多种条件共存

        Args:
            tag (str, optional): 根据已有tag筛选. Defaults to None.
            offset (int, optional): 偏移. Defaults to None.
            limit (int, optional): 限制条数. Defaults to None.
            status (STATUS, optional): 状态. Defaults to 'NORMAL'.
            visibility (VISIBILITY | None, optional): 可见性. Defaults to None.

        Returns:
            List[dict]: 筛选后的数据
        """
        url = f'{self.scheme}://{self.netloc}/{self.memo_path}?{self.query}'
        params = {
            'rowStatus': status
        }
        if limit is not None:
            params.update({'limit': limit})
        if tag is not None:
            params.update({'tag': tag})
        if offset is not None:
            params.update({'offset': offset})
        if visibility is not None:
            params.update({'visibility': visibility})

        logger.debug(f'搜索参数为：{params}')
        async with request("GET", url, params=params) as resp:
            logger.debug(f'搜索响应为{await resp.json()}')
            assert resp.status == 200
            resp_data = await resp.json()
            return resp_data['data']

    async def delete_memo(self, memo_id: int) -> None:
        """删除memo

        Args:
            memo_id (int): memo id
        """         
        memo_id = str(memo_id)
        url = f'{self.scheme}://{self.netloc}/{self.memo_path}/{memo_id}?{self.query}'
        async with request("DELETE", url) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200


class Resource(Base):
    async def get_resources(self) -> List[dict]:
        """获取资源

        Returns:
            List[dict]: 成功返回资源数据
        """
        url = f'{self.scheme}://{self.netloc}/{self.res_path}?{self.query}'
        async with Request("GET", url) as r:
            logger.debug(f'获取资源响应数据为：{await r.json()}')
            assert r.status == 200
            data = await r.json()
            logger.debug(f'资源为：{data["data"]}')
            return data['data']

    async def upload_resource(self, res_path: Path, filename: str, content_type: str = 'image/*') -> int:
        """从本地上传图片

        Args:
            res_path (Path): 本地路径
            filename (str): 图片名字
            content_type (str, optional): 资源类型. Defaults to 'image/*'.

        Returns:
            int: 成功返回资源id
        """
        data = FormData()
        data.add_field(
            'file',
            Path(res_path).open(mode="rb"),
            filename=filename,
            content_type=content_type
        )
        url = f'{self.scheme}://{self.netloc}/{self.res_path}/blob?{self.query}'
        async with request("POST", url, data=data) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200
            res_data = await resp.json()
            return res_data['data']['id']

    async def upload_resource_by_exlink(self, res_link: str, filename: str, content_type: str = 'image/*') -> int:
        """图床链接上传到资源

        Args:
            res_link (str): 图床链接
            filename (str): 文件名
            content_type (str, optional): 资源类型. Defaults to 'image/*'.

        Returns:
            int: 成功返回资源id
        """
        url = f'{self.scheme}://{self.netloc}/{self.res_path}?{self.query}'
        data = {
            'filename': filename,
            'externalLink': res_link,
            'type': content_type
        }
        logger.debug(f'请求数据为：{data}')
        async with request("POST", url, json=data) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200
            res_data = await resp.json()
            return res_data['data']['id']

    async def upload_resource_by_stream(self, res_link: str , filename: str, content_type: str = 'image/*') -> int:
        """从图片流上传到资源,例如TG发来的图片

        Args:
            res_link (str): 图片流链接
            filename (str): 文件名
            content_type (str, optional): 资源类型. Defaults to 'image/*'.

        Returns:
            int: _description_
        """
        url = f'{self.scheme}://{self.netloc}/{self.res_path}/blob?{self.query}'
        async with request("GET", res_link) as r:
            data = FormData()
            data.add_field('file', r.content, filename=filename, content_type=content_type)
            async with request("POST", url, data=data) as resp:
                logger.debug(f'响应数据为：{await resp.json()}')
                assert resp.status == 200
                res_data = await resp.json()
                return res_data['data']['id']


    async def delete_resource(self, res_id: int) -> None:
        """删除资源

        Args:
            res_id (int): 资源id

        Raises:
            ValueError: 
        """
        res_data: List[dict] = await self.get_resources()
        res_ids = []
        for data in res_data:
            res_ids.append(data['id'])
        if res_id in res_ids:
            res_id = str(res_id)
            url = f'{self.scheme}://{self.netloc}/{self.res_path}/{res_id}?{self.query}'
            async with request("DELETE", url) as resp:
                logger.debug(f'资源删除响应数据为：{await resp.json()}')
                assert resp.status == 200
        else:
            logger.debug(f'不存在这个资源，请查看是否拼写错误！要删除的tag为{res_id}')
            raise ValueError(res_id)


    async def clear_resource(self):
        """清除未被使用的资源，谨慎操作！！！
        """
        url = f'{self.scheme}://{self.netloc}/{self.res_path}?{self.query}'
        no_link_memo_ids: List[int] = []
        async with Request("GET", url) as r:
            logger.debug(f'获取资源响应数据为：{await r.json()}')
            assert r.status == 200
            data = await r.json()
            for res in data['data']:
                if res['linkedMemoAmount'] == 0:
                    no_link_memo_ids.append(res['id'])
        logger.debug(f'未被使用的资源：{no_link_memo_ids}')
        if len(no_link_memo_ids) != 0:
            tasks = [ asyncio.create_task(self.delete_resource(res_id)) for res_id in no_link_memo_ids ]
            finished, unfinished = await asyncio.wait(tasks)
            all_results = [r.result() for r in finished]
            logger.debug(all_results)
            for result in all_results:
                logger.debug(f'{result}\n')
        else:
            logger.debug(f'没有未被使用的资源')


class Tag(Base):
    async def get_tags(self) -> List[str]:
        """获取所有TAG

        Returns:
            List[str]: tag列表
        """
        url = f'{self.scheme}://{self.netloc}/{self.tag_path}?{self.query}'
        async with Request("GET", url) as r:
            logger.debug(f'获取TAG响应数据为：{await r.json()}')
            assert r.status == 200
            data = await r.json()
            return data['data']

    async def create_tag(self, name: str) -> None:
        """创建tag

        Args:
            name (str): tag的名字
        """
        url = f'{self.scheme}://{self.netloc}/{self.tag_path}?{self.query}'
        data = {'name': name}
        async with request("POST", url, json=data) as resp:
            logger.debug(f'响应数据为：{await resp.json()}')
            assert resp.status == 200

    async def delete_tag(self, name: str) -> None:
        """删除tag

        Args:
            name (str): tag名字

        Raises:
            ValueError: 
        """
        tags: List[str] = await self.get_tags()
        logger.debug(f'全部tags为：{tags}')
        if name in tags:
            url = f'{self.scheme}://{self.netloc}/{self.tag_path}/delete?{self.query}'
            data = {'name': name}
            async with request("POST", url, json=data) as resp:
                logger.debug(f'响应数据为：{await resp.json()}')
                assert resp.status == 200
        else:
            logger.debug(f'不存在这个tag，请查看是否拼写错误！要删除的tag为{name}')
            raise ValueError(name)


class Shortcut(Base):
    async def get_shortcut(self) -> List[dict]:
        pass
    async def create_shortcut(self, title: str, payload: List[dict]) -> Dict[str, dict]:
        pass
    async def delete_shortcut(self, shortcut_id: int) -> None:
        pass


if __name__ == '__main__':
    pass