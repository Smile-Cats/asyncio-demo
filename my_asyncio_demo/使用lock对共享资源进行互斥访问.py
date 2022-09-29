import asyncio

NON_ATOMIC_SUM = 'non_atomic_sum'  # atomic: 原子
ATOMIC_SUM = 'atomic_sum'
DATABASE = {ATOMIC_SUM: 0, NON_ATOMIC_SUM: 0}


async def add_with_delay(key, value, delay):
    """非原子操作，期间交出控制权"""
    old_value = DATABASE[key]
    await asyncio.sleep(delay)
    DATABASE[key] = old_value + value


async def add_locked_with_delay(lock, key, value, delay):
    """使用锁保证安全，只有一个协程在读写过程中可以访问字典"""
    async with lock:
        old_value = DATABASE[key]
        await asyncio.sleep(delay)
        DATABASE[key] = old_value + value


async def main():
    # 使用asyncio.Lock 来保证对共享资源的互斥访问
    lock = asyncio.Lock()
    atomic_workers = [add_locked_with_delay(lock, ATOMIC_SUM, 1, 3),
                      add_locked_with_delay(lock, ATOMIC_SUM, 1, 2)]
    non_atomic_workers = [add_with_delay(NON_ATOMIC_SUM, 1, 3),
                          add_with_delay(NON_ATOMIC_SUM, 1, 2)]

    await asyncio.gather(*atomic_workers)
    await asyncio.gather(*non_atomic_workers)

    print(DATABASE)


asyncio.run(main())