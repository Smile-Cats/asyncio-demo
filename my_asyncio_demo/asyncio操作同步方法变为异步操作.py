import time
import asyncio
from concurrent.futures import ThreadPoolExecutor


# 这是个同步的函数
def long_blocking_function():
    print(time.time())
    time.sleep(2)
    return 1


async def run():
    loop = asyncio.get_event_loop()
    # 新建线程池
    pool = ThreadPoolExecutor()
    # 任务列表
    tasks = [loop.run_in_executor(pool, long_blocking_function),
             loop.run_in_executor(pool, long_blocking_function)]

    # print(loop.run_in_executor(pool, long_blocking_function))
    result = await asyncio.gather(*tasks)  # asyncio.gather打包协程对象，并将协程运行的结果以列表返回
    print(result)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    now = time.time()
    loop.run_until_complete(run())
    print(time.time() - now)
