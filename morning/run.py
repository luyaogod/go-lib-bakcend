from utils.clock import clock
from utils.ocr import Ocr
from .funcs import MUser
from settings import orm_conf
from settings import mlog as log
from models import Morning_Task_Pool,User
from tortoise import Tortoise, connections
import uvloop
import asyncio
from .settings import *
from .funcs import MUser

async def pull_morn_task():
    """拉取早晨任务"""
    users_ids = []
    user_names = []
    datas = await Morning_Task_Pool.all().prefetch_related('user')
    for data in datas:
        user:User = data.user
        users_ids.append(user.id)
        user_names.append(user.username)
    log.info(f"今日任务列表: {user_names}")
    return users_ids

async def new_muser_task(id, ocr):
    muser = MUser(id, ocr)
    await muser.ini()
    return muser.tasks_group()

async def clean():
    """清理任务池"""
    conn = connections.get("default")
    await conn.execute_query("""
DELETE FROM morning_seat_user;
DELETE FROM morning_task_pool;
""")

async def m_main(host:str):
    log.info(f"TIME_PULL_TASK {TIME_PULL_TASKS}")
    log.info(f"TIME_RUN_TASKS {TIME_RUN_TASKS}")
    await Tortoise.init(config=orm_conf(host))
    
    while True:
        admin = await User.get_or_none(id=1)
        if admin:
            log.info(f'数据库测试成功-admin-{admin.username}')
        await clock(TIME_PULL_TASKS)
        ocr = Ocr()
        log.info("正在拉取任务...")
        # 拉取任务
        ids = await pull_morn_task()
        musers = [await new_muser_task(id, ocr) for id in ids]
        
        await clock(TIME_RUN_TASKS)
        await asyncio.gather(*musers)

        log.info("正在清理任务池...")
        await clean()
        log.info("今日任务完成")


def setup(host:str):
    uvloop.run(m_main(host=host))