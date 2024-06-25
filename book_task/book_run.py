import asyncio
import uvloop
from .book_func import Book
from typing import List,Tuple
from tortoise import Tortoise
from settings import orm_conf
from utils.clock import clock
from datetime import datetime
from models import Task_Pool,User
from settings import mlog

TIME_PULL_TASK = (19,59,0)
TIME_WS_CONNECT = (19,59,59)
TIME_WS_SEND = (20,0,0)
SLEEP_WS=0.1
SLEEP_POST=1
WORKER_SIZE = 1
WORKER_ID = 0
TASKS_TIMEOUT=300
WS_SIZE=120

class Worker():
    def __init__(
            self,
            host:str,
            worker_size:int=WORKER_SIZE,
            worker_id:int=WORKER_ID,
            pull_task_time:Tuple[int]=TIME_PULL_TASK,
            ws_connect_time:Tuple[int]=TIME_WS_CONNECT,
            ws_send_time:Tuple[int]=TIME_WS_SEND,
            ws_sleep:int=SLEEP_WS,
            post_sleep:int=SLEEP_POST,
            ws_size:int=WS_SIZE,
    )->None:
        self.log = mlog
        self.host = host
        self.worker_size = worker_size
        self.worker_id= worker_id
        self.pull_task_time = pull_task_time
        self.ws_connect_time = ws_connect_time
        self.ws_send_time = ws_send_time
        self.ws_sleep = ws_sleep
        self.post_sleep = post_sleep
        self.ws_size = ws_size

    async def orm_init(self):
        await Tortoise.init(
            config=orm_conf(self.host)
        )

    async def task_pull(self) -> List[int]:
        today_all_task_users = []
        data_list = await Task_Pool.all().prefetch_related('task')
        for i in data_list:
            data = i.task
            today_all_task_users.append(data.user_id)
        distributed_tasks = []
        for i in range(len(today_all_task_users)):
            if i % self.worker_size == self.worker_id:
                distributed_tasks.append(today_all_task_users[i])
        return distributed_tasks

    async def single_task_chain(self,user_id:int)->bool:
        Booker = Book(user_id=user_id,log=self.log)
        Booker.post_sleep = self.post_sleep
        Booker.ws_sleep =self.ws_sleep
        Booker.ws_send_time = self.ws_send_time
        Booker.ws_size = self.ws_size
        await Booker.init()
        if Booker.inited == False:
            self.log.warning(f'Booker实例init调用失败-user-{Booker.user_id}')
            return False
        ret = await Booker.run_book_chain()
        return ret
            
    async def main(self):
        self.log.info('BOOKER启动')
        self.log.info(f"HOST:{self.host}")
        self.log.info(f"BOOKER-SIZE: {self.worker_size}")
        self.log.info(f'BOOKER-ID: {self.worker_id}')
        self.log.info(f"SET-WS-SIZE:{self.ws_size}")
        self.log.info(f"TIME-PULL-TASK:{self.pull_task_time}")
        self.log.info(f"TIME-WS-CONNECT:{self.ws_connect_time}")
        self.log.info(f"TIME-WS-SEND:{self.ws_send_time}")
        self.log.info('正在测试数据库...')
        await self.orm_init()
        while True:
            admin = await User.get_or_none(id=1)
            if admin:
                self.log.info(f'数据库测试成功-admin-{admin.username}')

            await clock(self.pull_task_time)
            self.log.info(f'{datetime.now()}-正在拉取任务')
            user_id_list = await self.task_pull()
            
            await clock(self.ws_connect_time)
            self.log.info(f'{datetime.now()}-开始创建任务并运行至连接WS服务器')
            ret = asyncio.gather(
                *[self.single_task_chain(user_id) for user_id in user_id_list]
            )
            try:
                await asyncio.wait_for(ret, timeout=TASKS_TIMEOUT)
            except asyncio.TimeoutError:
                self.log.warning('任务超时！')

        # await asyncio.sleep(3000) #仅测试使用！

    def setup(self):
        uvloop.run(self.main())
