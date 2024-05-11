from datetime import datetime
from utils.clock import sleep_to
from settings import TIME_CLEAR_MORNING_TASK_POOL
from models import Morning_Task_Pool


async def morning_pool_clean_main(logger):
    logger.info('MorningPool清理程序')
    while True:
        now = datetime.now()
        push_time = datetime(now.year, now.month, now.day, *TIME_CLEAR_MORNING_TASK_POOL)
        await sleep_to(push_time)
        logger.info('正在清理MorningPool')
        await Morning_Task_Pool.all().delete()
        logger.info('MorningPool清理完毕')
