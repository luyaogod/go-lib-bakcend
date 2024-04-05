import asyncio, random
import aiohttp
from datetime import datetime,timedelta
from models import User

#程序目的，在fastapi项目中创建一个全局queue
#fastapi的接口充当queue的消费者
#在项目中嵌入一个程序，每天到达指定时间创建一批消费者开始监听queue处理里面的任务并执行，并在一定时间后销毁消费者

KEEP_SPEED = 180

#任务-保持cookie存活
async def task(wx_cookie:str):
    setting = {
        "url":'http://wechat.v2.traceint.com/index.php/graphql/',
        "json":{"operationName": "index","query": "query index {\n userAuth {\n tongJi {\n rank\n allTime\n dayTime\n }\n config: user {\n feedback: getSchConfig(fields: \"adm.feedback\")\n }\n }\n}"},
        "headers":{"Cookie": wx_cookie,}
    }
    now = datetime.now()
    target = datetime(now.year, now.month, now.day, 19, 40, 0)
    result = True
    async with aiohttp.ClientSession() as session:
        count = 0
        while count < ((target-now).total_seconds() // KEEP_SPEED):
            try:
                async with session.post(url=setting["url"], headers=setting["headers"], json=setting["json"], ) as rep:
                    data = await rep.text()
                    if "errors" not in data:#cookie已失效
                        result = False
                        break
                    else:
                        count += 1
                        await asyncio.sleep(KEEP_SPEED)
            except Exception:
                result = False
                break
    await session.close()
    return result

#消费者
async def consumer(queue):
    while True:
        wx_cookie = await queue.get()
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
        now = datetime.now()
        begin_time = datetime(now.year, now.month, now.day, 17, 59, 0)
        await sleep_to(begin_time)
        users =  await User.all()
        consumer_size = len(users) #根据用户数量准备消费者
        consumers = [asyncio.create_task(consumer(COOKIE_KEEPER_QUEUE))
                     for _ in range(consumer_size)]
        end_time = datetime(now.year, now.month, now.day, 19, 40, 0)
        await sleep_to(end_time) #时间到清除所有的消费者
        for c in consumers:
            c.cancel()


async def virtual_fastApi_api_producer(queue):
    data = [
        "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjIxNDk5fQ.qqsSMJqhSqHTv2YVUeQ2AFyc0zBSB-fxnpMh5n0ll6bBfsat7Te20MLhZZxT98hFG9YQIqx2DUVUrX5bXACIaRdM-aSZ4sP3jgS7XwsfLro0YtzYP4O5hOuu5RdP4NK3MZ9sBE30MazczR9gMitjtkAEtUyxavTjHgvBAg9iWj6ncBywFbV3S5qnz9YxRRQteQkWTcgVNA5JRRBkvADOuwwEi4xmrEcmrRjh_4RzLRAEPacAwnKyZOTpIoapbRP8oPollCwI56f6F-Dg-32FRbnr8P1JaOZm2rrhxt1eRLCgEWZOn1wzW9Cn_l_m0VRiq6ps7B8zQNh8ipfy8mP8YA; SERVERID=d3936289adfff6c3874a2579058ac651|1712214300|1712214300; SERVERID=d3936289adfff6c3874a2579058ac651|1712214299|1712214299",
        "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjIxNDk5fQ.qqsSMJqhSqHTv2YVUeQ2AFyc0zBSB-fxnpMh5n0ll6bBfsat7Te20MLhZZxT98hFG9YQIqx2DUVUrX5bXACIaRdM-aSZ4sP3jgS7XwsfLro0YtzYP4O5hOuu5RdP4NK3MZ9sBE30MazczR9gMitjtkAEtUyxavTjHgvBAg9iWj6ncBywFbV3S5qnz9YxRRQteQkWTcgVNA5JRRBkvADOuwwEi4xmrEcmrRjh_4RzLRAEPacAwnKyZOTpIoapbRP8oPollCwI56f6F-Dg-32FRbnr8P1JaOZm2rrhxt1eRLCgEWZOn1wzW9Cn_l_m0VRiq6ps7B8zQNh8ipfy8mP8YA; SERVERID=d3936289adfff6c3874a2579058ac651|1712214300|1712214300; SERVERID=d3936289adfff6c3874a2579058ac651|1712214299|1712214299",
        "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjIxNDk5fQ.qqsSMJqhSqHTv2YVUeQ2AFyc0zBSB-fxnpMh5n0ll6bBfsat7Te20MLhZZxT98hFG9YQIqx2DUVUrX5bXACIaRdM-aSZ4sP3jgS7XwsfLro0YtzYP4O5hOuu5RdP4NK3MZ9sBE30MazczR9gMitjtkAEtUyxavTjHgvBAg9iWj6ncBywFbV3S5qnz9YxRRQteQkWTcgVNA5JRRBkvADOuwwEi4xmrEcmrRjh_4RzLRAEPacAwnKyZOTpIoapbRP8oPollCwI56f6F-Dg-32FRbnr8P1JaOZm2rrhxt1eRLCgEWZOn1wzW9Cn_l_m0VRiq6ps7B8zQNh8ipfy8mP8YA; SERVERID=d3936289adfff6c3874a2579058ac651|1712214300|1712214300; SERVERID=d3936289adfff6c3874a2579058ac651|1712214299|1712214299",
        "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjIxNDk5fQ.qqsSMJqhSqHTv2YVUeQ2AFyc0zBSB-fxnpMh5n0ll6bBfsat7Te20MLhZZxT98hFG9YQIqx2DUVUrX5bXACIaRdM-aSZ4sP3jgS7XwsfLro0YtzYP4O5hOuu5RdP4NK3MZ9sBE30MazczR9gMitjtkAEtUyxavTjHgvBAg9iWj6ncBywFbV3S5qnz9YxRRQteQkWTcgVNA5JRRBkvADOuwwEi4xmrEcmrRjh_4RzLRAEPacAwnKyZOTpIoapbRP8oPollCwI56f6F-Dg-32FRbnr8P1JaOZm2rrhxt1eRLCgEWZOn1wzW9Cn_l_m0VRiq6ps7B8zQNh8ipfy8mP8YA; SERVERID=d3936289adfff6c3874a2579058ac651|1712214300|1712214300; SERVERID=d3936289adfff6c3874a2579058ac651|1712214299|1712214299",
        "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjIxNDk5fQ.qqsSMJqhSqHTv2YVUeQ2AFyc0zBSB-fxnpMh5n0ll6bBfsat7Te20MLhZZxT98hFG9YQIqx2DUVUrX5bXACIaRdM-aSZ4sP3jgS7XwsfLro0YtzYP4O5hOuu5RdP4NK3MZ9sBE30MazczR9gMitjtkAEtUyxavTjHgvBAg9iWj6ncBywFbV3S5qnz9YxRRQteQkWTcgVNA5JRRBkvADOuwwEi4xmrEcmrRjh_4RzLRAEPacAwnKyZOTpIoapbRP8oPollCwI56f6F-Dg-32FRbnr8P1JaOZm2rrhxt1eRLCgEWZOn1wzW9Cn_l_m0VRiq6ps7B8zQNh8ipfy8mP8YA; SERVERID=d3936289adfff6c3874a2579058ac651|1712214300|1712214300; SERVERID=d3936289adfff6c3874a2579058ac651|1712214299|1712214299",
        "Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOjExMjY5MTI5LCJzY2hJZCI6MTAwMjUsImV4cGlyZUF0IjoxNzEyMjIxNDk5fQ.qqsSMJqhSqHTv2YVUeQ2AFyc0zBSB-fxnpMh5n0ll6bBfsat7Te20MLhZZxT98hFG9YQIqx2DUVUrX5bXACIaRdM-aSZ4sP3jgS7XwsfLro0YtzYP4O5hOuu5RdP4NK3MZ9sBE30MazczR9gMitjtkAEtUyxavTjHgvBAg9iWj6ncBywFbV3S5qnz9YxRRQteQkWTcgVNA5JRRBkvADOuwwEi4xmrEcmrRjh_4RzLRAEPacAwnKyZOTpIoapbRP8oPollCwI56f6F-Dg-32FRbnr8P1JaOZm2rrhxt1eRLCgEWZOn1wzW9Cn_l_m0VRiq6ps7B8zQNh8ipfy8mP8YA; SERVERID=d3936289adfff6c3874a2579058ac651|1712214300|1712214300; SERVERID=d3936289adfff6c3874a2579058ac651|1712214299|1712214299",
    ]
    for i in data:
        await queue.put(i)
        await asyncio.sleep(4)

async def virtual_fastpi_project_top_main():
    COOKIE_KEEPER_QUEUE = asyncio.Queue() #在项目中定义了一个全局队列
    task1 = asyncio.create_task(virtual_fastApi_api_producer(COOKIE_KEEPER_QUEUE)) #项目中有一个api充当生产者
    task2 = asyncio.create_task(cookies_keep_main(COOKIE_KEEPER_QUEUE))#它负责定时创建消费者处理任务
    tasks = [task1,task2]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # 定义一个全局的队列
    asyncio.run(virtual_fastpi_project_top_main())