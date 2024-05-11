from models import Task_Pool,Task,User
from api_funcs.user_func import user_all_seat
from utils.clock import sleep_to
from settings import TIME_PUSH_TASK_IN_POOL,TIME_CLEAR_POOL
from datetime import datetime

async def get_pool_tasks():
    all_tasks_in_pool = await Task_Pool.all().prefetch_related('task')
    for i in all_tasks_in_pool:
        print(dict(i.task))

async def push_task_to_pool():
    tasks = await Task.all()
    for i in tasks:
        if (i.open == False):
            continue  # 任务为关闭状态
        if (i.status == 0):
            continue  # 失效cookie
        user = await User.get_or_none(id=i.user_id)
        if user == None:
            continue  # 用户不存在
        if user.balance<=0:
            continue #用户余额不足

        data = await user_all_seat(user)
        if data == None:
            continue
        await Task_Pool.create(task=i)


async def daily_task_pull_main(logger):
    logger.info("启动日常任务推送程序")
    while True:
        #推送任务进池
        now = datetime.now()
        push_time = datetime(now.year, now.month, now.day, *TIME_PUSH_TASK_IN_POOL)
        await sleep_to(push_time)
        logger.info(f"开始推送日常任务入池-{datetime.now()}")
        await push_task_to_pool()
        logger.info(f"推送完成")

        #清空池
        now = datetime.now()
        clear_time = datetime(now.year, now.month, now.day, *TIME_CLEAR_POOL)
        await sleep_to(clear_time)
        logger.info('开始清理任务池')
        await Task_Pool.all().delete()
        logger.info(f'任务池清理完毕-{datetime.now()}')
