import asyncio, random
import aiohttp
from datetime import datetime,timedelta
from models import User

KEEP_SPEED = 180

#任务-保持cookie存活
async def task(wx_cookie):
    #测试-wxcookie结构{wx_cookie:"",id:""}
    setting = {
        "url":'http://wechat.v2.traceint.com/index.php/graphql/',
        "json":{"operationName": "index","query": "query index {\n userAuth {\n tongJi {\n rank\n allTime\n dayTime\n }\n config: user {\n feedback: getSchConfig(fields: \"adm.feedback\")\n }\n }\n}"},
        "headers":{"Cookie": wx_cookie["wx_cookie"],}
    }

    async with aiohttp.ClientSession() as session:
        count = 0
        while count < 10:
            try:
                async with session.post(url=setting["url"], headers=setting["headers"], json=setting["json"], ) as rep:
                    data = await rep.text()
                    if "errors" not in data:#cookie已失效
                        print("[cookie已失效]:",wx_cookie["id"]) #测试标记
                        result = False
                        break
                    else:
                        print("[cookie存活]:",wx_cookie["id"]) #测试标记
                        count += 1
                        await asyncio.sleep(KEEP_SPEED)
            except Exception:
                print("[请求异常]")
                result = False
                break
    await session.close()
    return result

#消费者
async def consumer(queue):
    while True:
        wx_cookie = await queue.get()
        print("[我收到任务了]",wx_cookie["wx_cookie"])
        await task(wx_cookie)
        queue.task_done()

#定时器
async def sleep_to(target_time):
    now = datetime.now()
    if now > target_time:
        target_time += timedelta(days=1)
    remaining =  (target_time - now).total_seconds()
    await asyncio.sleep(remaining)


async def main(COOKIE_KEEPER_QUEUE):
    while True:
        print("[等待预定时间]")
        now = datetime.now()
        begin_time = datetime(now.year, now.month, now.day, 17, 59, 0)
        await sleep_to(begin_time)
        print("[监听开始]")
        users =  await User.all()
        consumer_size = len(users) #根据用户数量准备消费者
        print("[消费者组准备完成]")
        consumers = [asyncio.create_task(consumer(COOKIE_KEEPER_QUEUE))
                     for _ in range(consumer_size)]
        end_time = datetime(now.year, now.month, now.day, 19, 40, 0)
        print("[到达预定结束时间]")
        await sleep_to(end_time) #时间到清除所有的消费者
        for c in consumers:
            c.cancel()
        print("[清除消费者组]")

