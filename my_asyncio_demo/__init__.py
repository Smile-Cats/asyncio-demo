import asyncio


async def future():
    await asyncio.sleep(1)
    print('run this future')
    return 22


async def main():
    loop = asyncio.get_running_loop()
    # asyncio.ensure_future将协程注册到事件循环， 返回future对象
    # future对象将等待事件循环执行它，最后返回协程的执行结果
    a = asyncio.ensure_future(future(), loop=loop)
    print(a)
    # await 代表等待future执行的结果
    print(await a)
    b = asyncio.gather(*[future() for _ in range(10)])
    print(b)
    print(await b)

asyncio.run(main())