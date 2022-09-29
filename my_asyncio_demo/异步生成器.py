import asyncio
import random


# 编写异步生成器
async def gen_random_number(delay, start, end):
    while True:
        yield random.randint(start, end)
        await asyncio.sleep(delay)


# 运行异步生成器
async def main():
    async for i in gen_random_number(1, 0, 100):
        print(i)


try:
    print('start to print random numbers')
    asyncio.run(main())
except KeyboardInterrupt:
    print('closed the main loop')