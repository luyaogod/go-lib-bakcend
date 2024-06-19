from utils.clock import clock
from utils.ocr import Ocr
from utils.sql import Sql
from .morning_func import MUser
from settings import mlog as log
import aiohttp
import asyncio

TIME_PULL_TASKS = [6,29,55]
TIME_RUN_TASKS= [6,30,0]

async def m_task_main():
    async with aiohttp.ClientSession() as ocr_ses:
        OCR = Ocr(ocr_choice=2, ses=ocr_ses)
        while True:
            connector = aiohttp.TCPConnector(limit_per_host=30)
            post_ses = aiohttp.ClientSession(connector=connector)
            log.info("Setup finished")
            await clock(TIME_PULL_TASKS)
            log.info("正在拉取任务..")
            sql = Sql()
            userids = sql.pull_morning_ids()
            log.debug(userids)
            user_infos = sql.get_users_info(userids=userids , time=1)
            await clock(TIME_RUN_TASKS)
            tasks = []
            log.info("正在执行任务...")
            users:list[MUser] = []
            for user_info in user_infos:
                user = MUser(
                    id=user_info["id"],
                    username=user_info["username"],
                    wx_cookie=user_info["wx_cookie"],
                    seats=user_info["seats"],
                    ocr=OCR,
                    ses=post_ses
                )
                users.append(user)
                task = asyncio.create_task(user.tasks_group())
                tasks.append(task)
            rets = await asyncio.gather(*tasks)
            for ret in rets:
                print(ret)
            for user in users:
                log.debug(await user.get_user_info())
            
            await post_ses.close()

def setup():
    asyncio.run(m_task_main())
