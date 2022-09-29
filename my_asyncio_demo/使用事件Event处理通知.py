import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO)


async def busy_loop(interval, work, worker, shutdown_event):
    '''持续工作，直到shutdown_event被设置'''
    while not shutdown_event.is_set():
        await worker(work)
        await asyncio.sleep(interval)
    logging.info('shutdown event set, exit busy_loop')
    return work


async def shutdown(delay, shutdown_event):
    '''阻塞等待delay秒， 然后设置shutdown_event'''
    await asyncio.sleep(delay)
    shutdown_event.set()


async def cleanup(mess, shutdown_event):
    '''阻塞等待shutdown_event被设置，然后清理mess垃圾'''
    await shutdown_event.wait()
    logging.info('cleaning up the mess(脏东西/粪便): %s', mess)


async def add_mess(mess_pile):
    '''向mess_pile垃圾堆中添加一个mess垃圾'''
    mess = random.randint(1, 100)
    logging.info('adding mess: %s', mess)
    mess_pile.append(mess)


async def main():
    shutdown_event = asyncio.Event()
    shutdown_delay = 10
    work = []
    await asyncio.gather(*[shutdown(shutdown_delay, shutdown_event),
                           cleanup(work, shutdown_event),
                           busy_loop(1, work, add_mess, shutdown_event)])


asyncio.run(main())
