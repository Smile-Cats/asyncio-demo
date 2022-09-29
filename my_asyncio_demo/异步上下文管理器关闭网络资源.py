import asyncio
import socket
from contextlib import asynccontextmanager


@asynccontextmanager
async def tcp_client(host='google.de', port=80):
    address_info = (await asyncio.get_running_loop().getaddrinfo(host, port, proto=socket.IPPROTO_TCP)).pop()
    print('address_info: ', address_info)

    if not address_info:
        raise ValueError(f'Could not resolve {host}:{port}')

    host, port = address_info[-1]
    # asyncio 提供了高级工具，用来打开指定端口的URL上的异步写入器writer和读取器reader，读写对象分别为 StreamReader 和 StreamWriter 实例
    reader, writer = await asyncio.open_connection(host, port)

    try:
        yield reader, writer
    finally:
        # 写入器需要正确管理，以释放连接过程中打开的套接字。否则连接双方都仍然处于连接状态。
        writer.close()  # 关闭写入器
        await asyncio.shield(writer.wait_closed())  # 为了确保已经关闭，使用shield屏蔽等待，这样他不能从外部取消。


async def main():
    async with tcp_client() as (reader, writer):
        # 给服务器发消息，二进制
        writer.write(b'GET /us HTTP/1.1\r\nhost:apress.com\r\n\r\n')

        # drain是一个与底层IO输入缓冲区交互的流量控制方法。（一个控制消息的数据量控制阀）
        # 若当缓冲区上限，drain()会阻塞，等到缓存区回落下限，写操作恢复。这里由于消息内容较少，不会阻塞
        await writer.drain()  # 流

        # 接受数据是二进制
        content = await reader.read(1024 * 2)
        print(content)


asyncio.run(main())
