from models import Task_Pool,User,Task
from tortoise import Tortoise
from settings import orm_conf
from utils.clock import clock
import uvloop
import logging

#settings
TIME_PUSH_EVE_TASK = (19,55,0)
TIME_CLEAN_EVE_POOL = (20,5,0)

class PoolM():
    def __init__(self,host:str) -> None:
        self._log = logging.getLogger(__name__)
        self.db_host = host
        self.time_push_task = TIME_PUSH_EVE_TASK
        self.time_clean_pool = TIME_CLEAN_EVE_POOL

    async def db_ini(self)->None:
        await Tortoise.init(
        config=orm_conf(self.db_host)
    )
        
    async def db_test(self)->None:
        admin = await User.get_or_none(id=1)
        if admin:
            self._log.info(f"数据库连接成功-admin-{admin.username}")
        else:
            self._log.info('数据库连接失败，管理员数据不存在')

    async def eve_push_task(self):
        tasks = await Task.all().prefetch_related('user')
        task_user_list = []
        for task in tasks:
            if task.user.balance <=0:
                continue
            if task.open == False:
                continue
            if task.status == 0:
                continue
            if task.wx_cookie == "" or task.wx_cookie == None:
                continue
            await Task_Pool.create(task=task)
            isCreate = await Task_Pool.get_or_none(task__id = task.id)
            if isCreate:
                task_user_list.append(task.user.username)
            else:
                self._log.warning(f"任务添加失败-{task.user.username}")
        self._log.info(f"今日任务列表：{task_user_list}")

    async def eve_clean_pool(self):
        await Task_Pool.all().delete()
        if (await Task_Pool.all() == []):
            self._log.info("任务清理成功")
        else:
            self._log.info("任务清理失败")


    async def main(self)->None:
        self._log.info('启动POOL-MANAGER')
        self._log.info(f"HOST:{self.db_host}")
        self._log.info(f"TIME-PUSH-TASK:{self.time_push_task}")
        self._log.info(f"TIME-CLEAN-POOL:{self.time_clean_pool}")
        await self.db_ini()
        while True:
            await self.db_test()
            await clock(self.time_push_task)
            self._log.info('正在推送任务入池')
            await self.eve_push_task()
            
            await clock(self.time_clean_pool)
            self._log.info("正在清理任务池")  
            await self.eve_clean_pool()

    def setup(self):
        uvloop.run(self.main())

