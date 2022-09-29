from contextvars import ContextVar
import asyncio

context_var = ContextVar('key', default=None)


async def memory_two(context_var_: ContextVar):
    value = context_var_.get()
    print(f'memory value:{value}')


async def memory(context_var_: ContextVar, value):
    old_value = context_var_.get()
    context_var_.set(value)
    print(f'memory old_value:{old_value}, value:{value}')
    await memory_two(context_var_)


async def main():
    await memory(context_var, 31)
    await asyncio.gather(*[memory(context_var, i) for i in range(10)])


asyncio.run(main())