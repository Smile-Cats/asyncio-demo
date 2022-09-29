import tracemalloc  # from 3.4

tracemalloc.start()  # 开始跟踪内存分配

d = [dict(zip('xy', (5, 6))) for _ in range(1000000)]
t = [tuple(zip('xy', (5, 6))) for _ in range(1000000)]

snapshot = tracemalloc.take_snapshot()  # 快照，当前内存分配
top_stats = snapshot.statistics('lineno')  # 快照对象的统计 按代码行统计

for stat in top_stats:
    print(stat)
