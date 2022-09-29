import asyncio


async def cancelable():
    print("start do-1")
    await asyncio.sleep(3)
    print("start do-2")
    await asyncio.sleep(3)
    print("start do-3")


async def main():
    coro = cancelable()
    # task = asyncio.create_task(coro)
    shield_task = asyncio.shield(coro)
    await asyncio.sleep(1)
    shield_task.cancel()

    await asyncio.sleep(10)  # shield_task.cancel 表面上让 shield_task 关闭了，但是如果loop仍在运行的话，协程依然会运行完
    try:
        await shield_task
    except asyncio.CancelledError:
        print('shield_task canceled')

        # shield_task.cancel 虽然取消了 shield_task 任务，但是 Inner 任务(coro)还是 running 状态的
        # 等待下次事件循环 ( loop.run_until_complete 的目标是等待 shield_task 执行结束，它并不关注 coro 运行状态)。
        # 所以这里不加await sleep ，整个loop会结束掉，coro任务也会跟着结束
        await asyncio.sleep(10)  # shield_task.cancel 表面上让 shield_task 关闭了，但是如果loop仍在运行的话，协程依然会运行完

asyncio.run(main())

