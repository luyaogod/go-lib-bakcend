import aiomysql
import asyncio
import uvloop
from settings import mlog as log
from .cancel import cancels_run
from .pool import db_config, morning, evening
from .settings import *

async def main_loop(host:str)->None:
    log.info("Group程序启动.")
    log.info(f"TIME_MORNING_CLEAN {TIME_MORNING_CLEAN}")
    log.info(f"TIME_EVE_PUSH {TIME_EVE_PUSH}")
    log.info(f"TIME_EVE_CLEAN {TIME_EVE_CLEAN}")
    log.info(f"TIME_SEAT_CLEAN {TIME_SEAT_CLEAN}")

    #建立数据库连接池
    config = db_config(host)
    db = await aiomysql.create_pool(loop=asyncio.get_event_loop(),**config)

    await asyncio.gather(
        morning(db),
        evening(db),
        cancels_run(db),
    )   

def setup(host:str):
    uvloop.run(main_loop(host))