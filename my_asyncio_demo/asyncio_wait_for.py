import asyncio


async def wait_do():
    print("start do-1")
    await asyncio.sleep(3)
    print("start do-2")
    await asyncio.sleep(3)
    print("start do-3")


async def main():
    waiter = wait_do()
    # 等待 6 秒，如果还没执行完就报错
    # 不超时情况
    await asyncio.wait_for(waiter, timeout=7)

    # 超时情况
    try:
        waiter2 = wait_do()
        await asyncio.wait_for(waiter2, timeout=3)
    except asyncio.TimeoutError:
        print(f'time out 3 seconds')

asyncio.run(main())

