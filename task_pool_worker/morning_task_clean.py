from datetime import datetime
from utils.clock import sleep_to
from settings import TIME_CLEAR_MORNING_TASK_POOL
from models import Morning_Task_Pool

async def morning_pool_clean_main():
    print('INFO:    [启动MorningPool清理程序]')
    # 清理Morning任务池
    while True:
        now = datetime.now()
        push_time = datetime(now.year, now.month, now.day, *TIME_CLEAR_MORNING_TASK_POOL)
        await sleep_to(push_time)
        print("[清理Morning任务池]")
        await Morning_Task_Pool.all().delete()
        print("[任务池清理完毕]")