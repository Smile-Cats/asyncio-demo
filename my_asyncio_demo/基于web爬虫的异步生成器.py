import asyncio
import re
import typing
from concurrent.futures import Executor, ThreadPoolExecutor
from urllib.request import urlopen

# patch for:urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
# unable to get local issuer certificate (_ssl.c:1131)>
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

DEFAULT_EXECUTOR = ThreadPoolExecutor(4)
ANCHOR_TAG_PATTERN = re.compile(
    re.compile(b"<a href=[\"|\'](.*?)[\"|\']>", re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE))


async def wrap_async(generator: typing.Generator, executor: Executor = DEFAULT_EXECUTOR, sentinel=object(), *,
                     loop: asyncio.AbstractEventLoop = None):
    '''封装一个生成器 并返回一个异步生成器'''
    if not loop:
        loop = asyncio.get_running_loop()

    while True:
        result = await loop.run_in_executor(executor, next, generator, sentinel) # next(generator, default=sentinel)
        if result == sentinel:
            break
        yield result


def follow(*links):
    '''链接和链接的网页内容'''
    return ((link, urlopen(link).read()) for link in links)


def get_links(text: bytes):
    '''返回一个迭代器，让我们以迭代且安全的方式获取文本中的所有链接'''
    return (match.groups()[-1] for match in ANCHOR_TAG_PATTERN.finditer(text) if
            hasattr(match, 'groups') and len(match.groups()))  # 这里的if限制是防止匹配结果为None和href匹配数为0

async def main(*links):
    async for current, body in wrap_async(follow(*links)):
        print('curren url:', current)
        print('content:', body)
        async for link in wrap_async(get_links(body)):
            print(link)

asyncio.run(main('http://apress.com'))
