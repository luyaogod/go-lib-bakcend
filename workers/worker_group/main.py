import aiomysql
import asyncio
import uvloop
from .cancel import cancels_run
from .pool import db_config, morning, evening

async def main_loop(host:str)->None:
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