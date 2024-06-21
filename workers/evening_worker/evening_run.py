import asyncio
import uvloop
from .evening_func import Book
from tortoise import Tortoise
from settings import orm_conf
from utils.clock import clock
from datetime import datetime
from models import Task_Pool,User
from settings import mlog as log
from .settings import *

async def task_pull(
    worker_size:int,
    worker_id:int,
):
    today_all_task_users = []
    data_list = await Task_Pool.all().prefetch_related('task')
    for i in data_list:
        data = i.task
        today_all_task_users.append(data.user_id)
    distributed_tasks = []
    for i in range(len(today_all_task_users)):
        if i % worker_size == worker_id:
            distributed_tasks.append(today_all_task_users[i])
    return distributed_tasks
    
async def single_task(user_id:int):
    booker = Book(user_id)
    await booker.init()
    if booker.inited == False:
        log.warning(f'Booker实例init调用失败-user-{booker.user_id}')
        return False
    ret = await booker.do_chain()
    return ret

async def main(
    host:str,
    worker_size:int,
    worker_id:int,
):
    log.info('BOOKER启动')
    log.info(f"HOST:{host}")
    log.info(f"BOOKER-SIZE: {worker_size}")
    log.info(f'BOOKER-ID: {worker_id}')
    log.info(f"TIME-PULL-TASK:{TIME_PULL_TASK}")
    log.info(f"TIME-WS-CONNECT:{TIME_WS_CONNECT}")
    log.info(f"TIME-WS-SEND:{TIME_WS_SEND}")
    if not Tortoise._inited:
        await Tortoise.init(
                config=orm_conf(host)
            )
    while True:
        admin = await User.get_or_none(id=1)
        if admin:
            log.info(f'数据库测试成功-admin-{admin.username}')

        await clock(TIME_PULL_TASK)
        log.info(f'{datetime.now()}-正在拉取任务')
        user_id_list = await task_pull(
            worker_size=worker_size,
            worker_id=worker_id
        )
        
        await clock(TIME_WS_CONNECT)
        log.info(f'{datetime.now()}-开始创建任务并运行至连接WS服务器')
        ret = asyncio.gather(
            *[single_task(user_id) for user_id in user_id_list]
        )
        try:
            await asyncio.wait_for(ret, timeout=TASKS_TIMEOUT)
        except asyncio.TimeoutError:
            log.warning('任务超时！')

def setup(
    host:str,
    worker_size:int,
    worker_id:int,
):
    uvloop.run(main(host=host, worker_size=worker_size, worker_id=worker_id))



