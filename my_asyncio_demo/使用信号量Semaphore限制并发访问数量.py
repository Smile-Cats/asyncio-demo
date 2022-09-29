import asyncio


async def run(i, semaphore: asyncio.Semaphore):
    async with semaphore:
        print(f'{i} working')
        return await asyncio.sleep(1)


async def main():
    semaphore = asyncio.Semaphore(3)  # 只允许3个协程
    await asyncio.gather(*[run(i, semaphore) for i in range(10)])


asyncio.run(main())