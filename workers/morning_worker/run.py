from utils.clock import clock
from utils.ocr import Ocr
from .sql import Sql
from .funcs import MUser
from settings import mlog as log
import aiohttp
import uvloop
import asyncio
from .settings import *

async def m_task_main(db_host:str):
    async with aiohttp.ClientSession() as ses:
        #choice 3 ddddocr
        OCR = Ocr(ocr_choice=3, ses=ses) 
        log.info("早晨抢座启动.")
        log.info(f"TIME_PULL_TASK {TIME_PULL_TASKS}")
        log.info(f"TIME_RUN_TASKS {TIME_RUN_TASKS}")
        #创建数据库连接池
        sql = Sql(host=db_host)
        while True:
            await clock(TIME_PULL_TASKS)
            log.info("正在拉取任务..")
            # 拉取任务
            userids = await sql.pull_morning_ids()
            log.info( f"今日任务 {userids}")
            # 拉取用户数据
            user_infos =await sql.get_users_info(userids=userids , time=1)
            await clock(TIME_RUN_TASKS)
            # 创建user实例
            users:list[MUser] = []
            for user_info in user_infos:
                user = MUser(
                    id=user_info["id"],
                    username=user_info["username"],
                    wx_cookie=user_info["wx_cookie"],
                    seats=user_info["seats"],
                    ocr=OCR,
                    ses=ses
                )
                users.append(user)
            # 创建协程task
            await asyncio.gather(
                *[ user.tasks_group(sql) for user in users]
            )
            #处理任务结构
            for user in users:
                print(f"{user._username} {user._mret}")
                if user._mret:
                    await sql.reduce_balance(user_id=user._id)
                    await sql.add_ret(user._id, 1)
                else:
                    await sql.add_ret(user._id, 0)

def setup(host:str):
    uvloop.run(m_task_main(db_host=host))
