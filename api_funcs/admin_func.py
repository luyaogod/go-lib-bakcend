from models import User,Task,Task_Ret,Morning_Task_Pool,Morning_Task_Ret
from utils.create_uuid import generate_uuid
from settings import ADMIN_NAME
from datetime import datetime,timedelta

async def create_user(username,balance):
    uuid = generate_uuid()
    await User.create(username=username,balance=balance,uuid=uuid)

async def update_user(user_id,username,balance):
    user = await User.get_or_none(id = user_id)
    if not user:
        return False
    user.username = username
    user.balance = balance
    await user.save()
    return True

async def delete_user(user_id):
    if user_id == 1:
        return -100
    user = await User.get_or_none(id = user_id)
    if user:
        if user.username == ADMIN_NAME:
            return None
        else:
            username = user.username
            await user.delete()
            return username
    else:
        return None

async def get_all_user():
    users = await User.all().values()
    try:
        for user in users:
            user['uuid'] = str(user['uuid'])
    except Exception:
        return []
    return users

async def get_all_task():
    tasks = await Task.all().prefetch_related("user")
    ret_list = []
    for task in tasks:
        task_dict = dict(task)
        task_dict["username"] = task.user.username
        task_dict.pop('wx_cookie',None)
        ret_list.append(task_dict)
    return ret_list

async def task_ret(offset:int):
    #offset为0为当日，每+1减一天
    now = datetime.now().date()
    interval = timedelta(days=offset)
    ret = await Task_Ret.filter(time=now-interval).all().order_by('-time').prefetch_related('user')
    rep_data = []
    for i in ret:
        dataItem = dict(i)
        dataItem['username'] = i.user.username
        rep_data.append(dataItem)
    return rep_data

#全部早上任务
async def get_all_task_morning():
    dataList =[]
    morning_tasks = await Morning_Task_Pool.all().prefetch_related('user')
    for i in morning_tasks:
        dataList.append(i.user.username)
    return dataList

#全部早上任务结果
async def task_ret_morning(offset:int):
    #offset为0为当日，每+1减一天
    now = datetime.now().date()
    interval = timedelta(days=offset)
    ret = await Morning_Task_Ret.filter(time=now-interval).all().order_by('-time').prefetch_related('user')
    rep_data = []
    for i in ret:
        dataItem = dict(i)
        dataItem['username'] = i.user.username
        rep_data.append(dataItem)
    return rep_data
