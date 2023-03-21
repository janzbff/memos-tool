# memos-tool
实现了memos一些实用工具

## 功能
- 实现了memos大部分的api,`memos/memosapi.py`
- 提供了cli的接口，可以操作memos部分功能
- 提供了TG Bot部署
- 计划实现一些网页不好操作的批量操作的功能
  - 批量公开特定的memo
  - 批量重命名tag

## 安装
1. Python版本要求`3.10+`
2. clone代码并配置虚拟环境
    ```bash
    $ git clone https://github.com/janzbff/memos-tool.git
    $ cd memos-tool
    $ python3 -m venv .venv

    # 激活虚拟环境
    $ source .venv/bin/activate

    # 安装第三方库
    $ pip install -r requirements.txt
    ```
## 配置`.env`文件
`$ vim .env`
### `env`文件参考

```bash
# Memos的open api
OPEN_API=http://localhost:3001/api/memo?openId=00118412EFA02227B49BD145D6F75940
# TG Bot api #'563623xxxx:AAGg6Fg_sEm1u5sZ1Twg-lhhm2K-xxxxxg'
API_TOKEN="" 
# bot工作模式 `webhook` or `polling`
MODE="polling"
# webhook域名，需要https
WEBHOOK_HOST="https://tgbot.janz.eu.org"    #'https://bot.tg.com'
# 端口
WEBHOOK_PORT="8443"   #8443  # 443, 80, 88 or 8443 (port need to be 'open')
# docker需要配置成0.0.0.0
WEBHOOK_LISTEN="127.0.0.1"    #'127.0.0.1'  # In some VPS you may need to put here the IP addr
```
## CLI
```bash
$ python3 app.py <group_name> <args>

group_name:
    bot: Tg bot
    memo: memo相关操作
        send_memo:
        get_memos:
        get_memo:
        update_memo:
        delete_memo:
        filter_memo: 
    tag: tag相关操作
        get_tags:
        create_tag:
        delete_tag:
    resource: 资源相关操作
    tool: 批量工具
```
### 例如
1. 以polling运行bot
   ```
   $ python app.py bot 
   ```
2. 发送一条memo
    ```bash
    $ python app.py memo send_memo --text="#memos 第一条memo"
    ```
3. 把`#memos`重命名为`memo`, 谨慎操作！！！注意备份
    ```bash
    $ python app.py tool rename_tag --old_tag="memos" --new_tag="memo" 
    ```