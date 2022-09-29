import asyncio
import random
from typing import Union, Callable


async def get_baidu(loop):
    seconds: int = random.randint(1, 5)
    resp: str = await asyncio.sleep(seconds, result='www.baidu.com ' + str(seconds))
    await show_baidu(resp, loop)


async def show_baidu(resp: str, loop):
    print(f"this craw {resp}")
    seconds = int(resp.split(' ')[-1])
    if seconds < 4:
        asyncio.ensure_future(get_baidu(loop))
    else:
        loop.stop()


def main():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(get_baidu(loop), loop=loop)
    loop.run_forever()


if __name__ == '__main__':
    main()
