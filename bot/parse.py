from loguru import logger

STATUS = ['NORMAL', 'ARCHIVED']
VISIBILITY = ['PRIVATE', 'PROTECTED', 'PUBLIC']

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


# #
# def parse_html(text: str, entities):
#     tags = []
#     visibility: str = 'PRIVATE'
#     status: str = 'NORMAL'
#     deleted: list = []
#     res_ids = []
#
#     for entity in entities:
#         t = text[entity.offset:entity.offset + entity.length]
#         if entity.type == 'hashtag':
#             if t.strip('#') in VISIBILITY:
#                 visibility = t.strip('#')
#                 deleted.append(t)
#                 logger.debug(f'发现VISIBILITY为：{t}')
#             elif t.strip('#') in STATUS:
#                 status: str = t.strip('#')
#                 deleted.append(t)
#                 logger.debug(f'发现STATUS为：{t}')
#             else:
#                 logger.debug(f'发现TAG为：{t}')
#                 tags.append(t.strip('#'))
#         elif entity.type == 'cashtag':
#             logger.debug(f'{t}')
#             res_ids.append(int(t.strip('$')))
#             deleted.append(t)
#         else:
#             pass
#     if not deleted:
#         for d in deleted:
#             text = text.replace(d, '')
#
#     return text, tags, res_ids, visibility, status





