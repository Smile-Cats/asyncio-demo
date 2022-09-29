import asyncio
import functools


async def main(loop):
    print('print in main')


def stop_loop(fut, *, loop):
    loop.call_soon_threadsafe(loop.stop)


loop = asyncio.get_event_loop()
tasks = [loop.create_task(main(loop)) for _ in range(10)]
# 在tasks运行完成后 执行回调函数 stop_loop
asyncio.gather(*tasks).add_done_callback(functools.partial(stop_loop, loop=loop))


try:
    loop.run_forever()
finally:
    try:
        loop.run_until_complete(loop.shutdown_asyncgens())  # 清理未被完全消费的异步生成器。关闭事件循环的习惯操作。)
    finally:
        loop.close()