import asyncio
import time
from concurrent.futures.process import ProcessPoolExecutor
from multiprocessing import freeze_support


def print_one():
    n = 1
    while n < 10:
        print("10"*n)
        n += 1
        time.sleep(1)
    return n


async def main():
    p = ProcessPoolExecutor(2)
    fut = p.submit(print, "1111")
    await asyncio.wrap_future(fut)
    fut2 = p.submit(print_one)
    result = await asyncio.wrap_future(fut2)
    return result


if __name__ == '__main__':
    freeze_support()

    asyncio.run(main())