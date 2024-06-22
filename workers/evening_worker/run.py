import asyncio
from aiohttp import ClientSession
from .funcs import EUser
from .sql import Sql
from .settings import *
from settings import mlog as log
from utils import clock

async def main_loop(
    host:str,
    worker_size:int,
    worker_id:int,
):
    log.info("早晨任务启动.")
    log.info(f"HOST {host}")
    log.info(f"WORKER_SIZE {worker_size}")
    log.info(f"WORKER_ID {worker_id}")
    log.info(f"TIME_WS_CONNECT {TIME_PULL_TASK}")
    log.info(f"TIME_WS_CONNECT {TIME_WS_CONNECT}")
    log.info(f"TIME_WS_SEND {TIME_WS_SEND}")

    db = Sql(host=host)
    await db._get_pool()
    ses:ClientSession
    async with ClientSession() as ses:
        while True:
            log.info("等待预定时间到达...")
            await clock(TIME_PULL_TASK)
            log.info("正在拉取任务...")
            user_ids = await db.pull_eve_ids(
                worker_size=worker_size,
                worker_id=worker_id
            )
            log.info(f"今日任务 {user_ids}")
            user_infos = await db.pull_users_info(user_ids)
            log.debug(user_infos)
            log.info("正在创建任务实例...")
            eusers:list[EUser] = []
            for  info in user_infos:
                euser = EUser(
                    id=info["id"],
                    username=info["username"],
                    cookie=info["wx_cookie"],
                    seats=info["seats"],
                    ses=ses
                )
                eusers.append(euser)
            await clock(TIME_WS_CONNECT)
            log.info("正在连接ws...")
            ret = asyncio.gather(
                *[euser.do_chain(db=db) for euser in eusers]
            )
            #总任务时长不超过TASKS_TIMEOUT
            try:
                await asyncio.wait_for(ret, timeout=TASKS_TIMEOUT)
            except asyncio.TimeoutError:
                log.warning('任务超时！')
            log.info("今日任务完成...")

async def one_time_task(
    host:str,
    user_id:int
):
    log.info("任务启动.")
    log.info(f"USER {user_id}")
    log.info(f"HOST {host}")
    log.info(f"TIME_WS_CONNECT {TIME_PULL_TASK}")
    log.info(f"TIME_WS_CONNECT {TIME_WS_CONNECT}")
    log.info(f"TIME_WS_SEND {TIME_WS_SEND}")
    db = Sql(host=host)
    await db._get_pool()
    ses:ClientSession
    async with ClientSession() as ses:
        log.info("等待预定时间到达...")
        await clock(TIME_PULL_TASK)
        log.info("正在拉取任务...")
        info = await db.get_user_info(userid=user_id)
        log.debug(info)
        log.info("正在创建任务实例...")
        euser = EUser(
                id=info["id"],
                username=info["username"],
                cookie=info["wx_cookie"],
                seats=info["seats"],
                ses=ses
            )
        await euser.do_chain(db=db)
        await ses.close()
       

def setup(
    host:str,
    worker_size:int,
    worker_id:int,
):
    asyncio.run(main_loop(host, worker_size, worker_id))

def one_time_setup(
    host:str,
    user_id:int
):
    asyncio.run(one_time_task(host,user_id))
