import multiprocessing
import asyncio
import random
import os
import typing


async def worker() -> None:
    """模拟一个耗时任务,打印当前进程的pid"""
    random_deplay = random.randint(1, 3)
    result = await asyncio.sleep(random_deplay, result=f'working in process {os.getpid()}')
    print(result)


def main_process(coro_worker: typing.Callable, num_of_coroutines: int) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        workers = [coro_worker() for _ in range(num_of_coroutines)]
        loop.run_until_complete(asyncio.gather(*workers, loop=loop))
        # 这里其实更建议使用asyncio.run(), 示例是为了说明如何在不同的进程中实例化event loop
    except KeyboardInterrupt:
        print(f'stopping {os.getpid()}')
        loop.stop()
    finally:
        loop.close()


def main(num_procs, num_coros, process_main):
    """创建多个进程"""
    for _ in range(num_procs):
        proc = multiprocessing.Process(target=process_main, args=(worker, num_coros))  # 创建一个子进程
        proc.start()  # 启动子进程


if __name__ == '__main__':
    try:
        main(10, 2, main_process)  # 开10个子进程，每个进程中2个协程
    except KeyboardInterrupt:
        # 这里不会执行
        print('ctrl + c was pressed, stopping all process')