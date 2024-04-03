from models import User,Task
from utils.create_uuid import generate_uuid
from settings import ADMIN_NAME

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

