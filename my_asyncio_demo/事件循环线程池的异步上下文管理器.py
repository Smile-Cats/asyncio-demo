import asyncio
from contextlib import asynccontextmanager
from functools import partial


class SchedulerLoop(asyncio.SelectorEventLoop):
    def __init__(self):
        super(SchedulerLoop, self).__init__()
        self._scheduled_callback_futures = []
        self.results = []

    @staticmethod
    def unwrapper(fut: asyncio.Future, function):
        """消除fut隐藏参数"""
        return function()

    def _future(self, done_hook):
        """创建一个future对象，在等待时调用done_hook"""
        fut = self.create_future()
        fut.add_done_callback(partial(self.unwrapper, function=done_hook))
        return fut

    def schedule_soon_threadsafe(self, callback, *args, context=None):
        fut = self._future(partial(callback, *args))
        self._scheduled_callback_futures.append(fut)
        self.call_soon_threadsafe(fut.set_result, None, context=context)

    def schedule_soon(self, callback, *args, context=None):
        fut = self._future(partial(callback, *args))
        self._scheduled_callback_futures.append(fut)
        self.call_soon(fut.set_result, None, context=context)  # 委托父类实现

    def schedule_later(self, delay_in_seconds, callback, *args, context=None):
        fut = self._future(partial(callback, *args))
        self._scheduled_callback_futures.append(fut)
        self.call_later(delay_in_seconds, fut.set_result, None, context=context)

    def schedule_at(self, when, callback, *args, context=None):
        fut = self._future(partial(callback, *args))
        self._scheduled_callback_futures.append(fut)
        self.call_at(when, fut.set_result, None, context=context)

    async def await_callbacks(self):
        callback_futs = self._scheduled_callback_futures[:]
        self._scheduled_callback_futures[:] = []  # 清空列表 self._scheduled_callback_futures = []
        return await asyncio.gather(*callback_futs, return_exceptions=True, loop=self)


class SchedulerLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self):
        return SchedulerLoop()


@asynccontextmanager
async def scheduler_loop():
    """异步上下文管理器，确保运行的事件循环是SchedulerLoop"""
    loop = asyncio.get_running_loop()
    print(loop)
    if not isinstance(loop, SchedulerLoop):
        raise ValueError('you can run the scheduler_loop async context manager only in a SchedulerLoop')

    try:
        yield loop
    finally:  # 在__aexit__中调用，等待所有回调完成
        loop.results = await loop.await_callbacks()


async def main():
    async with scheduler_loop() as loop:
        loop.schedule_soon(print, 'hello')
        loop.schedule_later(1, print, 'world')
        loop.schedule_at(loop.time() + 1, print, 'bye')
        await asyncio.sleep(2)
        print(loop.results)


asyncio.set_event_loop_policy(SchedulerLoopPolicy())
asyncio.run(main())