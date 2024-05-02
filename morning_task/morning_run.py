from morning_task.morning_func import captcha_get_and_seat_get
import asyncio
from datetime import datetime
from models import User,Task,Morning_Task_Pool,Morning_Task_Ret
from settings import orm_conf,TIME_PULL_MORNING_TASK_FROM_POOL,TIME_MORNING_BOOK_GO
from tortoise import Tortoise
import ddddocr
from utils.clock import sleep_to

async def init(host):
    await Tortoise.init(
        config=orm_conf(host)
    )

async def user_all_seat(user):
    data =  await user.morning_seats.all().prefetch_related('lib')
    if not len(data)<1:
        seat_list = []
        for i in data:
            data_dict = {}
            data_dict['seat_data'] = dict(i)
            data_dict['seat_lib'] = dict(i.lib)
            seat_list.append(data_dict)
        return seat_list
    else:
        return None #用户无座位

async def user_all_seats_clean(data,is_book=True):
    task_data_list = []
    for i in data:
        data_dict = {}
        data_dict["lib_id"] = str(i["seat_lib"]["lib_id"])
        seat_key =i["seat_data"]["seat_key"]
        if is_book:
            pass
        else:
            seat_key =seat_key.replace(".","")
        data_dict["seat_key"] = seat_key
        task_data_list.append(data_dict)
    return task_data_list

async def pull_morning_tasks():
    task_list = []
    data_list = await Morning_Task_Pool.all()
    user_id_list = []
    for i in data_list:
        user_id_list.append(i.user_id)
    # 拿cookie
    tasks = await Task.filter(user__id__in=user_id_list)
    for i in tasks:
        task_item = {}
        task_item['user_id'] = i.user_id
        task_item['wx_cookie'] = i.wx_cookie
        # task_item['task_id'] = i.id
        user = await User.get_or_none(id=i.user_id)
        if user == None:
            task_item['seats'] = []
        else:
            data = await user_all_seat(user)
            if data == None:
                pass
            else:
                task_item['seats'] = await user_all_seats_clean(data, is_book=False)
                task_list.append(task_item)
    return task_list

async def create_workers(data_list):
    ocr = ddddocr.DdddOcr(show_ad=False)
    tasks = []
    for data in data_list:
        task = asyncio.create_task(captcha_get_and_seat_get(ocr=ocr,**data))
        tasks.append(task)
    if tasks == []: #今日没有任务
        return []
    else:
        ret = await asyncio.gather(*tasks)
    return ret

async def main(host):
    print(host)
    print('[MORNING BOOKER SETUP]')
    await init(host)


    print("[DB]:数据库连接测试...")
    user = await User.get_or_none(username='mario')
    if (user):
        print(f'[DB]:数据库连接成功,{user.username}')
    else:
        print('[DB]:数据库连接出错')

    while True:
        print("[DB]:数据库连接测试...")
        user = await User.get_or_none(username='mario')
        if (user):
            print(f'[DB]:数据库连接成功,{user.username}')
        else:
            print('[DB]:数据库连接出错')

        # 任务拉取和分配
        now = datetime.now()
        pull_time = datetime(now.year, now.month, now.day, *TIME_PULL_MORNING_TASK_FROM_POOL)
        await sleep_to(pull_time)
        print("[开始装载任务列表]",datetime.now())
        try:
            data_list = await pull_morning_tasks()
            # print(data_list) #测试输出
        except Exception as e:
            data_list = []
            print("[book_task-truck-error]:",e)
        # print(data_list) 测试输出

        #抢座tasks创建
        connect_time = datetime(now.year, now.month, now.day, *TIME_MORNING_BOOK_GO)
        await sleep_to(connect_time)
        print("[开始执行抢座任务]",datetime.now())
        ret =  await create_workers(data_list)
        print(ret)

        #更新数据库任务执行状态
        print("[更新数据库任务状态]",datetime.now())
        for r in ret:
            print("[任务状态]:",r)
            user = await User.get_or_none(id=r['user_id'])
            if r["result"]:
                #任务成功
                await Morning_Task_Ret.create(user=user, time=datetime.now().date(), status=1)
                user.balance -= 1
                await user.save()
            else:
                #任务失败
                await Morning_Task_Ret.create(user=user, time=datetime.now().date(), status=0)
        print("[今日任务结束]", datetime.now())
        await asyncio.sleep(3600) #测试使用!!!!!!

asyncio.run(main('localhost'))