from utils.clock import clock
from utils.ocr import Ocr
from utils.sql import Sql
from .morning_func import MUser
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
        while True:
            # post_ses = aiohttp.ClientSession()
            await clock(TIME_PULL_TASKS)
            log.info("正在拉取任务..")
            sql = Sql(host=db_host)
            userids = sql.pull_morning_ids()
            log.info( f"今日任务 {userids}")
            user_infos = sql.get_users_info(userids=userids , time=1)
            await clock(TIME_RUN_TASKS)
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
            rets = await asyncio.gather(
                *[ user.tasks_group() for user in users]
            )
            for ret in rets:
                print(ret)
            for user in users:
                log.debug(await user.get_user_info())
                # if not user._ses.closed:
                #     await user._ses.close()
            
            # await post_ses.close()

def setup(host:str):
    uvloop.run(m_task_main(db_host=host))
