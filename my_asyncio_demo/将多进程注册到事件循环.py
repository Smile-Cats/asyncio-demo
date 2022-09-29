import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from contextlib import asynccontextmanager
from multiprocessing import get_context, freeze_support

CONTEXT = get_context('spawn')  # 启动进程的方式
# spawn: 赴清池启动一个新的Python解释器进程。子进程只会继承那些运行进程对象的 run() 方法所需的资源。
# # 特别是父进程中非必须的文件描述符和句柄不会被继承。相对于使用 fork 或者 forkserver，使用这个方法启动进程相当慢。


class AsyncProcessPool:
    def __init__(self, executor, loop=None):
        self.executor = executor
        if not loop:
            loop = asyncio.get_running_loop()
        self.loop = loop
        self.pending = []
        self.result = None

    def submit(self, fn, *args, **kwargs):
        """
        将多进程程序包装成future对象并注册到loop上执行
        concurrent.futures模块中也有一个Future对象，这个对象是基于线程池和进程池实现异步操作时使用的对象
          # 第一步：内部会先调用 ProcessPoolExecutor 的 submit 方法去进程池中申请一个进程去执行fn函数，
                   并返回一个concurrent.futures.Future对象
          # 第二步：调用asyncio.wrap_future将concurrent.futures.Future对象包装为asyncio.Future对象。
        """
        process_future = self.executor.submit(fn, *args, **kwargs)  # 多进程future对象
        loop_future = asyncio.wrap_future(process_future, loop=self.loop)  # 将进程future包装成事件循环future
        return loop_future


@asynccontextmanager
async def pool(max_workers=None, mp_context=CONTEXT, initializer=None, initargs=(), loop=None, return_exceptions=True):
    with ProcessPoolExecutor(max_workers=max_workers,
                             mp_context=mp_context,
                             initializer=initializer,
                             initargs=initargs) as executor:
        async_process_pool = AsyncProcessPool(executor=executor, loop=loop)
        try:
            yield async_process_pool
        finally:
            # 在finally语句块中等待所有future对象完成
            async_process_pool.result = await asyncio.gather(*async_process_pool.pending,
                                                             return_exceptions=return_exceptions)


async def main():
    async with pool() as p:
        p.submit(print, 'this works perfectly fine')
        result = await p.submit(sum, [1, 2, 3])
        print(result)

    print(p.result)


if __name__ == '__main__':
    freeze_support()  # 针对Windows平台：为使用了 multiprocessing 的程序，提供冻结以产生 Windows 可执行文件的支持。

    asyncio.run(main())