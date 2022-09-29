import asyncio
import random

STOCK_MARKET = {'DAX': 100, 'SPR': 10, 'AMAZON': 1000}  # 股市详情
INITTAL_STOCK_MARKET = STOCK_MARKET.copy()  # 浅拷贝


class MarketException(BaseException):
    pass


async def stock_watcher(on_alert, stock, price, cond: asyncio.Condition):
    """股票监视"""
    async with cond:
        print(f'waiting for {stock} to be under {price}$')
        # 当结果不为true时 wait_for 一直阻塞
        await cond.wait_for(lambda: STOCK_MARKET.get(stock) < price)
        await on_alert()


def random_stock():
    """随机选出一只股票"""
    while True:
        yield random.choice(list(STOCK_MARKET.keys()))


async def twitter_quotes(conditions, threshold):  # threshold:临界点，阈值
    """模拟推特报价"""
    for stock in random_stock():
        STOCK_MARKET[stock] -= random.randint(1, 10)  # 模拟股票下跌
        new_value = STOCK_MARKET[stock]
        print(f'New stock market value for {stock}:{new_value}')

        cond = conditions.get(stock)
        async with cond:
            # 开始唤醒 condition.wait_for 程序， 如果wait_for内部验证为true即可进行下一步
            print(f'开始启动condition.notify, 这个股票是{stock}，猜猜下个协程切换到了哪？')
            cond.notify(2)

        await asyncio.sleep(.1)


async def governmental_market_surveillance():
    """政府市场监管"""
    raise MarketException()


async def main():
    """任何一支股票，跌破-50以后，都会触发alert"""
    # 为每只股票都创建了一个stock_watcher实例，并向他传递一个具有相同锁实例的条件变量
    lock = asyncio.Lock()
    conditions = {stock: asyncio.Condition(lock) for stock in STOCK_MARKET}  # 每只股票对应一个事件
    threshold = -50
    stock_watchers = [
        stock_watcher(governmental_market_surveillance, stock, threshold, conditions.get(stock))
        for stock in STOCK_MARKET]

    await asyncio.gather(*[twitter_quotes(conditions, threshold), *stock_watchers], return_exceptions=False)


try:
    asyncio.run(main())
except MarketException:
    print('STOCK_MARKET:', STOCK_MARKET)
    print('restoring the stock market...')
    STOCK_MARKET = INITTAL_STOCK_MARKET.copy()