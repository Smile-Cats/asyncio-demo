import asyncio


async def cancelable():
    print("start do-1")
    await asyncio.sleep(3)
    print("start do-2")
    await asyncio.sleep(3)
    print("start do-3")


async def main():
    coro = cancelable()
    task = asyncio.create_task(coro)
    await asyncio.sleep(6)

    def canceller(task):
        task.cancel()

    loop = asyncio.get_running_loop()
    # 以线程安全的方式取消 协程
    loop.call_soon_threadsafe(canceller, task)

asyncio.run(main())

