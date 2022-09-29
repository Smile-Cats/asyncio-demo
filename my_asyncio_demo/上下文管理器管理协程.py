import asyncio


class Sync:
    def __init__(self):
        self.pending = []
        self.finished = None

    def schedule_coro(self, coro, shield=False):
        # sheild 参数指定协程是否可以被取消
        fut = asyncio.shield(coro) if shield else asyncio.ensure_future(coro)
        self.pending.append(fut)
        return fut

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.finished = await asyncio.gather(*self.pending, return_exceptions=True)


async def workload():
    '''模拟一个耗时的工资协程'''
    await asyncio.sleep(3)
    print('these coroutines will be executed simultaneously(同时) and return 42')
    return 42


async def main():
    async with Sync() as sync:
        sync.schedule_coro(workload())
        sync.schedule_coro(workload())
        sync.schedule_coro(workload())

    print('all scheduled coroutines have returned or thrown:', sync.finished)


asyncio.run(main())