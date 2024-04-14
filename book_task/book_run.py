from book_task.book_func import book
import asyncio
from datetime import datetime
from models import User,Task
from api_funcs.user_func import user_all_seat,user_all_seats_clean
from settings import TORTOISE_ORM,BOOK_TASK_PULL,BOOK_TASK_CONNECT,BOOK_TASK_CONNECT_ADJUST
from tortoise import Tortoise
from utils.clock import sleep_to

async def init():
    await Tortoise.init(
        config=TORTOISE_ORM
    )

async def tasks_truck():
    task_list = []
    tasks = await Task.all()
    for i in tasks:
        if (i.status == 0):
            continue  # 任务为关闭状态
        if (i.status == 4):
            continue  # 失效cookie
        user = await User.get_or_none(id=i.user_id)
        if user == None:
            continue  # 用户不存在

        task_item = {}
        task_item['task_id'] = i.id
        task_item['wx_cookie'] = i.wx_cookie

        data = await user_all_seat(user)
        if data == None:
            continue # 用户无座位
        task_item['seats'] = await user_all_seats_clean(data)
        task_list.append(task_item)
        i.add_time = datetime.now()
        i.status = 1 #设置为待执行状态
        await i.save()

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
        await sleep_to(connect_time,BOOK_TASK_CONNECT_ADJUST)
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
                    user = await User.get_or_none(pk=task.user_id)
                    user.balance -= 1
                    await user.save()
                else:
                    task.status = 3 #失败
                await task.save()
        print("[今日任务结束]", datetime.now())
        # await asyncio.sleep(30) #测试使用!!!!!!

if __name__ == "__main__":
    asyncio.run(main())