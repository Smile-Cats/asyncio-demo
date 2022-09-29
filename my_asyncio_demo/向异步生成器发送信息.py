import asyncio
import logging
from contextlib import asynccontextmanager


class Interactor:
    "Interactor（交互者）类封装了可以与异步生成器进行通信的功能。使用asend协程方法传递通用的payload（负载）给异步生成器。"

    def __init__(self, agen):
        self.agen = agen  #异步生成器

    async def interact(self, *args, **kwargs):
        try:
            await self.agen.asend((args, kwargs))
        except StopAsyncIteration:
            logging.exception('The async generator is already exhausted(枯竭).')


async def wrap_in_asyngen(handler):
    """将普通函数包装成生成器"""
    while True:
        args, kwargs = yield
        handler(*args, **kwargs)


@asynccontextmanager
async def start(agen):
    """上下文管理器：预激和关闭生成器"""
    try:
        await agen.asend(None)  # 预激协程，启动生成器
        yield Interactor(agen)  # 封装一个Interactor返回
    finally:
        await agen.aclose()


async def main():
    async with start(wrap_in_asyngen(print)) as w:
        await w.interact('put')
        await w.interact('the')
        await w.interact('worker')
        await w.interact('to')
        await w.interact('work')


asyncio.run(main())