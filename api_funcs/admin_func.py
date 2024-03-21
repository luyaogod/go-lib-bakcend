from models import User,Seat,Lib
from utils.create_uuid import generate_uuid
from settings import ADMIN_NAME

async def create_user(username):
    username = username
    uuid = generate_uuid()
    await User.create(username=username,uuid=uuid)

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

