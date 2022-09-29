import asyncio
import functools
from concurrent.futures.thread import ThreadPoolExecutor

import sys
import certifi
import urllib3


async def request(poolmanager: urllib3.PoolManager,
                  executor,
                  *,
                  method='GET',
                  url,
                  fields=None,
                  headers=None,
                  loop: asyncio.AbstractEventLoop=None):
    """urllib3是一个阻塞的HTTP库，对它进行异步处理，需要loop.run_in_executor()"""
    if not loop:
        loop = asyncio.get_running_loop()
    request_ = functools.partial(poolmanager.request, method, url, fields=fields, headers=headers)
    # request_是个同步函数, 调用run_in_executor以协程的方式调用同步函数
    return loop.run_in_executor(executor, request_)


async def bulk_requests(poolmanager: urllib3.PoolManager,
                        executor,
                        *,
                        method='GET',
                        urls,
                        fields=None,
                        headers=None,
                        loop: asyncio.AbstractEventLoop=None):
    '''一个异步生成器, 遍历url列表, 并返回url内容的future对象'''
    for url in urls:
        yield await request(poolmanager, executor, method=method, url=url, fields=fields, headers=headers, loop=loop)


def filter_unsuccessful_requests(response_and_exception: dict):
    # response_and_exception 键为url
    return filter(lambda url_and_response: not isinstance(url_and_response[1], Exception),
                  response_and_exception.items())


async def main():
    # 使用certifi收集根证书， 使用这些证书访问TLS加密的网址
    poolmanager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    executor = ThreadPoolExecutor(10)

    urls = ['https://www.baidu.com', 'https://www.liaoxuefeng.com/']

    # 异步推导式 收集所有请求的future对象
    requests = [request_ async for request_ in bulk_requests(poolmanager, executor, urls=urls,)]
    ponse_and_exceptions = dict(zip(urls, await asyncio.gather(*requests, return_exceptions=True)))
    # 将 ponse_and_exceptions 的结果进行过滤 去除exception的值
    responses = {url: resp.data for (url, resp) in
                 filter_unsuccessful_requests(ponse_and_exceptions)}

    # 正常访问的网址
    for res in responses.items():
        print(res)

    # 不能正常访问的网站异常信息
    for url in urls:
        if url not in responses:
            print(f'No successful request could be made to {url}. Reason:{ponse_and_exceptions[url]}',
                  file=sys.stderr)

asyncio.run(main())