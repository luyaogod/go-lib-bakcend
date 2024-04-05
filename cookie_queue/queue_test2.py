import asyncio, random
import aiohttp
from datetime import datetime,timedelta
from models import User

#程序目的，在fastapi项目中创建一个全局queue
#fastapi的接口充当queue的消费者
#在项目中嵌入一个程序，每天到达指定时间创建一批消费者开始监听queue处理里面的任务并执行，并在一定时间后销毁消费者

KEEP_SPEED = 180

#任务-保持cookie存活
async def task(wx_cookie:str): #预计每个任务将耗费40秒左右
    for i in range(6):
        print('[keep]:',wx_cookie,'-',datetime.now().time())
        await asyncio.sleep(10)

#消费者
async def consumer(queue):
    while True:
        wx_cookie = await queue.get()
        print('[我收到任务了]',wx_cookie)
        await task(wx_cookie)
        queue.task_done()

#定时器
async def sleep_to(target_time):
    now = datetime.now()
    if now > target_time:
        target_time += timedelta(days=1)
    remaining =  (target_time - now).total_seconds()
    await asyncio.sleep(remaining)

async def cookies_keep_main(COOKIE_KEEPER_QUEUE):
    while True:
        print('[等待到达预定时间]')
        now = datetime.now()
        # begin_time = datetime(now.year, now.month, now.day, 17, 21, 0)
        # await sleep_to(begin_time)
        print('[监听开始了]')
        consumers = [asyncio.create_task(consumer(COOKIE_KEEPER_QUEUE))
                     for _ in range(6)] #模拟准备6个消费者
        print('[消费者创建完成了]')
        end_time = datetime(now.year, now.month, now.day, 17, 26, 0)
        await sleep_to(end_time) #时间到清除所有的消费者
        print('[时间到清除消费者]')
        for c in consumers:
            c.cancel()


async def virtual_fastApi_api_producer(queue):
    data = [
        "cookie-1",
        "cookie-2",
        "cookie-3",
        "cookie-4",
        "cookie-5",
        "cookie-6",
    ]
    for i in data:
        await queue.put(i)
        print("[新任务]",i)
        await asyncio.sleep(5) #模拟一直有新任务被生产

async def virtual_fastpi_project_top_main():
    COOKIE_KEEPER_QUEUE = asyncio.Queue() #在项目中定义了一个全局队列
    task1 = asyncio.create_task(virtual_fastApi_api_producer(COOKIE_KEEPER_QUEUE)) #项目中有一个api充当生产者
    task2 = asyncio.create_task(cookies_keep_main(COOKIE_KEEPER_QUEUE))#它负责定时创建消费者处理任务
    tasks = [task1,task2]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # 定义一个全局的队列
    asyncio.run(virtual_fastpi_project_top_main())