import asyncio
from functools import partial
from signal import SIGINT


# 信号处理函数：当SIGINT信号时 loop stop
def sigint_handler(loop):
    print("loop stop because ctrl c")
    loop.stop()


loop = asyncio.get_event_loop()
loop.add_signal_handler(SIGINT, partial(sigint_handler, loop=loop))

loop.run_forever()