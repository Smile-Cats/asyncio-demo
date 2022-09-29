import asyncio


async def cancellable(delay=10, *, loop):
    now = loop.time()

    try:
        print(f'sleeping from {now} for {delay} seconds ...')
        await asyncio.sleep(delay)
        print(f'slept {delay} seconds. without disturbance（打扰）')
    except asyncio.CancelledError:
        print(f'cancelled at {now} after {loop.time() - now} seconds')


def canceller(task, fut):
    task.cancel()  # 如果这里的task是asyncio.gather生成的一组task，可以一起取消
    fut.set_result(None)


async def cancel_threadsafe(gathered_tasks, loop):
    fut = loop.create_future()
    loop.call_soon_threadsafe(canceller, gathered_tasks, fut)
    await fut


async def main():
    loop = asyncio.get_running_loop()
    coros = [cancellable(i, loop=loop) for i in range(10)]  # 协程列表

    gathered_tasks = asyncio.gather(*coros)  # 将协程列表打包

    # 在这里增加延迟，这样我们可以看到前四个协程不间断的运行
    await asyncio.sleep(3)

    await cancel_threadsafe(gathered_tasks, loop)
    try:
        await gathered_tasks
    except asyncio.CancelledError:
        print('was cancelled')


asyncio.run(main())