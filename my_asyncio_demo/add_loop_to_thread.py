import threading
import asyncio
from typing import Callable


def loop_thread(func: Callable) -> None:
    loop = asyncio.new_event_loop()  # 新建一个loop
    asyncio.set_event_loop(loop)  # 将loop 加载到当前线程
    try:
        loop.run_until_complete(func())
    finally:
        loop.close()


async def print_l():
    print("ssssss")


def main():
    t = threading.Thread(target=loop_thread, args=(print_l,))
    t.start()
    t.join()


main()