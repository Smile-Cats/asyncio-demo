import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def coroutine_work():
    print('this is a coroutine')


async def coroutine_work2():
    print('this is a coroutine2')


def func():
    print("this is a func")


loop.call_soon(func)

# 运行单个协程任务
# 将协程对象包装为future对象
# asyncio.ensure_future(coroutine_work2(), loop=loop) # 将协程注册到loop
# loop.run_until_complete(coroutine_work())
# loop.run_forever()

# 运行多个协程任务
# future_list = [asyncio.ensure_future(coroutine_work()) for _ in range(10)]
# loop.run_until_complete(asyncio.gather(*future_list)) # asyncio.gather将多个future打包

asyncio.create_task(coroutine_work2())
loop.run_forever()

