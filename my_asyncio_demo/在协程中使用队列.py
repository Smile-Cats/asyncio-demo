import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)


async def producer(iterable, queue: asyncio.Queue, shutdown_event: asyncio.Event):
    """生产者：向队列中添加数据"""
    for item in iterable:
        if shutdown_event.is_set():
            break

        try:
            queue.put_nowait(item)
        except asyncio.QueueFull as err: # 使用队列时我们必须处理QueueFull异常
            logging.warning('The queue is full, Maybe the worker are too slow')
            raise err
    shutdown_event.set()


async def worker(name, handler, queue: asyncio.Queue, shutdown_event: asyncio.Event):
    """消费者： 从队列中获取数据并处理"""
    while not shutdown_event.is_set() or not queue.empty():
        try:
            work = queue.get_nowait()
            # 模拟任务
            handler(await asyncio.sleep(0.1, result=work))
            logging.debug(f'worker {name} handled {work}')
        except asyncio.QueueEmpty as err:
            await asyncio.sleep(0)  # 交出控制权


async def main():
    n, handler, iterable = 10, lambda  x: None, [i for i in range(500)]
    shutdown_event = asyncio.Event()
    queue = asyncio.Queue()
    worker_coros = [worker(f'worker-{i}', handler, queue, shutdown_event) for i in range(n)]
    producer_coro = producer(iterable, queue, shutdown_event)
    coro = asyncio.gather(producer_coro, *worker_coros, return_exceptions=True)
    try:
        await coro
    except KeyboardInterrupt:
        shutdown_event.set()
        coro.cancel()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    logging.info('Pressed ctrl+c')
