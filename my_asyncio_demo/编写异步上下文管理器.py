from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
import asyncio


class AsyncFile:
    def __init__(self, file, loop=None, executor=None):
        if not loop:
            loop = asyncio.get_running_loop()
        if not executor:
            executor = ThreadPoolExecutor()
        self.file = file
        self.loop = loop
        self.executor = executor
        self.pending = []
        self.result = []

    def write(self, string):
        self.pending.append(self.loop.run_in_executor(self.executor, self.file.write, string))

    def read(self, size=-1):
        self.pending.append(self.loop.run_in_executor(self.executor, self.file.read, size))

    def readlines(self):
        self.pending.append(self.loop.run_in_executor(self.executor, self.file.readlines))


@asynccontextmanager
async def async_open(path, mode='w'):
    '''异步上下为管理器实现非阻塞文件IO'''
    with open(path, mode) as f:
        loop = asyncio.get_running_loop()
        async_file_obj = AsyncFile(f, loop=loop)
        try:
            # try语句模块对应__aenter__, with ....open as
            yield async_file_obj
        finally:
            # finally语句块对应__aexit__, 执行读取任务
            async_file_obj.result = await asyncio.gather(*async_file_obj.pending)


import tempfile
import os


async def main():
    tempdir = tempfile.gettempdir()
    path = os.path.join(tempdir, 'run.txt')
    print(f'writing asynchronously(异步) to {path}')

    async with async_open(path, mode='w') as f:
        f.write('顺序\n')
        f.write('可能\n')
        f.write('就是\n')
        f.write('乱的\n')
        f.write('！\n')

    print(AsyncFile('/').result)


asyncio.run(main())