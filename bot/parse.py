from typing import Literal
from loguru import logger
from markdownify import markdownify as md

STATUS = Literal['NORMAL', 'ARCHIVED']
VISIBILITY = Literal['PRIVATE', 'PROTECTED', 'PUBLIC']

def parse_text(text: str):
    """解析信息
    Args:
        text (str): 文字信息
    Returns:
        tuple: 返回一个4元组
            texts (str): 解析后的信息包含TAG
            tags (list): tag列表
            visibility (str): 是否公开，默认为不公开
            res_ids (list): 资源列表
    """
    text_list = text.split(' ')
    tags = []
    res_ids = []
    visibility = "PRIVATE"
    status = "NORMAL"
    word_list = []
    for t in text_list:
        if t in VISIBILITY:
            visibility = t.strip('#')
        elif t in STATUS:
            status = t.strip('#')
        elif t.startswith('#'):
            tags.append(t.strip('#'))
            word_list.append(t)
        elif t.startswith('&'):
            if t.strip('&').isnumeric():
                res_ids.append(int(t.strip('&')))
            else:
                word_list.append(t)
        else:
            word_list.append(t)
    texts = ' '.join(word_list)
    return texts, tags, res_ids, visibility, status


def parse_html(text: str, html: str, entities):
    visibility: VISIBILITY = 'PRIVATE'
    status: STATUS = 'NORMAL'
    tags: list | None = []
    res_ids: list | None = []
    if entities is None:
        text = md(html=html)
    else:
        for entity in entities:
            t = text[entity.offset:entity.offset + entity.length]
            if entity.type == 'hashtag':
                if t.strip('#') in ['PRIVATE', 'PROTECTED', 'PUBLIC']:
                    logger.debug(f'发现可见性状态:{t}')
                    visibility = t.strip('#')
                    html = html.replace(t, '') 
                elif t.strip('#') in ['NORMAL', 'ARCHIVED']:
                    logger.debug(f'发现发布状态:{t}')
                    status = t.strip('#')
                    html = html.replace(t, '')
                elif t.startswith('#RES'):
                    logger.debug(f'发现资源:{t}')
                    res_ids.append(int(t.strip('#RES')))
                    html = html.replace(t, '')
                else:
                    logger.debug(f'发现标签:{t}')
                    tags.append(t.strip('#'))
        text = md(html)        
                                 
            # match entity.type:
            #     case 'hashtag' if t.strip('#') in ['PRIVATE', 'PROTECTED', 'PUBLIC']:
            #         logger.debug(f'发现可见性状态:{t}')
            #         visibility = t.strip('#')
            #         html = html.replace(t, '')
            #     case 'hashtag' if t.strip('#') in ['NORMAL', 'ARCHIVED']:
            #         logger.debug(f'发现发布状态:{t}')
            #         status = t.strip('#')
            #         html = html.replace(t, '')
            #     case 'hashtag' if t.startswith('#RES'):
            #         logger.debug(f'发现资源:{t}')
            #         res_ids.append(int(t.strip('#RES')))
            #         html = html.replace(t, '')
            #     case 'hashtag':
            #         logger.debug(f'发现标签:{t}')
            #         tags.append(t.strip('#'))
            #     case _:
            #         pass
        # text = md(html)
    return text, tags, res_ids, visibility, status





