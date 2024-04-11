from book_task.book_func import book
import asyncio
from datetime import datetime
from models import User,Task
from api_funcs.user_func import user_all_seat,user_all_seats_clean
from settings import TORTOISE_ORM,BOOK_TASK_PULL,BOOK_TASK_CONNECT
from tortoise import Tortoise
from utils.clock import sleep_to

async def init():
    await Tortoise.init(
        config=TORTOISE_ORM
    )

async def tasks_truck():
    today = datetime.now().date()
    task_list = []
    tasks = await Task.all()
    for i in tasks:
        if not (i.add_time.date() == today):
            continue #不是今天的任务
        task_item = {}
        task_item['task_id'] = i.id
        task_item['wx_cookie'] = i.wx_cookie
        user = await User.get_or_none(id=i.user_id)
        if not user:
            continue
        else:
            data = await user_all_seat(user)
            if data:
                clean_data = await user_all_seats_clean(data)
            else:
                # 用户没保存座位
                no_seat_task = await Task.get_or_none(user=user)
                if no_seat_task:
                    no_seat_task.status = 3  # 设置状态为任务失败
                    await no_seat_task.save()
                continue
            task_item['seats'] = clean_data
        task_list.append(task_item)
    return task_list

async def tasks_worker(data_list):
    tasks = []
    for data in data_list:
        task = asyncio.create_task(book(**data))
        tasks.append(task)
    if tasks == []: #今日没有任务
        return []
    else:
        ret = await asyncio.gather(*tasks)
    return ret

async def main():
    while True:
        #任务拉取
        now = datetime.now()
        pull_time = datetime(now.year, now.month, now.day, *BOOK_TASK_PULL)
        await sleep_to(pull_time)
        print("[开始装载任务列表]",datetime.now())
        # await init() #数据库初始化，测试用的!!!!!!
        try:
            data_list = await tasks_truck()
            # print(data_list) #测试输出
        except Exception as e:
            data_list = []
            print("[book_task-truck-error]:",e)

        #抢座tasks创建
        connect_time = datetime(now.year, now.month, now.day, *BOOK_TASK_CONNECT)
        await sleep_to(connect_time)
        print("[开始连接WS]",datetime.now())
        ret =  await tasks_worker(data_list)
        # print("[任务执行结果]:",ret)

        #更新数据库任务执行状态
        print("[更新数据库任务状态]",datetime.now())
        for r in ret:
            print("[任务状态]:",r)
            task = await Task.get_or_none(id = r["task_id"])
            if task:
                if r["result"]:
                    task.status = 2 #成功
                else:
                    task.status = 3 #失败
                await task.save()
        print("[今日任务结束]", datetime.now())
        # await asyncio.sleep(30) #测试使用!!!!!!

if __name__ == "__main__":
    asyncio.run(main())