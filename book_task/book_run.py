import asyncio
import uvloop
import aiohttp
from .book_func import Book
from tortoise import Tortoise
from settings import orm_conf
from utils.clock import clock
from models import Task_Pool
from settings import mlog as log

TIME_PULL_TASK = (19,59,0)
TIME_WS_CONNECT = (19,59,59)
TIME_WS_SEND = (20,0,0)
SLEEP_WS=0.1
SLEEP_POST=1
WORKER_SIZE = 1
WORKER_ID = 0
TASKS_TIMEOUT=300
WS_SIZE=120

async def main_loop(
        host:str,
        worker_size:int=WORKER_SIZE,
        worker_id:int=WORKER_ID,
):
    await Tortoise.init(
            config=orm_conf(host)
        )
    
    log.info('BOOKER启动')
    log.info(f"HOST:{host}")
    log.info(f"BOOKER-SIZE: {worker_size}")
    log.info(f'BOOKER-ID: {worker_id}')
    log.info(f"TIME-WS-SEND:{TIME_WS_SEND}")
    
    while True:
    #任务拉取分配
        await clock(TIME_PULL_TASK)
        connector = aiohttp.TCPConnector(limit_per_host=30)
        ses = aiohttp.ClientSession(connector=connector)

        today_all_task_users = []
        data_list = await Task_Pool.all().prefetch_related('task')
        for i in data_list:
            data = i.task
            today_all_task_users.append(data.user_id)
        distributed_tasks = []
        for i in range(len(today_all_task_users)):
            if i % worker_size == worker_id:
                distributed_tasks.append(today_all_task_users[i])

        bookers:list[Book] = []
        for id in distributed_tasks:
            booker = Book(
                user_id=id,
                ses=ses,
                ws_send_time=TIME_WS_SEND,  #发送ws真正时间
                ws_size=WS_SIZE,
                ws_sleep=SLEEP_WS,
                post_sleep=SLEEP_POST
            )
            try:
                init_ret = await booker.init()
            except Exception as e:
                log.warning(f"初始化失败：{booker.user_id}-{e}")
            if init_ret:
                bookers.append(booker)

        await clock(TIME_WS_CONNECT)
        tasks = []
        for booker in bookers:
            task = asyncio.create_task(booker.do_chain())
            tasks.append(task)
        
        ret = asyncio.gather(*tasks)
        try:
            await asyncio.wait_for(ret, timeout=TASKS_TIMEOUT)
        except asyncio.TimeoutError:
            log.warning('任务超时！')

        log.info("处理结果")
        for booker in bookers:
            if booker.ret == True:
                await booker.reduce_balance()
                await booker.add_task_ret(1)
            else:
                booker.ret == False
        log.info("今日任务完成...")
        await ses.close()
        #测试使用
        
        # await asyncio.sleep(10000)

def setup(
    host:str,
    worker_size:int=WORKER_SIZE,
    worker_id:int=WORKER_ID,
):
    """启动"""
    uvloop.run(
        main_loop(host=host, worker_size=worker_size, worker_id=worker_id)
    )
