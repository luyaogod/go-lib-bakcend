from book_task.book_func import book
import asyncio
from datetime import datetime
from models import User,Task,Task_Ret,Task_Pool
from api_funcs.user_func import user_all_seat,user_all_seats_clean
from settings import orm_conf,TIME_PULL_TASK_FROM_POOL,TIME_WS_CONNECT
from tortoise import Tortoise
from utils.clock import sleep_to

async def init(host):
    await Tortoise.init(
        config=orm_conf(host)
    )

async def pull_tasks(workers_size,worker_id):
    task_list = []
    #从池中获取任务
    data_list = await Task_Pool.all().prefetch_related('task')
    print("row_data:",data_list)
    for data in data_list:
        print(dict(data.task))
        i = data.task
        task_item = {}
        task_item['task_id'] = i.id
        task_item['wx_cookie'] = i.wx_cookie
        task_item['user_id'] = i.user_id
        user = await User.get_or_none(id=i.user_id)
        if user == None:
            task_item['seats'] = []
        else:
            data = await user_all_seat(user)
            if data == None:
                task_item['seats'] = []
            else:
                task_item['seats'] = await user_all_seats_clean(data)
                task_list.append(task_item)
    print('clean_data',task_list)
    #负载均衡任务分配
    distributed_tasks = []
    for i in range(len(task_list)):
        if i % workers_size == worker_id:
            distributed_tasks.append(task_list[i])
    return distributed_tasks

async def tasks_worker(data_list):
    tasks = []
    for data in data_list:
        task = asyncio.create_task(book(**data))
        tasks.append(task)
    if tasks == []: #今日没有任务
        return []
    else:
        ret = await asyncio.gather(*tasks)
    return ret

async def main(host,worker_size,worker_id):
    worker_size = int(worker_size)
    worker_id = int(worker_id)
    print('[BOOKER SETUP]')
    print(f"BOOKER SIZE: {worker_size}")
    print(f'BOOKER ID: {worker_id}')
    await init(host)

    print("[DB]:数据库连接测试...")
    user = await User.get_or_none(username='mario')
    if (user):
        print(f'[DB]:数据库连接成功,{user.username}')
    else:
        print('[DB]:数据库连接出错')

    while True:
        print("[DB]:数据库连接测试...")
        user = await User.get_or_none(username='mario')
        if (user):
            print(f'[DB]:数据库连接成功,{user.username}')
        else:
            print('[DB]:数据库连接出错')

        # 任务拉取和分配
        # now = datetime.now()
        # pull_time = datetime(now.year, now.month, now.day, *TIME_PULL_TASK_FROM_POOL)
        # await sleep_to(pull_time)
        print("[开始装载任务列表]",datetime.now())
        try:
            data_list = await pull_tasks(worker_size,worker_id)
            # print(data_list) #测试输出
        except Exception as e:
            data_list = []
            print("[book_task-truck-error]:",e)
        print(data_list)

        #抢座tasks创建
        # connect_time = datetime(now.year, now.month, now.day, *TIME_WS_CONNECT)
        # await sleep_to(connect_time)
        # print("[开始连接WS]",datetime.now())
        # ret =  await tasks_worker(data_list)
        #
        # #更新数据库任务执行状态
        # print("[更新数据库任务状态]",datetime.now())
        # for r in ret:
        #     print("[任务状态]:",r)
        #     task = await Task.get_or_none(id = r["task_id"])
        #     if task:
        #         user = await User.get_or_none(pk=task.user_id)
        #         if r["result"]:
        #             #任务成功
        #             await Task_Ret.create(user=user, time=datetime.now().date(), status=1)
        #             user.balance -= 1
        #             await user.save()
        #         else:
        #             #任务失败
        #             await Task_Ret.create(user=user, time=datetime.now().date(), status=0)
        # print("[今日任务结束]", datetime.now())
        await asyncio.sleep(3600) #测试使用!!!!!!
