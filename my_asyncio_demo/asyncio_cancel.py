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
    task.cancel()

asyncio.run(main())

